import os
import re

import bugsnag
from bugsnag.notification import Notification

from labels.config import utils
from labels.config.context import BASE_DIR, CI_COMMIT_SHORT_SHA


def _remove_nix_hash(path: str) -> str:
    pattern = r"(\/nix\/store\/[a-z0-9]{32}-)"
    result = re.search(pattern, path)
    if not result:
        return path
    return path[result.end(0) :]


def bugsnag_remove_nix_hash(
    notification: Notification,
) -> None:
    notification.stacktrace = [
        {**trace, "file": _remove_nix_hash(trace["file"])} for trace in notification.stacktrace
    ]


def bugsnag_add_batch_metadata(
    notification: Notification,
) -> None:
    if batch_job_id := os.environ.get("AWS_BATCH_JOB_ID"):
        batch_job_info = {"batch_job_id": batch_job_id}
        notification.add_tab("batch_job_info", batch_job_info)


def initialize_bugsnag() -> None:
    bugsnag.before_notify(bugsnag_add_batch_metadata)
    bugsnag.before_notify(bugsnag_remove_nix_hash)
    bugsnag.configure(
        notify_release_stages=["production"],
        release_stage=utils.guess_environment(),
        app_version=CI_COMMIT_SHORT_SHA,
        project_root=BASE_DIR,
        send_environment=True,
    )
    bugsnag.start_session()

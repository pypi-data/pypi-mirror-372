from os import environ
from typing import Literal


def get_artifact_from_env(env_var: str) -> str | None:
    if value := environ.get(env_var):
        return value
    return None


def guess_environment() -> Literal["development", "production"]:
    return (
        "production"
        if environ.get("AWS_BATCH_JOB_ID") or environ.get("CI_COMMIT_REF_NAME") == "trunk"
        else "development"
    )

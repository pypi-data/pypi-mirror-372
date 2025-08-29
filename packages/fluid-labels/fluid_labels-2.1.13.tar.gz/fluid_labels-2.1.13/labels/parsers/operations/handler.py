from collections.abc import Callable

import reactivex
from reactivex import (
    Observable,
)
from reactivex import (
    operators as ops,
)
from reactivex.scheduler import (
    ThreadPoolScheduler,
)

from labels.model.parser import Request
from labels.parsers.cataloger.cpp.cataloger import (
    on_next_cpp,
)
from labels.parsers.cataloger.dart.cataloger import (
    on_next_dart,
)
from labels.parsers.cataloger.db_parser import (
    on_next_db_file,
)
from labels.parsers.cataloger.dotnet.cataloger import (
    on_next_dotnet,
)
from labels.parsers.cataloger.elixir.cataloger import (
    on_next_elixir,
)
from labels.parsers.cataloger.github.cataloger import (
    on_next_github_action,
)
from labels.parsers.cataloger.golang.cataloger import (
    on_next_golang,
)
from labels.parsers.cataloger.java.cataloger import (
    on_next_java,
)
from labels.parsers.cataloger.javascript.cataloger import (
    on_next_javascript,
)
from labels.parsers.cataloger.php.cataloger import (
    on_next_php,
)
from labels.parsers.cataloger.python.cataloger import (
    on_next_python,
)
from labels.parsers.cataloger.redhat.cataloger import (
    on_next_redhat,
)
from labels.parsers.cataloger.ruby.cataloger import (
    on_next_ruby,
)
from labels.parsers.cataloger.rust.cataloger import (
    on_next_rust,
)
from labels.parsers.cataloger.swift.cataloger import (
    on_next_swift,
)


def handle_parser(
    scheduler: ThreadPoolScheduler,
) -> Callable[[Observable[str]], Observable[Request]]:
    def _apply_parsers(source: Observable[str]) -> Observable[Request]:
        return source.pipe(
            ops.flat_map(
                lambda item: reactivex.merge(  # type: ignore[arg-type, return-value]
                    (on_next_python(reactivex.just(item, scheduler))),
                    (on_next_db_file(reactivex.just(item, scheduler))),
                    (on_next_java(reactivex.just(item, scheduler))),
                    (on_next_javascript(reactivex.just(item, scheduler))),
                    (on_next_redhat(reactivex.just(item, scheduler))),
                    (on_next_dotnet(reactivex.just(item, scheduler))),
                    (on_next_rust(reactivex.just(item, scheduler))),
                    (on_next_ruby(reactivex.just(item, scheduler))),
                    (on_next_elixir(reactivex.just(item, scheduler))),
                    (on_next_php(reactivex.just(item, scheduler))),
                    (on_next_swift(reactivex.just(item, scheduler))),
                    (on_next_dart(reactivex.just(item, scheduler))),
                    (on_next_cpp(reactivex.just(item, scheduler))),
                    (on_next_golang(reactivex.just(item, scheduler))),
                    (on_next_github_action(reactivex.just(item, scheduler))),
                ),
            ),
        )

    return _apply_parsers

import logging
import re
from collections.abc import Iterator
from contextlib import suppress
from typing import cast

import tree_sitter_toml
from more_itertools import mark_ends
from tree_sitter import Language as TLanguage
from tree_sitter import Node, Parser

from labels.model.indexables import IndexedDict, IndexedList, ParsedValue
from labels.utils.exceptions import DuplicatedKeyError, InvalidTypeError, UnexpectedNodeError

LOGGER = logging.getLogger(__name__)
EMPTY_DICT: IndexedDict[str, ParsedValue] = IndexedDict()


def _validate_key_pairs(root_node: Node) -> bool:
    all_children_pairs = tuple(
        node.start_point[0] for node in root_node.children if node.type == "pair"
    )
    return len(all_children_pairs) == len(set(all_children_pairs))


def handle_string(node: Node) -> str:
    value = node.text.decode("utf-8") if node.text else ""
    str_quote = "'" if value.startswith("'") else None
    str_quote = str_quote or ('"' if value.startswith('"') else None)
    if str_quote and (value.startswith(str_quote)) and (value.endswith(str_quote)):
        value = value.strip(str_quote)
        # Remove surrounding triple quotes if present
        value = re.sub(r'"""|\'\'\'', "", value)

        value = value.strip()

    return value


def handle_array(node: Node) -> IndexedList[ParsedValue]:
    data: IndexedList[ParsedValue] = IndexedList(node)
    for children_node in node.children:
        if children_node.type in ("[", "]", ",", "comment"):
            continue
        node_results = handle_node(children_node)
        if not isinstance(node_results, tuple):
            data.append((node_results, children_node))
    return data


def handle_bare_key(node: Node) -> str:
    return handle_string(node)


def handle_quoted_key(node: Node) -> str:
    value = handle_string(node)
    if value.startswith(('"', "'")):
        return value[1:-1]
    return value


def handle_dotted_key(node: Node) -> list[str]:
    value = handle_string(node)
    parts = cast("list[str]", re.findall(r'"[^"]*"|[\w-]+', value))
    return [part.strip('" ') for part in parts]


def handle_table_array_element(
    node: Node,
) -> tuple[tuple[ParsedValue, Node], IndexedDict[str, ParsedValue]]:
    data: IndexedDict[str, ParsedValue] = IndexedDict(node)
    bare_key = node.named_children[0]
    bare_key_value = handle_node(bare_key)
    if isinstance(bare_key_value, tuple):
        return (None, bare_key), data

    # the children's are pair nods
    for children_node in node.named_children[1:]:
        if children_node.type in ("[", "]", ", ", "comment"):
            continue
        if children_node.type != "pair":
            LOGGER.error("Unexpected node: %s", children_node)
            continue
        node_results = handle_node(children_node)
        if isinstance(node_results, tuple):
            key, value = node_results
            if isinstance(key[0], str):
                data[(key[0], key[1])] = value
    return (bare_key_value, bare_key), data


def handle_pair(node: Node) -> tuple[tuple[ParsedValue, Node], tuple[ParsedValue, Node]]:
    bare_key_node, value_node = node.named_children[:2]
    bare_key_value = handle_node(bare_key_node)
    value_resolved = handle_node(value_node)
    if isinstance(bare_key_value, tuple) or isinstance(value_resolved, tuple):
        return (None, bare_key_node), (None, value_node)
    return (bare_key_value, bare_key_node), (value_resolved, value_node)


def handle_boolean(node: Node) -> bool:
    value = node.text.decode("utf-8") if node.text else ""
    return value.lower() == "true"


def handle_integer(node: Node) -> int:
    decode_str = node.text.decode("utf-8") if node.text else ""
    with suppress(ValueError):
        return int(decode_str)
    with suppress(ValueError):
        return int(decode_str, 16)
    with suppress(ValueError):
        return int(decode_str, 8)

    error_msg = f"Invalid integer value: {decode_str}"
    raise ValueError(error_msg)


def handle_float(node: Node) -> float:
    decoded_str = node.text.decode("utf-8") if node.text else ""
    with suppress(ValueError):
        return float(decoded_str)

    with suppress(ValueError):
        return float(decoded_str.replace(".", "").lower())

    error_msg = f"Invalid float value: {decoded_str}"
    raise ValueError(error_msg)


def handle_local_date(node: Node) -> str:
    return handle_string(node)


def handle_inline_table(node: Node) -> IndexedDict[str, ParsedValue]:
    data: IndexedDict[str, ParsedValue] = IndexedDict(node)
    for children_node in node.named_children:
        node_results = handle_node(children_node)
        if isinstance(node_results, tuple):
            key, value = node_results
            if isinstance(key[0], str | list):
                nested_dict(
                    data=data,
                    keys=key[0],
                    keys_node=key[1],
                    value=value[0],
                    value_node=value[1],
                )
    return data


def handle_table(node: Node, data_1: IndexedDict[str, ParsedValue]) -> None:
    data_new: IndexedDict[str, ParsedValue] = IndexedDict(node)
    for children_node in node.named_children[1:]:
        if children_node.type == "comment":
            continue
        node_results = handle_node(children_node)
        if isinstance(node_results, tuple):
            key, value = node_results
            if isinstance(key[0], str | list):
                nested_dict(
                    data=data_new,
                    keys=key[0],
                    keys_node=key[1],
                    value=value[0],
                    value_node=value[1],
                )
    bare_key_node = node.named_children[0]
    bare_key_value = handle_node(bare_key_node)
    if isinstance(bare_key_value, list):
        nested_dict(
            data=data_1,
            keys=bare_key_value,
            keys_node=bare_key_node,
            value=data_new,
            value_node=node,
        )
    elif isinstance(bare_key_value, str):
        data_1[(bare_key_value, bare_key_node)] = (
            data_new,
            node,
        )


def handle_node(  # noqa: C901, PLR0912
    node: Node,
) -> ParsedValue | tuple[tuple[ParsedValue, Node], tuple[ParsedValue, Node]]:
    value: ParsedValue | tuple[tuple[ParsedValue, Node], tuple[ParsedValue, Node]] = None
    match node.type:
        case "comment":
            value = None
        case "string":
            value = handle_string(node)
        case "array":
            value = handle_array(node)
        case "pair":
            value = handle_pair(node)
        case "bare_key":
            value = handle_bare_key(node)
        case "quoted_key":
            value = handle_quoted_key(node)
        case "dotted_key":
            value = handle_dotted_key(node)
        case "boolean":
            value = handle_boolean(node)
        case "integer":
            value = handle_integer(node)
        case "float":
            value = handle_float(node)
        case "inline_table":
            value = handle_inline_table(node)
        case "local_date":
            value = handle_local_date(node)
        case _:
            raise UnexpectedNodeError(node.type)

    return value


def _nested_dict_handle_list(data: ParsedValue) -> ParsedValue:
    if not isinstance(data, IndexedDict):
        if not isinstance(data, IndexedList):
            error_msg = "Attempted to extend non-table type"
            raise InvalidTypeError(error_msg)
        data = data[-1]
    return data


def _nested_dict_validate_duplicated_data(
    data: IndexedDict[str, ParsedValue],
    key: str,
    *,
    is_last: bool,
) -> None:
    def _check_for_duplicates(
        data: IndexedDict[str, ParsedValue],
        key: str,
        *,
        is_last: bool,
    ) -> None:
        if is_last and key in data:
            raise DuplicatedKeyError(key)

    try:
        _check_for_duplicates(data, key, is_last=is_last)
    except DuplicatedKeyError:
        LOGGER.exception(
            "Duplicated key detected: %s",
            key,
            extra={
                "extra": {
                    "key": key,
                    "is_last": is_last,
                },
            },
        )


def nested_dict(
    *,
    data: IndexedDict[str, ParsedValue],
    keys: list[str] | str,
    keys_node: Node,
    value: ParsedValue = None,
    value_node: Node | None = None,
) -> None:
    build_key = []
    for _, is_last, key in _mark_ends(keys):
        build_key.append(key)
        data_result = _nested_dict_handle_list(data)
        if not isinstance(data_result, IndexedDict):
            continue
        data = data_result

        _nested_dict_validate_duplicated_data(data, key, is_last=is_last)
        if key not in data:
            if is_last:
                data[(key, keys_node)] = (
                    value if value is not None else IndexedDict(),
                    value_node or keys_node,
                )
                continue
            data[(key, keys_node)] = (IndexedDict(), value_node or keys_node)
        data = data[key]  # type: ignore[assignment]


def _mark_ends(keys: list[str] | str) -> Iterator[tuple[bool, bool, str]]:
    yield from mark_ends(keys if isinstance(keys, list) else [keys])


def _nested_list_handle_list(data: ParsedValue) -> ParsedValue:
    if isinstance(data, IndexedList):
        data = data[-1]
    return data


def _nested_list_handle_fists_keys(
    data: IndexedDict[str, ParsedValue],
    key: str,
    *,
    is_last: bool,
) -> bool:
    return key not in data and not is_last


def _nested_list_handle_last_keys(
    data: IndexedDict[str, ParsedValue],
    key: str,
    *,
    is_last: bool,
) -> bool:
    return key not in data and is_last


def _nested_list_handle_fists_keys_exists(
    data: IndexedDict[str, ParsedValue],
    key: str,
    *,
    is_last: bool,
) -> bool:
    return key in data and not is_last


def _nested_list(  #  noqa: PLR0913
    *,
    data: IndexedDict[str, ParsedValue],
    key: str,
    is_last: bool,
    keys_node: Node,
    build_key: list[str],
    value: ParsedValue = None,
    value_node: Node | None = None,
) -> None:
    if is_last:  # if the doted key is the last, the item is a value to append
        try:
            data[key].append((value, value_node or keys_node))  # type: ignore[union-attr, arg-type]
        except AttributeError:
            LOGGER.exception("Attempted to extend non-table type: %s", ".".join(build_key))
            return
        return
    data_val = data[key]
    if isinstance(data_val, IndexedDict):
        data = data_val


def nested_list(
    *,
    data: IndexedDict[str, ParsedValue],
    keys: list[str] | str,
    keys_node: Node,
    value: ParsedValue = None,
    value_node: Node | None = None,
) -> None:
    build_key = []
    for _, is_last, key in _mark_ends(keys):
        build_key.append(key)
        data_result = _nested_list_handle_list(data)
        if not isinstance(data_result, IndexedDict):
            continue
        data = data_result
        if _nested_list_handle_fists_keys(data, key, is_last=is_last):
            data[(key, keys_node)] = (IndexedDict(), value_node or keys_node)
            dict_value = data[key]
            if isinstance(dict_value, IndexedDict):
                data = dict_value
            continue
        if _nested_list_handle_fists_keys_exists(data, key, is_last=is_last):
            data = data[key]  # type: ignore[assignment]
            continue

        if _nested_list_handle_last_keys(data, key, is_last=is_last):
            data[(key, keys_node)] = (
                IndexedList(keys_node),
                value_node or keys_node,
            )

        _nested_list(
            data=data,
            key=key,
            is_last=is_last,
            keys_node=keys_node,
            build_key=build_key,
            value=value,
            value_node=value_node,
        )


def _process_node(node: Node, data: IndexedDict[str, ParsedValue]) -> None:
    if node.type == "pair":
        node_results = handle_node(node)
        if isinstance(node_results, tuple):
            key, value = node_results
            if isinstance(key[0], str | list):
                nested_dict(
                    data=data,
                    keys=key[0],
                    keys_node=key[1],
                    value=value[0],
                    value_node=value[1],
                )
    elif node.type == "table":
        handle_table(node, data)
    elif node.type == "table_array_element":
        key, table_value = handle_table_array_element(node)
        if isinstance(key[0], str | list):
            nested_list(
                data=data,
                keys=key[0],
                keys_node=key[1],
                value=table_value,
                value_node=node,
            )
    elif node.type == "ERROR":
        raise UnexpectedNodeError(node)


def parse_toml_with_tree_sitter(toml_content: str) -> IndexedDict[str, ParsedValue]:
    parser_language = TLanguage(tree_sitter_toml.language())
    parser = Parser(parser_language)
    result = parser.parse(toml_content.encode("utf-8"))
    data: IndexedDict[str, ParsedValue] = IndexedDict(result.root_node)
    if result.root_node.type != "document":
        return data
    if not _validate_key_pairs(result.root_node):
        LOGGER.error("Invalid document", extra={"extra": {"toml_content": toml_content}})
        return IndexedDict()
    for node in result.root_node.children:
        try:
            _process_node(node=node, data=data)
        except (UnexpectedNodeError, ValueError, InvalidTypeError) as exc:
            LOGGER.exception(
                "Error processing node of type '%s'",
                node.type,
                extra={"extra": {"node_type": node.type, "toml": toml_content}},
                exc_info=exc,
            )
    return data

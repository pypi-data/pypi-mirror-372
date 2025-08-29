import logging
import re
from contextlib import suppress

import tree_sitter_yaml
from tree_sitter import Language as TLanguage
from tree_sitter import Node, Parser

from labels.model.indexables import FileCoordinate, IndexedDict, IndexedList, ParsedValue, Position
from labels.utils.exceptions import (
    UnexpectedChildrenLengthError,
    UnexpectedNodeError,
    UnexpectedNodeTypeError,
)

LOGGER = logging.getLogger(__name__)


def _generate_position(node: Node) -> Position:
    return Position(
        start=FileCoordinate(line=node.start_point[0] + 1, column=node.start_point[1] + 1),
        end=FileCoordinate(line=node.end_point[0] + 1, column=node.end_point[1] + 1),
    )


def _handle_block_mapping_node(
    node: Node,
) -> tuple[Node, IndexedDict[str, ParsedValue]]:
    def _check_expected_children_structure(childs: tuple[Node, ...], node: Node) -> None:
        if childs[1].type != ":":
            raise UnexpectedChildrenLengthError(node, 3)

    data: IndexedDict[str, ParsedValue] = IndexedDict(node)
    for child in node.children:
        if child.type != "block_mapping_pair":
            continue
        childs = tuple(x for x in child.children if x.type != "comment")
        if len(childs) != 3:
            childs = (*childs, None)  # type: ignore[arg-type]
            try:
                _check_expected_children_structure(childs, node)
            except UnexpectedChildrenLengthError as exc:
                LOGGER.exception(
                    "Unexpected child node structure. Expected 3 children, but got %d",
                    len(childs),
                    exc_info=exc,
                    extra={
                        "node": node,
                        "childs": childs,
                    },
                )
                continue
        key_up_node, _, value_up_node = childs
        key_node, key_value = handle_node(key_up_node)
        if value_up_node is None:
            data[  # type: ignore[unreachable]
                (
                    key_value,
                    _generate_position(key_node),
                )
            ] = (
                None,
                None,
            )
            continue
        if not isinstance(key_value, str):
            continue
        value_node, value_value = handle_node(value_up_node)
        data[(key_value, _generate_position(key_node))] = (
            value_value,
            _generate_position(value_node),
        )
    return node, data


def _handle_flow_mapping_node(node: Node) -> tuple[Node, IndexedDict[str, ParsedValue]]:
    pair_nodes = [x for x in node.children if x.type == "flow_pair"]
    data: IndexedDict[str, ParsedValue] = IndexedDict(node)
    for pair_node in pair_nodes:
        if len(pair_node.children) != 3:
            raise UnexpectedNodeError(pair_node)
        key_up_node, _, value_up_node = pair_node.children
        key_node, key_value = handle_node(key_up_node)
        value_node, value_value = handle_node(value_up_node)
        if not isinstance(key_value, str):
            continue
        data[(key_value, _generate_position(key_node))] = (
            value_value,
            _generate_position(value_node),
        )
    return node, data


def _handle_boolean_scalar_node(node: Node) -> tuple[Node, bool]:
    node_string_value = node.text.decode("utf-8").lower() if node.text else "false"
    return node, node_string_value == "true"


def _handle_block_sequence_node(
    node: Node,
) -> tuple[Node, IndexedList[ParsedValue]]:
    data: IndexedList[ParsedValue] = IndexedList(node)
    for child in (x for x in node.children if x.type != "comment"):
        if child.type != "block_sequence_item":
            raise UnexpectedNodeTypeError(child.type, "block_sequence_item")
        resolved_item = handle_node(child)
        data.append((resolved_item[1], _generate_position(resolved_item[0])))
    return node, data


def _handle_block_sequence_item(node: Node) -> tuple[Node, ParsedValue]:
    if len(node.children) != 2 or node.children[0].type != "-":
        raise UnexpectedNodeTypeError(node)
    return handle_node(node.children[1])


def _handle_integer_scalar_node(node: Node) -> tuple[Node, int]:
    decode_str = node.text.decode("utf-8") if node.text else ""
    with suppress(ValueError):
        return node, int(decode_str)
    with suppress(ValueError):
        return node, int(decode_str, 16)

    error_msg = f"Invalid integer value: {decode_str}"
    raise ValueError(error_msg)


def _handle_flow_sequence_node(
    node: Node,
) -> tuple[Node, IndexedList[ParsedValue]]:
    data: IndexedList[ParsedValue] = IndexedList(node)
    for child in [x for x in node.children if x.type not in ("[", "]", ",")]:
        if child.type != "flow_node":
            raise UnexpectedNodeTypeError(child.type, "flow_node")
        resolved_node, resolved_item = handle_node(child)
        data.append((resolved_item, _generate_position(resolved_node)))
    return node, data


def _handle_float_scalar_node(node: Node) -> tuple[Node, float]:
    decoded_str = node.text.decode("utf-8") if node.text else ""
    with suppress(ValueError):
        return node, float(decoded_str)

    with suppress(ValueError):
        return node, float(decoded_str.replace(".", "").lower())

    error_msg = f"Invalid float value: {decoded_str}"
    raise ValueError(error_msg)


def _handle_block_scalar(node: Node) -> tuple[Node, str]:
    decoded_str = node.text.decode("utf-8") if node.text else ""
    value = ""
    if match := re.search(r"^>(\d+)", decoded_str):
        indent_spaces = int(match.group(1))
        decoded_str = re.sub(r"^>\d+", "", decoded_str).strip()
    else:
        indent_spaces = 1  # Default to no indent removal if no marker is found

    if decoded_str.startswith(">"):
        value = (" " * indent_spaces).join(decoded_str.lstrip(">+-").strip().split())
    elif decoded_str.startswith("|"):
        normalized_str = decoded_str.replace("\xa0", " ").lstrip("|+-")
        value = "\n".join(line.strip() for line in normalized_str.split("\n"))
        value = value.replace("\n", "", 1)
    return node, value


def _handle_block_node(node: Node) -> tuple[Node, ParsedValue]:
    if len(node.children) > 1:
        raise UnexpectedChildrenLengthError(node.type, 1)
    return handle_node(node.children[0])


def _handle_flow_node(node: Node) -> tuple[Node, ParsedValue]:
    if len(node.children) > 1:
        raise UnexpectedChildrenLengthError(node.type, 1)
    return handle_node(node.children[0])


def _handle_plain_scalar(node: Node) -> tuple[Node, ParsedValue]:
    if len(node.children) > 1:
        raise UnexpectedChildrenLengthError(node.type, 1)
    return handle_node(node.children[0])


def _handle_string_scalar(node: Node) -> tuple[Node, str]:
    return node, node.text.decode("utf-8") if node.text else ""


def _handle_quote_scalar(node: Node) -> tuple[Node, str]:
    return node, node.text.decode("utf-8").strip("'\"") if node.text else ""


def _handle_null_scalar(node: Node) -> tuple[Node, None]:
    return node, None


_NODE_HANDLERS = {
    "block_node": _handle_block_node,
    "block_mapping": _handle_block_mapping_node,
    "flow_node": _handle_flow_node,
    "plain_scalar": _handle_plain_scalar,
    "string_scalar": _handle_string_scalar,
    "single_quote_scalar": _handle_quote_scalar,
    "double_quote_scalar": _handle_quote_scalar,
    "float_scalar": _handle_float_scalar_node,
    "flow_mapping": _handle_flow_mapping_node,
    "boolean_scalar": _handle_boolean_scalar_node,
    "null_scalar": _handle_null_scalar,
    "integer_scalar": _handle_integer_scalar_node,
    "block_sequence_item": _handle_block_sequence_item,
    "block_sequence": _handle_block_sequence_node,
    "flow_sequence": _handle_flow_sequence_node,
    "block_scalar": _handle_block_scalar,
}


def _handle_node_result(
    node_result: tuple[Node, ParsedValue | Exception],
) -> tuple[Node, ParsedValue]:
    node, value = node_result
    if isinstance(value, Exception):
        raise value
    return node, value


def handle_node(node: Node) -> tuple[Node, ParsedValue]:
    handler = _NODE_HANDLERS.get(node.type)
    if handler is None:
        raise UnexpectedNodeError(node.type)

    try:
        return _handle_node_result(handler(node))
    except Exception as e:
        if isinstance(
            e,
            UnexpectedNodeError
            | ValueError
            | UnexpectedNodeTypeError
            | UnexpectedChildrenLengthError,
        ):
            raise
        raise UnexpectedNodeError(node.type) from e


def parse_yaml_with_tree_sitter(content: str) -> ParsedValue | None:
    parser_language = TLanguage(tree_sitter_yaml.language())
    parser = Parser(parser_language)
    result = parser.parse(content.encode("utf-8"))
    documents = [x for x in result.root_node.children if x.type == "document"]
    if len(documents) != 1:
        return None
    block_node = next((x for x in documents[0].children if x.type == "block_node"), None)
    if not block_node:
        return None
    try:
        _, value = handle_node(block_node)
    except (
        UnexpectedNodeError,
        ValueError,
        UnexpectedNodeTypeError,
        UnexpectedChildrenLengthError,
    ):
        LOGGER.exception(
            "Failed to handle block node of type '%s' while parsing YAML content",
            block_node.type,
            extra={"extra": {"node_type": block_node.type, "yaml": content}},
        )
        return None
    return value

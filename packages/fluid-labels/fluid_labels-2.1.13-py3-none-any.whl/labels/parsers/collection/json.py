import logging

import tree_sitter_json
from tree_sitter import Language as TLanguage
from tree_sitter import Node, Parser

from labels.model.indexables import IndexedDict, IndexedList, ParsedValue

LOGGER = logging.getLogger(__name__)


def _handle_array_node(node: Node) -> tuple[Node, IndexedList[ParsedValue]]:
    data: IndexedList[ParsedValue] = IndexedList(node)
    for child in node.children:
        if child.type not in ("[", "]", ","):
            if not (parsed_node := handle_json_node(child)):
                continue
            value_node, value = parsed_node
            data.append((value, value_node))
    return node, data


def _handle_object_node(node: Node) -> tuple[Node, IndexedDict[str, ParsedValue]]:
    data: IndexedDict[str, ParsedValue] = IndexedDict(node)
    for child in node.children:
        if child.type == "pair":
            key_n, _, value_n = child.children
            if not key_n.text:
                continue
            key = key_n.text[1:-1].decode("utf-8")
            if not (parsed_node := handle_json_node(value_n)):
                continue
            value_node, value_value = parsed_node
            data[(key, key_n)] = (value_value, value_node)
    return node, data


def handle_json_node(node: Node) -> tuple[Node, ParsedValue] | None:
    value: tuple[Node, ParsedValue]
    match node.type:
        case "array":
            value = _handle_array_node(node)
        case "object":
            value = _handle_object_node(node)
        case "string":
            node_value = node.text[1:-1].decode("utf-8") if node.text else ""
            value = node, node_value
        case "number":
            node_value = node.text.decode("utf-8") if node.text else "0"
            try:
                value = node, int(node_value)
            except ValueError:
                value = node, float(node_value)
        case "true":
            value = node, True
        case "false":
            value = node, False
        case "null":
            value = node, None
        case _:
            LOGGER.debug("Ignoring unexpected node type encountered: %s", node.type)
            return None
    return value


def parse_json_with_tree_sitter(
    json: str,
) -> ParsedValue:
    parser_language = TLanguage(tree_sitter_json.language())
    parser = Parser(parser_language)
    result = parser.parse(json.encode("utf-8"))
    value: ParsedValue = IndexedDict()
    for child in result.root_node.children:
        if not (parsed_node := handle_json_node(child)):
            continue
        value = parsed_node[1]

    if json and (value is None or not isinstance(value, IndexedDict | IndexedList)):
        LOGGER.error("JSON parsing failed.", extra={"extra": {"json": json}})
        return IndexedDict()
    return value

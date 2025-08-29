import logging
from collections.abc import Iterator
from itertools import count

import networkx as nx
import tree_sitter_python
import tree_sitter_swift
from tree_sitter import Language, Node, Parser, Tree

LOGGER = logging.getLogger(__name__)

PYTHON_FIELDS = {
    "aliased_import": ["alias", "name"],
    "as_pattern": ["alias"],
    "assignment": ["left", "right", "type"],
    "attribute": ["attribute", "object"],
    "augmented_assignment": ["left", "operator", "right"],
    "binary_operator": ["left", "operator", "right"],
    "block": ["alternative"],
    "boolean_operator": ["left", "operator", "right"],
    "call": ["arguments", "function"],
    "case_clause": ["consequence", "guard"],
    "class_definition": ["body", "name", "superclasses", "type_parameters"],
    "comparison_operator": ["operators"],
    "decorated_definition": ["definition"],
    "default_parameter": ["name", "value"],
    "dict_pattern": ["key", "value"],
    "dictionary_comprehension": ["body"],
    "elif_clause": ["condition", "consequence"],
    "else_clause": ["body"],
    "except_clause": ["alias", "value"],
    "exec_statement": ["code"],
    "for_in_clause": ["left", "right"],
    "for_statement": ["alternative", "body", "left", "right"],
    "format_expression": ["expression", "format_specifier", "type_conversion"],
    "function_definition": ["body", "name", "parameters", "return_type", "type_parameters"],
    "future_import_statement": ["name"],
    "generator_expression": ["body"],
    "if_statement": ["alternative", "condition", "consequence"],
    "import_from_statement": ["module_name", "name"],
    "import_statement": ["name"],
    "interpolation": ["expression", "format_specifier", "type_conversion"],
    "keyword_argument": ["name", "value"],
    "lambda": ["body", "parameters"],
    "list_comprehension": ["body"],
    "match_statement": ["body", "subject"],
    "named_expression": ["name", "value"],
    "not_operator": ["argument"],
    "pair": ["key", "value"],
    "print_statement": ["argument"],
    "raise_statement": ["cause"],
    "set_comprehension": ["body"],
    "subscript": ["subscript", "value"],
    "try_statement": ["body"],
    "type_alias_statement": ["left", "right"],
    "typed_default_parameter": ["name", "type", "value"],
    "typed_parameter": ["type"],
    "unary_operator": ["argument", "operator"],
    "while_statement": ["alternative", "body", "condition"],
    "with_item": ["value"],
    "with_statement": ["body"],
}

SWIFT_FIELDS: dict[str, list[str]] = {
    "additive_expression": ["lhs", "op", "rhs"],
    "array_literal": ["element"],
    "array_type": ["element", "name"],
    "as_expression": ["expr", "name", "type"],
    "assignment": ["operator", "result", "target"],
    "associatedtype_declaration": ["default_value", "must_inherit", "name"],
    "await_expression": ["expr"],
    "bitwise_operation": ["lhs", "op", "rhs"],
    "call_suffix": ["name"],
    "capture_list_item": ["name", "value"],
    "catch_block": ["error"],
    "check_expression": ["name", "op", "target", "type"],
    "class_declaration": ["body", "declaration_kind", "name"],
    "comparison_expression": ["lhs", "op", "rhs"],
    "conjunction_expression": ["lhs", "op", "rhs"],
    "constructor_expression": ["constructed_type"],
    "constructor_suffix": ["name"],
    "control_transfer_statement": ["result"],
    "deinit_declaration": ["body"],
    "dictionary_literal": ["key", "value"],
    "dictionary_type": ["key", "name", "value"],
    "disjunction_expression": ["lhs", "op", "rhs"],
    "enum_entry": ["data_contents", "name", "raw_value"],
    "enum_type_parameters": ["name"],
    "equality_constraint": ["constrained_type", "must_equal", "name"],
    "equality_expression": ["lhs", "op", "rhs"],
    "for_statement": ["collection", "item"],
    "function_declaration": ["body", "default_value", "name", "return_type"],
    "function_type": ["name", "params", "return_type"],
    "guard_statement": ["bound_identifier", "condition", "name"],
    "if_statement": ["bound_identifier", "condition", "name"],
    "infix_expression": ["lhs", "op", "rhs"],
    "inheritance_constraint": ["constrained_type", "inherits_from", "name"],
    "inheritance_specifier": ["inherits_from"],
    "init_declaration": ["body", "default_value", "name"],
    "interpolated_expression": ["name", "reference_specifier", "value"],
    "lambda_function_type": ["name", "return_type"],
    "lambda_literal": ["captures", "type"],
    "lambda_parameter": ["external_name", "name", "type"],
    "line_string_literal": ["interpolation", "text"],
    "macro_declaration": ["default_value", "definition"],
    "macro_definition": ["body"],
    "multi_line_string_literal": ["interpolation", "text"],
    "multiplicative_expression": ["lhs", "op", "rhs"],
    "navigation_expression": ["element", "suffix", "target"],
    "navigation_suffix": ["suffix"],
    "nil_coalescing_expression": ["if_nil", "value"],
    "open_end_range_expression": ["start"],
    "open_start_range_expression": ["end"],
    "optional_type": ["wrapped"],
    "parameter": ["external_name", "name", "type"],
    "pattern": ["bound_identifier", "name"],
    "postfix_expression": ["operation", "target"],
    "prefix_expression": ["operation", "target"],
    "property_declaration": ["computed_value", "name", "value"],
    "protocol_body": ["body"],
    "protocol_declaration": ["body", "declaration_kind", "name"],
    "protocol_function_declaration": ["default_value", "name", "return_type"],
    "protocol_property_declaration": ["name"],
    "range_expression": ["end", "op", "start"],
    "raw_str_interpolation": ["interpolation"],
    "raw_string_literal": ["interpolation", "text"],
    "repeat_while_statement": ["bound_identifier", "condition", "name"],
    "subscript_declaration": ["default_value", "name", "return_type"],
    "suppressed_constraint": ["suppressed"],
    "switch_statement": ["expr"],
    "ternary_expression": ["condition", "if_false", "if_true"],
    "try_expression": ["expr"],
    "tuple_expression": ["name", "value"],
    "tuple_type": ["element"],
    "tuple_type_item": ["element", "name", "type"],
    "type_annotation": ["name", "type"],
    "type_arguments": ["name"],
    "type_parameter": ["name"],
    "typealias_declaration": ["name", "value"],
    "value_argument": ["name", "reference_specifier", "value"],
    "value_binding_pattern": ["mutability"],
    "while_statement": ["bound_identifier", "condition", "name"],
}


class Graph(nx.DiGraph):
    pass


NId = str
NAttrs = dict[str, str | int]


class ParsingError(Exception):
    pass


PARSER_LANGUAGES: dict[str, Language] = {
    "python": Language(tree_sitter_python.language()),
    "swift": Language(tree_sitter_swift.language()),
}


LANGUAGE_FIELDS: dict[str, dict[str, list[str]]] = {
    "python": PYTHON_FIELDS,
    "swift": SWIFT_FIELDS,
}


def hash_node(node: Node) -> int:
    return hash((node.end_point, node.start_point, node.type))


def _build_ast_graph(
    *,
    content: bytes,
    node: Node,
    counter: Iterator[str],
    graph: Graph,
    language: str,
    _edge_index: str | None = None,
    _parent: str | None = None,
    _parent_fields: dict[int, str] | None = None,
) -> Graph:
    if not isinstance(node, Node) or node.has_error:
        raise ParsingError

    n_id = next(counter)
    raw_l, raw_c = node.start_point

    graph.add_node(n_id, label_l=raw_l + 1, label_c=raw_c + 1, label_type=node.type)

    if _parent is not None:
        graph.add_edge(_parent, n_id, label_ast="AST", label_index=_edge_index)
        if field := (_parent_fields or {}).get(hash_node(node)):
            graph.nodes[_parent][f"label_field_{field}"] = n_id

    if not node.children:
        # Extract the text from it
        node_content = content[node.start_byte : node.end_byte]
        graph.nodes[n_id]["label_text"] = node_content.decode("latin-1")

    if node.children:
        # It's not a final node, recurse
        for edge_index, child in enumerate(node.children):
            _build_ast_graph(
                content=content,
                node=child,
                counter=counter,
                graph=graph,
                language=language,
                _edge_index=str(edge_index),
                _parent=n_id,
                _parent_fields={
                    hash_node(child): fld
                    for fld in LANGUAGE_FIELDS[language].get(node.type, ())
                    for child in [node.child_by_field_name(fld)]
                    if child
                },
            )

    return graph


def parse_ast_graph(content: bytes, language: str) -> Graph | None:
    parser_language = PARSER_LANGUAGES.get(language)
    if not parser_language:
        LOGGER.warning("Unable to parse content for language %s", language)
        return None
    parser = Parser(parser_language)
    raw_tree: Tree = parser.parse(content)
    node: Node = raw_tree.root_node

    counter = map(str, count(1))
    try:
        return _build_ast_graph(
            content=content,
            node=node,
            counter=counter,
            graph=Graph(),
            language=language,
        )
    except ParsingError:
        return None


def adj_lazy(
    graph: Graph,
    n_id: NId,
    depth: int = 1,
) -> Iterator[NId]:
    """Return adjacent nodes to `n_id`, following just edges with given attrs.

    - Parameter `depth` may be -1 to indicate infinite depth.
    - Search is done breadth first.
    - Nodes are returned ordered ascending by index on each level.

    This function must be used instead of graph.adj, because graph.adj
    becomes unstable (unordered) after mutating the graph.
    """
    if depth == 0:
        return

    childs: list[str] = sorted(graph.adj[n_id], key=int)

    # Append direct childs
    yield from childs

    # Recurse into childs
    if depth < 0 or depth > 1:
        for c_id in childs:
            yield from adj_lazy(
                graph,
                c_id,
                depth=depth - 1,
            )


def adj(
    graph: Graph,
    n_id: NId,
    depth: int = 1,
) -> tuple[NId, ...]:
    return tuple(adj_lazy(graph, n_id, depth=depth))


def iter_childs(graph: Graph, n_id: str) -> Iterator[str]:
    for c_id in adj(graph, n_id):
        yield from iter_childs(graph, c_id)
    yield n_id


def lazy_text_childs(graph: Graph, n_id: str) -> Iterator[str]:
    for c_id in iter_childs(graph, n_id):
        if "label_text" in graph.nodes[c_id]:
            yield c_id


def lazy_childs_text(graph: Graph, n_id: str) -> Iterator[str]:
    for c_id in lazy_text_childs(graph, n_id):
        yield graph.nodes[c_id]["label_text"]


def node_to_str(graph: Graph, n_id: str, sep: str = "") -> str:
    return sep.join(lazy_childs_text(graph, n_id))

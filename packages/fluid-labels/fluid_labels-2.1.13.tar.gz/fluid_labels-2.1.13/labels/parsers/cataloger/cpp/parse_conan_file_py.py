import ast
from collections.abc import Iterator
from contextlib import suppress
from copy import deepcopy

from labels.model.file import Location, LocationReadCloser
from labels.model.package import Package
from labels.model.relationship import Relationship
from labels.model.release import Environment
from labels.model.resolver import Resolver
from labels.parsers.cataloger.cpp.package import new_conan_file_py_dep
from labels.parsers.cataloger.graph_parser import Graph, NId, adj, node_to_str, parse_ast_graph


def get_method_requirements(
    *,
    graph: Graph,
    method_id: NId,
    location: Location,
    is_dev: bool,
    requires_attributes: dict[str, str],
) -> Iterator[Package]:
    childs = adj(graph, method_id, depth=-1)
    requirements_nodes = [
        child for child in childs if graph.nodes[child].get("label_type") == "call"
    ]
    for req_node in requirements_nodes:
        node_attrs = graph.nodes[req_node]
        if (c_id := node_attrs.get("label_field_function")) and node_to_str(
            graph,
            c_id,
        ) != requires_attributes["method_requires"]:
            continue
        req_args_id = graph.nodes[req_node]["label_field_arguments"]
        req_args = adj(graph, req_args_id)
        yield new_conan_file_py_dep(
            graph=graph,
            node_id=req_args[1],
            location=location,
            is_dev=is_dev,
        )


def get_attr_requirements(
    *,
    graph: Graph,
    attr_info: dict,
    location: Location,
    is_dev: bool,
) -> Iterator[Package]:
    with suppress(SyntaxError):
        val_id = attr_info["label_field_right"]
        requires_info = graph.nodes[val_id]

        if requires_info["label_type"] == "string":
            requires_eval = ast.literal_eval(node_to_str(graph, val_id))
            yield new_conan_file_py_dep(
                graph=graph,
                node_id=val_id,
                dep_info=requires_eval,
                location=location,
                is_dev=is_dev,
            )
        elif requires_info["label_type"] == "expression_list":
            requires_eval = adj(graph, val_id)
            for require in requires_eval:
                if graph.nodes[require].get("label_type") != "string":
                    continue
                dep_info = node_to_str(graph, require)
                yield new_conan_file_py_dep(
                    graph=graph,
                    node_id=val_id,
                    location=location,
                    is_dev=is_dev,
                    dep_info=dep_info,
                )
        elif requires_info["label_type"] == "list":
            arr_elements_ids = adj(graph, val_id)
            for elem_id in arr_elements_ids:
                elem_attrs = graph.nodes[elem_id]
                if elem_attrs["label_type"] not in {
                    "string",
                    "list",
                    "tuple",
                    "parenthesized_expression",
                }:
                    continue
                if elem_attrs["label_type"] in {"list", "tuple", "parenthesized_expression"}:
                    elem_id = adj(graph, elem_id)[1]  # noqa: PLW2901
                yield new_conan_file_py_dep(
                    graph=graph,
                    node_id=elem_id,
                    is_dev=is_dev,
                    location=location,
                )


def _resolve_deps(
    *,
    graph: Graph,
    conan_class_id: NId,
    location: Location,
    is_dev: bool,
    requires_attributes: dict[str, str],
) -> Iterator[Package]:
    class_block_id = graph.nodes[conan_class_id]["label_field_body"]

    for n_id in adj(graph, class_block_id):
        n_attrs = graph.nodes[n_id]
        if (
            n_attrs["label_type"] == "expression_statement"
            and (child := adj(graph, n_id)[0])
            and graph.nodes[child]["label_type"] == "assignment"
            and (left_id := graph.nodes[child].get("label_field_left"))
            and graph.nodes[left_id].get("label_text") == requires_attributes["requires"]
        ):
            yield from get_attr_requirements(
                graph=graph,
                attr_info=graph.nodes[child],
                location=location,
                is_dev=is_dev,
            )
        elif (
            n_attrs["label_type"] == "function_definition"
            and (name_id := graph.nodes[n_id].get("label_field_name"))
            and graph.nodes[name_id].get("label_text") == requires_attributes["requirements"]
        ):
            yield from get_method_requirements(
                graph=graph,
                method_id=n_id,
                location=location,
                is_dev=is_dev,
                requires_attributes=requires_attributes,
            )


def parse_conan_file_py(
    _: Resolver | None,
    __: Environment | None,
    reader: LocationReadCloser,
) -> tuple[list[Package], list[Relationship]]:
    packages: list[Package] = []
    content = reader.read_closer.read().encode("utf-8")
    if not content or not (graph := parse_ast_graph(content, "python")):
        return [], []
    conan_class_id = None
    for node in graph.nodes:
        if graph.nodes[node].get("label_type") != "class_definition":
            continue
        al_id = graph.nodes[node].get("label_field_superclasses")
        if al_id and any(
            graph.nodes[arg_id].get("label_text") == "ConanFile" for arg_id in adj(graph, al_id)
        ):
            conan_class_id = node
            break
    location = deepcopy(reader.location)
    if not conan_class_id:
        return [], []

    packages.extend(
        _resolve_deps(
            graph=graph,
            conan_class_id=conan_class_id,
            location=location,
            is_dev=False,
            requires_attributes={
                "requires": "requires",
                "requirements": "requirements",
                "method_requires": "self.requires",
            },
        ),
    )

    packages.extend(
        _resolve_deps(
            graph=graph,
            conan_class_id=conan_class_id,
            location=location,
            is_dev=True,
            requires_attributes={
                "requires": "tool_requires",
                "requirements": "build_requirements",
                "method_requires": "self.tool_requires",
            },
        ),
    )
    return packages, []

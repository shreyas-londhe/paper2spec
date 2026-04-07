#!/usr/bin/env python3
"""
Cross-reference dependency graph builder for paper2spec.

Parses extracted environments (from extract_environments.py) and builds
a dependency DAG showing which theorems/protocols reference which definitions/lemmas.

Usage:
    python build_dependency_graph.py <environments.json> [--output graph.json]
"""

import json
import sys
import argparse
from pathlib import Path
from collections import defaultdict


def build_label_index(data: dict) -> dict[str, dict]:
    """Build a lookup from label -> environment/section/equation."""
    index = {}
    for env in data['environments']:
        if env['label']:
            index[env['label']] = {
                'type': env['env_type'],
                'name': env['name'],
                'line_start': env['line_start'],
                'line_end': env['line_end'],
            }
    for sec in data['sections']:
        if sec['label']:
            index[sec['label']] = {
                'type': f"section:{sec['level']}",
                'name': sec['title'],
                'line_start': sec['line_number'],
                'line_end': sec['line_number'],
            }
    for eq in data['equations']:
        if eq['label']:
            index[eq['label']] = {
                'type': 'equation',
                'name': eq['label'],
                'line_start': eq['line_start'],
                'line_end': eq['line_end'],
            }
    return index


def build_dependency_graph(data: dict) -> dict:
    """Build a dependency graph from environments' cross-references."""
    label_index = build_label_index(data)

    # Edges: from_label -> [to_labels]
    edges = defaultdict(set)

    for env in data['environments']:
        if not env['label']:
            continue
        for ref in env['cross_refs']:
            if ref in label_index and ref != env['label']:
                edges[env['label']].add(ref)

    # Build the graph
    nodes = {}
    for label, info in label_index.items():
        nodes[label] = {
            'type': info['type'],
            'name': info['name'],
            'lines': f"{info['line_start']}-{info['line_end']}",
        }

    edge_list = []
    for source, targets in edges.items():
        for target in sorted(targets):
            edge_list.append({
                'from': source,
                'to': target,
                'from_type': nodes.get(source, {}).get('type', '?'),
                'to_type': nodes.get(target, {}).get('type', '?'),
            })

    # Compute protocol dependency chains
    protocol_deps = {}
    for env in data['environments']:
        if env['env_type'] == 'protocol' and env['label']:
            deps = set()
            visited = set()
            stack = list(env['cross_refs'])
            while stack:
                ref = stack.pop()
                if ref in visited or ref not in label_index:
                    continue
                visited.add(ref)
                deps.add(ref)
                # Follow transitive deps
                for env2 in data['environments']:
                    if env2['label'] == ref:
                        stack.extend(env2['cross_refs'])
            protocol_deps[env['label']] = sorted(deps)

    # Topological ordering (simple: sort by line number)
    ordered = sorted(nodes.keys(), key=lambda l: nodes[l]['lines'])

    return {
        'nodes': nodes,
        'edges': edge_list,
        'protocol_dependencies': protocol_deps,
        'topological_order': ordered,
        'summary': {
            'total_nodes': len(nodes),
            'total_edges': len(edge_list),
            'protocols': [l for l, n in nodes.items() if n['type'] == 'protocol'],
            'theorems': [l for l, n in nodes.items() if n['type'] == 'theorem'],
        },
    }


def print_ascii_graph(graph: dict) -> None:
    """Print a readable ASCII dependency graph."""
    nodes = graph['nodes']
    edges = graph['edges']

    # Group edges by source
    by_source = defaultdict(list)
    for e in edges:
        by_source[e['from']].append(e)

    print("\n=== Dependency Graph ===\n")
    for label in graph['topological_order']:
        node = nodes[label]
        deps = by_source.get(label, [])
        name_str = f" [{node['name']}]" if node['name'] else ""
        print(f"  {node['type']:12s} {label}{name_str}")
        for dep in deps:
            target = nodes.get(dep['to'], {})
            target_name = f" [{target.get('name', '')}]" if target.get('name') else ""
            print(f"    -> {dep['to']}{target_name}")

    if graph['protocol_dependencies']:
        print("\n=== Protocol Dependency Chains ===\n")
        for proto, deps in graph['protocol_dependencies'].items():
            print(f"  {proto}:")
            for d in deps:
                node = nodes.get(d, {})
                print(f"    - {d} ({node.get('type', '?')})")


def main():
    parser = argparse.ArgumentParser(description='Build cross-reference dependency graph')
    parser.add_argument('input', help='Input environments.json from extract_environments.py')
    parser.add_argument('--output', '-o', help='Output graph JSON file')
    args = parser.parse_args()

    data = json.loads(Path(args.input).read_text())
    graph = build_dependency_graph(data)

    if args.output:
        Path(args.output).write_text(json.dumps(graph, indent=2, ensure_ascii=False))
        print(f"Wrote graph to {args.output}", file=sys.stderr)

    print_ascii_graph(graph)


if __name__ == '__main__':
    main()

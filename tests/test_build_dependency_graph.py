"""Tests for build_dependency_graph.py"""
import sys
import os
import json
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from build_dependency_graph import build_label_index, build_dependency_graph


SAMPLE_DATA = {
    "environments": [
        {
            "env_type": "protocol",
            "label": "proto:main",
            "name": "Main Protocol",
            "line_start": 100,
            "line_end": 150,
            "content": "...",
            "cross_refs": ["def:field", "thm:soundness"]
        },
        {
            "env_type": "definition",
            "label": "def:field",
            "name": "Field Definition",
            "line_start": 10,
            "line_end": 20,
            "content": "...",
            "cross_refs": []
        },
        {
            "env_type": "theorem",
            "label": "thm:soundness",
            "name": "Soundness",
            "line_start": 200,
            "line_end": 220,
            "content": "...",
            "cross_refs": ["def:field"]
        },
    ],
    "sections": [
        {"level": "section", "title": "Intro", "label": "sec:intro", "line_number": 1}
    ],
    "equations": [
        {"label": "eq:main", "content": "E=mc^2", "line_start": 50, "line_end": 52}
    ],
}


class TestBuildLabelIndex:
    def test_indexes_environments(self):
        index = build_label_index(SAMPLE_DATA)
        assert "proto:main" in index
        assert "def:field" in index
        assert "thm:soundness" in index

    def test_indexes_sections(self):
        index = build_label_index(SAMPLE_DATA)
        assert "sec:intro" in index

    def test_indexes_equations(self):
        index = build_label_index(SAMPLE_DATA)
        assert "eq:main" in index

    def test_skips_unlabeled(self):
        data = {"environments": [
            {"env_type": "lemma", "label": None, "name": None,
             "line_start": 1, "line_end": 5, "content": "...", "cross_refs": []}
        ], "sections": [], "equations": []}
        index = build_label_index(data)
        assert len(index) == 0


class TestBuildDependencyGraph:
    def test_finds_edges(self):
        graph = build_dependency_graph(SAMPLE_DATA)
        edge_pairs = {(e["from"], e["to"]) for e in graph["edges"]}
        assert ("proto:main", "def:field") in edge_pairs
        assert ("proto:main", "thm:soundness") in edge_pairs
        assert ("thm:soundness", "def:field") in edge_pairs

    def test_protocol_deps(self):
        graph = build_dependency_graph(SAMPLE_DATA)
        assert "proto:main" in graph["protocol_dependencies"]
        deps = graph["protocol_dependencies"]["proto:main"]
        assert "def:field" in deps
        assert "thm:soundness" in deps

    def test_transitive_deps(self):
        graph = build_dependency_graph(SAMPLE_DATA)
        # proto:main -> thm:soundness -> def:field (transitive)
        deps = graph["protocol_dependencies"]["proto:main"]
        assert "def:field" in deps

    def test_empty_input(self):
        data = {"environments": [], "sections": [], "equations": []}
        graph = build_dependency_graph(data)
        assert graph["summary"]["total_nodes"] == 0
        assert graph["summary"]["total_edges"] == 0

    def test_summary(self):
        graph = build_dependency_graph(SAMPLE_DATA)
        assert graph["summary"]["total_nodes"] > 0
        assert "proto:main" in graph["summary"]["protocols"]
        assert "thm:soundness" in graph["summary"]["theorems"]

"""Tests for extract_environments.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from extract_environments import extract_environments, extract_sections, extract_equations


SAMPLE_TEX = r"""
\begin{theorem}[Soundness]
\label{thm:soundness}
If the prover cheats, the verifier rejects with high probability.
See \cref{lem:helper} for details.
\end{theorem}

\begin{lemma}
\label{lem:helper}
A helper lemma.
\end{lemma}

\begin{protocol}[Sumcheck]
\label{proto:sumcheck}
Round 1: Prover sends $g_1$.
\end{protocol}

\begin{definition}[RS Code]
\label{def:rs}
The Reed-Solomon code.
\end{definition}
"""


class TestExtractEnvironments:
    def test_finds_all_types(self):
        envs = extract_environments(SAMPLE_TEX)
        types = {e.env_type for e in envs}
        assert "theorem" in types
        assert "lemma" in types
        assert "protocol" in types
        assert "definition" in types

    def test_extracts_labels(self):
        envs = extract_environments(SAMPLE_TEX)
        labels = {e.label for e in envs if e.label}
        assert "thm:soundness" in labels
        assert "lem:helper" in labels
        assert "proto:sumcheck" in labels
        assert "def:rs" in labels

    def test_extracts_names(self):
        envs = extract_environments(SAMPLE_TEX)
        names = {e.name for e in envs if e.name}
        assert "Soundness" in names
        assert "Sumcheck" in names
        assert "RS Code" in names

    def test_extracts_cross_refs(self):
        envs = extract_environments(SAMPLE_TEX)
        thm = [e for e in envs if e.label == "thm:soundness"][0]
        assert "lem:helper" in thm.cross_refs

    def test_nested_environments(self):
        tex = r"""
\begin{theorem}[Outer]
\label{thm:outer}
\begin{proof}
Inner proof.
\end{proof}
\end{theorem}
"""
        envs = extract_environments(tex)
        outer = [e for e in envs if e.env_type == "theorem"][0]
        assert "Inner proof" in outer.content

    def test_empty_input(self):
        envs = extract_environments("")
        assert len(envs) == 0


SECTION_TEX = r"""
\section{Introduction}\label{sec:intro}
Some text.
\subsection{Background}
More text.
\subsubsection{Details}\label{sec:details}
Even more text.
"""


class TestExtractSections:
    def test_finds_all_levels(self):
        sections = extract_sections(SECTION_TEX)
        levels = {s.level for s in sections}
        assert "section" in levels
        assert "subsection" in levels
        assert "subsubsection" in levels

    def test_extracts_titles(self):
        sections = extract_sections(SECTION_TEX)
        titles = {s.title for s in sections}
        assert "Introduction" in titles
        assert "Background" in titles
        assert "Details" in titles

    def test_extracts_labels(self):
        sections = extract_sections(SECTION_TEX)
        labeled = {s.label for s in sections if s.label}
        assert "sec:intro" in labeled
        assert "sec:details" in labeled

    def test_empty_input(self):
        sections = extract_sections("")
        assert len(sections) == 0


EQUATION_TEX = r"""
\begin{equation}
\label{eq:main}
E = mc^2
\end{equation}

\begin{align}
\label{eq:align}
a &= b + c \\
d &= e + f
\end{align}
"""


class TestExtractEquations:
    def test_finds_equations(self):
        eqs = extract_equations(EQUATION_TEX)
        assert len(eqs) == 2

    def test_extracts_labels(self):
        eqs = extract_equations(EQUATION_TEX)
        labels = {e.label for e in eqs if e.label}
        assert "eq:main" in labels
        assert "eq:align" in labels

    def test_extracts_content(self):
        eqs = extract_equations(EQUATION_TEX)
        main_eq = [e for e in eqs if e.label == "eq:main"][0]
        assert "mc^2" in main_eq.content

"""Tests for expand_macros.py"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

from expand_macros import extract_macros, expand_single_macro, iterative_expand, parse_braced, strip_comments


class TestParseBraced:
    def test_simple(self):
        content, pos = parse_braced("{hello}", 0)
        assert content == "hello"
        assert pos == 7

    def test_nested(self):
        content, pos = parse_braced("{a{b}c}", 0)
        assert content == "a{b}c"

    def test_empty(self):
        content, pos = parse_braced("{}", 0)
        assert content == ""

    def test_no_brace(self):
        content, pos = parse_braced("hello", 0)
        assert content == ""
        assert pos == 0

    def test_unbalanced(self, capsys):
        content, pos = parse_braced("{hello", 0)
        # Should warn on stderr
        captured = capsys.readouterr()
        assert "WARNING" in captured.err or "Unbalanced" in captured.err


class TestExtractMacros:
    def test_newcommand_no_args(self):
        tex = r"\newcommand{\F}{\mathbb{F}}"
        macros = extract_macros(tex)
        assert r"\F" in macros
        assert macros[r"\F"].body == r"\mathbb{F}"
        assert macros[r"\F"].num_args == 0

    def test_newcommand_with_args(self):
        tex = r"\newcommand{\set}[1]{\left\{#1\right\}}"
        macros = extract_macros(tex)
        assert r"\set" in macros
        assert macros[r"\set"].num_args == 1

    def test_def(self):
        tex = r"\def\RAPR{R_{\mathrm{APR}}}"
        macros = extract_macros(tex)
        assert r"\RAPR" in macros
        assert macros[r"\RAPR"].body == r"R_{\mathrm{APR}}"

    def test_declare_math_operator(self):
        tex = r"\DeclareMathOperator{\RPT}{RPT}"
        macros = extract_macros(tex)
        assert r"\RPT" in macros
        assert "operatorname" in macros[r"\RPT"].body

    def test_renewcommand(self):
        tex = r"\renewcommand{\N}{{\mathbb{N}}}"
        macros = extract_macros(tex)
        assert r"\N" in macros

    def test_newcommand_star(self):
        tex = r"\newcommand*{\foo}{bar}"
        macros = extract_macros(tex)
        assert r"\foo" in macros
        assert macros[r"\foo"].body == "bar"


class TestExpandSingleMacro:
    def test_simple_expansion(self):
        from expand_macros import Macro
        macro = Macro(name=r"\F", num_args=0, default_arg=None,
                      body=r"\mathbb{F}", line_number=1, kind="newcommand")
        result = expand_single_macro(r"Let \F be a field", r"\F", macro)
        assert result == r"Let \mathbb{F} be a field"

    def test_no_partial_match(self):
        from expand_macros import Macro
        macro = Macro(name=r"\F", num_args=0, default_arg=None,
                      body=r"\mathbb{F}", line_number=1, kind="newcommand")
        result = expand_single_macro(r"Let \FF be something", r"\F", macro)
        # \F should NOT match \FF
        assert result == r"Let \FF be something"

    def test_expansion_with_args(self):
        from expand_macros import Macro
        macro = Macro(name=r"\set", num_args=1, default_arg=None,
                      body=r"\left\{#1\right\}", line_number=1, kind="newcommand")
        result = expand_single_macro(r"\set{0,1}", r"\set", macro)
        assert result == r"\left\{0,1\right\}"


class TestIterativeExpand:
    def test_nested_macros(self):
        tex = r"\newcommand{\nice}[1]{{\sf{#1}}\xspace}" + "\n" + r"\newcommand{\FRI}{\nice{FRI}}"
        macros = extract_macros(tex)
        result = iterative_expand(r"The \FRI protocol", macros)
        assert r"\FRI" not in result
        assert "FRI" in result

    def test_converges(self):
        tex = r"\newcommand{\foo}{bar}"
        macros = extract_macros(tex)
        result = iterative_expand(r"\foo and \foo", macros)
        assert result == "bar and bar"


class TestStripComments:
    def test_basic(self):
        assert strip_comments("hello % comment") == "hello "

    def test_escaped_percent(self):
        assert strip_comments(r"50\% done") == r"50\% done"

    def test_multiline(self):
        result = strip_comments("line1 % comment\nline2")
        assert result == "line1 \nline2"

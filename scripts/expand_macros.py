#!/usr/bin/env python3
r"""
LaTeX macro expander for paper2spec.

Parses \newcommand, \def, \DeclareMathOperator from a .tex preamble,
builds a macro table, and iteratively expands all macros in the document body.

Usage:
    python expand_macros.py <input.tex> [--output-text expanded.tex] [--output-macros macros.yaml]
"""

import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Macro:
    name: str
    num_args: int
    default_arg: Optional[str]
    body: str
    line_number: int
    kind: str  # 'newcommand', 'def', 'DeclareMathOperator', 'newif'

    def expand(self, args: list[str]) -> str:
        result = self.body
        for i, arg in enumerate(args, 1):
            result = result.replace(f"#{i}", arg)
        return result


def parse_braced(text: str, pos: int) -> tuple[str, int]:
    """Parse a brace-delimited group starting at pos (which should be '{').
    Returns (content, position_after_closing_brace)."""
    if pos >= len(text) or text[pos] != '{':
        return '', pos
    depth = 1
    start = pos + 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == '{' and (i == 0 or text[i-1] != '\\'):
            depth += 1
        elif text[i] == '}' and (i == 0 or text[i-1] != '\\'):
            depth -= 1
        i += 1
    if depth > 0:
        print(f"WARNING: Unbalanced braces starting at position {pos}, "
              f"depth {depth} remaining", file=sys.stderr)
    return text[start:i-1], i


def parse_bracketed(text: str, pos: int) -> tuple[Optional[str], int]:
    """Parse an optional bracket-delimited group starting at pos.
    Returns (content_or_None, position_after)."""
    if pos >= len(text) or text[pos] != '[':
        return None, pos
    depth = 1
    start = pos + 1
    i = start
    while i < len(text) and depth > 0:
        if text[i] == '[':
            depth += 1
        elif text[i] == ']':
            depth -= 1
        i += 1
    return text[start:i-1], i


def extract_macros(tex_content: str) -> dict[str, Macro]:
    """Extract all macro definitions from a .tex file."""
    macros = {}
    lines = tex_content.split('\n')

    # Join lines for multi-line macro definitions
    full_text = tex_content

    # Pattern: \newcommand{\name}[nargs][default]{body}
    # Also handles \newcommand*{\name}...
    # Also handles \renewcommand
    newcmd_pattern = re.compile(
        r'\\(?:re)?newcommand\*?\s*\{?(\\[a-zA-Z]+)\}?'
    )

    for match in newcmd_pattern.finditer(full_text):
        name = match.group(1)
        pos = match.end()

        # Skip whitespace
        while pos < len(full_text) and full_text[pos] in ' \t\n':
            pos += 1

        # Optional: [num_args]
        num_args_str, pos = parse_bracketed(full_text, pos)
        num_args = int(num_args_str) if num_args_str else 0

        # Skip whitespace
        while pos < len(full_text) and full_text[pos] in ' \t\n':
            pos += 1

        # Optional: [default] for first arg
        default_arg, pos = parse_bracketed(full_text, pos)

        # Skip whitespace
        while pos < len(full_text) and full_text[pos] in ' \t\n':
            pos += 1

        # Required: {body}
        body, pos = parse_braced(full_text, pos)

        line_number = full_text[:match.start()].count('\n') + 1

        macros[name] = Macro(
            name=name,
            num_args=num_args,
            default_arg=default_arg,
            body=body,
            line_number=line_number,
            kind='newcommand',
        )

    # Pattern: \def\name{body} or \def\name#1#2{body}
    def_pattern = re.compile(r'\\def\s*(\\[a-zA-Z]+)((?:#\d)*)')
    for match in def_pattern.finditer(full_text):
        name = match.group(1)
        param_str = match.group(2)
        num_args = param_str.count('#') if param_str else 0
        pos = match.end()

        while pos < len(full_text) and full_text[pos] in ' \t\n':
            pos += 1

        body, pos = parse_braced(full_text, pos)
        line_number = full_text[:match.start()].count('\n') + 1

        macros[name] = Macro(
            name=name,
            num_args=num_args,
            default_arg=None,
            body=body,
            line_number=line_number,
            kind='def',
        )

    # Pattern: \DeclareMathOperator{\name}{body}
    # Also \DeclareMathOperator*
    declmath_pattern = re.compile(r'\\DeclareMathOperator\*?\s*\{(\\[a-zA-Z]+)\}\s*\{([^}]*)\}')
    for match in declmath_pattern.finditer(full_text):
        name = match.group(1)
        body = f'\\operatorname{{{match.group(2)}}}'
        line_number = full_text[:match.start()].count('\n') + 1
        macros[name] = Macro(
            name=name,
            num_args=0,
            default_arg=None,
            body=body,
            line_number=line_number,
            kind='DeclareMathOperator',
        )

    return macros


def expand_single_macro(text: str, name: str, macro: Macro) -> str:
    """Expand all occurrences of a single macro in the text."""
    # Escape the backslash in the name for regex
    escaped = re.escape(name)
    # Match the macro name followed by a word boundary (not another letter)
    pattern = escaped + r'(?![a-zA-Z])'

    result = text
    safety = 0
    while safety < 500:
        match = re.search(pattern, result)
        if not match:
            break
        safety += 1

        pos = match.end()

        if macro.num_args == 0:
            # Simple replacement, no args
            replacement = macro.body
            result = result[:match.start()] + replacement + result[pos:]
        else:
            # Parse arguments
            args = []

            # If there's a default arg, first arg is optional
            if macro.default_arg is not None:
                # Skip whitespace
                while pos < len(result) and result[pos] in ' \t\n':
                    pos += 1
                opt, new_pos = parse_bracketed(result, pos)
                if opt is not None:
                    args.append(opt)
                    pos = new_pos
                else:
                    args.append(macro.default_arg)

            # Parse remaining required args
            remaining = macro.num_args - len(args)
            for _ in range(remaining):
                while pos < len(result) and result[pos] in ' \t\n':
                    pos += 1
                if pos < len(result) and result[pos] == '{':
                    arg, pos = parse_braced(result, pos)
                    args.append(arg)
                elif pos < len(result):
                    # Single token arg (no braces)
                    args.append(result[pos])
                    pos += 1

            replacement = macro.expand(args)
            result = result[:match.start()] + replacement + result[pos:]

    return result


def iterative_expand(text: str, macros: dict[str, Macro], max_passes: int = 20) -> str:
    """Iteratively expand all macros until no more expansions are possible."""
    for pass_num in range(max_passes):
        prev = text
        # Sort by name length descending to avoid partial matches
        for name in sorted(macros.keys(), key=len, reverse=True):
            text = expand_single_macro(text, name, macros[name])
        if text == prev:
            break
    else:
        # Loop completed without convergence
        if text != prev:
            print(f"WARNING: Macros did not fully converge after {max_passes} passes. "
                  f"Some macros may remain unexpanded.", file=sys.stderr)
    return text


def strip_comments(text: str) -> str:
    """Remove LaTeX comments (% to end of line) but preserve \\%."""
    lines = text.split('\n')
    result = []
    for line in lines:
        cleaned = []
        i = 0
        while i < len(line):
            if line[i] == '%' and (i == 0 or line[i-1] != '\\'):
                break
            cleaned.append(line[i])
            i += 1
        result.append(''.join(cleaned))
    return '\n'.join(result)


def find_document_body(text: str) -> tuple[str, str]:
    """Split into preamble and body at \\begin{document}."""
    match = re.search(r'\\begin\{document\}', text)
    if match:
        return text[:match.start()], text[match.end():]
    return '', text


def macros_to_dict(macros: dict[str, Macro]) -> list[dict]:
    """Convert macros to a serializable list."""
    result = []
    for name, m in sorted(macros.items()):
        result.append({
            'name': m.name,
            'num_args': m.num_args,
            'default_arg': m.default_arg,
            'body': m.body,
            'line_number': m.line_number,
            'kind': m.kind,
        })
    return result


def main():
    parser = argparse.ArgumentParser(description='Expand LaTeX macros for paper2spec')
    parser.add_argument('input', help='Input .tex file')
    parser.add_argument('--output-text', '-t', help='Output expanded .tex file')
    parser.add_argument('--output-macros', '-m', help='Output macro table as JSON')
    parser.add_argument('--strip-comments', action='store_true', default=True,
                        help='Strip LaTeX comments (default: true)')
    parser.add_argument('--body-only', action='store_true',
                        help='Output only the document body (after \\begin{document})')
    args = parser.parse_args()

    tex_content = Path(args.input).read_text(encoding='utf-8')

    # Extract macros from the full document (preamble + body, since some \def appear in body)
    macros = extract_macros(tex_content)
    print(f"Extracted {len(macros)} macros", file=sys.stderr)

    # Optionally strip comments
    if args.strip_comments:
        tex_content = strip_comments(tex_content)

    # Optionally extract body only
    if args.body_only:
        _, tex_content = find_document_body(tex_content)

    # Expand macros
    expanded = iterative_expand(tex_content, macros)
    print(f"Expansion complete", file=sys.stderr)

    # Output
    if args.output_text:
        Path(args.output_text).write_text(expanded, encoding='utf-8')
        print(f"Wrote expanded text to {args.output_text}", file=sys.stderr)
    else:
        print(expanded)

    if args.output_macros:
        macro_list = macros_to_dict(macros)
        Path(args.output_macros).write_text(
            json.dumps(macro_list, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        print(f"Wrote {len(macro_list)} macros to {args.output_macros}", file=sys.stderr)


if __name__ == '__main__':
    main()

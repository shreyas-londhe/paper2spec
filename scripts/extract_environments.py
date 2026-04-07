#!/usr/bin/env python3
"""
LaTeX environment extractor for paper2spec.

Extracts protocol, theorem, definition, lemma, algorithm, and other
environments from a .tex file. Outputs structured JSON.

Usage:
    python extract_environments.py <input.tex> [--output environments.json]
"""

import re
import sys
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Environment:
    env_type: str           # 'protocol', 'theorem', 'definition', 'lemma', 'corollary', 'claim', 'algorithm'
    label: Optional[str]    # from \label{...}
    name: Optional[str]     # from optional argument, e.g. \begin{theorem}[FRI soundness]
    line_start: int
    line_end: int
    content: str
    cross_refs: list[str]   # labels referenced via \cref, \ref, \eqref


@dataclass
class Section:
    level: str              # 'section', 'subsection', 'subsubsection'
    title: str
    label: Optional[str]
    line_number: int


@dataclass
class Equation:
    label: Optional[str]
    content: str
    line_start: int
    line_end: int


TRACKED_ENVS = {
    'protocol', 'theorem', 'definition', 'lemma', 'corollary',
    'claim', 'conjecture', 'remark', 'fact', 'example',
    'algorithm', 'algorithmic', 'proof',
}


def extract_cross_refs(text: str) -> list[str]:
    """Extract all \cref, \ref, \eqref labels from text."""
    refs = []
    for pattern in [r'\\cref\{([^}]+)\}', r'\\ref\{([^}]+)\}', r'\\eqref\{([^}]+)\}']:
        for match in re.finditer(pattern, text):
            # cref can have comma-separated labels
            for label in match.group(1).split(','):
                refs.append(label.strip())
    return list(set(refs))


def extract_environments(tex_content: str) -> list[Environment]:
    """Extract all tracked environments from the tex content."""
    envs = []
    lines = tex_content.split('\n')

    # Build a line-number lookup
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    def offset_to_line(offset: int) -> int:
        for i, lo in enumerate(line_offsets):
            if lo > offset:
                return i
        return len(lines)

    for env_type in TRACKED_ENVS:
        # Match \begin{env}[optional name]...\end{env}
        # Use non-greedy matching and handle nesting
        begin_pattern = re.compile(
            rf'\\begin\{{{env_type}\}}(\[[^\]]*\])?',
        )

        for begin_match in begin_pattern.finditer(tex_content):
            optional_arg = begin_match.group(1)
            name = optional_arg[1:-1] if optional_arg else None

            # Find matching \end{env_type} handling nesting
            start_pos = begin_match.end()
            depth = 1
            search_pos = start_pos

            end_pattern_begin = re.compile(rf'\\begin\{{{env_type}\}}')
            end_pattern_end = re.compile(rf'\\end\{{{env_type}\}}')

            end_pos = None
            while search_pos < len(tex_content):
                next_begin = end_pattern_begin.search(tex_content, search_pos)
                next_end = end_pattern_end.search(tex_content, search_pos)

                if next_end is None:
                    break

                if next_begin and next_begin.start() < next_end.start():
                    depth += 1
                    search_pos = next_begin.end()
                else:
                    depth -= 1
                    if depth == 0:
                        end_pos = next_end.end()
                        break
                    search_pos = next_end.end()

            if end_pos is None:
                continue

            content = tex_content[start_pos:end_pos].strip()
            # Remove the \end{...} from content
            content = re.sub(rf'\\end\{{{env_type}\}}\s*$', '', content).strip()

            # Extract label if present
            label_match = re.search(r'\\label\{([^}]+)\}', content)
            label = label_match.group(1) if label_match else None

            # Extract cross-references
            cross_refs = extract_cross_refs(content)

            line_start = offset_to_line(begin_match.start())
            line_end = offset_to_line(end_pos)

            envs.append(Environment(
                env_type=env_type,
                label=label,
                name=name,
                line_start=line_start,
                line_end=line_end,
                content=content,
                cross_refs=cross_refs,
            ))

    # Sort by line_start
    envs.sort(key=lambda e: e.line_start)
    return envs


def extract_sections(tex_content: str) -> list[Section]:
    """Extract section/subsection/subsubsection headings."""
    sections = []
    lines = tex_content.split('\n')

    for i, line in enumerate(lines, 1):
        for level in ['subsubsection', 'subsection', 'section']:
            pattern = rf'\\{level}\*?\s*\{{([^}}]+)\}}'
            match = re.search(pattern, line)
            if match:
                title = match.group(1)

                # Check for label on same or next line
                label = None
                label_match = re.search(r'\\label\{([^}]+)\}', line)
                if not label_match and i < len(lines):
                    label_match = re.search(r'\\label\{([^}]+)\}', lines[i])
                if label_match:
                    label = label_match.group(1)

                sections.append(Section(
                    level=level,
                    title=title,
                    label=label,
                    line_number=i,
                ))
                break

    return sections


def extract_equations(tex_content: str) -> list[Equation]:
    """Extract labeled equations."""
    equations = []
    lines = tex_content.split('\n')
    line_offsets = [0]
    for line in lines:
        line_offsets.append(line_offsets[-1] + len(line) + 1)

    def offset_to_line(offset: int) -> int:
        for i, lo in enumerate(line_offsets):
            if lo > offset:
                return i
        return len(lines)

    # Match \begin{equation}...\end{equation}
    for match in re.finditer(r'\\begin\{equation\}(.*?)\\end\{equation\}', tex_content, re.DOTALL):
        content = match.group(1).strip()
        label_match = re.search(r'\\label\{([^}]+)\}', content)
        label = label_match.group(1) if label_match else None
        equations.append(Equation(
            label=label,
            content=content,
            line_start=offset_to_line(match.start()),
            line_end=offset_to_line(match.end()),
        ))

    # Match \begin{align}...\end{align}
    for match in re.finditer(r'\\begin\{align\*?\}(.*?)\\end\{align\*?\}', tex_content, re.DOTALL):
        content = match.group(1).strip()
        label_match = re.search(r'\\label\{([^}]+)\}', content)
        label = label_match.group(1) if label_match else None
        equations.append(Equation(
            label=label,
            content=content,
            line_start=offset_to_line(match.start()),
            line_end=offset_to_line(match.end()),
        ))

    equations.sort(key=lambda e: e.line_start)
    return equations


def main():
    parser = argparse.ArgumentParser(description='Extract LaTeX environments for paper2spec')
    parser.add_argument('input', help='Input .tex file')
    parser.add_argument('--output', '-o', help='Output JSON file')
    parser.add_argument('--expanded', action='store_true',
                        help='Input is already macro-expanded (skip macro warnings)')
    args = parser.parse_args()

    tex_content = Path(args.input).read_text(encoding='utf-8')

    envs = extract_environments(tex_content)
    sections = extract_sections(tex_content)
    equations = extract_equations(tex_content)

    result = {
        'environments': [asdict(e) for e in envs],
        'sections': [asdict(s) for s in sections],
        'equations': [asdict(e) for e in equations],
        'summary': {
            'total_environments': len(envs),
            'by_type': {},
            'total_sections': len(sections),
            'total_equations': len(equations),
        }
    }

    for e in envs:
        result['summary']['by_type'][e.env_type] = result['summary']['by_type'].get(e.env_type, 0) + 1

    if args.output:
        Path(args.output).write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding='utf-8',
        )
        print(f"Wrote {len(envs)} environments, {len(sections)} sections, "
              f"{len(equations)} equations to {args.output}", file=sys.stderr)
    else:
        print(json.dumps(result, indent=2, ensure_ascii=False))

    # Print summary
    print(f"\nSummary:", file=sys.stderr)
    print(f"  Environments: {len(envs)}", file=sys.stderr)
    for t, c in sorted(result['summary']['by_type'].items()):
        print(f"    {t}: {c}", file=sys.stderr)
    print(f"  Sections: {len(sections)}", file=sys.stderr)
    print(f"  Equations: {len(equations)}", file=sys.stderr)


if __name__ == '__main__':
    main()

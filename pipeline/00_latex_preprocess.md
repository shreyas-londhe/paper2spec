# Stage 0: LaTeX Preprocessing

## Purpose
Acquire the paper source, expand all LaTeX macros, extract structured environments
(protocols, theorems, definitions), and build a cross-reference dependency graph.
All downstream stages consume these artifacts.

## Input
- `PAPER_SOURCE`: arXiv ID, ePrint URL, or local `.tex` path

## Output
- `.paper2spec_work/{PAPER_ID}/main.tex` — the raw `.tex` source
- `.paper2spec_work/{PAPER_ID}/expanded.tex` — macro-expanded document body
- `.paper2spec_work/{PAPER_ID}/macros.json` — table of all extracted macros
- `.paper2spec_work/{PAPER_ID}/environments.json` — protocols, theorems, definitions, lemmas, equations
- `.paper2spec_work/{PAPER_ID}/graph.json` — cross-reference dependency DAG

---

## Reasoning protocol

### Step 1: Acquire the source

**If arXiv ID:**
```bash
mkdir -p .paper2spec_work/{PAPER_ID}
curl -sL "https://arxiv.org/e-print/{ARXIV_ID}" -o .paper2spec_work/{PAPER_ID}/source.tar.gz
cd .paper2spec_work/{PAPER_ID} && tar xzf source.tar.gz
```

Find the main `.tex` file (search recursively — tarballs may have subdirectories):
```bash
grep -rl '\\begin{document}' .paper2spec_work/{PAPER_ID} --include="*.tex"
```
If multiple files match, the one with `\title{}` is usually the main file.
If the source is a single file (not a tarball), it was served as a `.tex` directly.

**If ePrint URL (e.g., `https://eprint.iacr.org/YYYY/NNNN`):**
1. Fetch the ePrint page and search for an arXiv cross-post link.
2. If found, use the arXiv `.tex` source (far better quality).
3. If not found, inform the user: "This paper is ePrint-only (no LaTeX source available).
   PDF extraction for math-heavy crypto papers is lossy. Consider finding the `.tex` source
   from the authors or a preprint server."

**If local `.tex` path:**
Copy to `.paper2spec_work/{PAPER_ID}/main.tex`.

### Step 2: Run macro expander

```bash
python ${CLAUDE_SKILL_DIR}/scripts/expand_macros.py .paper2spec_work/{PAPER_ID}/main.tex \
  -t .paper2spec_work/{PAPER_ID}/expanded.tex \
  -m .paper2spec_work/{PAPER_ID}/macros.json \
  --body-only
```

**Verify macro expansion quality.** Read `macros.json` and check:
- [ ] Protocol names expanded (e.g., `\FRI` -> `FRI`, custom protocol macros)
- [ ] Mathematical objects expanded (e.g., `\F` -> `\mathbb{F}`)
- [ ] Superscript shorthands expanded (e.g., `\zr` -> `^{(0)}`, `\ii` -> `^{(i)}`)
- [ ] Operations expanded (e.g., `\QUOTIENT` -> some readable form)

**Common issues:**
- Macros defined in separate `.sty` or `.cls` files: look for `\input{}` or `\usepackage{local-file}` in the preamble and cat those files to find missing macro definitions.
- Nested macros not fully resolved: the expander runs up to 20 passes, but deeply nested chains may need manual resolution. Check `expanded.tex` for remaining `\custom_macro` patterns.

### Step 3: Run environment extractor

```bash
python ${CLAUDE_SKILL_DIR}/scripts/extract_environments.py .paper2spec_work/{PAPER_ID}/expanded.tex \
  -o .paper2spec_work/{PAPER_ID}/environments.json
```

**Verify extraction.** Check that:
- [ ] All `\begin{protocol}...\end{protocol}` blocks found (these are the primary targets)
- [ ] All `\begin{theorem}...\end{theorem}` blocks with labels found
- [ ] All `\begin{definition}...\end{definition}` blocks found
- [ ] All `\begin{algorithm}...\end{algorithm}` or `\begin{algorithmic}` blocks found
- [ ] Section structure matches the paper's table of contents

**If the paper doesn't use `\begin{protocol}`:** Many crypto papers describe protocols
in plain enumerate environments or algorithmic blocks instead. In that case, manually
identify protocol descriptions by looking for keywords: "Protocol", "COMMIT", "QUERY",
"Prover", "Verifier", "Round", or algorithmic pseudocode patterns.

### Step 4: Run dependency graph builder

```bash
python ${CLAUDE_SKILL_DIR}/scripts/build_dependency_graph.py .paper2spec_work/{PAPER_ID}/environments.json \
  -o .paper2spec_work/{PAPER_ID}/graph.json
```

Review the dependency chains. The graph shows which theorems reference which definitions
and which protocols depend on which lemmas. This determines the order of extraction
in Stages 1-3.

### Step 5: Build notation resolution table

From `macros.json`, produce a human-readable notation table. Focus on:
- Macros that appear in protocol/theorem environments (skip formatting-only macros)
- Mathematical objects: fields, groups, domains, polynomials
- Protocol-specific notation: round indices, challenge names, oracle names

**Save to `.paper2spec_work/{PAPER_ID}/notation_table_draft.md`.**

This becomes `notation-table.md` in the final output after Stage 2 enriches it
with semantic meanings.

### Step 6: Search for reference implementations

Search for existing implementations of the protocol:
```bash
gh search repos "{protocol_name}" --limit 10
gh search code "{protocol_name} commit verify" --limit 10
```

Record any found implementations in `.paper2spec_work/{PAPER_ID}/references.md`:
- Repository URL
- Language
- Key file paths (if identifiable from search results)

These will be used in Stage 6 (Cross-Validation) to verify the spec.

---

## Fallback protocol

### If arXiv source download fails:
1. Check if the paper exists: `curl -sI "https://arxiv.org/abs/{ID}"`
2. Some papers are PDF-only (no source). Try the ar5iv HTML version:
   `https://ar5iv.labs.arxiv.org/html/{ID}` — this has MathML but not raw LaTeX.
3. Last resort: ask the user to provide the `.tex` file directly.

### If macro expansion produces errors:
1. Check for missing input files (`\input{...}` in the preamble)
2. Check for package-defined macros (e.g., `\cryptocode` package defines many macros)
3. Manually add missing macro definitions and re-run

### If the paper uses non-standard environments:
Many crypto papers use custom theorem styles (`\newtheorem{protocol}[theorem]{Protocol}`).
The environment extractor handles these. But if protocols are described in plain
`enumerate` environments, you'll need to manually identify them by reading the text.

---

## Quality checklist before proceeding to Stage 1

- [ ] `expanded.tex` exists and has no remaining custom macros in protocol sections
- [ ] `macros.json` has all key domain-specific macros listed
- [ ] `environments.json` has at least 1 protocol (or protocol-like) environment
- [ ] `environments.json` has theorem environments (especially soundness theorems)
- [ ] `graph.json` exists
- [ ] You've identified the main protocol(s) in the paper
- [ ] You've searched for reference implementations

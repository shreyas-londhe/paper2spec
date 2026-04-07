---
name: paper2spec
description: Converts a cryptographic IOP paper into a structured, language-agnostic protocol specification that LLM agents can consume to implement the protocol in Rust, Go, Python, or any language. Trigger when user runs /paper2spec with an arXiv URL/ID, ePrint URL, or local .tex file path. Flags all algebraic ambiguities honestly. Never invents protocol details not stated in the paper.
argument-hint: "1903.12243 | https://eprint.iacr.org/2024/1586 | ./paper.tex [--mode minimal|full|delta]"
---

# paper2spec — Orchestration

You are executing the paper2spec skill. This file governs the high-level flow. Each stage dispatches to a detailed reasoning protocol in `pipeline/`. Do NOT skip stages. Do NOT combine stages. Execute them in order.

## Parse arguments

Extract from the user's input (`$ARGUMENTS`):

1. **`PAPER_SOURCE`**: the first argument. One of:
   - An arXiv URL (e.g., `https://arxiv.org/abs/1903.12243`) — extract the ID `1903.12243`
   - A bare arXiv ID (e.g., `1903.12243` or `1903.12243v2`)
   - An IACR ePrint URL (e.g., `https://eprint.iacr.org/2024/1586`)
   - A local `.tex` file path

2. **`PAPER_ID`**: derived from `PAPER_SOURCE`:
   - For arXiv: the bare ID without version suffix (e.g., `1903.12243`)
   - For ePrint: `eprint-YYYY-NNNN` (e.g., `eprint-2024-1586`)
   - For local file: the filename without extension (e.g., `my-paper`)

3. **`MODE`**: from `--mode` flag, one of `minimal` (default), `full`, `delta`.

## Set up working directory

```bash
WORK=".paper2spec_work/${PAPER_ID}"
mkdir -p "${WORK}"
```

All intermediate artifacts go in `${WORK}/`. The final output goes in `{paper_slug}/` in the current directory.

## Acquire the paper source

### If arXiv ID:
Download the LaTeX source (preferred — perfect math fidelity):
```bash
curl -sL "https://arxiv.org/e-print/${PAPER_ID}" -o "${WORK}/source.tar.gz"
```

Verify the download is a tarball (not a bare PDF):
```bash
file "${WORK}/source.tar.gz" | grep -q "gzip"
```
If it's NOT gzip (some arXiv papers serve raw PDF), inform the user: "This paper has no LaTeX source on arXiv. Please provide the `.tex` file directly or accept lossy PDF extraction."

Unpack and find the main `.tex` file (search recursively — arXiv tarballs may have subdirectories):
```bash
cd "${WORK}" && tar xzf source.tar.gz
TEX_FILE=$(grep -rl '\\begin{document}' "${WORK}" --include="*.tex" 2>/dev/null | head -1)
```
If multiple `.tex` files contain `\begin{document}`, prefer the one with `\title{}`.
If none found, check for a single `.tex` file and use that.

### If ePrint URL:
1. Fetch the ePrint page and search for an arXiv cross-post link.
2. If found on arXiv, use the arXiv source (far better quality).
3. If not found, inform the user: "This paper is ePrint-only (no LaTeX source). PDF extraction for math-heavy crypto papers is lossy. Consider finding the `.tex` from the authors."

### If local .tex file:
```bash
cp "${PAPER_SOURCE}" "${WORK}/main.tex"
TEX_FILE="${WORK}/main.tex"
```

At this point, `TEX_FILE` must be set to the path of the main `.tex` file. If it is not set, STOP and ask the user for help.

## Execute pipeline

The skill directory is `${CLAUDE_SKILL_DIR}` (set by Claude Code). If running standalone, use the directory containing this SKILL.md.

### Stage 0 — LaTeX Preprocessing
Read and follow: `pipeline/00_latex_preprocess.md`

Run the helper scripts to expand macros and extract structure:
```bash
python3 "${CLAUDE_SKILL_DIR}/scripts/expand_macros.py" "${TEX_FILE}" \
  -t "${WORK}/expanded.tex" -m "${WORK}/macros.json" --body-only
python3 "${CLAUDE_SKILL_DIR}/scripts/extract_environments.py" "${WORK}/expanded.tex" \
  -o "${WORK}/environments.json"
python3 "${CLAUDE_SKILL_DIR}/scripts/build_dependency_graph.py" "${WORK}/environments.json" \
  -o "${WORK}/graph.json"
```

Verify outputs exist before proceeding:
```bash
test -f "${WORK}/expanded.tex" && test -f "${WORK}/environments.json" && test -f "${WORK}/graph.json"
```
If any are missing, re-check `TEX_FILE` and re-run. Check `macros.json` for key protocol names and math symbols.

### Stage 1 — Protocol Inventory
Read and follow: `pipeline/01_protocol_inventory.md`

Read `${WORK}/expanded.tex` and `${WORK}/environments.json`. Identify all protocols, theorems, definitions. Classify the paper type. Determine scope. Save to `${WORK}/inventory.md`.

### Stage 2 — Algebraic Setting Extraction
Read and follow: `pipeline/02_algebraic_setting.md`

Extract every mathematical object: fields, groups, domains, codes, degree bounds, parameters. Resolve all notation. Save to `${WORK}/algebraic_setting.md`.

### Stage 3 — Protocol Decomposition
Read and follow: `pipeline/03_protocol_decompose.md`

Before this stage, read these guardrails:
- `guardrails/crypto_correctness.md` — non-negotiable correctness rules
- `guardrails/notation_fidelity.md` — notation consistency rules

Decompose each protocol round-by-round with prover/verifier actions and verification equations. Save to `${WORK}/protocols.md`.

### Stage 4 — Soundness Analysis
Read and follow: `pipeline/04_soundness.md`

Extract soundness bounds. Produce parameter guidance for 128-bit and 256-bit security. Save to `${WORK}/soundness.md`.

### Stage 5 — Implementation Bridge
Read and follow: `pipeline/05_impl_bridge.md`

Before this stage, read: `guardrails/implementation_pitfalls.md`

Produce Fiat-Shamir transcript schedule, primitive interfaces, and ambiguity register. Save to `${WORK}/primitives.md`, `${WORK}/transcript.md`, `${WORK}/ambiguity.md`.

### Stage 6 — Cross-Validation
Read and follow: `pipeline/06_cross_validate.md`

Search for reference implementations. If found, validate spec against them. If none found, mark spec as "unvalidated" and skip this stage.

## Assembly

**Generate the paper slug**: take the paper title, lowercase it, replace spaces and punctuation with hyphens, remove non-alphanumeric characters (except hyphens), collapse consecutive hyphens. Examples:
- "DEEP-FRI: Sampling Outside the Box Improves Soundness" → `deep-fri-sampling-outside-the-box-improves-soundness`
- "Spartan: Efficient and general-purpose zkSNARKs" → `spartan-efficient-and-general-purpose-zksnarks`
- Or use the short/common name if one exists: `deep-fri`, `spartan`, `sumcheck`

Assemble the final output under `{paper_slug}/`:

1. **`{paper_slug}-spec.md`** — the primary spec document. Build it section by section:
   - YAML frontmatter (paper title, authors, arXiv ID, protocol names)
   - Section 0: copy `${WORK}/algebraic_setting.md` content verbatim
   - Section 1: copy primitive interfaces from `${WORK}/primitives.md`
   - Sections 2..N: copy each protocol from `${WORK}/protocols.md`, one section per protocol, in dependency order (base protocols first)
   - Section N+1: copy `${WORK}/soundness.md` content
   - Section N+2: reference `fiat-shamir-transcript.md`
   - Section N+3: reference `ambiguity-register.md`
   Use `$...$` for inline math and `$$...$$` for display math (GitHub-rendered LaTeX).

2. **`notation-table.md`** — from `${WORK}/macros.json` + algebraic setting definitions

3. **`fiat-shamir-transcript.md`** — from `${WORK}/transcript.md`

4. **`ambiguity-register.md`** — from `${WORK}/ambiguity.md`

## Cleanup

Remove `.paper2spec_work/` after successful completion:
```bash
rm -rf .paper2spec_work/
```
If the skill exits early due to error, `.paper2spec_work/` may be left behind. The user can clean up manually with `rm -rf .paper2spec_work/`.

## Final output

Print a summary:
```
paper2spec complete for: {paper_title}
  Output directory: {paper_slug}/
  Files: {paper_slug}-spec.md, notation-table.md, fiat-shamir-transcript.md, ambiguity-register.md
  Protocols extracted: {protocol_names}
  Ambiguities flagged: {count} (see ambiguity-register.md)
  Mode: {MODE}
```

The output directory is in the current working directory, ready for use. No git operations are performed — the user decides when to commit.

## Mode-specific behavior

- **minimal** (default): Extract only the paper's primary protocol contribution. Skip recalled/imported base protocols (reference them by name only). Suitable for papers that present one new protocol.
- **full**: Extract ALL protocols in the paper, including base protocols recalled from prior work. Produce a fully self-contained spec. Suitable for papers with multiple novel protocols.
- **delta**: Extract only the *differences* from a base protocol. The paper's abstract/introduction typically names the base (e.g., "DEEP-FRI extends FRI"). In the spec, describe only operations that differ from the base. For identical steps, write "Same as {base_protocol}, Round N." Suitable for extension/optimization papers.

## Guardrails — always active

These apply at ALL stages. Read them before starting:
- `guardrails/crypto_correctness.md` — domain separation, challenge ordering, field size, degree tracking
- `guardrails/notation_fidelity.md` — no unexpanded macros, consistent notation
- `guardrails/implementation_pitfalls.md` — common IOP implementation mistakes

## Worked examples — consult for quality calibration

Before generating final output, compare against worked examples for detail level:
- `worked/sumcheck/` — simple protocol spec (good for format reference)
- `worked/deep-fri/` — complex protocol spec with multiple sub-protocols

## Quality checklist

Before marking the spec complete:
- [ ] Every symbol in protocol sections is defined in the Algebraic Setting
- [ ] Every protocol has explicit phases (COMMIT/QUERY or equivalent)
- [ ] Every verification equation is stated with algebraic derivation
- [ ] The Fiat-Shamir transcript schedule has no gaps (every SQUEEZE has prior ABSORBs)
- [ ] Degree bounds are tracked through every protocol round
- [ ] The ambiguity register covers all unspecified implementation choices
- [ ] No unexpanded LaTeX macros remain in the output
- [ ] Primitive interfaces list every external dependency
- [ ] Math uses `$...$` for inline and `$$...$$` for display (GitHub-renderable LaTeX)

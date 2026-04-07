---
name: paper2spec
description: Converts a cryptographic IOP paper into a structured, language-agnostic protocol specification that LLM agents can consume to implement the protocol in Rust, Go, Python, or any language. Trigger when user runs /paper2spec with an arXiv URL/ID, ePrint URL, or local .tex file path. Flags all algebraic ambiguities honestly. Never invents protocol details not stated in the paper.
argument-hint: "<arxiv-id | eprint-url | path/to/paper.tex> [--mode minimal|full|delta]"
---

# paper2spec — Orchestration

You are executing the paper2spec skill. This file governs the high-level flow. Each stage dispatches to a detailed reasoning protocol in `pipeline/`. Do NOT skip stages. Do NOT combine stages. Execute them in order.

## Parse arguments

Extract from the user's input:
- `PAPER_SOURCE`: one of:
  - An arXiv ID (e.g., `1903.12243`). Strip any URL prefix like `https://arxiv.org/abs/`.
  - An IACR ePrint URL (e.g., `https://eprint.iacr.org/2024/1586`).
  - A local `.tex` file path.
- `MODE`: one of `minimal` (default), `full`, `delta`.

If the user provided a full URL like `https://arxiv.org/abs/1903.12243`, extract the ID `1903.12243`.
If the user provided a versioned ID like `1903.12243v2`, keep the version.

## Set up working directory

Create a temporary working directory: `.paper2spec_work/{PAPER_ID}/`
This is where intermediate artifacts go. The final output goes in the current directory under `{paper_slug}/`.

## Acquire the paper source

### If arXiv ID:
Download the LaTeX source (preferred — perfect math fidelity):
```bash
curl -sL "https://arxiv.org/e-print/{ARXIV_ID}" -o .paper2spec_work/{PAPER_ID}/source.tar.gz
cd .paper2spec_work/{PAPER_ID} && tar xzf source.tar.gz
```
Find the main `.tex` file (the one containing `\begin{document}`):
```bash
grep -l '\\begin{document}' .paper2spec_work/{PAPER_ID}/*.tex
```

### If ePrint URL:
First check if the paper is cross-posted to arXiv (search ePrint page for arXiv links).
If found on arXiv, use the arXiv source. If not, download the PDF — note that PDF
extraction for math-heavy crypto papers is lossy. Inform the user.

### If local .tex file:
Use directly. Copy to `.paper2spec_work/{PAPER_ID}/`.

## Execute pipeline

### Stage 0 — LaTeX Preprocessing
Read and follow: `pipeline/00_latex_preprocess.md`

Run the helper scripts to expand macros and extract structure:
```bash
python ${CLAUDE_SKILL_DIR}/scripts/expand_macros.py {TEX_FILE} -t .paper2spec_work/{PAPER_ID}/expanded.tex -m .paper2spec_work/{PAPER_ID}/macros.json --body-only
python ${CLAUDE_SKILL_DIR}/scripts/extract_environments.py .paper2spec_work/{PAPER_ID}/expanded.tex -o .paper2spec_work/{PAPER_ID}/environments.json
python ${CLAUDE_SKILL_DIR}/scripts/build_dependency_graph.py .paper2spec_work/{PAPER_ID}/environments.json -o .paper2spec_work/{PAPER_ID}/graph.json
```
Verify the outputs exist before proceeding. Check that macros expanded correctly —
look for key protocol names and mathematical symbols in `macros.json`.

### Stage 1 — Protocol Inventory
Read and follow: `pipeline/01_protocol_inventory.md`

Read the expanded text and extracted environments. Identify all protocols, theorems,
definitions. Classify the paper type. Determine scope. Save inventory to
`.paper2spec_work/{PAPER_ID}/inventory.md`.

### Stage 2 — Algebraic Setting Extraction
Read and follow: `pipeline/02_algebraic_setting.md`

Extract every mathematical object: fields, groups, domains, codes, degree bounds,
parameters. Resolve all notation. Save to `.paper2spec_work/{PAPER_ID}/algebraic_setting.md`.

### Stage 3 — Protocol Decomposition
Read and follow: `pipeline/03_protocol_decompose.md`

Before reading this stage, also read:
- `guardrails/crypto_correctness.md` — non-negotiable correctness rules
- `guardrails/notation_fidelity.md` — notation consistency rules

Decompose each protocol into explicit round-by-round steps with prover/verifier
actions and verification equations. This is the core stage. Save to
`.paper2spec_work/{PAPER_ID}/protocols.md`.

### Stage 4 — Soundness Analysis
Read and follow: `pipeline/04_soundness.md`

Extract soundness bounds from theorem statements. Produce concrete parameter
guidance for standard security levels (128-bit, 256-bit). Save to
`.paper2spec_work/{PAPER_ID}/soundness.md`.

### Stage 5 — Implementation Bridge
Read and follow: `pipeline/05_impl_bridge.md`

Before reading this stage, also read:
- `guardrails/implementation_pitfalls.md` — common IOP implementation mistakes

Bridge from the IOP model to concrete implementation. Produce the Fiat-Shamir
transcript schedule, primitive interfaces, and ambiguity register. Save to
`.paper2spec_work/{PAPER_ID}/primitives.md`, `transcript.md`, `ambiguity.md`.

### Stage 6 — Cross-Validation
Read and follow: `pipeline/06_cross_validate.md`

Search for reference implementations of the protocol using `gh search repos` and
`gh search code`. Validate the spec against them. Fix discrepancies.

## Assembly

Determine the `paper_slug` from the paper title (lowercase, hyphens, no special chars).
Assemble the final output under `{paper_slug}/`:

1. **`{paper_slug}-spec.md`** — combine algebraic setting (Stage 2) + protocols (Stage 3) +
   soundness (Stage 4) + primitive interfaces (Stage 5) into one spec document.
   Use the scaffold template `scaffolds/spec_template.md` for structure.
2. **`notation-table.md`** — from Stage 0 macro table + Stage 2 symbol definitions.
   Use `scaffolds/notation_table_template.md`.
3. **`fiat-shamir-transcript.md`** — from Stage 5 transcript schedule.
   Use `scaffolds/fiat_shamir_template.md`.
4. **`ambiguity-register.md`** — from Stage 5 ambiguity audit.
   Use `scaffolds/ambiguity_register_template.md`.

## Cleanup

Remove the `.paper2spec_work/` directory after successful completion.

## Final output

Print a summary:
```
paper2spec complete for: {paper_title}
  Output directory: {paper_slug}/
  Protocols extracted: {protocol_names}
  Ambiguities flagged: {count} (see ambiguity-register.md)
  Mode: {MODE}
```

## Mode-specific behavior

- **minimal** (default): Extract only the paper's primary protocol contribution. Skip recalled/imported base protocols (reference them by name only). Suitable for papers that present one new protocol.
- **full**: Extract ALL protocols in the paper, including base protocols recalled from prior work. Suitable for self-contained specs or papers with multiple novel protocols.
- **delta**: Extract only the *differences* from a base protocol. The spec references the base protocol by name and describes modifications. Suitable for papers that optimize or extend a known protocol (e.g., DEEP-FRI extends FRI).

## Guardrails — always active

These apply at ALL stages. Read them if you haven't already:
- `guardrails/crypto_correctness.md` — the most important file in this skill. Non-negotiable rules about domain separation, challenge ordering, field size, degree tracking.
- `guardrails/notation_fidelity.md` — no unexpanded macros, consistent notation throughout.
- `guardrails/implementation_pitfalls.md` — common IOP implementation mistakes to flag.

## Worked examples — consult for quality calibration

Before generating your final output, compare against the worked examples to ensure
your spec has the same level of detail:
- `worked/deep-fri/` — complete spec for the DEEP-FRI paper (arXiv:1903.12243)

## Quality checklist

Before marking the spec complete:
- [ ] Every symbol in protocol sections is defined in the Algebraic Setting
- [ ] Every protocol has explicit COMMIT and QUERY (or equivalent) phases
- [ ] Every verification equation is stated explicitly with derivation (not just referenced)
- [ ] The Fiat-Shamir transcript schedule has no gaps (every SQUEEZE has prior ABSORBs)
- [ ] Degree bounds are tracked through every protocol round
- [ ] The ambiguity register covers all implementation choices not pinned by the paper
- [ ] No unexpanded LaTeX macros remain in the output
- [ ] Primitive interfaces list every external dependency needed for implementation

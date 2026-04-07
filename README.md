# paper2spec

A [Claude Code](https://claude.ai/claude-code) skill that converts cryptographic IOP papers into structured, language-agnostic protocol specifications.

## The Problem

Cryptographic papers describe protocols in theorem-proof style with dense notation. Implementations need step-by-step instructions with explicit data types. **paper2spec bridges that gap** — one careful extraction, many correct implementations.

## What It Produces

Given a LaTeX source of a crypto IOP paper, paper2spec outputs:

| File | Contents |
|------|----------|
| `{paper}-spec.md` | Full protocol spec: algebraic setting, round-by-round decomposition, verification equations, soundness bounds, primitive interfaces |
| `fiat-shamir-transcript.md` | Exact absorb/squeeze ordering for the Fiat-Shamir transform |
| `ambiguity-register.md` | Every implementation choice the paper leaves unspecified, with options and impact ratings |
| `notation-table.md` | Paper notation → implementation naming map |

## Quick Start

### Install

```bash
# Clone into your Claude Code skills directory
git clone https://github.com/shreyas-londhe/paper2spec ~/.claude/skills/paper2spec
```

### Use

In Claude Code, invoke the skill with a slash command:

```bash
# Run on an arXiv paper (downloads .tex source automatically)
/paper2spec 1903.12243

# Run on a local .tex file
/paper2spec /path/to/paper.tex

# Full mode (extract all protocols, not just the primary contribution)
/paper2spec 1903.12243 --mode full
```

### What happens

1. Downloads LaTeX source from arXiv (or uses your local `.tex`)
2. Expands all custom macros (deterministic, via Python scripts)
3. Extracts protocol/theorem/definition environments
4. Decomposes protocols round-by-round with explicit prover/verifier actions
5. Derives verification equations with algebraic derivations
6. Builds the Fiat-Shamir transcript schedule
7. Flags every unspecified implementation choice
8. Validates against known reference implementations

## Examples

### Sumcheck Protocol

The simplest IOP — [$\mu$ rounds, one equation pattern](worked/sumcheck/sumcheck-spec.md):

```
Round i:
  PROVER sends: g_i(0), g_i(1), ..., g_i(ℓ)    — degree-ℓ univariate polynomial
  VERIFIER checks: g_i(0) + g_i(1) = e_{i-1}
  VERIFIER sends: r_i ← random challenge

Final check: G(r_1, ..., r_μ) = e_μ
```

### DEEP-FRI

A more complex IOP with multiple sub-protocols — [full spec](worked/deep-fri/DEEP-FRI-spec.md):

- FRI base protocol (COMMIT + QUERY phases)
- DEEP-FRI extension (out-of-domain sampling + quotienting)
- Algebraic hash function $H_x$
- 14 flagged ambiguities with recommendations

## Project Structure

```
paper2spec/
├── SKILL.md                    ← Skill entry point (Claude reads this)
├── pipeline/                   ← Stage-by-stage reasoning protocols
│   ├── 00_latex_preprocess.md  ←   Acquire paper, expand macros, extract structure
│   ├── 01_protocol_inventory.md
│   ├── 02_algebraic_setting.md
│   ├── 03_protocol_decompose.md  ← Core stage: round-by-round extraction
│   ├── 04_soundness.md
│   ├── 05_impl_bridge.md        ← Fiat-Shamir schedule, primitives, ambiguities
│   └── 06_cross_validate.md
├── guardrails/                 ← Crypto-specific correctness constraints
│   ├── crypto_correctness.md   ←   Domain separation, challenge ordering, degree tracking
│   ├── notation_fidelity.md
│   └── implementation_pitfalls.md
├── scripts/                    ← Deterministic LaTeX processing (Python, no deps)
│   ├── expand_macros.py        ←   Expands \newcommand, \def, \DeclareMathOperator
│   ├── extract_environments.py ←   Extracts protocol/theorem/definition blocks
│   └── build_dependency_graph.py
├── scaffolds/                  ← Output format templates
└── worked/                     ← Reference specs for quality calibration
    ├── sumcheck/
    └── deep-fri/
```

## How It Works

The skill is a **reasoning protocol**, not a code generator. `SKILL.md` tells Claude to:

1. **Run Python scripts** on the `.tex` file — mechanical LaTeX processing (macro expansion, environment extraction, dependency graphing). These are deterministic and require no external dependencies beyond Python 3.9+ stdlib.

2. **Follow pipeline stages** — Claude reads each `pipeline/*.md` file and reasons through the extraction. The pipeline files are detailed instructions, not code.

3. **Apply guardrails** — crypto-specific correctness rules that prevent common mistakes (wrong Fiat-Shamir ordering, missed degree bounds, unexpanded notation).

4. **Assemble the spec** — combine stage outputs into the final spec files using the scaffold templates.

## Modes

| Mode | Description |
|------|-------------|
| `minimal` (default) | Primary protocol contribution only |
| `full` | All protocols including recalled base protocols |
| `delta` | Only differences from a base protocol (for extension papers) |

## Supported Input

| Source | How |
|--------|-----|
| arXiv | Downloads `.tex` source via `/e-print/` endpoint (perfect math fidelity) |
| IACR ePrint | Checks for arXiv cross-post first; PDF fallback with quality warning |
| Local `.tex` | Direct use |

## Limitations (alpha)

- **LaTeX source required** — PDF extraction for math-heavy crypto papers is lossy. Works best with arXiv papers that have `.tex` source.
- **IOP-focused** — designed for Interactive Oracle Proof papers (FRI, sumcheck, GKR, etc.). May work for other proof systems but not tested.
- **Not fully automated** — Claude follows the pipeline with human-in-the-loop reasoning. The scripts handle mechanical LaTeX processing; Claude handles the protocol understanding.

## License

MIT

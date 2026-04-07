# Stage 01: Protocol Inventory

## Purpose
Catalog all protocols, theorems, definitions in the paper. Determine the paper type,
identify what's novel vs. imported, and establish the scope of spec extraction.

## Input
- `environments.json` from Stage 00
- `graph.json` from Stage 00
- `expanded.tex` for reading context around environments

## Output
- `inventory.md` — structured inventory with classifications

## Process

### Step 1: Classify paper type

Read the abstract and introduction. Classify as one of:

| Type | Description | Spec Focus |
|------|-------------|------------|
| **(a) New IOP/argument** | Novel protocol with prover/verifier | Full protocol extraction |
| **(b) Optimization on existing IOP** | Modification to known protocol | Delta from base protocol |
| **(c) Commitment scheme** | Polynomial commitment construction | Interface + construction |
| **(d) Compiler/transformation** | IOP -> SNARK, IOP -> IOP | Transformation spec |
| **(e) Theoretical/impossibility** | Lower bounds, separations | Not suitable for spec |

### Step 2: List all protocols

For each `protocol` environment from `environments.json`:
- **Name**: from the optional argument
- **Label**: for cross-referencing
- **Lines**: location in source
- **Phases**: identify COMMIT/QUERY or equivalent phases
- **Role**: novel contribution vs. recalled from prior work

### Step 3: List key theorems and their roles

For each `theorem` environment:
- **Soundness theorem**: proves security of a protocol — extract bounds
- **Completeness theorem**: proves honest execution works — note conditions
- **Structural theorem**: mathematical result used in analysis — note for Section 6
- **Imported theorem**: cited from prior work — reference only

### Step 4: List definitions

For each `definition` environment:
- **Algebraic object**: field, group, code, etc. — extract for Section 0
- **Problem/relation**: R1CS, APR, etc. — extract for protocol context
- **Protocol primitive**: commitment scheme interface, etc. — extract for Section 1

### Step 5: Determine scope

Using the paper type and protocol list:
- **EXTRACT**: protocols that are the paper's contribution
- **SUMMARIZE**: base protocols that the paper extends (extract interface only)
- **REFERENCE**: standard definitions that can be cited without extraction
- **SKIP**: proofs, tightness results, counterexamples (unless they inform implementation)

### Step 6: Build dependency chain

From `graph.json`, determine the order of protocol decomposition:
- Which protocols depend on which definitions/lemmas?
- What is the minimal set of definitions needed to state each protocol?
- What is the natural bottom-up order for spec construction?

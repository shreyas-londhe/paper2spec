# Stage 04: Soundness Analysis

## Purpose
Extract precise soundness bounds from the paper's theorems.
Translate them into concrete parameter guidance for implementors.

## Input
- `environments.json` (theorem environments)
- `expanded.tex`
- `algebraic_setting.md` from Stage 02

## Output
- `soundness.md` — Section 6 of the spec

## Process

### Step 1: Identify soundness theorems

From `environments.json`, find all theorems with:
- "soundness" in the name or content
- Bounds on acceptance probability or error
- Conditions on field size, distance, parameters

### Step 2: For each soundness theorem, extract

1. **Statement**: the exact bound (copy the formula)
2. **Conditions**: what must hold for the bound to apply
   - Field size requirements (e.g., |F| >> n)
   - Distance requirements (e.g., delta > 0)
   - Honest prover conditions
3. **Decomposition**: split into commit-phase error and query-phase error if applicable
4. **Concrete instantiation**: plug in specific parameters

### Step 3: Produce parameter guidance

For standard security levels, compute required parameters:

```
For 128-bit security (soundness error < 2^{-128}):
  Given: rho = 1/8, |L^(0)| = 2^20, |F| = 2^64 (Goldilocks)
  
  Commit-phase error: [formula] = [concrete value]
  Query-phase error per rep: [formula] = [concrete value]
  Required repetitions ell: [computation] = [value]
  
  Total proof size: [computation]
  Verifier time: [computation]
```

### Step 4: Note conjectured bounds

If the paper gives both proven and conjectured bounds:
- State the proven bound as the primary
- Note the conjectured bound separately with the conjecture reference
- Explain the gap and what it means for implementors

### Step 5: Cross-check with paper's examples

If the paper provides worked examples or parameter tables:
- Verify your parameter guidance matches
- Note any discrepancies in the ambiguity register

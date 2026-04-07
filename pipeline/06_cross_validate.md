# Stage 06: Cross-Validation

## Purpose
Validate the generated spec against known reference implementations.
Fix any discrepancies before finalizing.

## Input
- Complete spec draft (all sections assembled)
- Reference implementation list (from paper inventory or known repos)

## Output
- `validation_report.md` — discrepancies found and resolved
- Corrected spec sections (if needed)

## When to skip

If no reference implementations exist (e.g., the paper is very new), mark the spec as
"**Unvalidated — no reference implementations found**" and skip this stage. This is
acceptable for alpha specs.

## Process

### Step 1: Identify reference implementations

Search for implementations in this priority order:
1. **Official code** linked in the paper (highest trust)
2. **Well-known libraries** that implement the protocol family (e.g., winterfell, plonky2, lambdaworks for FRI)
3. **Open-source projects** found via search:
```bash
gh search repos "{protocol_name}" --limit 10
gh search code "{protocol_name} commit verify" --limit 10
```

If multiple implementations exist and disagree, **the paper is ground truth** — the spec
should match the paper, not any particular implementation. Note disagreements in the
ambiguity register.

### Step 2: Validate protocol structure

For each reference implementation:
1. Find the prover code — does it match our COMMIT phase round order?
2. Find the verifier code — does it match our QUERY phase checks?
3. Find the transcript/channel code — does it match our Fiat-Shamir schedule?

Focus on:
- **Round ordering**: are challenges generated in the same order?
- **Verification equation**: does the code check the same equation?
- **Degree bounds**: does the code use the same degree tracking?

### Step 3: Validate algebraic operations

For the algebraic hash / folding function:
- Does the implementation compute it the same way?
- Are there optimizations that change the mathematical form?
  (e.g., using NTTs instead of point-by-point evaluation)

### Step 4: Resolve discrepancies

For each discrepancy:
1. Determine if it's a spec error, an implementation optimization, or a
   deliberate deviation from the paper
2. If spec error: fix the spec
3. If implementation optimization: note in implementation notes
4. If deviation: add to ambiguity register

### Step 5: Check ambiguity register completeness

Cross-reference the ambiguity register against implementation choices:
- For each ambiguity we flagged, what did implementations choose?
- Are there implementation choices we missed?
- Update recommended defaults based on what implementations actually do

### Step 6: Produce validation report

```
## Validation Report

### Reference Implementations Checked
- [repo name] ([language]) — [variant]

### Verified Correct
- [ ] COMMIT phase round ordering
- [ ] QUERY phase verification equations
- [ ] Fiat-Shamir transcript schedule
- [ ] Degree bound tracking
- [ ] Algebraic hash computation

### Discrepancies Found
| # | Spec Section | Implementation | Resolution |
|---|-------------|---------------|------------|

### Ambiguity Register Updates
| ID | Implementation Choice | Source |
|----|----------------------|--------|
```

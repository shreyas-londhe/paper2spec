# Guardrail: Implementation Pitfalls

Common mistakes in IOP implementations. The spec should proactively
flag these where relevant.

## 1. Off-by-One in Degree Bounds

**Mistake**: Starting with degree `d`, after one FRI fold the degree should be `floor((d-1)/2)`, not `d/2`.

**Why it matters**: If the verifier expects the wrong degree, it either rejects honest provers or accepts cheating ones.

**In the spec**: Provide an explicit degree table:
```
Round 0: degree < d^(0)
Round 1: degree < floor((d^(0) - 1) / 2)
...or for DEEP-FRI with quotienting:
Round 0: degree < d^(0)
After quotient: degree < d^(0) - 1
After fold: degree < floor((d^(0) - 2) / 2)
```

## 2. Forgetting to Absorb Merkle Roots

**Mistake**: Generating a Fiat-Shamir challenge without first absorbing the
Merkle root of the latest oracle commitment.

**Why it matters**: The prover can choose the oracle after seeing the challenge,
completely breaking soundness. This is a Fiat-Shamir transform error, not
visible in the interactive model.

**In the spec**: The transcript schedule must have ABSORB(root) before every SQUEEZE(challenge).

## 3. Batch Opening Inconsistency

**Mistake**: When opening multiple points in a Merkle tree, verifying only
some authentication paths.

**Why it matters**: An adversarial prover can provide correct leaves for
checked positions but wrong leaves for unchecked positions.

**In the spec**: State that ALL authentication paths must be verified for
every query position.

## 4. Constant Polynomial Check

**Mistake**: Checking that `f^(r)(s^(r)) == C` at the queried point only,
without verifying `f^(r)` is actually constant everywhere.

**Why it matters**: A cheating prover could commit to a non-constant `f^(r)`
that happens to equal `C` at the queried points.

**In the spec**: Clarify how the final round is handled. Options:
- Prover sends all evaluations of `f^(r)` (if domain is small enough)
- Prover sends just `C` and verifier checks at queried points (accepting
  soundness error from non-constant `f^(r)`)
- Prover sends the full last-layer polynomial coefficients

## 5. Index Translation Between Domains

**Mistake**: When computing `s^(i+1) = q^(i)(s^(i))`, incorrectly translating
between the field element `s^(i+1)` and the Merkle tree index of `f^(i+1)`.

**Why it matters**: Querying the wrong Merkle tree position returns the wrong
evaluation, causing honest provers to fail.

**In the spec**: If domain indexing is non-trivial, describe the mapping:
- How domain elements map to Merkle leaf indices
- How the two-to-one map translates between index spaces
- Whether the domain is in natural order or bit-reversed order

## 6. Extension Field Handling

**Mistake**: When the protocol operates over an extension field F_{p^k},
incorrectly reducing elements or mixing base field and extension field operations.

**Why it matters**: Challenges must be in the extension field for soundness,
but some evaluations may be in the base field. Mixing them silently corrupts results.

**In the spec**: If the protocol uses extension fields, clearly state:
- Which values are in the base field vs extension field
- When extension field arithmetic is needed
- How base field elements embed into the extension field

## 7. Parallelization Hazards

**Mistake**: Parallelizing rounds that have sequential dependencies.

**Why it matters**: In FRI, round `i+1` depends on the challenge `x^(i)` which
depends on the commitment of round `i`. These CANNOT be parallelized.
However, within a single round, the evaluations of `f^(i+1)` at different
domain points CAN be parallelized.

**In the spec**: Note which operations are parallelizable and which are sequential.

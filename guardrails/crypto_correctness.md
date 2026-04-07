# Guardrail: Cryptographic Correctness

These rules are NON-NEGOTIABLE. Violating any of them produces a spec that
compiles but is cryptographically unsound.

## 1. Domain Separation for Out-of-Domain Sampling

**Rule**: When the protocol samples z in F_q for quotienting, z MUST NOT be in the evaluation domain L.

**Why**: The quotient operation `(f(y) - b) / (y - z)` requires `y - z != 0` for all `y in L`. If `z in L`, division by zero occurs and the quotient is undefined.

**In the spec**: Explicitly state `z in F_q \ L` and note that if z accidentally lands in L (probability |L|/|F_q|, typically negligible), the protocol must resample.

## 2. Challenge Ordering in Fiat-Shamir

**Rule**: In the Fiat-Shamir transcript, challenges MUST be squeezed AFTER all relevant prover messages are absorbed.

**Why**: If a challenge is derived before the prover's message is committed, the prover can adaptively choose its message after seeing the challenge, breaking soundness.

**Specifically for DEEP-FRI-style protocols**:
- `z^(i)` must be squeezed BEFORE `B^(i)` is sent by the prover
- `x^(i)` must be squeezed AFTER `B^(i)` is absorbed
- Merkle root of `f^(i+1)` must be absorbed BEFORE `z^(i+1)` is squeezed

**In the spec**: The Fiat-Shamir transcript schedule must make this ordering explicit. Mark every absorb/squeeze with its position in the sequence.

## 3. Field Size Requirements

**Rule**: Soundness bounds require the field to be large enough. The spec MUST state the minimum field size.

**Why**: Soundness error typically includes terms like `r * d / |F|` (commit-phase error) and `(1 - delta + epsilon)^ell` (query-phase error). If `|F|` is too small relative to `r * d`, the commit phase is insecure regardless of how many queries.

**In the spec**: State the field size constraint from the soundness theorem. For concrete parameters, verify that the chosen field satisfies it.

## 4. Degree Bound Tracking

**Rule**: The spec MUST explicitly track the degree bound at every step of the protocol.

**Why**: Off-by-one in degree bounds is one of the most common bugs in IOP implementations. If the verifier checks the wrong degree, either honest provers fail (completeness broken) or cheating provers pass (soundness broken).

**Track through**:
- Starting degree `d^(0)` of the input polynomial
- After quotienting: degree drops by 1 (from `d` to `d - 1`)
- After folding (FRI step): degree halves (from `d` to `d/2`)
- After `r` rounds: final degree should be `< d^(0) / 2^r` (or adjusted for quotienting)

## 5. Coset vs Subgroup

**Rule**: The spec MUST distinguish between subgroups and cosets of subgroups.

**Why**: Many IOP protocols require the evaluation domain to be a COSET `g * H` (where H is a subgroup and g is a generator not in H), not the subgroup H itself. Using the subgroup directly can break the quotient polynomial construction (the vanishing polynomial Z_H has roots on H, but we need evaluation points away from those roots).

**In the spec**: When defining evaluation domains, state explicitly:
- Is this a subgroup or a coset?
- What is the coset shift (if any)?
- How do cosets chain across rounds?

## 6. Two-to-One Map Consistency

**Rule**: The folding/hash function H_x requires that for each point in L^(i+1), there are exactly 2 preimages in L^(i).

**Why**: The FRI fold interpolates a degree-1 polynomial through 2 points. If the two-to-one mapping is inconsistent (some points have 0 or 1 or 3 preimages), the fold produces garbage.

**In the spec**: Explicitly describe the two-to-one map (e.g., the subspace polynomial q^(i)) and verify it maps L^(i) onto L^(i+1) with exactly 2 preimages per point.

## 7. Verification Equation Direction

**Rule**: The spec MUST show the algebraic derivation of the verification equation, not just state it.

**Why**: The verification equation is a rearrangement of the protocol's core identity. Getting the sign or direction wrong (e.g., `a - b` vs `b - a`, or `a * b` vs `a / b`) produces a check that honest provers fail.

**Example for DEEP-FRI**:
```
From: f^(i+1)(y) = QUOTIENT(H_x[f^(i)], z, B_z(x))(y)
     = (H_x[f^(i)](y) - B_z(x)) / (y - z)

Rearranging: H_x[f^(i)](y) = f^(i+1)(y) * (y - z) + B_z(x)

So the verifier checks:
  H_{x^(i)}[f^(i)](s^(i+1)) == f^(i+1)(s^(i+1)) * (s^(i+1) - z^(i)) + B^(i)_{z^(i)}(x^(i))
```

Show this derivation in the spec so implementors can verify the direction.

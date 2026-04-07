# Ambiguity Register — DEEP-FRI

## Register

| ID | Category | Issue | Paper Ref | Status | Choices | Impact | Recommended |
|----|----------|-------|-----------|--------|---------|--------|-------------|
| A1 | Field | Field type: prime vs binary extension | Footnote, line 1127: "group can be additive... or multiplicative" | PARAMETERIZED | Prime field (multiplicative subgroup domain) / Binary extension (additive coset domain) | Structural | Prime field — most modern implementations (winterfell, plonky2) use multiplicative groups over prime fields like Goldilocks (p = 2^64 - 2^32 + 1) or BN254 scalar field |
| A2 | Domain | Query domain D vs L^(0) in QUERY phase | Protocol 4.6, line 1416: "s^(0) in D" but D is undefined in this context | PARTIALLY_SPECIFIED | `D = L^(0)` (most likely) / `D` could be a larger domain containing `L^(0)` | Correctness | Use `D = L^(0)` — this is what implementations do |
| A3 | Fiat-Shamir | Squeeze all query positions at once, or one at a time? | Not specified (paper is in IOP model) | UNSPECIFIED | Squeeze all `ell` positions in one batch / Squeeze one at a time | Interop | Squeeze all at once — matches winterfell and is more efficient |
| A4 | Optimization | Degree-corrected quotient vs simple quotient | Appendix, line 3000: describes `CorrectedQUOTIENT` variant | PARTIALLY_SPECIFIED | Simple `QUOTIENT` (as in Protocol 4.6) / Degree-corrected `CorrectedQUOTIENT` | Performance | Use simple QUOTIENT for correctness; degree-corrected is an optimization |
| A5 | Protocol | Multiple witness polynomials | Section 5.4, line 2044: "several witness polynomials" | PARTIALLY_SPECIFIED | Single witness (as formally defined) / Multiple witnesses via random linear combination | Performance | Start with single witness; add batch optimization later |
| A6 | Protocol | Single RPT invocation for h^1, h^2 in DEEP-ALI | Section 5.4, lines 2048-2058 | PARTIALLY_SPECIFIED | Separate DEEP-FRI for each / Combined via random linear combination | Performance | Combined — reduces proof size |
| A7 | Security | Grinding / proof-of-work | Not mentioned in paper | UNSPECIFIED | No grinding / Add N bits of grinding post-commit | Security | Add grinding — winterfell and plonky2 both use it for additional security bits |
| A8 | Hash | Hash function for Merkle tree | Not specified | UNSPECIFIED | SHA-256, Blake2, Blake3, Poseidon, Rescue | Performance/Security | Blake3 for software, Poseidon for in-circuit recursion |
| A9 | Hash | Hash function for Fiat-Shamir sponge | Not specified | UNSPECIFIED | Same as Merkle / Different hash / Algebraic hash | Security | Can differ from Merkle hash; use a proper sponge construction |
| A10 | Serialization | Endianness of field element encoding | Not specified | UNSPECIFIED | Little-endian / Big-endian | Interop | Little-endian — matches most Rust implementations |
| A11 | Optimization | Coset LDE vs direct evaluation | Not specified | UNSPECIFIED | Evaluate f^(i) on L^(i) directly / Use coset LDE with NTT | Performance | Coset LDE with NTT — orders of magnitude faster |
| A12 | Error handling | What if z^(i) lands in L^(i) | Not specified (probability negligible) | UNSPECIFIED | Abort / Resample / Treat as protocol failure | Correctness | Resample — probability is |L^(i)|/|F_q| which is negligible |
| A13 | Structure | Folding factor | Paper uses factor 2 (halve domain each round) | SPECIFIED | Factor 2 only (as in paper) / Factor 4, 8, etc. (generalized) | Structural | Factor 2 for spec fidelity; plonky2 supports higher factors as optimization |
| A14 | Verification | Last-layer check | Line 1423: "If f^(r)(s^(r)) != C, REJECT" | PARTIALLY_SPECIFIED | Send just C and spot-check / Send full last-layer evaluations / Send polynomial coefficients | Security | Send full last-layer evaluations — prevents cheating with non-constant f^(r) |

## Resolution Notes

**A1 (Field type)** is the most impactful choice. It determines:
- Domain tower construction (multiplicative: powers of generator; additive: cosets of F_2-subspaces)
- Subspace polynomial form (multiplicative: `q(X) = X^2` on roots of unity; additive: `q(X) = X^2 + alpha*X`)
- NTT/FFT algorithm (multiplicative: standard NTT; additive: additive FFT)

The paper's description of the algebraic hash H_x uses additive (F_2-subspace) notation, but the protocol works identically with multiplicative domains.

**A7 (Grinding)** is standard practice: after the commit phase, the prover searches for a nonce such that `H(transcript || nonce)` has `N` leading zero bits. This adds `N` bits of security to the commit phase cheaply.

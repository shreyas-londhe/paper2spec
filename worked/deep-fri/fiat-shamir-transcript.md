# Fiat-Shamir Transcript Schedule — DEEP-FRI

## Protocol: DEEP-FRI

### Initialization

| Step | Direction | Data | Operation | Encoding | Notes |
|------|-----------|------|-----------|----------|-------|
| 0 | — | `"DEEP-FRI-v1"` | ABSORB | UTF-8 | Domain separator |
| 1 | P -> V | `Merkle(f^(0))` | ABSORB | hash digest | Initial oracle commitment |

### COMMIT Phase (repeated for i = 0 to r-1)

| Step | Direction | Data | Operation | Encoding | Notes |
|------|-----------|------|-----------|----------|-------|
| 2+5i | V -> P | `z^(i)` | SQUEEZE | field element | OOD sample point; must verify `z^(i) not in L^(i)` |
| 3+5i | P -> V | `b0^(i), b1^(i)` | ABSORB | 2 field elements | Coefficients of `B^(i)(X) = b0 + b1*X` |
| 4+5i | V -> P | `x^(i)` | SQUEEZE | field element | Folding challenge |
| 5+5i | P -> V | `Merkle(f^(i+1))` | ABSORB | hash digest | Commitment to folded+quotiented oracle |

### Final Constant

| Step | Direction | Data | Operation | Notes |
|------|-----------|------|-----------|-------|
| 2+5r | P -> V | `C` | ABSORB | Final constant value (1 field element) |

### QUERY Phase

| Step | Direction | Data | Operation | Notes |
|------|-----------|------|-----------|-------|
| 3+5r | V | `s^(0)_1, ..., s^(0)_ell` | SQUEEZE | All `ell` query positions squeezed at once |
| — | P -> V | Merkle auth paths | — | Not absorbed into transcript (verifier checks directly) |

## Ordering Invariants

1. `z^(i)` is squeezed BEFORE `B^(i)` is absorbed (prover cannot choose B adaptively)
2. `x^(i)` is squeezed AFTER `B^(i)` is absorbed (challenge depends on prover's commitment)
3. `Merkle(f^(i+1))` is absorbed BEFORE `z^(i+1)` is squeezed (next OOD point depends on oracle)
4. ALL commit-phase data is absorbed BEFORE any query positions are squeezed

## Comparison: FRI vs DEEP-FRI Transcript

FRI is simpler — no `z^(i)` or `B^(i)` steps:

| FRI Step | DEEP-FRI Step | Difference |
|----------|--------------|------------|
| ABSORB `Merkle(f^(0))` | ABSORB `Merkle(f^(0))` | Same |
| SQUEEZE `x^(0)` | SQUEEZE `z^(0)`, ABSORB `B^(0)`, SQUEEZE `x^(0)` | DEEP adds OOD sample |
| ABSORB `Merkle(f^(1))` | ABSORB `Merkle(f^(1))` | Same |
| ... | ... | |

## Encoding Notes

- **Field elements**: serialized as fixed-width little-endian byte arrays (width = ceil(log2(q)/8) bytes)
- **Merkle roots**: output of the hash function (e.g., 32 bytes for SHA-256/Blake3)
- **Polynomial coefficients**: serialized as `[a_0, a_1]` in order (constant term first)

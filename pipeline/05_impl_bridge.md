# Stage 05: Implementation Bridge

## Purpose
Bridge from the IOP (interactive oracle) model to concrete implementation.
Produce the Fiat-Shamir transcript schedule, primitive interfaces, and
ambiguity register.

**Before starting**: Read `guardrails/implementation_pitfalls.md`.

## Input
- `protocols.md` from Stage 03
- `algebraic_setting.md` from Stage 02
- `soundness.md` from Stage 04

## Output
- `primitives.md` — Section 1 of the spec (primitive interfaces)
- `transcript.md` — Section 7 (Fiat-Shamir transcript schedule)
- `ambiguity.md` — Section 8 (ambiguity register)

## Process

### Step 1: Fiat-Shamir Transcript Schedule

The paper describes an interactive protocol. Every real implementation
uses the Fiat-Shamir transform. The transcript schedule specifies
what gets absorbed/squeezed and in what order.

**Rules:**
- Every oracle commitment (Merkle root) must be ABSORBED before the next SQUEEZE
- Every prover message must be ABSORBED before the verifier's response
- Challenges are SQUEEZED after all relevant prover messages are absorbed
- Domain separation: if the protocol has distinct sub-protocols, note separation points

**For each step in the protocol, record:**

| Step | Direction | Data | Operation | Type | Notes |
|------|-----------|------|-----------|------|-------|
| 1 | P -> V | Merkle(f^(0)) | ABSORB | commitment | initial oracle |
| 2 | V -> P | z^(0) | SQUEEZE | challenge | OOD sample point |
| 3 | P -> V | B^(0) coeffs | ABSORB | field elements | degree-1 poly (2 elements) |
| 4 | V -> P | x^(0) | SQUEEZE | challenge | folding challenge |
| 5 | P -> V | Merkle(f^(1)) | ABSORB | commitment | folded oracle |
| ... | | | | | |

**Critical**: The ordering z^(i) BEFORE B^(i) BEFORE x^(i) is essential
for soundness. Verify this matches the paper's protocol specification.

### Step 2: Primitive Interfaces

List every external primitive the protocol needs. For each:

| Primitive | Interface | Notes |
|-----------|-----------|-------|
| Field arithmetic | add, mul, inv, sub, neg, pow, random | Over F_q |
| Polynomial ops | eval(poly, point), interpolate_2(p1, v1, p2, v2) | Degree-1 interpolation for FRI fold |
| Merkle tree | commit(leaves) -> root, open(idx) -> (leaf, auth_path), verify(root, idx, leaf, path) -> bool | For oracle commitments |
| Hash function | H: bytes -> F_q | For Fiat-Shamir, must be collision-resistant |
| Transcript | new(), absorb(bytes), squeeze() -> F_q | Fiat-Shamir sponge |
| Domain ops | domain_generator(size), coset_shift(domain, g) | For constructing L^(i) |

Note which primitives are standard (use a library) vs. protocol-specific.

### Step 3: Ambiguity Register

Systematically audit the protocol for unspecified implementation choices.

**Check each category:**

1. **Field choice**: Is the field fully specified or parameterized?
2. **Domain construction**: How exactly are L^(i) constructed? Multiplicative vs additive?
3. **Hash function**: Which hash for Merkle trees? Which for Fiat-Shamir?
4. **Serialization**: How are field elements encoded for hashing? Endianness?
5. **Batch operations**: Can queries be batched? How?
6. **Proof-of-work / grinding**: Does the paper mention it? Do implementations add it?
7. **Error handling**: What if z^(i) lands in L^(i)?
8. **Optimizations**: Degree-corrected quotient? Coset FFTs?

**For each ambiguity, record:**

| ID | Issue | Paper Ref | Choices | Impact | Recommended Default |
|----|-------|-----------|---------|--------|-------------------|
| A1 | Field type | footnote, line X | prime / binary ext | Structural | Prime field (most implementations) |

**Impact levels:**
- **Structural**: changes the protocol's algebraic structure
- **Security**: affects soundness guarantees
- **Performance**: affects prover/verifier efficiency
- **Interop**: affects compatibility between implementations

### Step 4: Implementation Notes

Add practical notes that aren't in the paper but matter for implementation:
- Memory layout for polynomial evaluations
- Parallelization opportunities (which rounds are independent?)
- Common library mappings (e.g., "for Rust, use ark-poly for FFT")
- Known edge cases in reference implementations

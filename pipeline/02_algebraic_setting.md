# Stage 02: Algebraic Setting Extraction

## Purpose
Extract and precisely define every mathematical object used in the protocol.
This becomes Section 0 of the spec — the foundation everything else builds on.

## Input
- `expanded.tex`
- `environments.json` (definitions, especially)
- `inventory.md` from Stage 01

## Output
- `algebraic_setting.md` — Section 0 of the spec

## Process

### Step 1: Identify the field

Every IOP operates over a finite field. Extract:
- **Field notation**: F, F_q, F_p, GF(2^n), etc.
- **Field type**: prime field F_p, binary extension F_{2^n}, or generic
- **Size constraints**: any requirements on |F| (e.g., "|F| > n^2" for soundness)
- **Classification**: `SPECIFIED` (paper gives exact field) / `PARAMETERIZED` (generic over field choice) / `CONSTRAINED` (paper gives inequality)

### Step 2: Identify evaluation domains

IOPs use structured evaluation domains. Extract:
- **Domain names**: L, D, L^(0), L^(1), ..., L^(r)
- **Domain structure**: multiplicative subgroup, additive coset, roots of unity
- **Domain sizes**: |L^(i)| = 2^{k-i} or similar
- **Domain relationships**: L^(i+1) = q^(i)(L^(i)) or similar (how domains chain)
- **Coset structure**: is L a coset g*<omega> or the subgroup itself?

### Step 3: Identify codes

Extract Reed-Solomon or other code definitions:
- **Code notation**: RS[F, L, rho] or RS[F, L, d]
- **Rate vs degree**: clarify if the paper uses rate (rho) or degree (d) parameterization
- **Relationship**: d = rho * |L|
- **Code tower**: RS^(0), RS^(1), ... and how they relate to domains

### Step 4: Identify key polynomials and operations

- **Witness polynomial**: the polynomial being tested for proximity
- **Subspace/vanishing polynomials**: q^(i)(X), Z_H(X), etc.
- **Algebraic hash / folding**: H_x[f] and how it's computed
- **Quotient operation**: QUOTIENT(f, z, b) if used
- **Composition polynomials**: any polynomial constructed from multiple oracles

For each polynomial, record:
- Degree bound (exact or asymptotic)
- Domain (where it's evaluated)
- Representation (coefficient vs evaluation form)

### Step 5: Identify parameters

- **Security parameter**: lambda
- **Rate**: rho (and how it relates to code parameters)
- **Number of rounds**: r (and how it's computed from other params)
- **Repetition parameter**: ell (number of query repetitions)
- **Degree bounds**: d^(0), d^(1), ... through the protocol
- **List size bounds**: L, L* from list-decoding theorems

### Step 6: Produce algebraic setting section

Write Section 0 of the spec with all objects fully defined.
Every symbol that appears later in the protocol sections MUST
be defined here. Use consistent notation throughout — if the paper
uses both rho and R for rate, pick one and note the other.

**Format**:
```
## 0. Algebraic Setting

**Field**: F_q — [description, constraints]
**Evaluation domains**: L^(0), L^(1), ..., L^(r) — [structure, sizes]
**Reed-Solomon code**: RS[F_q, L^(i), rho] = {f: L^(i) -> F_q | deg(f) < rho * |L^(i)|}
**Rate**: rho = 2^{-R} for positive integer R
**Rounds**: r = log2(|L^(0)|) - log2(1/rho)
...
```

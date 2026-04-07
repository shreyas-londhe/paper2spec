---
paper: "DEEP-FRI: Sampling Outside the Box Improves Soundness"
arxiv: "1903.12243"
eprint: "2019/336"
authors:
    ["Eli Ben-Sasson", "Lior Goldberg", "Swastik Kopparty", "Shubhangi Saraf"]
protocols: ["FRI", "DEEP-FRI", "DEEP-ALI"]
spec_version: "1.0"
generated_by: "paper2spec"
---

# DEEP-FRI — Protocol Specification

> This spec is designed for LLM agents implementing the protocol.
> Every symbol is defined, every round is explicit, every check is spelled out.

---

## 0. Algebraic Setting

**Field**: `F_q` — a finite field of size `q`. May be a prime field `F_p` or a binary extension field `F_{2^n}`. The paper is generic over the field type (see Ambiguity A1). The field must satisfy `q >> |L^(0)|` for soundness (specifically, commit-phase error includes terms like `r / q`).

**Evaluation domains**: A sequence of nested domains:

- `L^(0)` — the initial evaluation domain, a coset of a (multiplicative or additive) subgroup of `F_q`, with `|L^(0)| = 2^k`
- `L^(i+1) = q^(i)(L^(i))` — each domain is the image of the previous under the "subspace polynomial" `q^(i)`, with `|L^(i)| = 2^{k-i}`
- `L^(r)` — the final domain, `|L^(r)| = 2^{k-r}`

**Subspace polynomial** (two-to-one map): For each round `i`, there is a 1-dimensional subspace `L^(i)_0 ⊆ L^(i)` and the subspace polynomial:

```
q^(i)(X) = prod_{alpha in L^(i)_0} (X - alpha)
```

This is a degree-2 polynomial that maps `L^(i)` onto `L^(i+1)` with exactly 2 preimages per point. The kernel of `q^(i)` is `L^(i)_0`.

**Reed-Solomon code**:

```
RS[F_q, L, rho] = {f: L -> F_q | there exists poly p of degree < rho * |L| such that f = p|_L}
```

where `rho` is the rate.

**Rate**: `rho = 2^{-R}` for a positive integer `R`.

**Number of rounds**: `r = k - R` (where `k = log2(|L^(0)|)`). After `r` rounds of folding, the domain has size `2^R = 1/rho`, and the degree bound matches the domain size (i.e., the polynomial is determined by its evaluations).

**RS code tower**: `RS^(i) = RS[F_q, L^(i), rho * |L^(i)|]`. Note: the rate `rho` is constant across rounds, but the degree bound `rho * |L^(i)|` halves each round since `|L^(i)|` halves.

**Repetition parameter**: `ell` — the number of independent query repetitions. Each repetition reduces soundness error multiplicatively.

**Coset structure**: `S^(i)` = the set of cosets of `L^(i)_0` within `L^(i)`. Since `dim(L^(i)_0) = 1`, each coset has 2 elements, and there are `|L^(i)|/2 = |L^(i+1)|` cosets.

---

## 1. Primitive Interfaces

| Primitive              | Interface                                                                                          | Notes                                      |
| ---------------------- | -------------------------------------------------------------------------------------------------- | ------------------------------------------ |
| Field arithmetic       | `add(a, b)`, `mul(a, b)`, `inv(a)`, `sub(a, b)`, `neg(a)`, `random()`                              | Over `F_q`                                 |
| Degree-1 interpolation | `interpolate_2(x0, y0, x1, y1) -> (a0, a1)` where `P(x) = a0 + a1*x`                               | Used in FRI fold: `P(x0) = y0, P(x1) = y1` |
| Degree-1 evaluation    | `eval_linear(a0, a1, x) -> a0 + a1*x`                                                              | Evaluate the interpolated polynomial       |
| Merkle tree            | `commit(leaves) -> root`, `open(index) -> (leaf, path)`, `verify(root, index, leaf, path) -> bool` | For oracle commitments                     |
| Cryptographic hash     | `H: bytes -> bytes`                                                                                | For Merkle tree and Fiat-Shamir            |
| Transcript (sponge)    | `new() -> T`, `T.absorb(data)`, `T.squeeze() -> F_q`                                               | Fiat-Shamir transform                      |
| Domain construction    | Given `k`, construct `L^(0)` and the two-to-one maps `q^(i)`                                       | Field-dependent (see A1)                   |

---

## 2. Algebraic Hash Function H_x (FRI Fold)

> Paper reference: Section A.2 (line 2161)

This is the building block used in both FRI and DEEP-FRI. Implementations typically call this the "FRI fold" or "degree-respecting projection (DRP)".

### Algorithm

Given a seed `x in F_q` and a function `f: L^(i) -> F_q`:

```
H_x[f]: L^(i+1) -> F_q

For each s in L^(i+1):
    1. Find the two preimages: {s_0, s_1} = (q^(i))^{-1}(s)
       i.e., q^(i)(s_0) = q^(i)(s_1) = s, with s_0 != s_1
    2. Query f(s_0) and f(s_1)
    3. Interpolate: let P(X) be the unique degree-1 polynomial with
       P(s_0) = f(s_0) and P(s_1) = f(s_1)
    4. Return H_x[f](s) = P(x)
```

### Explicit formula

```
P(X) = f(s_0) * (X - s_1)/(s_0 - s_1) + f(s_1) * (X - s_0)/(s_1 - s_0)
H_x[f](s) = P(x) = f(s_0) * (x - s_1)/(s_0 - s_1) + f(s_1) * (x - s_0)/(s_1 - s_0)
```

### Properties

- **Locality**: Computing `H_x[f](s)` requires exactly 2 queries to `f`
- **Completeness**: If `f in RS^(i)`, then `H_x[f] in RS^(i+1)` for all `x`
- **Degree**: If `deg(f) < d`, then `deg(H_x[f]) < d/2`

---

## 3. Protocol: FRI (Base Protocol)

> Paper reference: Section 4.1 (line 1124)

FRI is an Interactive Oracle Proof of Proximity (IOPP) for Reed-Solomon codes. It tests whether `f^(0): L^(0) -> F_q` is close to `RS^(0)`.

### 3.1 COMMIT Phase

```
Input: f^(0): L^(0) -> F_q

For i = 0 to r-1:
    VERIFIER: squeeze challenge x^(i) in F_q from transcript

    PROVER: compute f^(i+1): L^(i+1) -> F_q where
        f^(i+1)(s) = H_{x^(i)}[f^(i)](s) for each s in L^(i+1)

    PROVER: commit Merkle(f^(i+1)) and send root to verifier
    TRANSCRIPT: absorb Merkle root of f^(i+1)

PROVER: send C in F_q (claimed value of the constant polynomial f^(r))
TRANSCRIPT: absorb C
```

### 3.2 QUERY Phase

```
Repeat ell times:
    VERIFIER: squeeze s^(0) uniformly from L^(0)

    For i = 0 to r-1:
        1. Compute s^(i+1) = q^(i)(s^(i))
        2. Query f^(i) at the two preimages {s_0, s_1} of s^(i+1)
        3. Compute expected = H_{x^(i)}[f^(i)](s^(i+1))
           = interpolate through (s_0, f^(i)(s_0)), (s_1, f^(i)(s_1)), evaluate at x^(i)
        4. Query actual = f^(i+1)(s^(i+1))
        5. If expected != actual: REJECT

    If f^(r)(s^(r)) != C: REJECT

ACCEPT
```

### 3.3 Verification Equation

At each round `i`, the verifier checks:

```
H_{x^(i)}[f^(i)](s^(i+1)) == f^(i+1)(s^(i+1))
```

where the left side is computed from 2 queries to `f^(i)`, and the right side is queried from `f^(i+1)`.

---

## 4. QUOTIENT Operation

> Paper reference: Section 4.2.1 (line 1339)

### Definition

```
QUOTIENT(f, z, b): L -> F_q

Input:
  f: L -> F_q     — a function on domain L
  z in F_q \ L    — a point OUTSIDE the domain (CRITICAL: z must not be in L)
  b in F_q        — a claimed evaluation value

Output:
  g: L -> F_q where g(y) = (f(y) - b) / (y - z)
```

### Key Property (Lemma 4.7)

Let `z not in L`, `d >= 1`, `f: L -> F_q`, `b in F_q`, and `g = QUOTIENT(f, z, b)`. Then:

> There exists a polynomial `Q(X)` of degree `<= d-1` with `Delta(g, Q) < delta`
> **if and only if**
> there exists a polynomial `R(X)` of degree `<= d` with `Delta(f, R) < delta` and `R(z) = b`.

**Degree effect**: Quotienting reduces the degree by 1.

---

## 5. Protocol: DEEP-FRI

> Paper reference: Protocol 4.6 (line 1391)

DEEP-FRI modifies FRI by adding an out-of-domain (OOD) sampling step before each fold. This improves soundness from the "double Johnson" bound to the Johnson bound (provably) or beyond (conjecturally).

### 5.1 COMMIT Phase

```
Input: f^(0): L^(0) -> F_q, supposed to be of degree < d^(0)

For i = 0 to r-1:
    VERIFIER: squeeze z^(i) in F_q from transcript
        (out-of-domain sample point; z^(i) must NOT be in L^(i))

    PROVER: send B^(i)_{z^(i)}(X) — a degree-1 polynomial in F_q[X]
        (two coefficients: b0, b1 such that B(X) = b0 + b1*X)
        Semantics: B^(i)_{z^(i)}(x) should equal H_x[f^(i)](z^(i))
        i.e., the evaluation of the "folded" polynomial at the OOD point z^(i)
    TRANSCRIPT: absorb b0, b1 (the two coefficients of B^(i))

    VERIFIER: squeeze x^(i) in F_q from transcript
        (folding challenge)

    PROVER: compute f^(i+1): L^(i+1) -> F_q where for each y in L^(i+1):
        step1 = H_{x^(i)}[f^(i)](y)      — standard FRI fold
        step2 = B^(i)_{z^(i)}(x^(i))     — evaluate B at the folding challenge
        f^(i+1)(y) = (step1 - step2) / (y - z^(i))   — QUOTIENT operation

    PROVER: commit Merkle(f^(i+1)) and send root
    TRANSCRIPT: absorb Merkle root of f^(i+1)

PROVER: send C in F_q (final constant value)
TRANSCRIPT: absorb C
```

### 5.2 QUERY Phase

```
Repeat ell times:
    VERIFIER: squeeze s^(0) uniformly from L^(0)

    For i = 0 to r-1:
        1. Compute s^(i+1) = q^(i)(s^(i))

        2. Compute H_{x^(i)}[f^(i)](s^(i+1)):
           - Find preimages {s_0, s_1} of s^(i+1) under q^(i)
           - Query f^(i)(s_0) and f^(i)(s_1)
           - Interpolate degree-1 poly through (s_0, f^(i)(s_0)), (s_1, f^(i)(s_1))
           - Evaluate at x^(i) to get lhs

        3. Query f^(i+1)(s^(i+1)) to get rhs_f

        4. Compute rhs = rhs_f * (s^(i+1) - z^(i)) + B^(i)_{z^(i)}(x^(i))

        5. VERIFY: lhs == rhs
           If not equal: REJECT

    If f^(r)(s^(r)) != C: REJECT

ACCEPT
```

### 5.3 Verification Equation

**At each round `i`, the verifier checks:**

```
H_{x^(i)}[f^(i)](s^(i+1))  ==  f^(i+1)(s^(i+1)) * (s^(i+1) - z^(i)) + B^(i)_{z^(i)}(x^(i))
```

**Derivation:**

From the prover's construction:

```
f^(i+1)(y) = QUOTIENT(H_{x^(i)}[f^(i)], z^(i), B^(i)_{z^(i)}(x^(i)))(y)
           = (H_{x^(i)}[f^(i)](y) - B^(i)_{z^(i)}(x^(i))) / (y - z^(i))
```

Rearranging:

```
H_{x^(i)}[f^(i)](y) = f^(i+1)(y) * (y - z^(i)) + B^(i)_{z^(i)}(x^(i))
```

Substituting `y = s^(i+1)` gives the verification equation.

**Left side** (computed by verifier from 2 queries to `f^(i)`):

- Query `f^(i)` at the two preimages of `s^(i+1)` under `q^(i)`
- Interpolate degree-1 polynomial and evaluate at `x^(i)`

**Right side** (computed by verifier from 1 query to `f^(i+1)` + known values):

- Query `f^(i+1)(s^(i+1))` from the committed oracle
- Multiply by `(s^(i+1) - z^(i))` (known: `s^(i+1)` from domain, `z^(i)` from transcript)
- Add `B^(i)_{z^(i)}(x^(i))` (known: `B^(i)` was sent by prover, `x^(i)` from transcript)

### 5.4 Degree Tracking

```
Round 0: f^(0) has degree < d^(0)
  After H_x fold: degree < d^(0) / 2
  After QUOTIENT: degree < d^(0)/2 - 1

Round 1: f^(1) has degree < d^(0)/2 - 1
  After H_x fold: degree < (d^(0)/2 - 1) / 2
  After QUOTIENT: degree < (d^(0)/2 - 1)/2 - 1

General round i: f^(i) has degree < d^(i) where
  d^(i+1) = d^(i)/2 - 1  (fold halves, quotient subtracts 1)
```

---

## 6. Protocol: DEEP-ALI

> Paper reference: Protocol 5.5 (line 1871), Section 5

DEEP-ALI is an IOP for the Algebraic Placement and Routing (APR) relation. It uses DEEP-FRI as a sub-protocol for proximity testing.

### 6.1 APR Relation (Definition 5.2)

The relation R_APR consists of pairs `(x, w)` where:

**Instance** `x = (F_q, d, C)`:

- `F_q`: finite field
- `d`: integer degree bound on witness
- `C`: set of `|C|` constraint tuples `(M^i, P^i, Q^i)` where:
    - `M^i` (mask): sequence of field elements `{M^i_j}_{j=1}^{|M^i|} ⊆ F_q`
    - `P^i` (condition): polynomial with `|M^i|` variables
    - `Q^i` (domain polynomial): polynomial in `F_q[x]` vanishing on constraint locations

**Witness** `w`: a polynomial `f_tilde in F_q[X]` of degree `< d` satisfying all constraints:

- For each constraint `(M, P, Q)` and every `x` where `Q(x) = 0`:
  `P(f_tilde(x * M_1), ..., f_tilde(x * M_{|M|})) = 0`

**Derived notation**:

- Full mask: `M_full = union of all M^i_j`
- Max constraint degree: `d_C = max_i deg(P^i)`
- LCM domain polynomial: `Q_lcm = lcm(Q^1, ..., Q^{|C|})`

### 6.2 DEEP-ALI Protocol (sketch)

The protocol proceeds as:

1. Prover commits to witness oracle `f: D -> F_q` (evaluation of `f_tilde` on domain `D`)
2. Prover constructs composition polynomial `g_alpha: D' -> F_q` from random linear combination of constraints
3. Verifier samples OOD point `z in F_q`
4. Prover sends evaluations of `f_tilde` at mask points `{f_tilde(z * M_j)}` for all `M_j in M_full`
5. Verifier constructs quotient polynomials `h^1, h^2` using QUOTIENT operation
6. Both `h^1` and `h^2` are tested for proximity to RS codes using DEEP-FRI (or FRI)

> Full round-by-round decomposition of DEEP-ALI requires additional detail
> from the paper's Protocol 5.5 and is beyond the scope of this FRI-focused spec.
> See the paper lines 1871-1910 for the complete protocol.

---

## 7. Soundness Bounds

### FRI Soundness (Theorem 3.3, prior art from BKS18)

For `f^(0)` that is `delta^(0)`-far from `RS^(0)`, with `n = |L^(0)|`:

- **Commit-phase error**: at most `2 * log(n) / (epsilon^3 * |F|)`
- **Query-phase error** (per repetition): at most `(1 - min(delta^(0), 1 - rho^{1/4} - epsilon') + epsilon * log(n))^ell`

### DEEP-FRI Soundness (Theorem 4.8)

For `f^(0)` that is `delta^(0)`-far from `RS^(0)`:

- **Commit-phase error**: at most `r * nu*` where `nu*` depends on the list-decoding radius
- **Query-phase error** (per repetition): at most `(1 - delta* + r * epsilon)^ell`

where `delta* = min(delta^(0), delta_max)` and `delta_max` is the list-decoding threshold.

### Concrete Instantiations

**Using Johnson bound** (Example 4.10, proven):

```
delta_max = 1 - sqrt(rho) - o(1)
```

**Under list-decoding conjecture** (Conjecture 3.2):

```
delta_max = 1 - rho - o(1)
```

### Parameter Guidance

For 128-bit security with `rho = 1/8`:

| Parameter           | Value             | Derivation                                   |
| ------------------- | ----------------- | -------------------------------------------- |
| `rho`               | 1/8               | Chosen                                       |
| `R`                 | 3                 | `rho = 2^{-3}`                               |
| `\|L^(0)\|`         | 2^20              | Example: 1M constraint system                |
| `k`                 | 20                | `log2(\|L^(0)\|)`                            |
| `r`                 | 17                | `k - R = 20 - 3`                             |
| `\|F\|`             | 2^64 (Goldilocks) | Must be >> `\|L^(0)\|`                       |
| Johnson `delta_max` | ~0.646            | `1 - sqrt(1/8)`                              |
| Rejection per query | ~0.646            | `1 - delta_max` for delta close to delta_max |
| `ell` for 128-bit   | ~294              | `ceil(128 / log2(1/0.646))`                  |

---

## 8. Fiat-Shamir Transcript Schedule

See `fiat-shamir-transcript.md`.

---

## 9. Ambiguity Register

See `ambiguity-register.md`.

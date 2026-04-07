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

**Field**: $\mathbb{F}_q$ — a finite field of size $q$. May be a prime field $\mathbb{F}_p$ or a binary extension field $\mathbb{F}_{2^n}$. The paper is generic over the field type (see Ambiguity A1). The field must satisfy $q \gg |L^{(0)}|$ for soundness (specifically, commit-phase error includes terms like $r / q$).

**Evaluation domains**: A sequence of nested domains:

- $L^{(0)}$ — the initial evaluation domain, a coset of a (multiplicative or additive) subgroup of $\mathbb{F}_q$, with $|L^{(0)}| = 2^k$
- $L^{(i+1)} = q^{(i)}(L^{(i)})$ — each domain is the image of the previous under the "subspace polynomial" $q^{(i)}$, with $|L^{(i)}| = 2^{k-i}$
- $L^{(r)}$ — the final domain, $|L^{(r)}| = 2^{k-r}$

**Subspace polynomial** (two-to-one map): For each round $i$, there is a 1-dimensional subspace $L^{(i)}_0 \subseteq L^{(i)}$ and the subspace polynomial:

$$q^{(i)}(X) = \prod_{\alpha \in L^{(i)}_0} (X - \alpha)$$

This is a degree-2 polynomial that maps $L^{(i)}$ onto $L^{(i+1)}$ with exactly 2 preimages per point. The kernel of $q^{(i)}$ is $L^{(i)}_0$.

**Reed-Solomon code**:

$$\mathsf{RS}[\mathbb{F}_q, L, \rho] = \{f: L \to \mathbb{F}_q \mid \exists \text{ poly } p, \deg(p) < \rho \cdot |L|, \text{ s.t. } f = p|_L\}$$

where $\rho$ is the rate.

**Rate**: $\rho = 2^{-\mathcal{R}}$ for a positive integer $\mathcal{R}$.

**Number of rounds**: $r = k - \mathcal{R}$ (where $k = \log_2(|L^{(0)}|)$). After $r$ rounds of folding, the domain has size $2^{\mathcal{R}} = 1/\rho$, and the degree bound matches the domain size.

**RS code tower**: $\mathsf{RS}^{(i)} = \mathsf{RS}[\mathbb{F}_q, L^{(i)}, \rho \cdot |L^{(i)}|]$. The rate $\rho$ is constant across rounds, but the degree bound $\rho \cdot |L^{(i)}|$ halves each round since $|L^{(i)}|$ halves.

**Repetition parameter**: $\ell$ — the number of independent query repetitions. Each repetition reduces soundness error multiplicatively.

**Coset structure**: $\mathcal{S}^{(i)}$ = the set of cosets of $L^{(i)}_0$ within $L^{(i)}$. Since $\dim(L^{(i)}_0) = 1$, each coset has 2 elements, and there are $|L^{(i)}|/2 = |L^{(i+1)}|$ cosets.

---

## 1. Primitive Interfaces

| Primitive | Interface | Notes |
|-----------|-----------|-------|
| Field arithmetic | $\text{add}(a,b)$, $\text{mul}(a,b)$, $\text{inv}(a)$, $\text{sub}(a,b)$, $\text{neg}(a)$, $\text{random}()$ | Over $\mathbb{F}_q$ |
| Degree-1 interpolation | $\text{interpolate\_2}(x_0, y_0, x_1, y_1) \to (a_0, a_1)$ where $P(x) = a_0 + a_1 x$ | Used in FRI fold: $P(x_0) = y_0$, $P(x_1) = y_1$ |
| Degree-1 evaluation | $\text{eval\_linear}(a_0, a_1, x) \to a_0 + a_1 x$ | Evaluate the interpolated polynomial |
| Merkle tree | $\text{commit}(\text{leaves}) \to \text{root}$, $\text{open}(\text{idx}) \to (\text{leaf}, \text{path})$, $\text{verify}(\text{root}, \text{idx}, \text{leaf}, \text{path}) \to \text{bool}$ | For oracle commitments |
| Cryptographic hash | $H : \text{bytes} \to \text{bytes}$ | For Merkle tree and Fiat-Shamir |
| Transcript (sponge) | $\text{new}() \to T$, $T.\text{absorb}(\text{data})$, $T.\text{squeeze}() \to \mathbb{F}_q$ | Fiat-Shamir transform |
| Domain construction | Given $k$, construct $L^{(0)}$ and the two-to-one maps $q^{(i)}$ | Field-dependent (see A1) |

---

## 2. Algebraic Hash Function $H_x$ (FRI Fold)

> Paper reference: Section A.2 (line 2161)

This is the building block used in both FRI and DEEP-FRI. Implementations typically call this the "FRI fold" or "degree-respecting projection (DRP)".

### Algorithm

Given a seed $x \in \mathbb{F}_q$ and a function $f: L^{(i)} \to \mathbb{F}_q$:

$$H_x[f]: L^{(i+1)} \to \mathbb{F}_q$$

For each $s \in L^{(i+1)}$:
1. Find the two preimages: $\{s_0, s_1\} = (q^{(i)})^{-1}(s)$, i.e., $q^{(i)}(s_0) = q^{(i)}(s_1) = s$ with $s_0 \neq s_1$
2. Query $f(s_0)$ and $f(s_1)$
3. Interpolate: let $P(X)$ be the unique degree-1 polynomial with $P(s_0) = f(s_0)$ and $P(s_1) = f(s_1)$
4. Return $H_x[f](s) = P(x)$

### Explicit formula

$$P(X) = f(s_0) \cdot \frac{X - s_1}{s_0 - s_1} + f(s_1) \cdot \frac{X - s_0}{s_1 - s_0}$$

$$H_x[f](s) = P(x) = f(s_0) \cdot \frac{x - s_1}{s_0 - s_1} + f(s_1) \cdot \frac{x - s_0}{s_1 - s_0}$$

### Properties

- **Locality**: Computing $H_x[f](s)$ requires exactly 2 queries to $f$
- **Completeness**: If $f \in \mathsf{RS}^{(i)}$, then $H_x[f] \in \mathsf{RS}^{(i+1)}$ for all $x$
- **Degree**: If $\deg(f) < d$, then $\deg(H_x[f]) < d/2$

---

## 3. Protocol: FRI (Base Protocol)

> Paper reference: Section 4.1 (line 1124)

FRI is an Interactive Oracle Proof of Proximity (IOPP) for Reed-Solomon codes. It tests whether $f^{(0)}: L^{(0)} \to \mathbb{F}_q$ is close to $\mathsf{RS}^{(0)}$.

### 3.1 COMMIT Phase

**Input**: $f^{(0)}: L^{(0)} \to \mathbb{F}_q$

For $i = 0$ to $r-1$:
- **Verifier**: squeeze challenge $x^{(i)} \in \mathbb{F}_q$ from transcript
- **Prover**: compute $f^{(i+1)}: L^{(i+1)} \to \mathbb{F}_q$ where $f^{(i+1)}(s) = H_{x^{(i)}}[f^{(i)}](s)$ for each $s \in L^{(i+1)}$
- **Prover**: commit $\text{Merkle}(f^{(i+1)})$ and send root to verifier
- **Transcript**: absorb Merkle root of $f^{(i+1)}$

**Prover**: send $C \in \mathbb{F}_q$ (claimed value of the constant polynomial $f^{(r)}$). **Transcript**: absorb $C$.

### 3.2 QUERY Phase

Repeat $\ell$ times:
- **Verifier**: squeeze $s^{(0)}$ uniformly from $L^{(0)}$
- For $i = 0$ to $r-1$:
  1. Compute $s^{(i+1)} = q^{(i)}(s^{(i)})$
  2. Query $f^{(i)}$ at the two preimages $\{s_0, s_1\}$ of $s^{(i+1)}$
  3. Compute $\text{expected} = H_{x^{(i)}}[f^{(i)}](s^{(i+1)})$ by interpolating through $(s_0, f^{(i)}(s_0))$, $(s_1, f^{(i)}(s_1))$ and evaluating at $x^{(i)}$
  4. Query $\text{actual} = f^{(i+1)}(s^{(i+1)})$
  5. If $\text{expected} \neq \text{actual}$: **REJECT**
- If $f^{(r)}(s^{(r)}) \neq C$: **REJECT**

**ACCEPT**.

### 3.3 Verification Equation

At each round $i$, the verifier checks:

$$H_{x^{(i)}}[f^{(i)}](s^{(i+1)}) \stackrel{?}{=} f^{(i+1)}(s^{(i+1)})$$

where the left side is computed from 2 queries to $f^{(i)}$, and the right side is queried from $f^{(i+1)}$.

---

## 4. QUOTIENT Operation

> Paper reference: Section 4.2.1 (line 1339)

### Definition

$$\mathsf{QUOTIENT}(f, z, b): L \to \mathbb{F}_q$$

**Input**: $f: L \to \mathbb{F}_q$, a point $z \in \mathbb{F}_q \setminus L$ (**CRITICAL**: $z$ must not be in $L$), a value $b \in \mathbb{F}_q$.

**Output**: $g: L \to \mathbb{F}_q$ where

$$g(y) = \frac{f(y) - b}{y - z}$$

### Key Property (Lemma 4.7)

Let $z \notin L$, $d \geq 1$, $f: L \to \mathbb{F}_q$, $b \in \mathbb{F}_q$, and $g = \mathsf{QUOTIENT}(f, z, b)$. Then:

> There exists a polynomial $Q(X)$ of degree $\leq d-1$ with $\Delta(g, Q) < \delta$
> **if and only if**
> there exists a polynomial $R(X)$ of degree $\leq d$ with $\Delta(f, R) < \delta$ and $R(z) = b$.

**Degree effect**: Quotienting reduces the degree bound by 1.

---

## 5. Protocol: DEEP-FRI

> Paper reference: Protocol 4.6 (line 1391)

DEEP-FRI modifies FRI by adding an out-of-domain (OOD) sampling step before each fold. This improves soundness from the "double Johnson" bound to the Johnson bound (provably) or beyond (conjecturally).

### 5.1 COMMIT Phase

**Input**: $f^{(0)}: L^{(0)} \to \mathbb{F}_q$, supposed to be of degree $< d^{(0)}$

For $i = 0$ to $r-1$:

- **Verifier**: squeeze $z^{(i)} \in \mathbb{F}_q$ from transcript (out-of-domain sample point; $z^{(i)}$ must NOT be in $L^{(i)}$)

- **Prover**: send $B^{(i)}_{z^{(i)}}(X)$ — a degree-1 polynomial in $\mathbb{F}_q[X]$ (two coefficients: $b_0, b_1$ such that $B(X) = b_0 + b_1 X$). Semantically, $B^{(i)}_{z^{(i)}}(x)$ should equal $H_x[f^{(i)}](z^{(i)})$.
- **Transcript**: absorb $b_0, b_1$

- **Verifier**: squeeze $x^{(i)} \in \mathbb{F}_q$ from transcript (folding challenge)

- **Prover**: compute $f^{(i+1)}: L^{(i+1)} \to \mathbb{F}_q$ where for each $y \in L^{(i+1)}$:

$$f^{(i+1)}(y) = \frac{H_{x^{(i)}}[f^{(i)}](y) - B^{(i)}_{z^{(i)}}(x^{(i)})}{y - z^{(i)}}$$

  (This is the $\mathsf{QUOTIENT}$ of the folded function.)

- **Prover**: commit $\text{Merkle}(f^{(i+1)})$ and send root
- **Transcript**: absorb Merkle root of $f^{(i+1)}$

**Prover**: send $C \in \mathbb{F}_q$ (final constant). **Transcript**: absorb $C$.

### 5.2 QUERY Phase

Repeat $\ell$ times:
- **Verifier**: squeeze $s^{(0)}$ uniformly from $L^{(0)}$
- For $i = 0$ to $r-1$:
  1. Compute $s^{(i+1)} = q^{(i)}(s^{(i)})$
  2. Compute $H_{x^{(i)}}[f^{(i)}](s^{(i+1)})$: find preimages $\{s_0, s_1\}$ of $s^{(i+1)}$ under $q^{(i)}$, query $f^{(i)}(s_0)$ and $f^{(i)}(s_1)$, interpolate and evaluate at $x^{(i)}$ to get $\text{lhs}$
  3. Query $f^{(i+1)}(s^{(i+1)})$ to get $\text{rhs}_f$
  4. Compute $\text{rhs} = \text{rhs}_f \cdot (s^{(i+1)} - z^{(i)}) + B^{(i)}_{z^{(i)}}(x^{(i)})$
  5. If $\text{lhs} \neq \text{rhs}$: **REJECT**
- If $f^{(r)}(s^{(r)}) \neq C$: **REJECT**

**ACCEPT**.

### 5.3 Verification Equation

At each round $i$, the verifier checks:

$$H_{x^{(i)}}[f^{(i)}](s^{(i+1)}) \stackrel{?}{=} f^{(i+1)}(s^{(i+1)}) \cdot (s^{(i+1)} - z^{(i)}) + B^{(i)}_{z^{(i)}}(x^{(i)})$$

**Derivation**: From the prover's construction:

$$f^{(i+1)}(y) = \frac{H_{x^{(i)}}[f^{(i)}](y) - B^{(i)}_{z^{(i)}}(x^{(i)})}{y - z^{(i)}}$$

Rearranging:

$$H_{x^{(i)}}[f^{(i)}](y) = f^{(i+1)}(y) \cdot (y - z^{(i)}) + B^{(i)}_{z^{(i)}}(x^{(i)})$$

Substituting $y = s^{(i+1)}$ gives the verification equation.

**Left side** (computed from 2 queries to $f^{(i)}$):
Query $f^{(i)}$ at the two preimages of $s^{(i+1)}$ under $q^{(i)}$, interpolate degree-1 polynomial, evaluate at $x^{(i)}$.

**Right side** (computed from 1 query to $f^{(i+1)}$ + known values):
Query $f^{(i+1)}(s^{(i+1)})$, multiply by $(s^{(i+1)} - z^{(i)})$, add $B^{(i)}_{z^{(i)}}(x^{(i)})$.

### 5.4 Degree Tracking

| Round | Operation | Degree bound |
|-------|-----------|-------------|
| 0 | Input $f^{(0)}$ | $< d^{(0)}$ |
| 0 | After $H_x$ fold | $< d^{(0)} / 2$ |
| 0 | After QUOTIENT | $< d^{(0)}/2 - 1$ |
| $i$ | Input $f^{(i)}$ | $< d^{(i)}$ |
| $i$ | After fold + quotient | $< d^{(i)}/2 - 1 = d^{(i+1)}$ |

General: $d^{(i+1)} = d^{(i)}/2 - 1$

---

## 6. Protocol: DEEP-ALI (Overview)

> Paper reference: Protocol 5.5 (line 1871), Section 5

DEEP-ALI is an IOP for the Algebraic Placement and Routing (APR) relation. It uses DEEP-FRI as a sub-protocol.

### 6.1 APR Relation (Definition 5.2)

**Instance** $\mathbf{x} = (\mathbb{F}_q, d, \mathcal{C})$:
- $\mathbb{F}_q$: finite field
- $d$: degree bound on witness
- $\mathcal{C}$: set of constraint tuples $(M^i, P^i, Q^i)$ where $M^i$ is a mask (field element sequence), $P^i$ is a condition polynomial, $Q^i$ is a domain polynomial

**Witness** $\mathbf{w}$: a polynomial $\tilde{f} \in \mathbb{F}_q[X]$ of degree $< d$ satisfying all constraints: for each $(M, P, Q)$ and every $x$ where $Q(x) = 0$:

$$P(\tilde{f}(x \cdot M_1), \ldots, \tilde{f}(x \cdot M_{|M|})) = 0$$

### 6.2 Protocol Flow (sketch)

1. Prover commits to witness oracle $f: D \to \mathbb{F}_q$
2. Prover constructs composition polynomial $g_\alpha: D' \to \mathbb{F}_q$ from random linear combination of constraints
3. Verifier samples OOD point $z \in \mathbb{F}_q$
4. Prover sends evaluations $\{\tilde{f}(z \cdot M_j)\}$ for all mask points
5. Verifier constructs quotient polynomials $h^1, h^2$ using $\mathsf{QUOTIENT}$
6. Both $h^1$ and $h^2$ are tested via DEEP-FRI

> Full round-by-round DEEP-ALI decomposition requires the complete Protocol 5.5 (paper lines 1871-1910). Use `--mode full` to extract it.

---

## 7. Soundness Bounds

### FRI Soundness (Theorem 3.3, BKS18)

For $f^{(0)}$ that is $\delta^{(0)}$-far from $\mathsf{RS}^{(0)}$, with $n = |L^{(0)}|$:

- **Commit-phase error**: $\leq \frac{2 \log n}{\epsilon^3 \cdot |\mathbb{F}|}$
- **Query-phase error** (per repetition): $\leq \left(1 - \min\left(\delta^{(0)},\, 1 - \rho^{1/4} - \epsilon'\right) + \epsilon \log n\right)^\ell$

### DEEP-FRI Soundness (Theorem 4.8)

- **Commit-phase error**: $\leq r \cdot \nu^*$
- **Query-phase error** (per repetition): $\leq (1 - \delta^* + r \cdot \epsilon)^\ell$

where $\delta^* = \min(\delta^{(0)}, \delta_{\max})$.

### Concrete Instantiations

**Using Johnson bound** (Example 4.10, proven):

$$\delta_{\max} = 1 - \sqrt{\rho} - o(1)$$

**Under list-decoding conjecture** (Conjecture 3.2):

$$\delta_{\max} = 1 - \rho - o(1)$$

### Parameter Guidance

For 128-bit security with $\rho = 1/8$:

| Parameter | Value | Derivation |
|-----------|-------|------------|
| $\rho$ | $1/8$ | Chosen |
| $\mathcal{R}$ | $3$ | $\rho = 2^{-3}$ |
| $\|L^{(0)}\|$ | $2^{20}$ | Example: 1M constraint system |
| $k$ | $20$ | $\log_2(\|L^{(0)}\|)$ |
| $r$ | $17$ | $k - \mathcal{R} = 20 - 3$ |
| $\|\mathbb{F}\|$ | $2^{64}$ (Goldilocks) | Must be $\gg \|L^{(0)}\|$ |
| Johnson $\delta_{\max}$ | $\approx 0.646$ | $1 - \sqrt{1/8}$ |
| Rejection per query | $\approx 0.354$ | $1 - \delta_{\max}$ |
| $\ell$ for 128-bit | $\approx 124$ | $\lceil 128 / \log_2(1/0.354) \rceil$ |

---

## 8. Fiat-Shamir Transcript Schedule

See `fiat-shamir-transcript.md`.

---

## 9. Ambiguity Register

See `ambiguity-register.md`.

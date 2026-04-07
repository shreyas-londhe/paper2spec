---
paper: "Algebraic Methods for Interactive Proof Systems"
authors: ["Carsten Lund", "Lance Fortnow", "Howard Karloff", "Noam Nisan"]
year: 1992
protocols: ["Sumcheck"]
spec_version: "1.0"
generated_by: "paper2spec"
---

# Sumcheck Protocol — Specification

> This spec is designed for LLM agents implementing the protocol.
> Every symbol is defined, every round is explicit, every check is spelled out.

---

## 0. Algebraic Setting

**Field**: $\mathbb{F}$ — a finite field of size $|\mathbb{F}| = q$. The field must be large enough for soundness: $q > \mu \cdot \ell$ where $\mu$ is the number of variables and $\ell$ is the individual degree (see Section 5).

**Polynomial**: $G : \mathbb{F}^\mu \to \mathbb{F}$ — a $\mu$-variate polynomial over $\mathbb{F}$. The degree of $G$ in each variable is at most $\ell$.

**Claim**: The prover claims that

$$T = \sum_{x_1 \in \{0,1\}} \sum_{x_2 \in \{0,1\}} \cdots \sum_{x_\mu \in \{0,1\}} G(x_1, x_2, \ldots, x_\mu)$$

i.e., the sum of $G$ over the Boolean hypercube $\{0,1\}^\mu$ equals $T$.

**Parameters**:

- $\mu$ — number of variables (determines number of rounds)
- $\ell$ — maximum degree of $G$ in each variable
- $T \in \mathbb{F}$ — the claimed sum
- $q = |\mathbb{F}|$ — field size

---

## 1. Primitive Interfaces

| Primitive             | Interface                                                                                   | Notes                                                          |
| --------------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------- |
| Field arithmetic      | $\text{add}(a,b)$, $\text{mul}(a,b)$, $\text{sub}(a,b)$, $\text{inv}(a)$, $\text{random}()$ | Over $\mathbb{F}$                                              |
| Polynomial evaluation | $\text{eval}(G, \mathbf{x}) \to \mathbb{F}$                                                 | Evaluate $G$ at point $\mathbf{x} \in \mathbb{F}^\mu$          |
| Univariate sum        | $\sum_{t=0}^{\ell} g(t)$                                                                    | Sum a degree-$\ell$ univariate polynomial over $\ell+1$ points |
| Transcript (sponge)   | $\text{absorb}(\text{data})$, $\text{squeeze}() \to \mathbb{F}$                             | For Fiat-Shamir                                                |

---

## 2. Protocol: Sumcheck

The protocol has $\mu$ rounds. In each round, the prover sends a univariate polynomial and the verifier responds with a random challenge. After all rounds, the verifier makes one query to $G$.

### 2.1 Protocol Flow

**Input to both parties**: $G$, $\mu$, $\ell$, $T$

**Round 1:**

- **Prover** computes and sends the univariate polynomial:

$$g_1(X_1) = \sum_{x_2 \in \{0,1\}} \sum_{x_3 \in \{0,1\}} \cdots \sum_{x_\mu \in \{0,1\}} G(X_1, x_2, x_3, \ldots, x_\mu)$$

This is a polynomial of degree $\leq \ell$ in $X_1$. The prover sends it as $\ell + 1$ evaluations: $g_1(0), g_1(1), \ldots, g_1(\ell)$.

- **Verifier** checks:

$$g_1(0) + g_1(1) \stackrel{?}{=} T$$

If not equal: **REJECT**.

- **Verifier** samples random $r_1 \stackrel{\$}{\leftarrow} \mathbb{F}$ and sends to prover.

- Set $e_1 \leftarrow g_1(r_1)$.

---

**Round $i$ (for $i = 2, 3, \ldots, \mu$):**

- **Prover** computes and sends the univariate polynomial:

$$g_i(X_i) = \sum_{x_{i+1} \in \{0,1\}} \cdots \sum_{x_\mu \in \{0,1\}} G(r_1, r_2, \ldots, r_{i-1}, X_i, x_{i+1}, \ldots, x_\mu)$$

This is a polynomial of degree $\leq \ell$ in $X_i$, with all previous variables fixed to challenges $r_1, \ldots, r_{i-1}$. Sent as $\ell + 1$ evaluations: $g_i(0), g_i(1), \ldots, g_i(\ell)$.

- **Verifier** checks:

$$g_i(0) + g_i(1) \stackrel{?}{=} e_{i-1}$$

If not equal: **REJECT**.

- **Verifier** samples random $r_i \stackrel{\$}{\leftarrow} \mathbb{F}$ and sends to prover.

- Set $e_i \leftarrow g_i(r_i)$.

---

**Final check (after round $\mu$):**

- **Verifier** evaluates $G$ at the random point $(r_1, r_2, \ldots, r_\mu)$ and checks:

$$G(r_1, r_2, \ldots, r_\mu) \stackrel{?}{=} e_\mu$$

If not equal: **REJECT**. Otherwise: **ACCEPT**.

---

### 2.2 Verification Equations

There are $\mu + 1$ checks total:

| Check                           | Equation                        | When                  |
| ------------------------------- | ------------------------------- | --------------------- |
| Round 1                         | $g_1(0) + g_1(1) = T$           | After receiving $g_1$ |
| Round $i$ ($2 \leq i \leq \mu$) | $g_i(0) + g_i(1) = e_{i-1}$     | After receiving $g_i$ |
| Final                           | $G(r_1, \ldots, r_\mu) = e_\mu$ | After all rounds      |

**Why each check is sound:**

- **Round checks** ($g_i(0) + g_i(1) = e_{i-1}$): If $g_i$ is the honest polynomial, then summing over $X_i \in \{0,1\}$ collapses one summation, producing $e_{i-1}$. A cheating prover must send a _different_ degree-$\ell$ polynomial $g_i^* \neq g_i$ that still satisfies this equation. Since $g_i^* - g_i$ is a nonzero polynomial of degree $\leq \ell$, it agrees with $g_i$ at $r_i$ with probability $\leq \ell / q$ (Schwartz-Zippel).

- **Final check** ($G(r_1, \ldots, r_\mu) = e_\mu$): This anchors the protocol to the actual polynomial $G$. The verifier evaluates $G$ directly — no prover involvement.

### 2.3 Derivation of the Round Check

The key identity that makes the protocol work:

$$\underbrace{\sum_{x_i \in \{0,1\}} \cdots \sum_{x_\mu \in \{0,1\}} G(r_1, \ldots, r_{i-1}, x_i, \ldots, x_\mu)}_{= e_{i-1} \text{ (from previous round)}}$$

Split the outer sum over $x_i$:

$$= \underbrace{\sum_{x_{i+1} \in \{0,1\}} \cdots \sum_{x_\mu \in \{0,1\}} G(r_1, \ldots, r_{i-1}, 0, x_{i+1}, \ldots, x_\mu)}_{= g_i(0)} + \underbrace{\sum_{x_{i+1} \in \{0,1\}} \cdots \sum_{x_\mu \in \{0,1\}} G(r_1, \ldots, r_{i-1}, 1, x_{i+1}, \ldots, x_\mu)}_{= g_i(1)}$$

Therefore: $g_i(0) + g_i(1) = e_{i-1}$. This is what the verifier checks.

---

## 3. Prover Complexity

The honest prover must compute $g_i$ for each round $i$. Naively this costs $O(2^{\mu - i})$ evaluations of $G$ per evaluation point of $g_i$, and $g_i$ needs $\ell + 1$ evaluation points, giving total prover work:

$$\sum_{i=1}^{\mu} (\ell + 1) \cdot 2^{\mu - i} = (\ell + 1) \cdot (2^\mu - 1) \approx (\ell + 1) \cdot 2^\mu$$

For the common case $\ell = 1$ (multilinear polynomials), the prover can be optimized to $O(2^\mu)$ total field operations using the "bookkeeping table" technique.

---

## 4. Verifier Complexity

- **Communication**: $\mu \cdot (\ell + 1)$ field elements (one degree-$\ell$ polynomial per round)
- **Computation**: $\mu$ round checks (each costs $O(\ell)$) + one evaluation of $G$ at a random point
- **Rounds**: $\mu$ (one per variable)
- **Randomness**: $\mu$ random field elements

The verifier's bottleneck is the final evaluation $G(r_1, \ldots, r_\mu)$. If $G$ is given explicitly, this is $O(\text{size}(G))$. In practice, $G$ is structured (e.g., a multilinear extension) and the verifier delegates this evaluation to another protocol.

---

## 5. Soundness

**Completeness**: If $T = \sum_{\mathbf{x} \in \{0,1\}^\mu} G(\mathbf{x})$ and the prover is honest, the verifier always accepts.

**Soundness**: If $T \neq \sum_{\mathbf{x} \in \{0,1\}^\mu} G(\mathbf{x})$, then for any cheating prover $P^*$:

$$\Pr[\text{Verifier accepts}] \leq \frac{\mu \cdot \ell}{|\mathbb{F}|}$$

This follows from the union bound over $\mu$ rounds, each contributing at most $\ell / |\mathbb{F}|$ error from Schwartz-Zippel.

**Parameter guidance:**

| Security level | Field size $q$   | Variables $\mu$ | Degree $\ell$ | Soundness error                 |
| -------------- | ---------------- | --------------- | ------------- | ------------------------------- |
| 128-bit        | $q \geq 2^{64}$  | 20              | 1             | $20 / 2^{64} \approx 2^{-60}$   |
| 128-bit        | $q \geq 2^{128}$ | 20              | 3             | $60 / 2^{128} \approx 2^{-122}$ |

For 128-bit security with $\ell = 1$ (multilinear), use $|\mathbb{F}| \geq 2^{128}$ or repeat the protocol.

---

## 6. Fiat-Shamir Transcript Schedule

To make the protocol non-interactive, apply the Fiat-Shamir transform:

| Step | Direction | Data               | Operation | Notes                 |
| ---- | --------- | ------------------ | --------- | --------------------- |
| 0    | —         | domain separator   | ABSORB    | e.g., `"sumcheck-v1"` |
| 1    | —         | $T$, $\mu$, $\ell$ | ABSORB    | Public parameters     |

Then for each round $i = 1, \ldots, \mu$:

| Step   | Direction | Data                                | Operation | Notes                     |
| ------ | --------- | ----------------------------------- | --------- | ------------------------- |
| $2i$   | $P \to V$ | $g_i(0), g_i(1), \ldots, g_i(\ell)$ | ABSORB    | $\ell + 1$ field elements |
| $2i+1$ | $V \to P$ | $r_i$                               | SQUEEZE   | Random challenge          |

**Ordering invariant**: $g_i$ is absorbed BEFORE $r_i$ is squeezed. This ensures the prover commits to $g_i$ before seeing $r_i$.

---

## 7. Ambiguity Register

| ID  | Issue                      | Status        | Choices                                                                                        | Impact      | Recommended                                                                                             |
| --- | -------------------------- | ------------- | ---------------------------------------------------------------------------------------------- | ----------- | ------------------------------------------------------------------------------------------------------- |
| A1  | Field choice               | PARAMETERIZED | Any field with $q > \mu \cdot \ell$                                                            | Structural  | Use the field of the outer protocol (sumcheck is usually a sub-protocol)                                |
| A2  | Polynomial representation  | UNSPECIFIED   | Send $g_i$ as evaluations $g_i(0), \ldots, g_i(\ell)$ vs. coefficients $[a_0, \ldots, a_\ell]$ | Interop     | Evaluations at $0, 1, \ldots, \ell$ — more natural for the round check                                  |
| A3  | Final evaluation oracle    | UNSPECIFIED   | Verifier evaluates $G$ directly / delegated to another protocol                                | Structural  | Depends on context: direct if $G$ is small, delegated (e.g., via polynomial commitment) if $G$ is large |
| A4  | Fiat-Shamir hash           | UNSPECIFIED   | SHA-256, Blake3, Poseidon, etc.                                                                | Security    | Match the outer protocol's choice                                                                       |
| A5  | Multilinear specialization | UNSPECIFIED   | General degree-$\ell$ / specialize to $\ell = 1$ (multilinear)                                 | Performance | Multilinear ($\ell = 1$) covers most practical uses and enables $O(2^\mu)$ prover                       |

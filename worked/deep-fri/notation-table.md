# Notation Table — DEEP-FRI

> Resolved from 121 LaTeX macros in the paper source.

## Core Symbols

| Symbol | LaTeX | Meaning | Paper Section |
|--------|-------|---------|---------------|
| `F_q` | `\F_q`, `\mathbb{F}_q` | Finite field of size q | Prelim |
| `L^(i)` | `L\ii` | Evaluation domain at round i | §4.1 |
| `L^(0)_0` | `L_0\zr` | 1-dimensional subspace of L^(0) | §A.2 |
| `RS^(i)` | `\RS\ii` | Reed-Solomon code at round i: RS[F_q, L^(i), rho*\|L^(i)\|] | §4.1 |
| `rho` | `\Rate`, `\rho` | Code rate = 2^{-R} | §4.1 |
| `R` | `\RateInt`, `\cal{R}` | Rate exponent: rho = 2^{-R} | §4.1 |
| `r` | `\rounds`, `\RecInt` | Number of FRI rounds = k - R | §4.1 |
| `k` | — | log2(\|L^(0)\|), dimension of initial domain | §4.1 |
| `ell` | `\RepInt`, `\ell` | Number of query repetitions | §4.1 |
| `f^(i)` | `f\ii` | Oracle function at round i | §4.1 |
| `x^(i)` | `x\ii` | Folding challenge at round i | §4.1 |
| `z^(i)` | `z\ii` | Out-of-domain sample point at round i (DEEP-FRI only) | §4.3 |
| `B^(i)` | `B\ii` | Degree-1 polynomial sent by prover (DEEP-FRI only) | §4.3 |
| `q^(i)` | `q\ii` | Subspace polynomial: two-to-one map L^(i) -> L^(i+1) | §A.2 |
| `H_x[f]` | `H_x[f]` | Algebraic hash / FRI fold of f with seed x | §A.2 |
| `S^(i)` | `\cosets\ii` | Set of cosets of L^(i)_0 in L^(i) | §A.2 |
| `C` | `C` | Final constant value (f^(r) should be constant C) | §4.1 |
| `QUOTIENT` | `\QUOTIENT` | Quotient operation: (f(y)-b)/(y-z) | §4.2.1 |
| `Delta` | `\Delta` | Relative Hamming distance | Prelim |
| `d^(i)` | `d\ii` | Degree bound at round i | §4.1 |

## DEEP-ALI Symbols

| Symbol | LaTeX | Meaning | Paper Section |
|--------|-------|---------|---------------|
| `R_APR` | `\RAPR` | APR relation | Def 5.2 |
| `x` (instance) | `\xx`, `\mathbbmss{x}` | APR instance tuple (F_q, d, C) | Def 5.2 |
| `w` (witness) | `\ww`, `\mathbbmss{w}` | APR witness polynomial f_tilde | Def 5.2 |
| `d_C` | `\maxdeg` | Max total degree of constraint polynomials | Def 5.2 |
| `Q_lcm` | `\Qlcm` | LCM of domain polynomials | Def 5.2 |
| `RPT` | `\RPT` | Reed-Solomon Proximity Testing (= FRI or DEEP-FRI) | §5 |

## Implementation Naming

| Paper Notation | Common Implementation Name | Notes |
|---------------|---------------------------|-------|
| Algebraic hash H_x | FRI fold / DRP | "Degree-Respecting Projection" in winterfell |
| Subspace polynomial q^(i) | Two-to-one map / folding map | |
| Repetition parameter ell | `num_queries` | |
| Rate rho | `1 / blowup_factor` | plonky2 uses `rate_bits` = R |
| Rounds r | `num_fri_layers` | |
| COMMIT phase | `fri_commit` / `build_layers` | |
| QUERY phase | `fri_verify` / `verify_queries` | |
| L^(0) | `lde_domain` / `evaluation_domain` | Usually domain with blowup |

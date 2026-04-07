# Guardrail: Notation Fidelity

## 1. No Unexpanded Macros

**Rule**: The output spec MUST NOT contain any unexpanded LaTeX macros from the paper.

**Why**: LLM coding agents reading the spec don't have the paper's preamble. If `\DFRI` appears unexpanded, the agent has no idea what it means.

**Process**: After assembling the spec, search for `\` followed by uppercase letters. Any match that isn't standard LaTeX (`\mathbb`, `\mathsf`, `\operatorname`, etc.) is a missed expansion.

## 2. Consistent Notation Throughout

**Rule**: Pick ONE notation for each concept and use it consistently.

**Common conflicts**:
- Rate as `rho` vs `R` (where rho = 2^{-R})
- Degree as `d` vs `rho * |L|`
- Field as `F` vs `F_q` vs `F_p`
- Rounds as `r` vs `k` (when paper reuses symbols)

**Resolution**: Define the canonical notation in Section 0 (Algebraic Setting).
If the paper uses multiple names for the same thing, pick the most descriptive
one and note the alias.

## 3. Superscript/Subscript Clarity

**Rule**: Every superscript and subscript must have an unambiguous meaning.

**Common confusion**:
- `f^(i)` means "the oracle at round i", NOT "f raised to power i"
- `x^(i)` means "the challenge at round i", NOT "x to the i-th power"
- `d^(0)` means "degree bound at round 0", NOT "d to the 0"
- `B^(i)_{z^(i)}` has both a round superscript and a point subscript

**In the spec**: On first use of any superscripted variable, clarify:
"Here `f^(i)` denotes the oracle function at round `i` (not exponentiation)."

## 4. Rate vs Degree

**Rule**: The spec must clearly state whether it uses rate or degree parameterization.

- **Rate**: `RS[F, L, rho]` where `rho = d / |L|` is the ratio of degree to domain size
- **Degree**: `RS[F, L, d]` where `d` is the max degree of codeword polynomials

The two are equivalent: `d = rho * |L|`. But mixing them causes off-by-one bugs.
Pick one and stick with it. State the conversion formula once.

## 5. Paper Notation vs Implementation Notation

**Rule**: When the paper uses notation that differs from what implementations use,
provide a mapping.

**Common examples**:
- Paper: "algebraic hash H_x" -> Implementations: "FRI fold" or "DRP (degree-respecting projection)"
- Paper: "subspace polynomial q^(i)" -> Implementations: "folding map" or "two-to-one map"
- Paper: "repetition parameter ell" -> Implementations: "num_queries"
- Paper: "rate rho" -> Implementations: "blowup_factor = 1/rho"

# Stage 03: Protocol Decomposition (CORE STAGE)

## Purpose
The most critical stage. Decompose each protocol into explicit round-by-round
steps with prover actions, verifier actions, and verification equations.
This is what LLM agents consume to write implementations.

**Before starting**: Read `guardrails/crypto_correctness.md` and `guardrails/notation_fidelity.md`.

## Input
- `expanded.tex`
- `environments.json` (protocol environments)
- `algebraic_setting.md` from Stage 02
- `inventory.md` from Stage 01

## Output
- `protocols.md` — Sections 2-4+ of the spec (one section per protocol)

## Process

### Step 1: Order protocols by dependency

From the dependency graph, determine the decomposition order.
Base protocols first, extensions second.

Example for DEEP-FRI paper:
1. Algebraic hash H_x (building block)
2. FRI (base protocol)
3. DEEP-FRI (extends FRI with quotienting)
4. DEEP-ALI (uses DEEP-FRI as sub-protocol)

### Step 2: For each protocol, extract phases

Most IOP protocols have two phases:
- **COMMIT phase** (interactive): prover sends oracle commitments, verifier sends challenges
- **QUERY phase** (non-interactive after Fiat-Shamir): verifier queries oracles and checks

Some protocols have additional phases (e.g., preprocessing, online).
Identify all phases from the protocol environment.

### Step 3: Decompose COMMIT phase round-by-round

For each round i in the COMMIT phase, extract:

```
Round i:
  VERIFIER sends:
    - [challenge name] in [domain]          -- e.g., x^(i) in F_q
    - [how derived]                          -- e.g., squeezed from transcript
  
  PROVER computes:
    - [description of computation]           -- e.g., H_{x^(i)}[f^(i)]
    - [equation reference]                   -- e.g., §A.2, Eq. (7)
    - [input dependencies]                   -- e.g., requires f^(i), x^(i)
  
  PROVER sends:
    - [message name]: [type], [size]         -- e.g., f^(i+1): L^(i+1) -> F_q
    - [what it represents]                   -- e.g., folded polynomial evaluation
  
  TRANSCRIPT:
    - ABSORB [what]                          -- e.g., Merkle root of f^(i+1)
```

### Step 4: Decompose QUERY phase

For each query repetition, extract:

```
Query j (repeated ell times):
  VERIFIER samples:
    - [starting point]                       -- e.g., s^(0) in L^(0)
  
  For each round i:
    VERIFIER computes:
      - [derived values]                     -- e.g., s^(i+1) = q^(i)(s^(i))
    VERIFIER queries:
      - [oracle name] at [points]            -- e.g., f^(i) at {s_0, s_1}
    VERIFIER checks:
      - [VERIFICATION EQUATION]              -- THE CRITICAL OUTPUT
      - [equation in explicit form]
      - [what each term means]
```

### Step 5: State verification equations explicitly

This is the single most important output of this stage.

For each check the verifier performs, write:
1. The equation in mathematical notation
2. The equation with every variable spelled out
3. What the left side computes (and from which oracle queries)
4. What the right side computes (and from which prior values)
5. Why this check is sound (one sentence)

**Example for DEEP-FRI:**
```
VERIFICATION EQUATION (Round i):

  H_{x^(i)}[f^(i)](s^(i+1)) = f^(i+1)(s^(i+1)) * (s^(i+1) - z^(i)) + B^(i)_{z^(i)}(x^(i))

Left side:
  - Query f^(i) at the two preimages of s^(i+1) in L^(i)
  - Interpolate degree-1 polynomial P through those two values
  - Evaluate P(x^(i)) to get H_{x^(i)}[f^(i)](s^(i+1))

Right side:
  - Query f^(i+1)(s^(i+1)) from the committed oracle
  - Multiply by (s^(i+1) - z^(i))
  - Add B^(i)_{z^(i)}(x^(i)) where B^(i) was sent by prover in COMMIT

Why sound:
  This checks that f^(i+1) = QUOTIENT(H_x[f^(i)], z^(i), B^(i)_z(x^(i)))
  which means f^(i+1)(y) = (H_x[f^(i)](y) - B_z(x)) / (y - z)
```

### Step 6: Extract sub-protocol interfaces

When a protocol calls another protocol as a sub-routine (e.g., DEEP-ALI calls DEEP-FRI):
- State the exact interface: what inputs, what outputs
- How the parent protocol constructs the inputs
- How it uses the outputs

### Step 7: Handle building blocks

For algebraic operations used within protocols (hash functions, quotient operations):
- Provide a self-contained algorithmic description
- Include the degree analysis (input degree -> output degree)
- Note locality properties (how many queries needed)

## Quality Checks

After completing all protocol decompositions:
- [ ] Every round has explicit prover AND verifier actions
- [ ] Every oracle commitment is noted (for Fiat-Shamir in Stage 5)
- [ ] Every verification equation is written in explicit expanded form
- [ ] Degree bounds are tracked through every round
- [ ] Challenge domains are specified (in F_q, in L^(i), etc.)
- [ ] No step says "as before" or "similarly" — every round is explicit

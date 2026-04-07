# Fiat-Shamir Transcript Schedule — {{PAPER_TITLE}}

> This schedule specifies the exact order of absorb/squeeze operations
> for the Fiat-Shamir transform of the interactive protocol.

## Protocol: {{PROTOCOL_NAME}}

### Initialization
| Step | Direction | Data | Operation | Encoding | Notes |
|------|-----------|------|-----------|----------|-------|
| 0 | — | domain_separator | ABSORB | UTF-8 bytes | Protocol identifier |

### COMMIT Phase
| Step | Direction | Data | Operation | Encoding | Notes |
|------|-----------|------|-----------|----------|-------|
{{COMMIT_ROWS}}

### QUERY Phase
| Step | Direction | Data | Operation | Encoding | Notes |
|------|-----------|------|-----------|----------|-------|
{{QUERY_ROWS}}

## Ordering Invariants

1. Every ABSORB of a Merkle root happens BEFORE the next SQUEEZE
2. Prover messages are absorbed BEFORE the verifier's response is squeezed
3. {{PROTOCOL_SPECIFIC_INVARIANTS}}

## Encoding Notes

- Field elements: {{FIELD_ENCODING}} (e.g., little-endian 32 bytes for BN254 scalar)
- Merkle roots: {{ROOT_ENCODING}} (e.g., 32-byte hash digest)
- Polynomial coefficients: {{POLY_ENCODING}} (e.g., field elements in order [a_0, a_1])

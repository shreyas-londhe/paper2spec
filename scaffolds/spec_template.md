---
paper: "{{PAPER_TITLE}}"
arxiv: "{{ARXIV_ID}}"
eprint: "{{EPRINT_ID}}"
authors: [{{AUTHORS}}]
protocols: [{{PROTOCOL_NAMES}}]
spec_version: "1.0"
generated_by: "paper2spec"
---

# {{PAPER_TITLE}} — Protocol Specification

> This spec is designed for LLM agents implementing the protocol.
> Every symbol is defined, every round is explicit, every check is spelled out.

## 0. Algebraic Setting

{{ALGEBRAIC_SETTING}}

## 1. Primitive Interfaces

These primitives must be provided by the implementation. Do NOT re-implement them.

| Primitive | Interface | Notes |
|-----------|-----------|-------|
{{PRIMITIVES_TABLE}}

{{FOR_EACH_PROTOCOL}}
## {{N}}. Protocol: {{PROTOCOL_NAME}}

> Paper reference: {{PAPER_SECTION}}, lines {{LINE_START}}-{{LINE_END}}

### {{N}}.1 Overview

{{PROTOCOL_OVERVIEW}}

### {{N}}.2 COMMIT Phase

{{FOR_EACH_ROUND}}
**Round {{i}}:**

VERIFIER sends:
- {{CHALLENGE}}: squeezed from transcript

PROVER computes:
- {{COMPUTATION}}
- §{{SECTION}}, {{EQUATION_REF}}

PROVER sends:
- {{MESSAGE}}: {{TYPE}}, {{SIZE}}

TRANSCRIPT:
- ABSORB: {{WHAT}}
{{END_FOR_EACH_ROUND}}

### {{N}}.3 QUERY Phase

Repeat {{REPETITION_PARAM}} times:
{{QUERY_STEPS}}

### {{N}}.4 Verification Equations

{{FOR_EACH_CHECK}}
**Check {{j}} (Round {{i}}):**

```
{{EQUATION}}
```

Left side: {{LEFT_EXPLANATION}}
Right side: {{RIGHT_EXPLANATION}}
Why sound: {{SOUNDNESS_REASON}}
{{END_FOR_EACH_CHECK}}

{{END_FOR_EACH_PROTOCOL}}

## {{NEXT}}. Soundness Bounds

{{SOUNDNESS_SECTION}}

### Parameter Guidance

{{PARAMETER_TABLE}}

## {{NEXT+1}}. Fiat-Shamir Transcript Schedule

See `fiat-shamir-transcript.md` for the complete schedule.
<!-- For simple single-protocol specs, the transcript schedule may be inlined here instead. -->

## {{NEXT+2}}. Ambiguity Register

See `ambiguity-register.md` for all unspecified implementation choices.
<!-- For simple specs with few ambiguities, the register may be inlined here instead. -->

<!-- Section numbering: 0=Algebraic Setting, 1=Primitives, 2..N=Protocols, NEXT=Soundness, NEXT+1=Fiat-Shamir, NEXT+2=Ambiguity -->

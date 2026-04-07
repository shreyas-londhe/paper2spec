# Ambiguity Register — {{PAPER_TITLE}}

> Every implementation choice not fully specified by the paper.
> Resolve these before starting implementation.

## Classification

- **SPECIFIED**: paper gives exact value (no action needed)
- **PARAMETERIZED**: paper is generic, implementor chooses (e.g., field choice)
- **PARTIALLY_SPECIFIED**: paper gives constraints but not exact value
- **UNSPECIFIED**: paper is silent, implementor must decide

## Register

| ID | Category | Issue | Paper Ref | Status | Choices | Impact | Recommended |
|----|----------|-------|-----------|--------|---------|--------|-------------|
{{AMBIGUITY_ROWS}}

## Impact Levels

- **Structural**: changes algebraic structure (wrong choice = broken protocol)
- **Security**: affects soundness bound (wrong choice = weaker security)
- **Performance**: affects efficiency (wrong choice = slower, still correct)
- **Interop**: affects compatibility between implementations

## Resolution Notes

{{RESOLUTION_NOTES}}

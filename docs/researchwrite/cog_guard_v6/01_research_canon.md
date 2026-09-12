# Research canon

## Experimental facts

1. DeepSeek Travel diagnostic: 100 calls, 60 unique audited inputs and 40 repeats; 60/60 base fields correct, with two ontology mismatches.
2. Gemini 3 Flash diagnostic: 100 calls, 79 complete, 21 failed; among 60 unique inputs, 40 schema-valid outputs matched audited fields and 8 violated field types.
3. Existing main DARC diagnostics did not establish stable net task improvement over simple baselines.

## Constraints

- These are development diagnostics, not benchmark evidence.
- Gold/oracle constraints cannot enter model input.
- Failed, malformed, and fallback outputs remain in the denominator.

## Forbidden claims

- Do not claim COG-Guard is effective before Gate 1/2.
- Do not call schema repair alone semantic improvement.
- Do not silently map free text to an official category during scoring.

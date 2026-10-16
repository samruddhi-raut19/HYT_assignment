# Explanation-quality judge rubric

For each explanation, a human or LLM judge scores 0–2 on each dimension:

- **Evidence fidelity:** 2 = every positive claim is supported by an extracted resume span/skill; 1 = mostly supported; 0 = unsupported or invented.
- **Gap correctness:** 2 = missing must-have requirements are correctly named; 1 = partially correct; 0 = gaps are absent or wrong.
- **Decision rationale:** 2 = the advance/review decision follows the stated threshold and cost-sensitive policy; 1 = mostly clear; 0 = contradictory or unexplained.
- **Actionability:** 2 = a recruiter can verify the result quickly; 1 = some useful detail; 0 = vague.

Total score is 0–8. For calibration, two human raters should independently score at least 30 explanations; report exact agreement and mean absolute disagreement. The LLM judge must be compared against the human consensus before being used for the headline number.

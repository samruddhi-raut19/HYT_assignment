# Golden-set labeling guide

Review each row in `outputs/golden_eval.csv`.

- Label `1` only when the resume provides evidence for the job's explicit must-have requirements and is plausibly relevant to a Data Analyst or Business Analyst role.
- Label `0` when one or more explicit must-have requirements are missing, the evidence is too weak, or the candidate is clearly from an unrelated job family.
- Do not use name, gender cues, college name, age, or other protected/proxy characteristics.
- Keep hard cases: career changers, partial skill matches, vague job descriptions, and strong candidates with missing keywords.
- Record uncertain cases in a separate note rather than silently forcing an easy label.

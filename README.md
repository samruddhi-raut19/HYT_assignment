# HYT AI Screening Assistant

Author: Samruddhi Raut  
Repository: https://github.com/samruddhi-raut19/HYT_assignment

This repository contains a deterministic, local screening assistant for Data Analyst and Business Analyst jobs. It is designed to be reproducible in under 15 minutes and does not require an LLM API key.

## Run

```powershell
& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe" screening_pipeline.py
```

The default run reads the first 300 supplied postings as a documented subsample. Use `--max-jobs` to change it; the resume file is read in full.

Outputs are written to `outputs/`: `golden_eval.csv`, `metrics.json`, `sample_screening.json`, `fairness_check.json`, `golden_eval_review_template.csv`, and `explanation_judge_template.csv` after the second command.

## What it does

The pipeline extracts skills, years of experience, education, role cues, location, and must-have/nice-to-have requirements. It produces a 0-100 fit score, cites overlapping resume skills as evidence, lists missing must-have skills as gaps, and either advances or routes the candidate to human review. The policy is conservative because false rejection is more costly than an additional recruiter review.

## Evaluation

The harness reports precision, recall, accuracy, and a ranking metric, and compares the pipeline with keyword-overlap and TF-IDF baselines. The generated 200-row file is a **draft evaluation set**: labels are deterministic weak labels marked `weak_draft_needs_human_audit`. The assignment requests hand-labelled pairs; before submission, a reviewer should audit or relabel these rows using `golden_eval_review_template.csv`. This caveat is intentional and prevents overstating the result.

## Report coverage

See `report.md` for framing, baselines, fairness methodology, failure modes, the mandatory headline-number caveat, and next steps. See `decision_log.md` for non-obvious design decisions and `judge_rubric.md` for the explanation-quality rubric. After the main run, execute `python fairness_check.py` to generate `outputs/fairness_check.json`; its summary reports score and decision shifts, and `metrics.json` includes a threshold sweep.

## Privacy

The pipeline reads the supplied data in place and does not copy raw resumes into outputs. Do not publish raw resume PDFs or contact details.

## Submission checklist

- [ ] Complete `outputs/golden_eval_review_template.csv` with human-reviewed labels using the explicit must-have rule.
- [x] Run `screening_pipeline.py` and `fairness_check.py` one final time.
- [ ] Have two human raters complete the 30-row `outputs/explanation_judge_template.csv` and report agreement.
- [ ] Review `report.md`, `decision_log.md`, and `judge_rubric.md`.
- [ ] Add the resume PDF separately to the submission email; do not place it in the public repository unless desired.
- [ ] Submit the repository link and report before the deadline.

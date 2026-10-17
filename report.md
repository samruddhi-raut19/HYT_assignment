# HYT Screening Assistant Report

**Candidate:** Samruddhi Raut  
**Target roles:** Data Analyst and Business Analyst  
**Repository:** https://github.com/samruddhi-raut19/HYT_assignment

## Problem framing

For an HYT recruiter, “good” means a candidate is plausibly qualified for a Data Analyst or Business Analyst role, the recommendation is quick to verify, and missing requirements are visible. This system is a screening aid, not a hiring decision-maker. It does not infer personality, culture fit, protected traits, salary, or interview performance.

## Method

The deterministic extractor identifies technology skills, education cues, years of experience, role/category cues, and location. Job sentences are separated into must-have and nice-to-have requirements using explicit language. The score weights skills most heavily, then experience, education, location, and job-family cues. Scores below the advance threshold or with substantial must-have gaps go to a human recruiter.

## Baselines and results

On the saved 200-row draft-labelled run, the pipeline produced precision 0.231, recall 0.125, accuracy 0.845, and global NDCG 0.620. The keyword-overlap and TF-IDF cosine baselines have mean scores of 6.92 and 63.75. These are agreement measurements against weak labels, not recruiter-validated performance. A threshold sweep shows threshold 50 improves draft recall to 0.500 at precision 0.333, while the production threshold remains 62 until human labels support a change.

## Fairness check

The counterfactual test duplicates the same resume while changing only name, gender-coded language, and college name. On 40 generated variants, the current run produced a maximum absolute score delta of 0.0 and 0 decision shifts. This is a useful regression result, not proof of fairness: the test only covers the implemented cues and the extractor’s current vocabulary.

## Failure analysis

1. Synonyms and abbreviations can still be missed even after common aliases such as PowerBI, sklearn, Postgres, and MS Excel were normalized; inspect low-overlap rows in the review template.
2. Years-of-experience regexes can confuse a project date or graduation year with experience.
3. Job descriptions often mix mandatory and optional language in one sentence.
4. Location matching is weak for remote, hybrid, and relocation cases.
5. Category-based hard negatives can be misleading when candidates are changing careers.

These failures motivate human escalation and should be represented in the audited golden set.

## What is misleading about my headline number?

Any single headline score is misleading because the evaluation set has only 24 positive examples and may still contain subjective labels. Accuracy is especially misleading here because the majority class is “not relevant.” The honest headline is therefore: “A reproducible screening prototype with 0.845 accuracy and 0.620 NDCG on a 200-pair weak-labelled draft, but low recall that requires human-label validation and further tuning.”

## One more week

The engineering work is now in place: counterfactual score/decision summaries, common skill aliases, threshold analysis, and reviewer-ready templates. The remaining submission work is to hand-label the 200 pairs and have two human raters score the 30 explanation rows, then record agreement before using either result as a headline number.

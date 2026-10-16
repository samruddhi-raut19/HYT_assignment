# Decision log

1. **Job family:** Data Analyst and Business Analyst, operationalized as analyst/analytics/business-intelligence/reporting/insights titles and descriptions.
2. **Primary inputs:** The supplied `postings.csv` and `Resume.csv`; no external or synthetic evaluation data.
3. **Candidate representation:** Skills, years, education, category, role cues, and location are extracted deterministically.
4. **Skill vocabulary:** A compact, auditable technology vocabulary was used to keep the pipeline explainable.
5. **Must-have extraction:** Sentences containing required/must/minimum/qualifications are treated as must-have evidence.
6. **Nice-to-have extraction:** Preferred/plus/bonus/desired sentences are treated as nice-to-have evidence.
7. **Score weights:** Skills 55%, experience 20%, education 10%, location 5%, role/category 10%.
8. **Decision policy:** Advance at score >=62 with no more than half of must-have skills missing; otherwise human review.
9. **Error asymmetry:** Human review is the fallback because a false rejection is costlier than an extra recruiter read.
10. **Baselines:** Keyword overlap is intentionally trivial; TF-IDF cosine is the simple lexical baseline.
11. **Evaluation set:** A deterministic 200-row draft is generated from in-domain and hard-negative resumes.
12. **Label caveat:** Draft labels are weak labels and are explicitly marked for human audit; they are not presented as hand labels. The intended final rule is that a candidate is relevant only when the resume satisfies the job's explicit must-have requirements.
13. **Fairness test:** Counterfactual edits remove name/gender/college cues while holding the rest of the resume constant.
14. **Privacy:** Raw resume files are not copied into outputs or committed by the pipeline.

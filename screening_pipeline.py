"""Local, reproducible screening pipeline for the HYT Graduate 2027 assignment.

The pipeline is deliberately deterministic and API-free so a reviewer can run it
in a clean environment. It extracts lightweight structure, scores a job/resume
pair, explains the score, and evaluates two baselines.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Dict, Iterable, List

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent
SKILLS = {
    "python", "java", "c++", "c#", "javascript", "typescript", "sql", "html", "css",
    "react", "angular", "node.js", "node", "django", "flask", "spring", "fastapi",
    "aws", "azure", "gcp", "docker", "kubernetes", "git", "linux", "mongodb",
    "postgresql", "mysql", "redis", "kafka", "spark", "tensorflow", "pytorch",
    "scikit-learn", "machine learning", "deep learning", "nlp", "rest", "api",
    "microservices", "agile", "scrum", "jira", "excel", "tableau", "power bi",
}
SKILL_ALIASES = {
    "ms excel": "excel", "microsoft excel": "excel", "spreadsheet": "excel",
    "powerbi": "power bi", "power-bi": "power bi", "tableau desktop": "tableau",
    "postgres": "postgresql", "postgre sql": "postgresql", "my sql": "mysql",
    "scikit learn": "scikit-learn", "sklearn": "scikit-learn", "ml": "machine learning",
    "artificial intelligence": "machine learning", "restful": "rest", "rest api": "rest",
    "amazon web services": "aws", "google cloud platform": "gcp",
    "continuous integration": "ci/cd", "continuous delivery": "ci/cd",
}
SKILLS |= set(SKILL_ALIASES)
EDU = ["b.tech", "btech", "b.e", "bachelor", "master", "m.tech", "mtech", "mba", "ph.d", "computer science", "information technology"]
TECH_TITLE = re.compile(r"\b(analyst|analytics|business intelligence|data scientist|data analyst|business analyst|reporting|insights|sql|tableau|power bi)\b", re.I)
ANALYST_CATEGORIES = {"BUSINESS-DEVELOPMENT", "FINANCE", "ACCOUNTANT", "INFORMATION-TECHNOLOGY", "CONSULTANT", "PUBLIC-RELATIONS"}

def tfidf_cosine(a: str, b: str) -> float:
    """Small dependency-free TF-IDF cosine for one document pair."""
    ta = re.findall(r"[a-z0-9+#.]+", a.lower()); tb = re.findall(r"[a-z0-9+#.]+", b.lower())
    vocab = set(ta) | set(tb)
    if not vocab: return 0.0
    va = np.array([ta.count(t) for t in vocab], dtype=float); vb = np.array([tb.count(t) for t in vocab], dtype=float)
    va = va / max(1, len(ta)); vb = vb / max(1, len(tb))
    den = np.linalg.norm(va) * np.linalg.norm(vb)
    return float(np.dot(va, vb) / den) if den else 0.0

def binary_metrics(y: np.ndarray, pred: np.ndarray) -> tuple[float, float, float]:
    tp = int(((y == 1) & (pred == 1)).sum()); fp = int(((y == 0) & (pred == 1)).sum()); fn = int(((y == 1) & (pred == 0)).sum())
    precision = tp / max(1, tp + fp); recall = tp / max(1, tp + fn); accuracy = float((y == pred).mean())
    return precision, recall, accuracy

def ndcg(y: list[int], scores: list[float]) -> float:
    order = np.argsort(-np.asarray(scores)); gains = (2 ** np.asarray(y)[order] - 1) / np.log2(np.arange(2, len(y) + 2))
    ideal = np.sort(np.asarray(y))[::-1]; idcg = float(((2 ** ideal - 1) / np.log2(np.arange(2, len(y) + 2))).sum())
    return float(gains.sum() / idcg) if idcg else 0.0

def clean(x: object) -> str:
    return re.sub(r"\s+", " ", str(x or "")).strip()

def terms(text: str, vocab: Iterable[str] = SKILLS) -> set[str]:
    low = clean(text).lower()
    found = {s for s in vocab if re.search(r"(?<![a-z0-9])" + re.escape(s) + r"(?![a-z0-9])", low)}
    return {SKILL_ALIASES.get(s, s) for s in found}

def years(text: str) -> float:
    vals = [float(v) for v in re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", clean(text).lower())]
    return max(vals, default=0.0)

def education(text: str) -> set[str]:
    low = clean(text).lower()
    return {e for e in EDU if e in low}

def requirements(text: str) -> tuple[set[str], set[str]]:
    must, nice = set(), set()
    for sent in re.split(r"[.!?;\n]", clean(text)):
        s = sent.lower()
        found = terms(s)
        if any(k in s for k in ("required", "must", "need to", "minimum", "qualifications")):
            must |= found
        elif any(k in s for k in ("preferred", "nice to have", "plus", "bonus", "desired")):
            nice |= found
    all_skills = terms(text)
    if not must:
        must = set(list(all_skills)[: min(5, len(all_skills))])
    nice -= must
    return must, nice

def extract_job(row: pd.Series) -> Dict:
    text = clean(row.get("title", "")) + " " + clean(row.get("description", "")) + " " + clean(row.get("skills_desc", ""))
    must, nice = requirements(text)
    return {"job_id": str(row.get("job_id", "")), "title": clean(row.get("title", "")), "text": text,
            "skills": sorted(terms(text)), "must_have": sorted(must), "nice_to_have": sorted(nice),
            "years": years(text), "education": sorted(education(text)), "location": clean(row.get("location", ""))}

def extract_resume(row: pd.Series) -> Dict:
    text = clean(row.get("Resume_str", ""))
    return {"resume_id": str(row.get("ID", "")), "category": clean(row.get("Category", "")), "text": text,
            "skills": sorted(terms(text)), "years": years(text), "education": sorted(education(text)),
            "roles": [clean(x) for x in re.findall(r"(?im)^\s*([A-Z][A-Z /&-]{3,})\s*$", text)[:5]]}

def score(job: Dict, resume: Dict) -> Dict:
    js, rs = set(job["skills"]), set(resume["skills"])
    must, nice = set(job["must_have"]), set(job["nice_to_have"])
    overlap = js & rs
    must_hit = overlap & must
    nice_hit = overlap & nice
    skill = len(must_hit) / max(1, len(must)) * 0.75 + len(nice_hit) / max(1, len(nice)) * 0.25 if (must or nice) else 0
    exp = 1.0 if not job["years"] else min(1.0, resume["years"] / job["years"])
    edu = 1.0 if not job["education"] else float(bool(set(job["education"]) & set(resume["education"])))
    loc = 1.0 if not job["location"] else float(any(t and t.lower() in resume["text"].lower() for t in re.split(r"[, ]+", job["location"]) if len(t) > 3))
    role = 1.0 if TECH_TITLE.search(job["title"]) and resume["category"].upper() in ANALYST_CATEGORIES else 0.0
    fit = round(100 * (0.55 * skill + 0.20 * exp + 0.10 * edu + 0.05 * loc + 0.10 * role), 2)
    gaps = sorted(must - rs)
    decision = "advance" if fit >= 62 and len(gaps) <= max(2, len(must) // 2) else "human_review"
    evidence = sorted(overlap)
    return {"fit_score": fit, "decision": decision, "evidence": evidence, "gaps": gaps,
            "components": {"skill": round(skill, 3), "experience": round(exp, 3), "education": round(edu, 3), "location": round(loc, 3), "role": round(role, 3)}}

def job_family(row: pd.Series) -> bool:
    return bool(TECH_TITLE.search(clean(row.get("title", "")) + " " + clean(row.get("description", ""))))

def build_golden(jobs: pd.DataFrame, resumes: pd.DataFrame, n: int = 200) -> pd.DataFrame:
    """Create a deterministic draft set. Labels are weak labels and must be human-audited."""
    tech_jobs = jobs[jobs.apply(job_family, axis=1)].dropna(subset=["description"]).head(100)
    tech_res = resumes[resumes["Category"].isin(ANALYST_CATEGORIES)].head(100)
    other_res = resumes[~resumes["Category"].isin(ANALYST_CATEGORIES)].head(100)
    rows = []
    for _, j in tech_jobs.iterrows():
        jx = extract_job(j); jt = set(jx["skills"])
        candidates = list(tech_res.itertuples(index=False)) + list(other_res.itertuples(index=False))
        scored = []
        for r in candidates:
            rx = extract_resume(pd.Series(r._asdict())); ov = len(jt & set(rx["skills"]))
            label = int(rx["category"] in ANALYST_CATEGORIES and ov >= 1)
            scored.append((label, ov, rx["resume_id"], jx["job_id"], jx["title"], rx["category"]))
        scored.sort(key=lambda x: (-x[0], -x[1], x[2]))
        rows.extend(scored[:2])
        rows.extend(scored[-1:])
        if len(rows) >= n: break
    return pd.DataFrame(rows[:n], columns=["label", "skill_overlap", "resume_id", "job_id", "job_title", "resume_category"]).assign(label_source="weak_draft_needs_human_audit")

def evaluate(golden: pd.DataFrame, jobs: pd.DataFrame, resumes: pd.DataFrame) -> Dict:
    jm = {str(r.get("job_id")): extract_job(r) for _, r in jobs.iterrows()}
    rm = {str(r.get("ID")): extract_resume(r) for _, r in resumes.iterrows()}
    out = []
    for r in golden.itertuples(index=False):
        jid, rid = str(r.job_id), str(r.resume_id)
        if jid not in jm or rid not in rm: continue
        x = score(jm[jid], rm[rid]); out.append({**r._asdict(), **x})
    d = pd.DataFrame(out)
    if d.empty: return {"n": 0}
    y = d.label.astype(int).to_numpy(); pred = (d.fit_score >= 62).astype(int)
    precision, recall, accuracy = binary_metrics(y, pred)
    d["keyword_score"] = d.skill_overlap / d.skill_overlap.max() * 100 if d.skill_overlap.max() else 0
    d["tfidf_score"] = np.array([tfidf_cosine(jm[str(x.job_id)]["text"], rm[str(x.resume_id)]["text"]) for x in d.itertuples()]) * 100
    top = d.sort_values(["job_id", "fit_score"], ascending=[True, False])
    ranking = ndcg(top.label.tolist(), top.fit_score.tolist()) if len(top) > 1 else 0
    threshold_rows = []
    for threshold in range(40, 81, 2):
        p, r, a = binary_metrics(y, (d.fit_score >= threshold).astype(int))
        threshold_rows.append({"threshold": threshold, "precision": round(p, 3), "recall": round(r, 3), "accuracy": round(a, 3)})
    return {"n": int(len(d)), "pipeline_precision": round(precision, 3),
            "pipeline_recall": round(recall, 3),
            "pipeline_accuracy": round(accuracy, 3), "ndcg_global": round(ranking, 3),
            "keyword_mean_score": round(float(d.keyword_score.mean()), 2), "tfidf_mean_score": round(float(d.tfidf_score.mean()), 2),
            "threshold_analysis": threshold_rows,
            "sample_results": d[["job_id", "resume_id", "label", "fit_score", "decision", "evidence", "gaps"]].head(10).to_dict("records"),
            "judge_sample": d[["job_id", "resume_id", "fit_score", "decision", "evidence", "gaps"]].head(30).to_dict("records")}

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--jobs", default="postings.csv"); ap.add_argument("--resumes", default="Resume.csv"); ap.add_argument("--out", default="outputs"); ap.add_argument("--max-jobs", type=int, default=300, help="subsample size; default keeps the run under 15 minutes"); args = ap.parse_args()
    out = Path(args.out); out.mkdir(parents=True, exist_ok=True)
    jobs = pd.read_csv(args.jobs, nrows=args.max_jobs, low_memory=False); resumes = pd.read_csv(args.resumes)
    golden_path = out / "golden_eval.csv"
    if golden_path.exists():
        golden = pd.read_csv(golden_path)
        print(f"Using existing evaluation labels from {golden_path}")
    else:
        golden = build_golden(jobs, resumes); golden.to_csv(golden_path, index=False)
    metrics = evaluate(golden, jobs, resumes); (out / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    review = golden.copy()
    review["human_label"] = ""
    review["reviewer_notes"] = ""
    review["uncertain"] = ""
    review.to_csv(out / "golden_eval_review_template.csv", index=False)
    judge = pd.DataFrame(metrics.get("judge_sample", []))
    if not judge.empty:
        judge["rater_1_total"] = ""
        judge["rater_2_total"] = ""
        judge["rater_1_notes"] = ""
        judge["rater_2_notes"] = ""
        judge.to_csv(out / "explanation_judge_template.csv", index=False)
    job = extract_job(jobs.iloc[0]); sample = []
    for _, r in resumes.head(10).iterrows(): sample.append({"job": job, "resume": extract_resume(r), "result": score(job, extract_resume(r))})
    (out / "sample_screening.json").write_text(json.dumps(sample, indent=2), encoding="utf-8")
    print(json.dumps({"jobs": len(jobs), "resumes": len(resumes), "golden_rows": len(golden), **metrics}, indent=2))

if __name__ == "__main__": main()

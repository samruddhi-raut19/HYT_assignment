"""Counterfactual fairness smoke test on generated screening examples."""
import json
from pathlib import Path
from screening_pipeline import score

def main():
    src = Path("outputs/sample_screening.json")
    rows = json.loads(src.read_text(encoding="utf-8"))
    out = []
    for item in rows:
        base = item["resume"]
        variants = {
            "base": base["text"],
            "gender_neutral": base["text"].replace(" he ", " they ").replace(" she ", " they ").replace(" his ", " their ").replace(" her ", " their "),
            "college_changed": base["text"] + " Education: Example State University.",
            "name_changed": "Alex Candidate\n" + base["text"],
        }
        base_score = score(item["job"], {**base, "text": variants["base"]})["fit_score"]
        for name, text in variants.items():
            result = score(item["job"], {**base, "text": text})
            out.append({"job_id": item["job"]["job_id"], "resume_id": base["resume_id"], "variant": name,
                        "fit_score": result["fit_score"], "decision": result["decision"], "delta": round(result["fit_score"] - base_score, 4)})
    Path("outputs/fairness_check.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps({"pairs": len(out), "max_abs_score_delta": max(abs(x["delta"]) for x in out)}, indent=2))

if __name__ == "__main__": main()

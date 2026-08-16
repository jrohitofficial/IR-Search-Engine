import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "task1_vertical_search" / "backend"))
from database.mongo_client import research_outputs_col, profiles_col  # noqa: E402

EVID = Path(__file__).parent / "evidence"


def dump(doc, name):
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    for k, v in doc.items():
        if hasattr(v, "isoformat"):
            doc[k] = v.isoformat()
    (EVID / name).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", name)


dump(research_outputs_col().find_one({"title": {"$regex": "Mental Well-Being"}}), "mongo_research_output_sample.json")
dump(profiles_col().find_one({"name": "Sally Abbott"}), "mongo_profile_sample.json")

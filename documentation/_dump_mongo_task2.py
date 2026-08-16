import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "task2_document_clustering" / "backend"))
from database.mongo_client import predictions_col  # noqa: E402

EVID = Path(__file__).parent / "evidence"


def dump(doc, name):
    doc = dict(doc)
    doc["_id"] = str(doc["_id"])
    for k, v in doc.items():
        if hasattr(v, "isoformat"):
            doc[k] = v.isoformat()
    (EVID / name).write_text(json.dumps(doc, indent=2, ensure_ascii=False), encoding="utf-8")
    print("wrote", name)


dump(predictions_col().find_one(sort=[("timestamp", -1)]), "mongo_prediction_sample.json")

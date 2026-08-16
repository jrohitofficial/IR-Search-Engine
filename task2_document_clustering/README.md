# Task 2 — Document Clustering

See the [project root README](../README.md) for full setup, environment variables,
architecture notes and API documentation. Quick start:

```powershell
cd scripts
python build_dataset.py   # validates dataset, loads 540 docs into MongoDB
python train_model.py     # TF-IDF + K-Means, evaluation, visualisation

cd ..\backend
python run.py               # web app at http://localhost:5002
pytest -v                    # test suite
```

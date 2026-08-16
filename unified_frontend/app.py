"""
Unified frontend: a single polished web application that presents both
Task 1 (vertical search engine) and Task 2 (document clustering) in one
UI, as separate tabs. It is a thin presentation layer only -- all real
logic (crawling, TF-IDF/cosine ranking, K-Means classification, MongoDB
storage) still lives in the two independent Flask backends
(task1_vertical_search/backend on :5001, task2_document_clustering/backend
on :5002); this app calls their REST APIs from the browser.
"""
from flask import Flask, render_template

app = Flask(__name__)


@app.get("/")
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003, debug=False, use_reloader=False)

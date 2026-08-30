# IR_COURSEWORK — ST7071CEM Information Retrieval

Two working systems built for the Coventry/Softwarica ST7071CEM Information Retrieval coursework:

- **Task 1 — Vertical Search Engine**: crawls Coventry University's PurePortal for the
  *Centre for Healthcare and Community Transformation*, indexes research outputs with a
  TF-IDF Vector Space Model, and serves ranked, paginated search results with clickable
  links to the original publication and author profile pages.
- **Task 2 — Document Clustering**: clusters a 540-document Economics / Entertainment /
  Politics corpus with K-Means (K=3) and classifies new user-submitted text against the
  trained model, storing every prediction in MongoDB.

Both tasks share one MongoDB Atlas database and run as independent Flask backends
(`task1_vertical_search/backend` on :5001, `task2_document_clustering/backend` on :5002).
A single **unified frontend** (`unified_frontend/`, port 5003) presents both as tabs in one
polished web application — see [unified_frontend/](unified_frontend/).

A full evidence pack — real code listings, real screenshots, real crawl/training output,
real evaluation metrics, APA 7 references and a requirement traceability matrix — is
assembled into [documentation/final_documentation.docx](documentation/final_documentation.docx).
Sections requiring the student's own critical analysis are clearly marked
**"AUTHOR ANALYSIS REQUIRED"** rather than pre-written.

> **Scope note.** This project targets the *official* coursework brief
> (`ST7071CEM_InformationRetrieval_Coursework.pdf`) rather than a separately-circulated
> scheduler, React/TypeScript). Where the two disagreed, the official brief won.
> The 2000-word written report itself is intentionally **not** included here.

---

## Project overview

### System Architecture

```mermaid
graph TD
    subgraph Users
        U[User / Browser]
    end

    subgraph Frontend [Unified Frontend (Port 5003)]
        UI[Web Interface]
    end

    subgraph Backend_Services [Backend Services]
        subgraph Task1 [Task 1: Vertical Search (Port 5001)]
            T1_API[REST API]
            T1_Rank[TF-IDF Vector Space Model]
            T1_Sched[Crawl Scheduler]
            T1_Crawl[Web Crawler]
        end

        subgraph Task2 [Task 2: Document Clustering (Port 5002)]
            T2_API[REST API]
            T2_Preproc[Text Preprocessing Pipeline]
            T2_Model[K-Means Clustering Model K=3]
        end
    end

    subgraph Data_Storage [Data Storage]
        DB[(MongoDB Atlas)]
    end

    subgraph External_Sources [External Sources]
        PurePortal[Coventry PurePortal]
        Dataset[BBC News Dataset]
    end

    %% User Interactions
    U -->|Access UI| UI
    
    %% Frontend to Backend
    UI -->|Search Queries / GET| T1_API
    UI -->|Text Classification / POST| T2_API

    %% Task 1 Internal & External Flow
    T1_API <--> T1_Rank
    T1_Sched -->|Triggers| T1_Crawl
    T1_Crawl -->|Crawls/Scrapes| PurePortal
    T1_Crawl -->|Stores Docs & Profiles| DB
    T1_Rank -->|Reads Indexed Data| DB

    %% Task 2 Internal & External Flow
    T2_API --> T2_Preproc
    T2_Preproc --> T2_Model
    T2_API -->|Saves Predictions| DB
    T2_Model -->|Reads Corpus Stats| DB
    Dataset -->|Offline Training| T2_Model

    classDef frontend fill:#d4edda,stroke:#28a745,stroke-width:2px,color:#155724;
    classDef backend1 fill:#cce5ff,stroke:#007bff,stroke-width:2px,color:#004085;
    classDef backend2 fill:#e2e3e5,stroke:#6c757d,stroke-width:2px,color:#383d41;
    classDef storage fill:#fff3cd,stroke:#ffc107,stroke-width:2px,color:#856404;
    classDef external fill:#f8d7da,stroke:#dc3545,stroke-width:2px,color:#721c24;

    class UI frontend;
    class T1_API,T1_Rank,T1_Sched,T1_Crawl backend1;
    class T2_API,T2_Preproc,T2_Model backend2;
    class DB storage;
    class PurePortal,Dataset external;
```

### Directory Structure

```
IR_COURSEWORK/
├── task1_vertical_search/
│   └── backend/          Flask app: crawler, TF-IDF ranking, scheduler, API, UI
├── task2_document_clustering/
│   ├── backend/           Flask app: preprocessing, K-Means, API, UI
│   ├── dataset/            raw + processed corpus
│   └── scripts/           build_dataset.py, train_model.py
├── documentation/
│   └── figures/            generated evaluation charts
├── .env.example
└── .gitignore
```

## Requirements

- Python 3.11+ (developed and tested on 3.14)
- A MongoDB Atlas cluster (or any reachable MongoDB instance)
- Internet access (Task 1 crawls the live pureportal site; Task 2's dataset build reads
  a local archive already downloaded into `task2_document_clustering/dataset/raw/`)

## Installation

```powershell
cd IR_COURSEWORK
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r task1_vertical_search\backend\requirements.txt
pip install -r task2_document_clustering\backend\requirements.txt
```

(The two requirement files overlap; installing both into the same virtual environment,
as above, is the simplest option and is what was used to build and test this project.)

## MongoDB configuration

Copy `.env.example` to `.env` in the project root and fill in your real connection
string:

```
MONGODB_URI=mongodb+srv://<username>:<password>@<cluster-host>/?retryWrites=true&w=majority
DATABASE_NAME=ir_coursework
```

Both backends read this same `.env` file (via `python-dotenv`) from the project root.
**Never commit the real `.env` file** — it is already excluded in `.gitignore`.

## Environment variables

See `.env.example` for the full list. The important ones:

| Variable | Meaning | Default |
|---|---|---|
| `MONGODB_URI` | MongoDB Atlas connection string | — |
| `SEED_URL` | Task 1 crawl seed (must stay the Centre for Healthcare and Community Transformation page) | pureportal org URL |
| `CRAWL_INTERVAL_MONTHS` | How often the scheduler re-crawls | `3` |
| `MAX_PUBLICATIONS`, `MAX_PROFILES`, `MAX_CRAWL_SECONDS` | Crawl bounds (so it cannot run forever) | 200 / 200 / 1800 |
| `MIN_DOCS_PER_CATEGORY` | Task 2 dataset validation threshold | `150` |

## Running the Full Application

The application consists of three separate services that need to run simultaneously. You should open **three separate terminal windows/tabs**, activate the virtual environment in each, and run the following commands:

### Terminal 1: Task 1 Backend (Vertical Search)
This runs on port 5001.
```powershell
.venv\Scripts\activate
cd task1_vertical_search\backend
python run.py
```

### Terminal 2: Task 2 Backend (Document Clustering)
This runs on port 5002.
*(Note: If you haven't trained the dataset yet, run `python build_dataset.py` and `python train_model.py` in `task2_document_clustering/scripts` first).*
```powershell
.venv\Scripts\activate
cd task2_document_clustering\backend
python run.py
```

### Terminal 3: Unified Frontend
This is the main user interface running on port 5003.
```powershell
.venv\Scripts\activate
cd unified_frontend
python app.py
```

Once all three services are running, open your web browser and go to **http://localhost:5003** to access the unified frontend.

---

## Task 1 — Vertical Search Engine

### Run a single crawl (populates MongoDB)

```powershell
cd task1_vertical_search\backend
python run.py --crawl
```



### Crawler design

The seed page is fetched directly. Its *listing* sub-pages
(`.../publications/`, `.../persons/`) are protected by Cloudflare bot management on the
live site and return 403 regardless of headers used — this was verified directly
rather than assumed. The crawler therefore
discovers content the way a human following links would: the seed page embeds a
"highlighted research output" and "profiles" widget with real links; each profile page
lists that person's own publications; each publication page lists its authors' profile
links. A breadth-first search over this citation/co-authorship graph, bounded by
`MAX_PUBLICATIONS` / `MAX_PROFILES` / `MAX_CRAWL_SECONDS`, reaches a genuine, verifiable
subset of the unit's output using only pages the site serves openly. Every visited page
is checked against `robots.txt` first, and requests to the same host are spaced by the
site's published `Crawl-Delay: 5`.

Every publication/profile is only stored if the page itself confirms membership of the
target centre (an "at least one co-author is a member of this department" check, mirroring
the coursework wording).

### Scheduler

`scheduler/crawl_scheduler.py` uses APScheduler's `BackgroundScheduler` with an
`IntervalTrigger(days=settings.CRAWL_INTERVAL_MONTHS * 30)`. The interval defaults to 3 months,
matching the updated brief requirements,
and is fully configurable via `CRAWL_INTERVAL_MONTHS` in `.env` — set it to `1` for a
monthly schedule if a faster-moving data source required it.

### Ranking (Vector Space Model)

`ranking/vector_space_model.py` builds a TF-IDF matrix over all indexed documents
(`scikit-learn TfidfVectorizer`), applies the **same** preprocessing to the query, and
ranks by cosine similarity. Results are paginated at `TOP_K = 10` per page.

### REST API

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/search?q=...&page=1` | Ranked search, 10 results/page |
| GET | `/api/research-output/<id>` | Full stored record for one publication |
| GET | `/api/profile/<id>` | Full stored record for one profile |
| GET | `/api/crawler/status` | Last crawl stats, document counts, scheduler status |
| POST | `/api/crawler/run` | Trigger a crawl synchronously and rebuild the index |

### Tests

```powershell
cd task1_vertical_search\backend
pytest -v
```

---

## Task 2 — Document Clustering

### Dataset

The corpus uses the Greene & Cunningham BBC News dataset (see citation in
`task2_document_clustering/scripts/build_dataset.py`), **not** live scraping of
bbc.co.uk — that site's own `robots.txt` explicitly states *"No scraping, crawling, or
systematic extraction of content"* and *"No creating datasets from BBC content"*, and
blocks several AI-related crawlers by name. The dataset used here is a long-standing,
citable academic resource published specifically for non-commercial research/evaluation
use, hosted independently of bbc.co.uk. Its "business" category is used for the
coursework's "Economics" category.

### Build the dataset and train the model

```powershell
cd task2_document_clustering\scripts
python build_dataset.py     # validates >=150/category, loads 540 docs into MongoDB
python train_model.py       # TF-IDF + K-Means(K=3), evaluation, PCA visualisation
```



### Pipeline

`preprocessing/text_preprocessing.py`: clean → lowercase → tokenise → punctuation
removal → stop-word removal → Porter stemming.
`clustering/kmeans_model.py`: TF-IDF → K-Means (K=3, k-means++ init, n_init=10) →
majority-vote cluster→category mapping → persisted to disk with `joblib` so the live API
never retrains on a request.

### REST API

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/api/classify` | Classify submitted text, save the prediction to MongoDB |
| GET | `/api/dataset/stats` | Per-category document counts vs. the 150/category minimum |
| GET | `/api/model/evaluation` | Silhouette score, inertia, confusion matrix, accuracy/F1 |
| GET | `/api/predictions/history` | Recent classifications |

### Tests

```powershell
cd task2_document_clustering\backend
pytest -v
```

---

## Unified frontend

The unified frontend serves a combined UI at `http://localhost:5003`. It requires both backends (Task 1 on `:5001`, Task 2 on `:5002`) to already be running — it is a presentation layer only and calls their REST APIs directly from the browser.

## Troubleshooting

- **`robots.txt disallows crawling` for a URL that should be allowed** — make sure you're
  using the fixed `crawler/robots_check.py`, which fetches `robots.txt` with a browser
  User-Agent. Python's `RobotFileParser.read()` uses no custom headers and gets a 403
  from Cloudflare on this specific site, which otherwise silently makes it report the
  whole site as disallowed.
- **MongoDB connection timeout** — check `MONGODB_URI` in `.env` and that your current IP
  is allow-listed in Atlas's Network Access settings.
- **Task 2 `/api/classify` returns 503** — the model hasn't been trained yet; run
  `scripts/train_model.py`.

## Github Links
'https://github.com/jrohitofficial/IR-Search-Engine.git'


## Deployment Links
(http://www.onespotsearch.linkpc.net/)
OR
(http://unified-frontend-6qge.onrender.com/)

## Video Link




🏛️ Politics
(Triggers: labour, party, election, blair, government, mp, tax, law)

"The Labour party has announced a new election plan to increase public tax."
"Prime Minister Tony Blair told the government to pass a new law."
"The Tory MP gave a speech to the public about the upcoming election."


📈 Economics
(Triggers: bank, market, price, economic, growth, company, firm, shares, sales)

"The central bank increased interest rates to control market prices and boost economic growth."
"The company reported record sales and the firm's shares surged in the stock market."
"Oil prices hit a new high this year, impacting business growth and company sales."


🎬 Entertainment
(Triggers: film, oscar, director, actor, band, song, tv, music, album)

"The new film won the Oscar for best director and best actor."
"The famous band performed their new song live on TV."
"The music star released a new album that broke every record this year."
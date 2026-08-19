# Information Retrieval Coursework - 10-Minute Video Presentation Script

**Student:** Rohit Jha  
**Program:** MSc in Data Science & Computational Intelligence (Batch 8)  
**College:** Softwarica College  
**Course:** Information Retrieval  

---

## 🎬 Section 1: Introduction & Architecture (0:00 - 1:30)
**[Camera: On Speaker]**

"Hello everyone. My name is Rohit Jha, and I am from MSc Batch 8 of the MSc in Data Science & Computational Intelligence program at Softwarica College. 

Today, I will be presenting my coursework for the Information Retrieval module. This assignment challenged us to build two core IR systems: 
1. **Task 1:** A Vertical Search Engine to crawl and search academic publications.
2. **Task 2:** A Document Clustering system using K-Means to categorize text.

Instead of keeping them isolated, I engineered a **microservice architecture**. I built two independent Python Flask backends—one for crawling and searching, and one for machine learning and clustering. I then built a single, unified web application that communicates with both via REST APIs. This approach mirrors modern, scalable industry practices."

---

## 🗄️ Section 2: MongoDB Deep Dive (1:30 - 3:00)
**[Screen Recording: Open MongoDB Compass]**

"Before we run the code, let's look at where the data lives. I used MongoDB to store all persistent data. 

In MongoDB Compass, you can see my first database: **`task1_search`**. 
Let's open the `research_outputs` collection. **[Action: Click on `research_outputs` and expand a document]**. As you can see, the crawler successfully extracted rich metadata: the publication title, the date, publication type, and an array of author profile links. We also have `search_logs` to track user queries, and `crawl_logs` to monitor crawler health.

Now let's look at the second database: **`task2_clustering`**. 
Inside `clustering_documents` **[Action: Expand a document here]**, we have 540 labeled news articles from the BBC dataset. Each document has the raw text and its true category (Economics, Entertainment, or Politics) which we use to train and evaluate our K-Means model. The `clustering_predictions` collection serves as our history log for real-time user predictions."

---

## 💻 Section 3: Code Walkthrough - Task 1 Crawler & Ranking (3:00 - 4:30)
**[Screen Recording: Open VS Code. Open `task1_vertical_search/backend/crawler/pure_crawler.py`]**

"Let's look at the code driving this. For Task 1, I built a custom, polite vertical crawler in Python. **[Action: Highlight the robots.txt fetching logic]** As you can see here, it strictly respects `robots.txt` and implements a dynamic `crawl-delay`. It parses HTML using BeautifulSoup, ensuring it only extracts outputs where at least one co-author belongs to the specific Research Centre.

**[Action: Open `task1_vertical_search/backend/ranking/vector_space_model.py`]**
Once crawled, the documents must be searchable. In this file, I implemented the **Vector Space Model**. I use Scikit-Learn's `TfidfVectorizer` to map all documents into a multi-dimensional term space. When a user queries the system, the query is vectorized in the exact same space, and we compute the **Cosine Similarity** between the query and all documents, returning the highest-scoring matches."

---

## 🤖 Section 4: Code Walkthrough - Task 2 K-Means (4:30 - 5:30)
**[Screen Recording: Open `task2_document_clustering/backend/clustering/kmeans_model.py`]**

"For Task 2, we move to Machine Learning. **[Action: Highlight the preprocessing pipeline]** To prepare the text for clustering, I implemented a preprocessing pipeline that includes lowercasing, stop-word removal, and crucial **Porter Stemming** to reduce words to their root forms, which drastically improves clustering quality.

**[Action: Scroll down to the K-Means training block]**
I then vectorise the dataset using TF-IDF and train a **K-Means Clustering** model with K=3. The script evaluates itself by mapping the mathematical clusters back to our human-readable categories, generating accuracy scores and a confusion matrix which are saved to disk to be served by the API."

---

## 🚀 Section 5: Starting the Microservices (5:30 - 6:30)
**[Screen Recording: Show VS Code terminal with 3 split panes]**

"Let's bring the system to life."

**[Action: Terminal 1]**
"I'll start the Task 1 Vertical Search backend." *(Type `python run.py` in task 1)*. "It loads the crawled data from Mongo and builds the TF-IDF search index in memory."

**[Action: Terminal 2]**
"Next, the Task 2 Document Clustering backend." *(Type `python run.py` in task 2)*. "It loads the pre-trained K-Means model."

**[Action: Terminal 3]**
"Finally, our Unified Frontend." *(Type `python app.py` in unified_frontend)*. "This serves our UI. Let's head to the browser."

---

## 🔍 Section 6: Task 1 UI Demonstration (6:30 - 8:00)
**[Screen Recording: Open Chrome to http://localhost:5003/]**

"Welcome to OneSpot.AI. 

First, let's check on the crawler. **[Action: Click 'Crawler & Index Status' panel]**. This panel fetches live statistics from the Task 1 API. You can see how many documents are indexed and verify that the background scheduler is configured to run every 3 months—ensuring the search engine stays up to date without manual intervention.

**[Action: Close panel, click Search Bar, type 'mental']**
As I type the word 'mental', notice the dynamic **Search Suggestions**. The API is actively querying MongoDB to find matching author names or titles in real-time. 

**[Action: Type 'mental health' and hit Search]**
Let's search for 'mental health'. The Vector Space Model ranks the documents perfectly. For every result, I display the exact **Cosine Similarity score**, proving the mathematical ranking. If I search for a broader term like 'health' **[Action: Search 'health', scroll to bottom]**, the system seamlessly handles pagination, rendering exactly 10 results per page as required."

---

## 📊 Section 7: Task 2 UI Demonstration (8:00 - 9:30)
**[Screen Recording: Click the 'Document Clustering' tab]**

"Moving to the Document Clustering interface.

**[Action: Scroll to the Cluster Distribution Donut Chart]**
First, we have a dynamic 3D donut chart showing the exact distribution of our 540-document dataset. The counting animation pulls live data from the database. 

**[Action: Scroll to Model Evaluation Metrics]**
Here are the model evaluation metrics. The K-Means model achieved an impressive accuracy and F1-score of over 95%. I also plotted a **PCA 2D visualization**, which compresses the high-dimensional TF-IDF vectors into 2D space, proving visually that our three categories form distinct, well-separated clusters.

**[Action: Click the Help Icon ('?') near Document Text]**
To demonstrate the model flawlessly, I built a 'Help' module that stores perfectly engineered phrases aligned with the dataset's top TF-IDF features. 

**[Action: Copy the Politics phrase: 'The Labour party has announced a new election plan to increase public tax.' and close modal]**
Let's test the live classifier with this unseen sentence. 

**[Action: Paste the text and click Classify]**
The text is vectorized, compared against the centroids, and instantly classified as **Politics** with massive confidence (90%+). You can see the exact mathematical distances to all three clusters. 

**[Action: Clear text, type 'Donald Trump is president of India', click Classify]**
Now, watch what happens when I type something unexpected. It predicts **Economics**! This is not a bug; this perfectly demonstrates **Data Bias**. Our model was trained on BBC News from 2005. In the UK, the political leader is the 'Prime Minister'. The BBC dataset overwhelmingly uses the word 'President' for business leaders like the 'President of the World Bank'. Because the model only knows what it was trained on, it mathematically learned that 'President' is an Economics term! This showcases a deep understanding of how training data limits machine learning.

**[Action: Scroll down to Prediction History]**
Every live prediction is instantly saved to MongoDB and shown here in the **Prediction History** with accurate UTC-adjusted timestamps."

---

## 🎓 Section 8: Conclusion & Limitations (9:30 - 10:00)
**[Camera: On Speaker]**

"To wrap up, I have built a fully functional, end-to-end Information Retrieval system. 

While the system is highly robust, one limitation I encountered was Cloudflare bot-protection on the University's PurePortal, which restricted the crawler from accessing deeper pagination pages, limiting the total corpus size. Given more time, deploying the crawler from a trusted campus IP could overcome this.

By unifying the vertical search and document clustering into a professional, responsive web application backed by MongoDB, I've ensured this project is not just an academic exercise, but a production-ready application. 

Thank you for watching."

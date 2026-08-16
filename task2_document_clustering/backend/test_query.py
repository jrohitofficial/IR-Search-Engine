import os
from dotenv import load_dotenv
load_dotenv("../../.env")
from pymongo import MongoClient

client = MongoClient(os.environ["MONGODB_URI"])
col = client["Task_2_Document_Clustering"]["clustering_documents"]

print("Total docs:", col.count_documents({}))
doc = col.find_one()
if doc:
    print("Keys:", doc.keys())
    if "text" in doc:
        print("Text snippet:", doc["text"][:100])
    elif "content" in doc:
        print("Content snippet:", doc["content"][:100])

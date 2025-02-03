from pathlib import Path

from src.config import DOCUMENTS_DIR

path = Path(DOCUMENTS_DIR)

texts = []
for filename in path.glob("*.md"):
    with open(filename) as f:
        texts.append(f.read())


# %%
user_input: str = "how do do the sum of two  tensor"

def parse_class_add_title(text):
    chunks = text.split("##")
    title =  chunks[0].split("#")[0]
    return {"title": title, "chunks": [f"{title}|||: {chunk}" for chunk in chunks]}

chunks = sum((parse_class_add_title(txt)["chunks"] for txt in texts), [])


def jaccard_similarity(query, document):
    query = query.lower().split(" ")
    document = document.lower().split(" ")
    intersection = set(query).intersection(set(document))
    union = set(query).union(set(document))
    return len(intersection) / len(union)


def return_response(corpus):
    similarities = []
    for doc in corpus:
        similarity = jaccard_similarity(user_input, doc)
        similarities.append(similarity)
    return chunks[similarities.index(max(similarities))]

relevent_document = return_response(chunks)

full_response = []



import requests
import json
from src.llm_query import call_llm

response = call_llm(user_input, relevent_document, full_response, "llama2")
print(response)






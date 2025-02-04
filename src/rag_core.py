from pathlib import Path

from src.config import DOCUMENTS_DIR
from src.llm_query import call_llm
from src.retriever import return_response

path = Path(DOCUMENTS_DIR)

texts = []
for filename in path.glob("*.md"):
    with open(filename) as f:
        texts.append(f.read())

# %%
user_query: str = "how do do the sum of two  tensor"


def parse_class_add_title(text):
    chunks = text.split("##")
    title = chunks[0].split("#")[0]
    return {"title": title, "chunks": [f"{title}|||: {chunk}" for chunk in chunks]}

chunks = sum((parse_class_add_title(txt)["chunks"] for txt in texts), [])

relevent_document = return_response(chunks, user_query)

full_response = []

response = call_llm(user_query, relevent_document['response'], llm="llama2")
print(response)

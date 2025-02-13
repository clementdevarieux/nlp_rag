from pathlib import Path

from src.chunk import trunkate_on_h2
from src.config import DOCUMENTS_DIR
from src.llm_query import call_llm
from src.retriever import jaccard_retriever, get_fittest_chunk, tfidf_retriever

path = Path(DOCUMENTS_DIR)

texts = []
for filename in path.glob("*.md"):
    with open(filename, encoding='utf-8') as f:
        texts.append(f.read())

# %%
user_query: str = "how to sum two tensor"


chunks = trunkate_on_h2(texts)

fittest_document_id = jaccard_retriever(chunks, user_query)
#using jaccard_similarity
# fittest_document = get_fittest_chunk(relevent_documents, user_query)
# fittest_document_id = tfidf_retriever(chunks, user_query)

fittest_document = chunks[fittest_document_id[0]]

full_response = []

response = call_llm(user_query, fittest_document['chunk'], llm="llama2")
print(response)

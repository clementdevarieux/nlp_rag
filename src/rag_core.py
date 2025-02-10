from pathlib import Path

from src.config import DOCUMENTS_DIR
from src.llm_query import call_llm
from src.retriever import retreive_response, get_fittest_chunk, tfidf_vectorizer

path = Path(DOCUMENTS_DIR)

texts = []
for filename in path.glob("*.md"):
    with open(filename) as f:
        texts.append(f.read())

# %%
user_query: str = "how to sum two tensor"


def parse_class_add_title(text):
    chunks = text.split("##")
    title = chunks[0].split("\n")[0]
    return [
        {"title": title, 'chunk': f"{title}|||: {chunk}"} for chunk in chunks]


structured_chunks = [parse_class_add_title(txt) for txt in texts]
chunks = [chunk_value for chunk in structured_chunks for chunk_value in chunk]

fittest_document_id = retreive_response(chunks, user_query)
#using jaccard_similarity
# fittest_document = get_fittest_chunk(relevent_documents, user_query)
fittest_document_id = tfidf_vectorizer(chunks, user_query)

fittest_document = chunks[fittest_document_id]

full_response = []

response = call_llm(user_query, fittest_document['response'], llm="llama2")
print(response)

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
from transformers import AutoTokenizer, AutoModel
from transformers import BertTokenizer, BertModel
import torch
import torch.nn.functional as F

def jaccard_similarity(user_query, chunk):
    user_query = user_query.lower().split(" ")
    chunk = chunk.lower().split(" ")
    intersection = set(user_query).intersection(set(chunk))
    union = set(user_query).union(set(chunk))
    return len(intersection) / len(union)


def retreive_response(chunks_struct: list, user_query: str) -> dict:
    similarities = []
    for i, chunk in enumerate(chunks_struct):
        similarity = jaccard_similarity(user_query, chunk['chunk'])
        similarities.append((i, similarity, chunk))

    ordered_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return ordered_similarities[0][0]

def get_fittest_chunk(ordered_similarities: list, user_query:str) -> dict:
    fittest_chunk = ordered_similarities[0][2]
    return {
        "user_query": user_query,
        "chunk_name": fittest_chunk['title'],
        "response": fittest_chunk,
    }


def tfidf_vectorizer(chunks_struct: list, user_query: str):
    txt_chunk = []
    for chunk in chunks_struct:
        txt_chunk.append(chunk['chunk'])
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(txt_chunk + [user_query])

    cosin_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    fittest_chunk_index = np.argmax(cosin_similarities)
    return fittest_chunk_index

def transformers_retriever(chunks_struct: list, user_query: str):
    tokenizer = BertTokenizer.from_pretrained('bert-base-cased')
    model = BertModel.from_pretrained('bert-base-cased')

    def encode_text(texts, tokenizer, model):
        inputs = tokenizer(texts, padding=True, truncation=True, return_tensors='pt', max_length=512)
        with torch.no_grad():
            outputs = model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :]
        return embeddings
    #TODO
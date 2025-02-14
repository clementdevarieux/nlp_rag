import json
from pathlib import Path

import numpy as np
from FlagEmbedding import FlagModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from tqdm import tqdm

from src.chunk import truncate_on_h2
from src.config import DOCUMENTS_DIR, PROCESSED_DIR
from src.llm_query import call_llm
from src.prompt import build_prompt_question_generation, build_prompt_question_hyde


def get_fittest_chunk(ordered_similarities: list, user_query: str) -> dict:
    fittest_chunk = ordered_similarities[0][2]
    return {
        "user_query": user_query,
        "chunk_name": fittest_chunk['title'],
        "response": fittest_chunk,
    }


def jaccard_retriever(chunks_struct: list, user_query: str) -> list[int]:
    def jaccard_similarity(user_query, chunk):
        user_query = user_query.lower().split(" ")
        chunk = chunk.lower().split(" ")
        intersection = set(user_query).intersection(set(chunk))
        union = set(user_query).union(set(chunk))
        return len(intersection) / len(union)

    similarities = []
    for i, chunk in enumerate(chunks_struct):
        similarity = jaccard_similarity(user_query, chunk['chunk'])
        similarities.append((i, similarity, chunk))

    ordered_similarities = sorted(similarities, key=lambda x: x[1], reverse=True)
    return [ordered_similarities[0][0]]


def tfidf_retriever(chunks_struct: list, user_query: str) -> list[int]:
    txt_chunk = []
    for chunk in chunks_struct:
        txt_chunk.append(chunk['chunk'])
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(txt_chunk + [user_query])

    cosin_similarities = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    fittest_chunk_index = np.argmax(cosin_similarities)
    return [int(fittest_chunk_index)]


def transformers_retriever(chunks_struct: list, user_query: str) -> list[int]:
    model = FlagModel(
        'BAAI/bge-base-en-v1.5',
        query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
        use_fp16=True,
    )

    txt_chunk = []
    for chunk in chunks_struct:
        txt_chunk.append(chunk['chunk'])

    corpus_embedding = model.encode(txt_chunk)
    query_embedding = model.encode(user_query)

    sim_scores = query_embedding @ corpus_embedding.T

    sim_index = np.argmax(sim_scores)

    return [int(sim_index)]


def hypothetical_query_retriever(chunks_struct: list, user_query: str) -> list[int]:
    model = FlagModel(
        'BAAI/bge-base-en-v1.5',
        query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
        use_fp16=True,
    )

    generated_questions_file = Path(PROCESSED_DIR) / "generated_questions.json"
    generated_questions = []

    if generated_questions_file.is_file():
        with open(generated_questions_file, "r", encoding='utf-8') as f:
            generated_questions.append(f.read())
    else:
        for chunk in tqdm(chunks_struct, desc='generating questions'):
            prompt = build_prompt_question_generation(chunk['chunk'])
            generated_question = call_llm(prompt, llm='llama2')
            generated_questions.append(generated_question)
        with open(generated_questions_file, "w", encoding='utf-8') as f:
            json.dump(generated_questions, f)

    corpus_embedding = model.encode(generated_questions)
    query_embedding = model.encode(user_query)

    sim_scores = query_embedding @ corpus_embedding.T

    sim_index = np.argmax(sim_scores)

    return [int(sim_index)]


def hyde_retriever(chunks_struct: list, user_query: str) -> list[int]:
    model = FlagModel(
        'BAAI/bge-base-en-v1.5',
        query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
        use_fp16=True,
    )

    prompt = build_prompt_question_hyde(user_query)
    generated_question = call_llm(prompt, llm='llama2')

    txt_chunk = []
    for chunk in chunks_struct:
        txt_chunk.append(chunk['chunk'])

    corpus_embedding = model.encode(txt_chunk)
    query_embedding = model.encode(generated_question)

    sim_scores = query_embedding @ corpus_embedding.T
    sim_index = np.argmax(sim_scores)
    return [int(sim_index)]


if __name__ == "__main__":
    path = Path(DOCUMENTS_DIR)

    model = FlagModel(
        'BAAI/bge-base-en-v1.5',
        query_instruction_for_retrieval="Represent this sentence for searching relevant passages:",
        use_fp16=True,
    )

    texts = []
    for filename in path.glob("*.md"):
        with open(filename, encoding='utf-8') as f:
            texts.append(f.read())

    chunks = truncate_on_h2(texts)

    question = "What function is used to check the closeness of two tensors ?"

    print(hyde_retriever(chunks, question, model))

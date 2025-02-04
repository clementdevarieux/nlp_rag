def jaccard_similarity(user_query, chunk):
    user_query = user_query.lower().split(" ")
    chunk = chunk.lower().split(" ")
    intersection = set(user_query).intersection(set(chunk))
    union = set(user_query).union(set(chunk))
    return len(intersection) / len(union)


def return_response(chunks: list, user_query: str) -> dict:
    similarities = []
    for chunk in chunks:
        similarity = jaccard_similarity(user_query, chunk)
        similarities.append(similarity)

    fittest_chunk = chunks[similarities.index(max(similarities))]
    return {
        "user_query": user_query,
        "chunk_name": fittest_chunk.split("|||")[0],
        "response": fittest_chunk,
    }

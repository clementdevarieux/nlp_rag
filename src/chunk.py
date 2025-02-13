from typing import List, Dict


def trunkate_on_h2(texts: list[str]) -> list[dict[str, str]]:
    def parse_class_add_title(text: str):
        chunks = text.split("##")
        title = chunks[0].split("\n")[0]
        return [
            {"title": title, 'chunk': f"{title}|||: {chunk}"} for chunk in chunks]

    structured_chunks = [parse_class_add_title(txt) for txt in texts]
    chunks = [chunk_value for chunk in structured_chunks for chunk_value in chunk]
    for i in range(len(chunks)):
        chunks[i]["index"]= i

    return chunks

def find_chunk_indices_with_title(chunks: list[dict], title: str):
    chunks_lst = []
    for chunk in chunks:
        if chunk["title"] == title:
            chunks_lst.append(chunk['index'])
    return chunks_lst


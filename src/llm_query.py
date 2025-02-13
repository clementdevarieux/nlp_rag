import json

import requests

from src.prompt import build_prompt


# call LLM using Ollama api
def call_llm(user_input: str, relevant_document: str, llm: str) -> str:
    full_response = []
    url = 'http://localhost:11434/api/generate'
    data = {
        "model": llm,
        "prompt": build_prompt(query=user_input, context_str=relevant_document)
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
    try:
        for line in response.iter_lines():
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                full_response.append(decoded_line['response'])
    finally:
        response.close()
    return ''.join(full_response)

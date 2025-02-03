import prompt
import requests
import json

#call LLM using Ollama api
def call_llm(user_input, relevant_document, full_response: list, llm: str):
    url = 'http://localhost:11434/api/generate'
    data = {
        "model": llm,
        "prompt": prompt.build_prompt(query=user_input, context_str=relevant_document)
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(url, data=json.dumps(data), headers=headers, stream=True)
    try:
        count = 0
        for line in response.iter_lines():
            # filter out keep-alive new lines
            # count += 1
            # if count % 5== 0:
            #     print(decoded_line['response']) # print every fifth token
            if line:
                decoded_line = json.loads(line.decode('utf-8'))
                full_response.append(decoded_line['response'])
    finally:
        response.close()
    return ''.join(full_response)
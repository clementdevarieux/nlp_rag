def build_prompt(query, context_str):
    prompt = f"""<|im_start|>system
    You reply to the user's request using only context information.
    Context information to answer "{query}" is below
    ------
    Context:
    {context_str}
    ------
    You are a helpful assistant for rust developper. You reply to developper questions about specific documentation.
    <|im_end|>
    <|im_start|>user
    {query}
    <|im_reend|>
    """
    return prompt


def build_prompt_question_generation(query):
    prompt = f"""<|im_start|>system
    you will be given a text, with this text you will have to generate one question that could be answered 
    by the text given
    ------
    you are a question generator assistant
    <|im_end|>
    <|im_start|>text
    {query}
    <|im_reend|>
    """
    return prompt


def build_prompt_question_hyde(query):
    prompt = f"""
    You are an advanced AI model tasked with answering the following user query using the Hypothetical Document Embeddings (HyDE) method. Your goal is to generate hypothetical documents that could contain the answer to the query and then use these documents to retrieve the most relevant information.

**User Query:**
{query}

**Instructions:**
1. Generate three hypothetical documents that could potentially answer the user's query. Each document should be a short paragraph that provides contextually relevant information.
2. For each hypothetical document, extract the key points that directly address the user's query.
3. Compile the key points from all hypothetical documents into a coherent and concise answer.
4. Ensure that all examples of code or text are written in English.

**Hypothetical Documents:**

1. **Document 1:**
   [Insert a hypothetical document that could answer the query]

2. **Document 2:**
   [Insert a hypothetical document that could answer the query]

3. **Document 3:**
   [Insert a hypothetical document that could answer the query]

**Extracted Key Points:**

- From Document 1: [Key points that address the query]
- From Document 2: [Key points that address the query]
- From Document 3: [Key points that address the query]

**Compiled Answer:**
[Provide a coherent and concise answer to the user's query based on the extracted key points]

**Example:**

**User Query:**
"What is the capital of France?"

**Hypothetical Documents:**

1. **Document 1:**
   "France is a country in Europe known for its rich history and culture. The capital of France is Paris, which is also known as the City of Light."

2. **Document 2:**
   "Paris, the capital city of France, is famous for its iconic landmarks such as the Eiffel Tower and the Louvre Museum."

3. **Document 3:**
   "France has a long history with Paris as its capital. The city is a major global center for art, fashion, gastronomy, and culture."

**Extracted Key Points:**

- From Document 1: The capital of France is Paris.
- From Document 2: Paris is the capital city of France.
- From Document 3: Paris is the capital of France.

**Compiled Answer:**
The capital of France is Paris.
    """
    return prompt


def build_smoll_messages(query, context_str):
    messages = [
        {"role": "system", "content": f"""You reply to the user's request using only context information.
Context information to answer "{query}" is below
------
Context:
{context_str}
------
You are a helpful assistant for a developer. You reply to developer  about the documentation question they have.
"""},
        {"role": "user", "content": query},
    ]

    return messages

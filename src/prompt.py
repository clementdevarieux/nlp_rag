
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

import ollama


def generate_answer(query: str, chunks: list) -> str:
    """
    Generates answer by the answers and finded chunks.
    
    Args:
    - query: text of the question
    - chunks: chunks of the question

    Returns:
    - answer
    """

    context = "\n\n---\n\n".join([chunk["text"] for chunk in chunks])        # making context from chunks
                                                                             # making prompt for model
    prompt = f"""
    Ты — ассистент, который отвечает на вопросы, ИСПОЛЬЗУЯ ТОЛЬКО ПРЕДОСТАВЛЕННЫЕ ФРАГМЕНТЫ ТЕКСТА.
    Если ответа на вопрос нет в этих фрагментах — НЕ ПРИДУМЫВАЙ НИЧЕГО ОТ СЕБЯ,а напиши:
    "Я не нашел информации по этому вопросу в доступных источниках."

    Фрагменты текста:
    {context}

    Вопрос: {query}

    Ответ:
    """

    response = ollama.chat(
        model="qwen:4b",                                                     # using model with 4 billion parameters
        messages=[{"role": "user", "content": prompt}],
        options={"temperature": 0.3}                                         # more facts, less creativity
    )
    
    return response["message"]["content"]

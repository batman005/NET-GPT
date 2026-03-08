from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt

llm = get_llm()


def detect_intent(question: str):

    prompt_template = load_prompt("intent_prompt.txt")

    prompt = prompt_template.format(
        question=question
    )

    response = llm.invoke(prompt)

    return response.strip()
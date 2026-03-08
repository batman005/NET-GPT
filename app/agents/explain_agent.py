from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt

llm = get_llm()


def explain_query(sql: str):

    prompt_template = load_prompt("explain_prompt.txt")

    prompt = prompt_template.format(
        sql=sql
    )

    response = llm.invoke(prompt)

    return response.strip()
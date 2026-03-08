from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt

llm = get_llm()


def select_columns(question: str, tables: str, schema: str):

    prompt_template = load_prompt("column_prompt.txt")

    prompt = prompt_template.format(
        question=question,
        tables=tables,
        schema=schema
    )

    response = llm.invoke(prompt)

    return response.strip()
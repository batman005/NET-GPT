from app.llm.ollama_client import get_llm
from app.utils.prompt_loader import load_prompt

llm = get_llm()


def generate_sql(question: str, tables: str, columns: str, schema: str):

    prompt_template = load_prompt("sql_prompt.txt")

    prompt = prompt_template.format(
        question=question,
        tables=tables,
        columns=columns,
        schema=schema
    )

    response = llm.invoke(prompt)

    return response.strip()
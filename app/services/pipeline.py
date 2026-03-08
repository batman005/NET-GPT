from app.agents.intent_agent import detect_intent
from app.agents.table_agent import select_tables
from app.agents.column_agent import select_columns
from app.agents.sql_agent import generate_sql
from app.agents.explain_agent import explain_query

from app.db.mysql_client import execute_query
from app.db.schema_loader import load_schema
from app.utils.schema_formatter import format_schema
from app.utils.sql_extractor import extract_sql

def run_pipeline(question: str):

    # 1️⃣ Load schema
    raw_schema = load_schema()
    schema = format_schema(raw_schema)

    print("\n---- Loaded Schema ----")
    print(schema)

    # 2️⃣ Intent detection
    intent = detect_intent(question)

    print("\n---- Intent ----")
    print(intent)

    # 3️⃣ Table selection
    tables = select_tables(question, schema)

    print("\n---- Tables ----")
    print(tables)

    # 4️⃣ Column selection
    columns = select_columns(question, tables, schema)

    print("\n---- Columns ----")
    print(columns)

    # 5️⃣ SQL generation
    raw_sql = generate_sql(question, tables, columns, schema)

    sql = extract_sql(raw_sql)

    print("\n---- Generated SQL ----")
    print(sql)

    # 6️⃣ SQL explanation
    explanation = explain_query(sql)

    print("\n---- Explanation ----")
    print(explanation)

    # 7️⃣ Execute query
    try:
        result = execute_query(sql)
    except Exception as e:
        result = {"error": str(e)}

    # 8️⃣ Final response
    return {
        "question": question,
        "intent": intent,
        "tables": tables,
        "columns": columns,
        "sql": sql,
        "explanation": explanation,
        "result": result
    }
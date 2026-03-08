def format_schema(schema):

    formatted = ""

    for table, columns in schema.items():

        cols = ", ".join(columns)

        formatted += f"{table}({cols})\n"

    return formatted
import re

def extract_sql(text: str) -> str:

    # remove markdown blocks
    text = re.sub(r"```sql", "", text, flags=re.IGNORECASE)
    text = re.sub(r"```", "", text)

    # find SELECT query
    match = re.search(r"(SELECT .*?;)", text, re.IGNORECASE | re.DOTALL)

    if match:
        return match.group(1).strip()

    # fallback: return cleaned text
    return text.strip()
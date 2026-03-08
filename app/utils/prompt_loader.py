from pathlib import Path


def load_prompt(filename: str):

    base_path = Path(__file__).resolve().parent.parent
    prompt_path = base_path / "prompts" / filename

    with open(prompt_path, "r") as f:
        return f.read()
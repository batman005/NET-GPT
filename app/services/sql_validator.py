def validate_response(response):

    text = str(response).lower()

    if "error" in text:
        return False

    if len(text.strip()) == 0:
        return False

    return True
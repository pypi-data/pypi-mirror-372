def clean_dict(data: dict) -> dict:
    cleaned = {}
    for k, v in data.items():
        if isinstance(v, dict):
            nested = clean_dict(v)
            if nested:
                cleaned[k] = nested
        elif v is not None:
            cleaned[k] = v
    return cleaned

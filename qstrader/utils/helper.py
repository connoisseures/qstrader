def normalize_value(value_dict: dict) -> dict:
    total = sum(list(value_dict.values()))
    return {k: v / total for k, v in value_dict.items()}

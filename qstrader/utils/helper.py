import yaml
import json

def normalize_value(value_dict: dict) -> dict:
    total = sum(list(value_dict.values()))
    return {k: v / total for k, v in value_dict.items()}

def load_json_yaml(file_path):
    if isinstance(file_path, str):
        if file_path.endswith(".yaml"):
            # Handle path to YAML
            with open(file_path, "r") as f:
                return yaml.safe_load(f)
        elif file_path.endswith(".json"):
            # Handle path to JSON
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            # Handle JSON blob
            return json.loads(file_path)
    else:
        return file_path



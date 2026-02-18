import json
from pathlib import Path

def save_json(data, filepath):
    Path(filepath).write_text(json.dumps(data, indent=2))

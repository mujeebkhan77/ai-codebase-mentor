import json
from pathlib import Path


def get_repository_manifest(manifest_path: str = "repository_manifest.json"):
    """
    Load and return the repository-level manifest metadata generated during indexing.

    Use this tool when answering architectural or repository-level overview questions:
    - What is the structure of this repository?
    - What programming languages and entry points exist?
    - What are the main modules and configuration files?
    """
    path = Path(manifest_path)
    if not path.exists():
        return json.dumps({
            "error": f"Repository manifest '{manifest_path}' not found. Run repository indexing first."
        })

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return json.dumps(data, indent=2)
    except Exception as e:
        return json.dumps({"error": f"Failed to read manifest: {str(e)}"})

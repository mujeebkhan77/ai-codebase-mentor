import json
from pathlib import Path

from indexing.chunking import chunk_python_file
from indexing.symbols import extract_symbols
from indexing.relationships import (
    extract_relationships,
    resolve_relationships
)
from indexing.manifest import generate_manifest, save_manifest



def index_repository(repository_path):

    all_chunks = []
    all_symbols = []
    all_relationships = []

    repository_path = Path(repository_path)

    python_files = list(repository_path.rglob("*.py"))

    print(f"Found {len(python_files)} Python files.\n")

    for file_path in python_files:

        # Create code chunks
        chunks = chunk_python_file(file_path)
        all_chunks.extend(chunks)

        # Extract symbols
        symbols = extract_symbols(file_path)
        all_symbols.extend(symbols)

        # Extract relationships
        relationships = extract_relationships(file_path)
        all_relationships.extend(relationships)

    print(f"Created {len(all_chunks)} chunks.")
    print(f"Found {len(all_symbols)} symbols.")
    print(f"Found {len(all_relationships)} raw relationships.")

    # ---------------------------------------------------------
    # Save symbol index
    # ---------------------------------------------------------

    symbol_index_path = Path("symbol_index.json")

    with open(
        symbol_index_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            all_symbols,
            file,
            indent=2
        )

    print(
        f"Symbol index saved to: "
        f"{symbol_index_path}"
    )

    # ---------------------------------------------------------
    # Resolve relationships against symbols
    # ---------------------------------------------------------

    resolved_relationships = resolve_relationships(
        all_relationships,
        all_symbols
    )

    print(
        f"Resolved {len(resolved_relationships)} relationships."
    )

    # ---------------------------------------------------------
    # Save relationship index
    # ---------------------------------------------------------

    relationship_index_path = Path(
        "relationship_index.json"
    )

    with open(
        relationship_index_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            resolved_relationships,
            file,
            indent=2
        )

    print(
        f"Relationship index saved to: "
        f"{relationship_index_path}"
    )

    # ---------------------------------------------------------
    # Generate and save repository manifest
    # ---------------------------------------------------------
    manifest = generate_manifest(
        repository_path,
        all_symbols,
        resolved_relationships
    )
    save_manifest(manifest, "repository_manifest.json")
    print("Repository manifest saved to: repository_manifest.json")

    return all_chunks
import os
import json
import numpy as np
from sentence_transformers import SentenceTransformer
from utils.paths import safe_filename

# Paths
INPUT_DIR = "data/processed/"
OUTPUT_DIR = "data/embeddings/"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


def main() -> None:
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Load embedding model
    model = SentenceTransformer(MODEL_NAME)

    # Collect descriptions and corresponding output file paths
    descriptions: list[str] = []
    brand_names: list[str] = []
    embed_paths: list[str] = []

    for file_name in sorted(os.listdir(INPUT_DIR)):
        if not file_name.endswith(".json"):
            continue

        # Skip the master knowledge base file to avoid duplicate work
        if file_name == "brands_knowledge_base.json":
            continue

        file_path = os.path.join(INPUT_DIR, file_name)

        # Load product description
        with open(file_path, "r", encoding="utf-8") as f:
            product_data = json.load(f)

        description = (product_data or {}).get("description", "")
        brand_name = (product_data or {}).get("brand", file_name.replace(".json", ""))

        if description and description.strip():
            descriptions.append(description)
            brand_names.append(brand_name)
            embed_paths.append(os.path.join(OUTPUT_DIR, f"{safe_filename(brand_name)}.npy"))

    # Encode in batch for efficiency
    if descriptions:
        model_kwargs = {
            "batch_size": 32,
            "show_progress_bar": True,
        }
        embeddings = model.encode(descriptions, **model_kwargs)

        # Save each embedding
        for emb, brand_name, path in zip(embeddings, brand_names, embed_paths):
            np.save(path, emb)
            print(f"Saved embedding for {brand_name}")
    else:
        print("No descriptions found to embed.")


if __name__ == "__main__":
    main()

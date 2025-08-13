import os
import json
from typing import List
from chromadb import PersistentClient
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.core import Document, VectorStoreIndex, StorageContext
from llama_index.embeddings.huggingface import HuggingFaceEmbedding

PROCESSED_DIR = "data/processed/"
CHROMA_DIR = "data/chroma"
CHROMA_COLLECTION = "brands_kb"


def flatten_entry(entry: dict) -> str:
    brand = entry.get("brand", "Unknown")
    category = entry.get("category", "Unknown")
    description = entry.get("description", "")
    tagline = entry.get("tagline", "N/A")
    fun_fact = entry.get("fun_fact", "N/A")
    flavor_profile = entry.get("flavor_profile", "N/A")
    release_date = entry.get("release_date", "N/A")
    source_url = entry.get("source_url", "")

    text = (
        f"Brand: {brand}\n"
        f"Category: {category}\n"
        f"Description: {description}\n"
        f"Tagline: {tagline}\n"
        f"Fun Fact: {fun_fact}\n"
        f"Flavor Profile: {flavor_profile}\n"
        f"Release Date: {release_date}\n"
        f"Source: {source_url}\n"
    )
    return text


def load_flattened_documents(processed_dir: str) -> List[Document]:
    documents: List[Document] = []
    for file_name in sorted(os.listdir(processed_dir)):
        if not file_name.endswith(".json"):
            continue
        file_path = os.path.join(processed_dir, file_name)
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        # Master KB (list) or individual file (dict)
        if isinstance(data, list):
            for entry in data:
                text = flatten_entry(entry)
                metadata = {
                    "brand": entry.get("brand"),
                    "category": entry.get("category"),
                    "source_url": entry.get("source_url"),
                    "source_file": file_name,
                }
                documents.append(Document(text=text, metadata=metadata))
        elif isinstance(data, dict):
            text = flatten_entry(data)
            metadata = {
                "brand": data.get("brand"),
                "category": data.get("category"),
                "source_url": data.get("source_url"),
                "source_file": file_name,
            }
            documents.append(Document(text=text, metadata=metadata))
    return documents


def main():
    os.makedirs(CHROMA_DIR, exist_ok=True)

    embed_model = HuggingFaceEmbedding(model_name="sentence-transformers/all-MiniLM-L6-v2")

    documents = load_flattened_documents(PROCESSED_DIR)
    if not documents:
        print("No documents found to index.")
        return

    # Initialize Chroma persistent client and collection
    client = PersistentClient(path=CHROMA_DIR)
    collection = client.get_or_create_collection(CHROMA_COLLECTION)

    # Wrap in LlamaIndex vector store and storage context
    vector_store = ChromaVectorStore(chroma_collection=collection)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    # Build index backed by Chroma
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        embed_model=embed_model,
    )

    print(f"Index built and persisted to Chroma at {CHROMA_DIR} in collection '{CHROMA_COLLECTION}'.")


if __name__ == "__main__":
    main()

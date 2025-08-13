import os
import sys

# Ensure project root is on sys.path when running as a script
PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from scripts.fetch_data import fetch_all_brands
from scripts.process_data import process_from_raw_dir


def run():
    print("Starting brand knowledge base pipeline...")

    # 1) Fetch and save raw HTML + metadata sidecars
    fetched = fetch_all_brands()
    print(f"Fetched {len(fetched)} brand pages.")

    # 2) Process by parsing saved HTML (no refetch)
    entries = process_from_raw_dir()
    print(f"Processed {len(entries)} entries.")

    # 3) Generate embeddings
    from scripts import generate_embeddings as gen
    gen.main()

    # 4) Build index (Chroma backend)
    from scripts import build_index as build
    build.main()

    print("Pipeline finished.")


if __name__ == "__main__":
    run()

import re
import os
import json
from typing import Iterable, List, Optional, Tuple
from utils.constants import PROCESSED_DIR, BRANDS, RAW_DIR
from utils.json_formatter import format_brand_entry
from scripts.error_handler import log_error
from utils.wiki_api import fetch_page_html
from utils.paths import safe_filename

os.makedirs(PROCESSED_DIR, exist_ok=True)

# Tuple shape from fetch_all_brands: (brand, category, used_title, html, url)
FetchedTuple = Tuple[str, str, Optional[str], Optional[str], Optional[str]]

def process_single(brand_raw: str, category: str, html: Optional[str] = None, used_title: Optional[str] = None, url: Optional[str] = None):
    try:
        # If html not supplied, fetch it (backwards compatible)
        if html is None or used_title is None or url is None:
            used_title, html, url = fetch_page_html(brand_raw)
        if not html:
            return None
        entry = format_brand_entry(brand_raw, category, used_title, html, url)
        filename = safe_filename(used_title) + ".json"
        path = os.path.join(PROCESSED_DIR, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(entry, f, ensure_ascii=False, indent=2)
        return entry
    except Exception as e:
        log_error(f"processing {brand_raw}", e)
        return None

def process_from_fetched(fetched: Iterable[FetchedTuple]) -> List[dict]:
    """Process entries from pre-fetched data to avoid refetching.
    fetched tuples are (brand, category, used_title, html, url)
    """
    all_entries: List[dict] = []
    for brand_raw, category, used_title, html, url in fetched:
        print(f"Processing {brand_raw} ...")
        entry = process_single(brand_raw, category, html=html, used_title=used_title, url=url)
        if entry:
            all_entries.append(entry)
        else:
            print(f"  -> Failed to process {brand_raw}")
    master_path = os.path.join(PROCESSED_DIR, "brands_knowledge_base.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f"Saved master KB to {master_path}")
    return all_entries

def process_from_raw_dir(raw_dir: str = RAW_DIR, processed_meta_dir: str = PROCESSED_DIR) -> List[dict]:
    """Process all brands by parsing saved HTML in raw_dir and metadata sidecars in processed_meta_dir."""
    all_entries: List[dict] = []
    # iterate over meta files in processed dir
    for file_name in sorted(os.listdir(processed_meta_dir)):
        if not file_name.endswith(".meta.json"):
            continue
        meta_path = os.path.join(processed_meta_dir, file_name)
        with open(meta_path, "r", encoding="utf-8") as f:
            meta = json.load(f)
        brand_raw = meta.get("brand_raw")
        category = meta.get("category")
        used_title = meta.get("used_title")
        url = meta.get("source_url")
        html_path = os.path.join(raw_dir, file_name.replace(".meta.json", ".html"))
        if not os.path.exists(html_path):
            print(f"[WARN] Missing HTML for {brand_raw} at {html_path}")
            continue
        with open(html_path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"Processing {brand_raw} from saved HTML ...")
        entry = process_single(brand_raw, category, html=html, used_title=used_title, url=url)
        if entry:
            all_entries.append(entry)
        else:
            print(f"  -> Failed to process {brand_raw}")
    master_path = os.path.join(PROCESSED_DIR, "brands_knowledge_base.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f"Saved master KB to {master_path}")
    return all_entries

def process_all():
    all_entries = []
    for category, brands in BRANDS.items():
        for b in brands:
            print(f"Processing {b} ...")
            entry = process_single(b, category)
            if entry:
                all_entries.append(entry)
            else:
                print(f"  -> Failed to process {b}")
    master_path = os.path.join(PROCESSED_DIR, "brands_knowledge_base.json")
    with open(master_path, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f"Saved master KB to {master_path}")
    return all_entries

if __name__ == "__main__":
    process_all()

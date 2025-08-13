import os
import time
import json
from utils.constants import RAW_DIR, PROCESSED_DIR, BRANDS
from utils.wiki_api import fetch_page_html
from scripts.error_handler import log_missing, log_error
from utils.paths import safe_filename

os.makedirs(RAW_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

def fetch_all_brands(output_raw_dir=RAW_DIR, pause=1.0):
    results = []
    for category, brand_list in BRANDS.items():
        for brand in brand_list:
            try:
                used_title, html, url = fetch_page_html(brand)
                if not html:
                    log_missing(brand, reason="page_not_found")
                    print(f"[MISSING] {brand}")
                    results.append((brand, category, None, None, None))
                else:
                    print(f"[OK] {brand} -> {used_title}")
                    os.makedirs(output_raw_dir, exist_ok=True)
                    base = safe_filename(brand)
                    html_path = os.path.join(output_raw_dir, f"{base}.html")
                    meta_path = os.path.join(PROCESSED_DIR, f"{base}.meta.json")

                    # Save raw HTML
                    with open(html_path, "w", encoding="utf-8") as f:
                        f.write(html)

                    # Save sidecar metadata for downstream processing
                    with open(meta_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "brand_raw": brand,
                            "category": category,
                            "used_title": used_title,
                            "source_url": url
                        }, f, ensure_ascii=False, indent=2)

                    results.append((brand, category, used_title, html, url))
                time.sleep(pause)
            except Exception as e:
                log_error(f"fetching {brand}", e)
                results.append((brand, category, None, None, None))
    return results

if __name__ == "__main__":
    fetch_all_brands()

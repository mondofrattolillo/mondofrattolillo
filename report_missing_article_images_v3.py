#!/usr/bin/env python3
import json
from pathlib import Path

SRC = Path("missing_article_images_report_v2.json")

def main():
    data = json.loads(SRC.read_text(encoding="utf-8"))
    articles = data.get("articles", [])

    rows = []
    for article in articles:
        high = article.get("high_confidence", [])
        fig_count = sum(1 for x in high if x["type"] == "figcaption_without_image")
        italic_count = sum(1 for x in high if x["type"] == "italic_caption_without_image")
        total = len(high)
        rows.append({
            "slug": article["slug"],
            "total": total,
            "figcaption": fig_count,
            "italic": italic_count,
            "file": article["file"],
        })

    rows.sort(key=lambda x: (-x["figcaption"], -x["total"], x["slug"]))

    print(f"Articoli segnalati: {len(rows)}")
    print()
    print(f"{'TOT':>4}  {'FIG':>4}  {'ITA':>4}  SLUG")
    print("-" * 80)
    for r in rows:
        print(f"{r['total']:>4}  {r['figcaption']:>4}  {r['italic']:>4}  {r['slug']}")

if __name__ == "__main__":
    main()

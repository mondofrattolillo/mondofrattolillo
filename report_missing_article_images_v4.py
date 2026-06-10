#!/usr/bin/env python3
import json
from pathlib import Path

REPORT = Path("missing_article_images_report_v2.json")
OUT = Path("missing_article_images_audit_v4.json")

def main():
    print("Start audit v4")

    if not REPORT.exists():
        print(f"ERRORE: file non trovato -> {REPORT}")
        return

    data = json.loads(REPORT.read_text(encoding="utf-8"))
    articles = data.get("articles", [])
    print(f"Articoli nel report v2: {len(articles)}")

    audited = []

    for article in articles:
        high = article.get("high_confidence", [])
        figs = [x for x in high if x.get("type") == "figcaption_without_image"]

        if not figs:
            continue

        audited.append({
            "slug": article.get("slug"),
            "file": article.get("file"),
            "figcaption_without_image_count": len(figs),
            "missing_figcaptions": figs
        })

    audited.sort(key=lambda x: (-x["figcaption_without_image_count"], x["slug"]))

    out = {
        "articles_audited": len(audited),
        "articles": audited
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Articoli auditati: {len(audited)}")
    print(f"File generato: {OUT}")
    print()

    for article in audited[:10]:
        print(f"- {article['slug']}: {article['figcaption_without_image_count']} figcaption senza immagine")

if __name__ == "__main__":
    main()

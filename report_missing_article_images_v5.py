#!/usr/bin/env python3
import json
from pathlib import Path

AUDIT_V4 = Path("missing_article_images_audit_v4.json")
PUBLIC = Path.home() / "Documents/mondofrattolillo-site/public/blog-images"
OUT = Path("missing_article_images_inventory_v5.json")

IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}

def main():
    if not AUDIT_V4.exists():
        print(f"ERRORE: file non trovato -> {AUDIT_V4}")
        return

    data = json.loads(AUDIT_V4.read_text(encoding="utf-8"))
    articles = data.get("articles", [])

    inventory = []

    for article in articles:
        slug = article["slug"]
        missing_count = article["figcaption_without_image_count"]
        img_dir = PUBLIC / slug

        image_files = []
        if img_dir.exists() and img_dir.is_dir():
            image_files = sorted(
                [p.name for p in img_dir.iterdir() if p.suffix.lower() in IMG_EXTS]
            )

        inventory.append({
            "slug": slug,
            "missing_figcaptions": missing_count,
            "image_dir_exists": img_dir.exists(),
            "image_dir": str(img_dir),
            "image_file_count": len(image_files),
            "image_files": image_files,
            "difference_images_minus_figcaptions": len(image_files) - missing_count
        })

    inventory.sort(
        key=lambda x: (
            not x["image_dir_exists"],
            abs(x["difference_images_minus_figcaptions"]),
            -x["image_file_count"],
            x["slug"]
        )
    )

    out = {
        "articles_inventory": len(inventory),
        "articles": inventory
    }

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Articoli inventariati: {len(inventory)}")
    print(f"File generato: {OUT}")
    print()
    print(f"{'MISS':>4} {'IMG':>4} {'DIFF':>5}  {'DIR':>8}  SLUG")
    print("-" * 90)

    for item in inventory:
        status = "OK" if item["image_dir_exists"] else "MANCANTE"
        print(
            f"{item['missing_figcaptions']:>4} "
            f"{item['image_file_count']:>4} "
            f"{item['difference_images_minus_figcaptions']:>5}  "
            f"{status:>8}  "
            f"{item['slug']}"
        )

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import re
import unicodedata
from difflib import SequenceMatcher
from pathlib import Path

AUDIT_V4 = Path("missing_article_images_audit_v4.json")
PUBLIC = Path.home() / "Documents/mondofrattolillo-site/public/blog-images"
OUT = Path("missing_article_images_matches_v6.json")

TARGET_SLUGS = {
    "ginevra-capitale-internazionale",
    "7-febbraio-2018-la-neve-a-parigi",
    "cern-dove-nacque-il-web",
    "italia-francia-cosi-uguali-cosi-diverse-aerosol-vs-kine",
    "parigi-a-novembre",
}

IMG_EXTS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif"}

STOPWORDS = {
    "di", "de", "del", "della", "dell", "des", "du", "la", "le", "les", "il", "lo", "i", "gli",
    "un", "una", "photo", "foto", "image", "immagine", "images", "sur", "par", "by", "con",
    "nel", "nella", "a", "au", "et", "e", "the", "of", "da", "per", "in", "on", "cc", "copyright",
    "2018", "2019", "2020"
}

def normalize(text):
    text = unicodedata.normalize("NFKD", text)
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'[^a-z0-9]+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def tokenize(text):
    return [t for t in normalize(text).split() if t not in STOPWORDS and len(t) > 2]

def similarity(a, b):
    return SequenceMatcher(None, normalize(a), normalize(b)).ratio()

def score_candidate(caption, filename):
    stem = Path(filename).stem
    cap_tokens = set(tokenize(caption))
    file_tokens = set(tokenize(stem))

    overlap = sorted(cap_tokens & file_tokens)
    ratio = similarity(caption, stem)

    token_score = len(overlap) * 20
    ratio_score = ratio * 100
    score = round(token_score + ratio_score, 2)

    return {
        "filename": filename,
        "score": score,
        "overlap_tokens": overlap,
        "similarity_ratio": round(ratio, 3)
    }

def main():
    if not AUDIT_V4.exists():
        print(f"ERRORE: file non trovato -> {AUDIT_V4}")
        return

    data = json.loads(AUDIT_V4.read_text(encoding="utf-8"))
    articles = data.get("articles", [])
    results = []

    for article in articles:
        slug = article["slug"]
        if slug not in TARGET_SLUGS:
            continue

        img_dir = PUBLIC / slug
        image_files = []
        if img_dir.exists() and img_dir.is_dir():
            image_files = sorted(
                [p.name for p in img_dir.iterdir() if p.suffix.lower() in IMG_EXTS]
            )

        caption_matches = []
        for item in article.get("missing_figcaptions", []):
            caption = item["caption"]
            scored = [score_candidate(caption, fname) for fname in image_files]
            scored.sort(key=lambda x: (-x["score"], x["filename"]))

            caption_matches.append({
                "line": item["line"],
                "caption": caption,
                "top_candidates": scored[:3]
            })

        results.append({
            "slug": slug,
            "image_dir": str(img_dir),
            "image_file_count": len(image_files),
            "image_files": image_files,
            "matches": caption_matches
        })

    OUT.write_text(
        json.dumps({"articles": results}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )

    print(f"File generato: {OUT}")
    print()

    for article in results:
        print(f"## {article['slug']}")
        print(f"File immagini: {article['image_file_count']}")
        for match in article["matches"][:10]:
            print(f"  - Linea {match['line']}: {match['caption']}")
            for cand in match["top_candidates"]:
                overlap = ", ".join(cand["overlap_tokens"]) if cand["overlap_tokens"] else "-"
                print(
                    f"    -> {cand['filename']} | score={cand['score']} | "
                    f"ratio={cand['similarity_ratio']} | overlap={overlap}"
                )
        print()

if __name__ == "__main__":
    main()

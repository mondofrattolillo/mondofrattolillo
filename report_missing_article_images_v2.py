#!/usr/bin/env python3
import re
import json
from pathlib import Path

ROOT = Path.home() / "Documents/mondofrattolillo-site/src/content/blog"

IMG_RE = re.compile(r'^\s*!\[[^\]]*\]\(([^)]+)\)\s*$')
EMPTY_RE = re.compile(r'^\s*$')
ITALIC_LINE_RE = re.compile(r'^\s*_(.+?)_\s*$')
FIGCAPTION_BLOCK_RE = re.compile(r'<figcaption>(.*?)</figcaption>', re.DOTALL | re.IGNORECASE)

EXCLUDE_PATTERNS = [
    r'^\s*$',
    r'^\s*trad\.',
    r'^\s*di\s+[A-ZÀ-ÿ]',
    r'^\s*photo\b',
    r'^\s*foto\b',
    r'^\s*video\b',
    r'creativecommons',
    r'cc by',
    r'licensed under',
    r'wikimedia',
    r'pexels',
    r'flickr',
    r'getty images',
    r'ap photo',
    r'ansa',
    r'la presse',
    r'email',
    r'per saperne di più',
    r'informazioni tratte',
]
EXCLUDE_RE = re.compile("|".join(EXCLUDE_PATTERNS), re.IGNORECASE)

VISUAL_HINTS = [
    r'champs', r'tour eiffel', r'metro', r'montmartre', r'parc', r'villa',
    r'battaglia', r'truppe', r'mentone', r'castello', r'camera', r'cappella',
    r'affresco', r'palais', r'new york', r'manhattan', r'wall street',
    r'beirut', r'cern', r'globe', r'muse', r'op[eé]ra', r'pigalle',
    r'issy', r'bir-hakeim', r'les pinettes', r'colle', r'confine'
]
VISUAL_HINTS_RE = re.compile("|".join(VISUAL_HINTS), re.IGNORECASE)

LONG_TEXT_THRESHOLD = 220

def previous_nonempty(lines, idx):
    j = idx - 1
    while j >= 0 and EMPTY_RE.match(lines[j]):
        j -= 1
    return j

def next_nonempty(lines, idx):
    j = idx + 1
    while j < len(lines) and EMPTY_RE.match(lines[j]):
        j += 1
    return j

def has_markdown_image_immediately_before(lines, idx):
    j = previous_nonempty(lines, idx)
    if j < 0:
        return False, None
    m = IMG_RE.match(lines[j])
    return bool(m), (m.group(1) if m else None)

def looks_like_false_positive(caption):
    text = re.sub(r'\s+', ' ', caption).strip().lower()
    if EXCLUDE_RE.search(text):
        return True
    if len(text) > LONG_TEXT_THRESHOLD and not VISUAL_HINTS_RE.search(text):
        return True
    return False

def classify_italic_caption(lines, idx, caption):
    text = re.sub(r'\s+', ' ', caption).strip()
    if looks_like_false_positive(text):
        return None

    prev_i = previous_nonempty(lines, idx)
    next_i = next_nonempty(lines, idx)

    prev_line = lines[prev_i].strip() if prev_i >= 0 else ""
    next_line = lines[next_i].strip() if next_i < len(lines) else ""

    isolated = EMPTY_RE.match(lines[idx - 1]) if idx - 1 >= 0 else True
    isolated = isolated and (EMPTY_RE.match(lines[idx + 1]) if idx + 1 < len(lines) else True)

    high_conf = (
        bool(VISUAL_HINTS_RE.search(text))
        or prev_line == "<figcaption>"
        or next_line == "</figcaption>"
        or (len(text) < 120 and isolated)
    )

    return "high_confidence" if high_conf else "needs_review"

def scan_file(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    high_confidence = []
    needs_review = []

    for i, line in enumerate(lines):
        m = ITALIC_LINE_RE.match(line)
        if not m:
            continue
        ok, img = has_markdown_image_immediately_before(lines, i)
        if ok:
            continue

        caption = m.group(1).strip()
        category = classify_italic_caption(lines, i, caption)
        if not category:
            continue

        item = {
            "line": i + 1,
            "type": "italic_caption_without_image",
            "caption": caption,
            "preceding_image": img,
        }
        if category == "high_confidence":
            high_confidence.append(item)
        else:
            needs_review.append(item)

    for m in FIGCAPTION_BLOCK_RE.finditer(text):
        start_pos = m.start()
        line_no = text[:start_pos].count("\n") + 1
        caption_text = re.sub(r'\s+', ' ', m.group(1)).strip()
        ok, img = has_markdown_image_immediately_before(lines, line_no - 1)
        if ok:
            continue
        if looks_like_false_positive(caption_text):
            continue

        high_confidence.append({
            "line": line_no,
            "type": "figcaption_without_image",
            "caption": caption_text,
            "preceding_image": img,
        })

    return high_confidence, needs_review

def main():
    if not ROOT.exists():
        print(json.dumps({"error": f"Path not found: {ROOT}"}, ensure_ascii=False, indent=2))
        return

    results = []
    total_high = 0
    total_review = 0

    for md in sorted(ROOT.rglob("index.md")):
        high, review = scan_file(md)
        if high or review:
            rel = md.relative_to(ROOT)
            slug = rel.parent.as_posix()
            results.append({
                "slug": slug,
                "file": str(md),
                "high_confidence_count": len(high),
                "needs_review_count": len(review),
                "high_confidence": high,
                "needs_review": review,
            })
            total_high += len(high)
            total_review += len(review)

    report = {
        "root": str(ROOT),
        "articles_flagged": len(results),
        "high_confidence_total": total_high,
        "needs_review_total": total_review,
        "articles": results,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import re
import json
from pathlib import Path

ROOT = Path.home() / "Documents/mondofrattolillo-site/src/content/blog"

IMG_RE = re.compile(r'^\s*!\[[^\]]*\]\(([^)]+)\)\s*$')
ITALIC_CAPTION_RE = re.compile(r'^\s*_[^_].*?_\s*$')
FIGCAPTION_BLOCK_RE = re.compile(r'<figcaption>(.*?)</figcaption>', re.DOTALL | re.IGNORECASE)
EMPTY_RE = re.compile(r'^\s*$')

def previous_nonempty(lines, idx):
    j = idx - 1
    while j >= 0 and EMPTY_RE.match(lines[j]):
        j -= 1
    return j

def has_markdown_image_immediately_before(lines, idx):
    j = previous_nonempty(lines, idx)
    if j < 0:
        return False, None
    m = IMG_RE.match(lines[j])
    return bool(m), (m.group(1) if m else None)

def scan_file(path: Path):
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    issues = []

    for i, line in enumerate(lines):
        if ITALIC_CAPTION_RE.match(line):
            ok, img = has_markdown_image_immediately_before(lines, i)
            if not ok:
                issues.append({
                    "line": i + 1,
                    "type": "italic_caption_without_image",
                    "caption": line.strip(),
                    "preceding_image": img,
                })

    for m in FIGCAPTION_BLOCK_RE.finditer(text):
        start_pos = m.start()
        line_no = text[:start_pos].count("\n") + 1
        caption_text = re.sub(r'\s+', ' ', m.group(1)).strip()
        ok, img = has_markdown_image_immediately_before(lines, line_no - 1)
        if not ok:
            issues.append({
                "line": line_no,
                "type": "figcaption_without_image",
                "caption": caption_text,
                "preceding_image": img,
            })

    return issues

def main():
    if not ROOT.exists():
        print(json.dumps({"error": f"Path not found: {ROOT}"}, ensure_ascii=False, indent=2))
        return

    results = []
    total_issues = 0

    for md in sorted(ROOT.rglob("index.md")):
        issues = scan_file(md)
        if issues:
            rel = md.relative_to(ROOT)
            slug = rel.parent.as_posix()
            results.append({
                "slug": slug,
                "file": str(md),
                "issue_count": len(issues),
                "issues": issues,
            })
            total_issues += len(issues)

    report = {
        "root": str(ROOT),
        "articles_with_issues": len(results),
        "total_issues": total_issues,
        "articles": results,
    }

    print(json.dumps(report, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()

"""Bundles docs/*.md into docs/assets/content.js so index.html works from file:// (no fetch of local files).

Run after editing any page: python3 docs/build.py
"""
import json
import re
from pathlib import Path

DOCS = Path(__file__).resolve().parent


def title_of(text: str, fallback: str) -> str:
    m = re.search(r"^# (.+)$", text, re.M)
    return m.group(1).strip() if m else fallback


def main() -> None:
    pages = []
    for f in sorted(DOCS.glob("*.md"), key=lambda p: (p.name != "README.md", p.name)):
        text = f.read_text(encoding="utf-8")
        pages.append({"id": f.stem, "file": f.name, "title": title_of(text, f.stem), "md": text})
    out = DOCS / "assets" / "content.js"
    out.write_text("window.T0_DOCS = " + json.dumps(pages, ensure_ascii=False) + ";\n", encoding="utf-8")
    print(f"{len(pages)} páginas -> {out.relative_to(DOCS.parent)}")


if __name__ == "__main__":
    main()

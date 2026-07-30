#!/usr/bin/env python3
"""Fill SOTAF templates (templates/*.md) from a metadata JSON file.

Usage:
    python generate.py sample_metadata.json
"""
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"
SUMMARIES_DIR = OUTPUT_DIR / "summaries"

PLACEHOLDER_RE = re.compile(r"\{\{\s*([\w.]+)\s*\}\}")


def resolve(key: str, metadata: dict):
    """Resolve a dotted key like 'A.purpose' against the metadata dict."""
    value = metadata
    for part in key.split("."):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def render(template_text: str, metadata: dict) -> tuple[str, list[str]]:
    """Replace {{key}} placeholders. Returns (rendered_text, missing_keys)."""
    missing = []

    def replace(match: re.Match) -> str:
        key = match.group(1)
        value = resolve(key, metadata)
        if value is None:
            missing.append(key)
            return match.group(0)
        return str(value)

    return PLACEHOLDER_RE.sub(replace, template_text), missing


def generate_all(metadata: dict, templates_dir: Path = TEMPLATES_DIR) -> list[dict]:
    """Render every template in templates_dir against metadata.

    Returns a list of dicts: {doc, rendered, summary} in template order.
    Does not touch disk — callers decide whether/where to persist.
    """
    results = []
    for template_path in sorted(templates_dir.glob("*.md")):
        letter = template_path.stem  # e.g. "A"
        text = template_path.read_text(encoding="utf-8")
        rendered, missing = render(text, metadata)

        summary = {
            "doc": letter,
            "project_name": metadata.get("project_name"),
            "author": metadata.get("author"),
            "version": metadata.get("version"),
            "fields": metadata.get(letter, {}),
            "missing_keys": missing,
        }
        results.append({"doc": letter, "rendered": rendered, "summary": summary})
    return results


def main():
    if len(sys.argv) != 2:
        print("Usage: python generate.py <metadata.json>")
        sys.exit(1)

    metadata_path = Path(sys.argv[1])
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    results = generate_all(metadata)
    if not results:
        print(f"No templates found in {TEMPLATES_DIR}")
        sys.exit(1)

    OUTPUT_DIR.mkdir(exist_ok=True)
    SUMMARIES_DIR.mkdir(parents=True, exist_ok=True)

    had_missing = False
    for item in results:
        letter = item["doc"]
        out_path = OUTPUT_DIR / f"{letter}.md"
        out_path.write_text(item["rendered"], encoding="utf-8")

        summary_path = SUMMARIES_DIR / f"{letter}.json"
        summary_path.write_text(
            json.dumps(item["summary"], ensure_ascii=False, indent=2), encoding="utf-8"
        )

        missing = item["summary"]["missing_keys"]
        status = "OK" if not missing else f"MISSING: {', '.join(missing)}"
        print(f"[{letter}] -> {out_path.relative_to(BASE_DIR)}  ({status})")
        had_missing = had_missing or bool(missing)

    print(f"\nDone. {len(results)} document(s) written to {OUTPUT_DIR}/")
    if had_missing:
        print("Warning: some placeholders were left unfilled (see MISSING above).")
        sys.exit(2)


if __name__ == "__main__":
    main()

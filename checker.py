#!/usr/bin/env python3
"""Basic consistency checks across generated SOTAF documents.

Usage:
    python checker.py output/summaries
"""
import json
import re
import sys
from pathlib import Path

PLACEHOLDER_RE = re.compile(r"\{\{\s*[\w.]+\s*\}\}")


def load_summaries(summaries_dir: Path) -> list[dict]:
    summaries = []
    for path in sorted(summaries_dir.glob("*.json")):
        summaries.append(json.loads(path.read_text(encoding="utf-8")))
    return summaries


def check_common_fields(summaries: list[dict]) -> list[str]:
    issues = []
    for field in ("project_name", "author", "version"):
        values = {s["doc"]: s.get(field) for s in summaries}
        distinct = set(values.values())
        if len(distinct) > 1:
            detail = ", ".join(f"{doc}={val!r}" for doc, val in values.items())
            issues.append(f"Inconsistent '{field}' across documents: {detail}")
        elif None in distinct:
            issues.append(f"'{field}' is missing in all documents")
    return issues


def check_missing_keys(summaries: list[dict]) -> list[str]:
    issues = []
    for s in summaries:
        if s.get("missing_keys"):
            issues.append(
                f"Document {s['doc']}: unresolved placeholders {s['missing_keys']}"
            )
    return issues


def check_empty_fields(summaries: list[dict]) -> list[str]:
    issues = []
    for s in summaries:
        for key, value in s.get("fields", {}).items():
            if value is None or (isinstance(value, str) and not value.strip()):
                issues.append(f"Document {s['doc']}: field '{key}' is empty")
    return issues


def check_rendered_docs(summaries_dir: Path, summaries: list[dict]) -> list[str]:
    issues = []
    output_dir = summaries_dir.parent
    for s in summaries:
        doc_path = output_dir / f"{s['doc']}.md"
        if not doc_path.exists():
            issues.append(f"Document {s['doc']}: rendered file {doc_path} not found")
            continue
        text = doc_path.read_text(encoding="utf-8")
        leftovers = PLACEHOLDER_RE.findall(text)
        if leftovers:
            issues.append(f"Document {s['doc']}: leftover placeholders {leftovers}")
    return issues


def check_rendered_texts(rendered_by_doc: dict[str, str], summaries: list[dict]) -> list[str]:
    """Same as check_rendered_docs but against in-memory rendered text (no disk)."""
    issues = []
    for s in summaries:
        text = rendered_by_doc.get(s["doc"])
        if text is None:
            issues.append(f"Document {s['doc']}: rendered text not found")
            continue
        leftovers = PLACEHOLDER_RE.findall(text)
        if leftovers:
            issues.append(f"Document {s['doc']}: leftover placeholders {leftovers}")
    return issues


def analyze(summaries: list[dict], rendered_by_doc: dict[str, str] | None = None) -> list[str]:
    """Run all consistency checks against in-memory summaries (+ optional rendered text)."""
    issues = []
    issues += check_common_fields(summaries)
    issues += check_missing_keys(summaries)
    issues += check_empty_fields(summaries)
    if rendered_by_doc is not None:
        issues += check_rendered_texts(rendered_by_doc, summaries)
    return issues


def main():
    if len(sys.argv) != 2:
        print("Usage: python checker.py <summaries_dir>")
        sys.exit(1)

    summaries_dir = Path(sys.argv[1])
    if not summaries_dir.is_dir():
        print(f"Summaries directory not found: {summaries_dir}")
        sys.exit(1)

    summaries = load_summaries(summaries_dir)
    if not summaries:
        print(f"No summary files found in {summaries_dir}")
        sys.exit(1)

    issues = []
    issues += check_common_fields(summaries)
    issues += check_missing_keys(summaries)
    issues += check_empty_fields(summaries)
    issues += check_rendered_docs(summaries_dir, summaries)

    print(f"Checked {len(summaries)} document(s) in {summaries_dir}\n")
    if not issues:
        print("No inconsistencies found.")
        sys.exit(0)

    print(f"Found {len(issues)} issue(s):")
    for issue in issues:
        print(f" - {issue}")
    sys.exit(1)


if __name__ == "__main__":
    main()

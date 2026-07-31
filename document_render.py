#!/usr/bin/env python3
"""Build a render-ready structure (doc -> sections -> text/table) from stored
metadata + the SOTAF schema. Shared by the styled-PDF export.
"""
from sotaf_schema import DOCUMENTS, DOC_ORDER, DOC_META


def _section_columns(section: dict) -> list[str]:
    if section["type"] == "table":
        return section["columns"]
    return [f["label"] for f in section["fields"]]


def build_documents_context(metadata: dict) -> list[dict]:
    docs = []
    for letter in DOC_ORDER:
        doc_data = metadata.get(letter, {})
        sections = []
        for section in DOCUMENTS[letter]:
            value = doc_data.get(section["id"])
            if section["type"] == "text":
                text = (value or "").strip()
                if text:
                    sections.append({"type": "text", "label": section["label"], "text": text})
            else:
                columns = _section_columns(section)
                rows = [r for r in (value or []) if any((v or "").strip() for v in r.values())]
                if rows:
                    sections.append({"type": "table", "label": section["label"], "columns": columns, "rows": rows})
        docs.append({
            "letter": letter,
            "title": DOC_META[letter]["title"],
            "subtitle": DOC_META[letter]["subtitle"],
            "sections": sections,
        })
    return docs


def sotaf_documents_for_ai(metadata: dict) -> list[dict]:
    """Flattened plain-text rendering of every non-empty document, for the AI review call."""
    docs = build_documents_context(metadata)
    result = []
    for doc in docs:
        if not doc["sections"]:
            continue
        parts = [f"{doc['title']} ({doc['subtitle']})"]
        for section in doc["sections"]:
            parts.append(f"## {section['label']}")
            if section["type"] == "text":
                parts.append(section["text"])
            else:
                for row in section["rows"]:
                    parts.append(" | ".join(f"{k}: {v}" for k, v in row.items() if (v or "").strip()))
        result.append({"doc": doc["letter"], "rendered": "\n".join(parts)})
    return result


def merge_findings_into_doc_h(metadata: dict, findings: list[dict]) -> None:
    """Write AI-review findings into Doc H's real 'ממצאי אי-התאמה' table (H2),
    so a consistency check shows up as an actual, exportable Doc H section
    instead of only living on the review page."""
    rows = [
        {
            "מסמך הנדסי / סעיף": f"מסמך {f.get('doc', '')} — {f.get('section', '')}",
            "מידע הנדסי": f.get("sotaf_info", ""),
            "לא תואם מידע במסמך": f.get("conflicting_info", ""),
            "מידע הנדסי סותר": "",
            "תיקון נדרש": f.get("recommendation", ""),
        }
        for f in findings
    ]
    metadata.setdefault("H", {})["findings"] = rows

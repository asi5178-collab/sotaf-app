#!/usr/bin/env python3
"""Minimal web UI for the SOTAF generator/checker.

Paste or upload a metadata JSON, get back the rendered A-G documents
plus a consistency report, all in one page. No files are written to disk.
"""
import json
import os

from flask import Flask, render_template, request

from generate import TEMPLATES_DIR, generate_all
from checker import analyze

app = Flask(__name__, template_folder="templates_web")

SAMPLE_METADATA_PATH = os.path.join(os.path.dirname(__file__), "sample_metadata.json")


def load_sample_metadata() -> str:
    with open(SAMPLE_METADATA_PATH, encoding="utf-8") as f:
        return f.read()


@app.route("/", methods=["GET", "POST"])
def index():
    metadata_text = load_sample_metadata()
    documents = None
    issues = None
    error = None

    if request.method == "POST":
        uploaded = request.files.get("metadata_file")
        if uploaded and uploaded.filename:
            metadata_text = uploaded.read().decode("utf-8")
        else:
            metadata_text = request.form.get("metadata_text", metadata_text)

        try:
            metadata = json.loads(metadata_text)
        except json.JSONDecodeError as exc:
            error = f"קובץ ה-JSON אינו תקין: {exc}"
        else:
            results = generate_all(metadata, TEMPLATES_DIR)
            if not results:
                error = "לא נמצאו תבניות בתיקיית templates/."
            else:
                documents = [{"doc": r["doc"], "rendered": r["rendered"]} for r in results]
                summaries = [r["summary"] for r in results]
                rendered_by_doc = {r["doc"]: r["rendered"] for r in results}
                issues = analyze(summaries, rendered_by_doc)

    return render_template(
        "index.html",
        metadata_text=metadata_text,
        documents=documents,
        issues=issues,
        error=error,
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

#!/usr/bin/env python3
"""Interactive web UI for the SOTAF generator, checker, and AI-assisted review.

Step 1 (/):        guided form -> generates the A-G SOTAF documents.
Step 2 (/review):  shows the documents + consistency report; upload project
                    files (PDF/Word) to have Claude find inconsistencies and
                    recommend corrections.
"""
import os
import secrets
import uuid

from flask import Flask, redirect, render_template, request, session, url_for

from generate import TEMPLATES_DIR, generate_all
from checker import analyze
from extract import extract_text
from ai_review import review as ai_review

app = Flask(__name__, template_folder="templates_web")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# In-memory per-process session store: {session_id: {...}}. Fine for a
# single-worker deployment; state is lost on restart.
SESSIONS: dict[str, dict] = {}

FORM_FIELDS = [
    ("project_name", "שם הפרויקט", None),
    ("author", "שם מחבר/ת", None),
    ("version", "גרסה", None),
    ("A.purpose", "מסמך A — מטרת המערכת (Purpose)", "A"),
    ("A.scope", "מסמך A — היקף הפרויקט (Scope)", "A"),
    ("B.technologies", "מסמך B — טכנולוגיות", "B"),
    ("C.functional_requirements", "מסמך C — דרישות פונקציונליות", "C"),
    ("C.interfaces", "מסמך C — ממשקים", "C"),
    ("D.operation_concept", "מסמך D — תפיסת הפעלה", "D"),
    ("E.business_case", "מסמך E — תועלת עסקית", "E"),
    ("F.management", "מסמך F — ניהול", "F"),
    ("G.incentives", "מסמך G — תמריצים", "G"),
]


def get_session_data() -> dict | None:
    sid = session.get("sid")
    return SESSIONS.get(sid) if sid else None


def metadata_to_flat(metadata: dict) -> dict:
    flat = {
        "project_name": metadata.get("project_name", ""),
        "author": metadata.get("author", ""),
        "version": metadata.get("version", ""),
    }
    for key, _, doc in FORM_FIELDS:
        if doc:
            _, field = key.split(".")
            flat[key] = metadata.get(doc, {}).get(field, "")
    return flat


def form_to_metadata(form) -> dict:
    metadata: dict = {
        "project_name": form.get("project_name", "").strip(),
        "author": form.get("author", "").strip(),
        "version": form.get("version", "").strip(),
    }
    for key, _, doc in FORM_FIELDS:
        if doc:
            _, field = key.split(".")
            metadata.setdefault(doc, {})[field] = form.get(key, "").strip()
    return metadata


@app.route("/", methods=["GET", "POST"])
def index():
    existing = get_session_data()
    values = metadata_to_flat(existing["metadata"]) if existing else {}

    if request.method == "POST":
        metadata = form_to_metadata(request.form)
        results = generate_all(metadata, TEMPLATES_DIR)

        sid = str(uuid.uuid4())
        SESSIONS[sid] = {"metadata": metadata, "results": results, "findings": None}
        session["sid"] = sid
        return redirect(url_for("review"))

    return render_template("form.html", fields=FORM_FIELDS, values=values)


@app.route("/review", methods=["GET"])
def review():
    data = get_session_data()
    if not data:
        return redirect(url_for("index"))

    results = data["results"]
    documents = [{"doc": r["doc"], "rendered": r["rendered"]} for r in results]
    summaries = [r["summary"] for r in results]
    rendered_by_doc = {r["doc"]: r["rendered"] for r in results}
    issues = analyze(summaries, rendered_by_doc)

    return render_template(
        "review.html",
        documents=documents,
        issues=issues,
        findings=data.get("findings"),
        analyze_error=data.get("analyze_error"),
    )


@app.route("/analyze", methods=["POST"])
def analyze_uploads():
    data = get_session_data()
    if not data:
        return redirect(url_for("index"))

    uploaded_files = []
    for f in request.files.getlist("project_files"):
        if not f or not f.filename:
            continue
        text = extract_text(f.filename, f.read())
        if text:
            uploaded_files.append({"filename": f.filename, "text": text})

    if not uploaded_files:
        data["analyze_error"] = "לא נמצאו קבצי PDF/Word תקינים בהעלאה."
        data["findings"] = None
        return redirect(url_for("review"))

    sotaf_documents = [
        {"doc": r["doc"], "rendered": r["rendered"]} for r in data["results"]
    ]

    try:
        findings = ai_review(sotaf_documents, uploaded_files)
        data["findings"] = findings
        data["analyze_error"] = None
    except Exception as exc:  # noqa: BLE001 - surface any API/config error to the user
        data["findings"] = None
        data["analyze_error"] = f"שגיאה בניתוח: {exc}"

    return redirect(url_for("review"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

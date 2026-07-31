#!/usr/bin/env python3
"""SOTAF Studio — interactive web app for building the full SOTAF document set
(0, A, B, C1, D, E, F, G, H), browsing real example projects, checking
cross-document consistency with Claude, and exporting a styled PDF.
"""
import datetime
import json
import os
import secrets
import uuid
from urllib.parse import quote

from flask import Flask, Response, redirect, render_template, request, session, url_for

from sotaf_schema import DOC_ORDER, DOC_META, DOCUMENTS, blank_metadata, doc_progress
from project_library import EXAMPLE_PROJECTS
from document_render import build_documents_context, sotaf_documents_for_ai, merge_findings_into_doc_h
from extract import extract_text
from ai_review import review as ai_review, review_standalone
from ai_generate import generate_all_documents

app = Flask(__name__, template_folder="templates_web")
app.secret_key = os.environ.get("SECRET_KEY") or secrets.token_hex(32)

# In-memory per-process project store: {session_id: {...}}. Fine for a
# single-worker deployment; state is lost on restart.
PROJECTS: dict[str, dict] = {}


def get_project() -> dict | None:
    pid = session.get("pid")
    return PROJECTS.get(pid) if pid else None


@app.context_processor
def inject_globals():
    return {"has_project": get_project() is not None}


def require_project():
    project = get_project()
    if not project:
        return redirect(url_for("home"))
    return None


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/create", methods=["POST"])
def create_project():
    metadata = blank_metadata()
    metadata["project_name"] = request.form.get("project_name", "").strip() or "פרויקט ללא שם"
    metadata["author"] = request.form.get("author", "").strip()
    metadata["description"] = request.form.get("description", "").strip()

    reference_files = []
    for f in request.files.getlist("reference_files"):
        if not f or not f.filename:
            continue
        text = extract_text(f.filename, f.read())
        if text:
            reference_files.append({"filename": f.filename, "text": text})

    generate_error = None
    if metadata["description"] or reference_files:
        try:
            generated = generate_all_documents(
                metadata["description"], metadata["project_name"], metadata["author"], reference_files
            )
            for letter, doc_data in generated.items():
                if letter in metadata:
                    metadata[letter].update(doc_data)
        except Exception as exc:  # noqa: BLE001 - fall back to a blank project rather than fail
            generate_error = f"יצירה אוטומטית נכשלה, נפתח פרויקט ריק למילוי ידני: {exc}"

    pid = str(uuid.uuid4())
    PROJECTS[pid] = {
        "metadata": metadata,
        "findings": None,
        "analyze_error": None,
        "generate_error": generate_error,
    }
    session["pid"] = pid
    return redirect(url_for("hub"))


@app.route("/library")
def library():
    return render_template("library.html", projects=EXAMPLE_PROJECTS)


@app.route("/check-project", methods=["GET", "POST"])
def check_project():
    if request.method == "GET":
        return render_template("check_project.html")

    project_name = request.form.get("project_name", "").strip() or "פרויקט קיים לבדיקה"

    uploaded_files = []
    skipped_files = []
    for f in request.files.getlist("project_files"):
        if not f or not f.filename:
            continue
        text = extract_text(f.filename, f.read())
        if text:
            uploaded_files.append({"filename": f.filename, "text": text})
        else:
            skipped_files.append(f.filename)

    if not uploaded_files:
        return render_template(
            "check_project.html",
            error="לא נמצאו קבצי PDF/Word תקינים בהעלאה.",
        )

    metadata = blank_metadata()
    metadata["project_name"] = project_name
    metadata["author"] = request.form.get("author", "").strip()

    pid = str(uuid.uuid4())
    project = {
        "metadata": metadata,
        "findings": None,
        "analyze_error": None,
        "analyzed_files": None,
        "generate_error": None,
    }
    PROJECTS[pid] = project
    session["pid"] = pid

    try:
        findings = review_standalone(uploaded_files)
        project["findings"] = findings
        project["analyzed_files"] = [f["filename"] for f in uploaded_files]
        project["analyze_error"] = (
            "לא ניתן היה לקרוא את הקבצים הבאים ולכן הם לא נכללו בניתוח: " + ", ".join(skipped_files)
            if skipped_files else None
        )
        merge_findings_into_doc_h(metadata, findings)
    except Exception as exc:  # noqa: BLE001 - surface any API/config error to the user
        project["findings"] = None
        project["analyze_error"] = f"שגיאה בניתוח: {exc}"

    return redirect(url_for("review"))


@app.route("/hub")
def hub():
    redirect_resp = require_project()
    if redirect_resp:
        return redirect_resp
    project = get_project()
    metadata = project["metadata"]

    docs = []
    for letter in DOC_ORDER:
        filled, total = doc_progress(metadata, letter)
        docs.append({
            "letter": letter,
            "title": DOC_META[letter]["title"],
            "subtitle": DOC_META[letter]["subtitle"],
            "filled": filled,
            "total": total,
            "pct": round(100 * filled / total) if total else 0,
        })

    return render_template(
        "hub.html",
        project_name=metadata.get("project_name", ""),
        description=metadata.get("description", ""),
        docs=docs,
        generate_error=project.get("generate_error"),
    )


@app.route("/doc/<doc>", methods=["GET", "POST"])
def doc_editor(doc):
    redirect_resp = require_project()
    if redirect_resp:
        return redirect_resp
    if doc not in DOCUMENTS:
        return redirect(url_for("hub"))

    project = get_project()
    metadata = project["metadata"]
    doc_data = metadata.setdefault(doc, {})

    if request.method == "POST":
        for section in DOCUMENTS[doc]:
            if section["type"] == "text":
                doc_data[section["id"]] = request.form.get(f"text__{section['id']}", "").strip()
            else:
                raw = request.form.get(f"table__{section['id']}", "[]")
                try:
                    doc_data[section["id"]] = json.loads(raw)
                except (ValueError, TypeError):
                    pass
        return redirect(url_for("hub"))

    blocks = []
    for section in DOCUMENTS[doc]:
        if section["type"] == "text":
            blocks.append({
                "type": "text",
                "label": section["label"],
                "name": f"text__{section['id']}",
                "value": doc_data.get(section["id"], ""),
            })
        else:
            if section["type"] == "table":
                fields = [{"id": c, "label": c, "kind": "text"} for c in section["columns"]]
            else:
                fields = section["fields"]
            config = {
                "fields": fields,
                "seed": section.get("seed", []),
                "value": doc_data.get(section["id"], []),
            }
            hidden_id = f"hidden__{section['id']}"
            blocks.append({
                "type": "dyn",
                "label": section["label"],
                "name": f"table__{section['id']}",
                "hidden_id": hidden_id,
                "config_json": json.dumps(config, ensure_ascii=False),
            })

    return render_template(
        "doc_editor.html",
        doc=doc,
        title=DOC_META[doc]["title"],
        subtitle=DOC_META[doc]["subtitle"],
        blocks=blocks,
    )


@app.route("/review")
def review():
    redirect_resp = require_project()
    if redirect_resp:
        return redirect_resp
    project = get_project()
    return render_template(
        "review.html",
        findings=project.get("findings"),
        analyze_error=project.get("analyze_error"),
        analyzed_files=project.get("analyzed_files"),
    )


@app.route("/analyze", methods=["POST"])
def analyze_uploads():
    redirect_resp = require_project()
    if redirect_resp:
        return redirect_resp
    project = get_project()

    uploaded_files = []
    skipped_files = []
    for f in request.files.getlist("project_files"):
        if not f or not f.filename:
            continue
        text = extract_text(f.filename, f.read())
        if text:
            uploaded_files.append({"filename": f.filename, "text": text})
        else:
            skipped_files.append(f.filename)

    if not uploaded_files:
        project["analyze_error"] = "לא נמצאו קבצי PDF/Word תקינים בהעלאה."
        project["findings"] = None
        project["analyzed_files"] = None
        return redirect(url_for("review"))

    sotaf_documents = sotaf_documents_for_ai(project["metadata"])

    try:
        findings = ai_review(sotaf_documents, uploaded_files)
        project["findings"] = findings
        project["analyzed_files"] = [f["filename"] for f in uploaded_files]
        project["analyze_error"] = (
            "לא ניתן היה לקרוא את הקבצים הבאים ולכן הם לא נכללו בניתוח: " + ", ".join(skipped_files)
            if skipped_files else None
        )
        merge_findings_into_doc_h(project["metadata"], findings)
    except Exception as exc:  # noqa: BLE001 - surface any API/config error to the user
        project["findings"] = None
        project["analyzed_files"] = None
        project["analyze_error"] = f"שגיאה בניתוח: {exc}"

    return redirect(url_for("review"))


@app.route("/export/pdf")
def export_pdf():
    redirect_resp = require_project()
    if redirect_resp:
        return redirect_resp
    project = get_project()
    metadata = project["metadata"]
    documents = build_documents_context(metadata)

    html = render_template(
        "pdf_document.html",
        project_name=metadata.get("project_name", ""),
        author=metadata.get("author", ""),
        description=metadata.get("description", ""),
        today=datetime.date.today().strftime("%d/%m/%Y"),
        documents=documents,
    )

    try:
        from weasyprint import HTML
    except Exception as exc:  # noqa: BLE001
        return Response(f"PDF generation is unavailable on this server: {exc}", status=500)

    pdf_bytes = HTML(string=html, base_url=os.path.dirname(__file__) + os.sep).write_pdf()

    # HTTP headers must be Latin-1; a Hebrew project name needs RFC 5987 encoding
    # (filename*=UTF-8''...), with a plain ASCII filename as a compatibility fallback.
    quoted_name = quote(f"{metadata.get('project_name', 'SOTAF')}.pdf")
    disposition = f"attachment; filename=\"SOTAF.pdf\"; filename*=UTF-8''{quoted_name}"
    return Response(
        pdf_bytes,
        mimetype="application/pdf",
        headers={"Content-Disposition": disposition},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

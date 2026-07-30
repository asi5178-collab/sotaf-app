#!/usr/bin/env python3
"""Use Claude to compare uploaded project files against generated SOTAF documents
and recommend corrections. Findings come back as structured tool input, not
free-text parsing.
"""
import anthropic

MODEL = "claude-opus-5"

REPORT_TOOL = {
    "name": "report_findings",
    "description": (
        "Report inconsistencies found between the uploaded project files and the "
        "SOTAF documents, with a recommended correction for each."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "findings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "doc": {
                            "type": "string",
                            "enum": ["A", "B", "C", "D", "E", "F", "G"],
                            "description": "Which SOTAF document this finding applies to.",
                        },
                        "issue": {
                            "type": "string",
                            "description": "The inconsistency, in Hebrew: what the project files say vs. what the SOTAF document says.",
                        },
                        "source": {
                            "type": "string",
                            "description": "Which uploaded file (and where in it) supports this finding.",
                        },
                        "recommendation": {
                            "type": "string",
                            "description": "A concrete recommended edit to the SOTAF document, in Hebrew.",
                        },
                    },
                    "required": ["doc", "issue", "source", "recommendation"],
                },
            }
        },
        "required": ["findings"],
    },
}

SYSTEM_PROMPT = """\
אתה עוזר בבדיקת עקביות של מסמכי SOTAF (A-G) המתארים מערכת, מול קבצי פרויקט \
שהמשתמש העלה (מצגות, דוחות, מסמכי דרישות וכו').

המשימה שלך: למצוא אי-התאמות עובדתיות בין תוכן קבצי הפרויקט לבין מסמכי ה-SOTAF - \
מידע שסותר את מה שכתוב במסמך, מידע חשוב שמופיע בקבצי הפרויקט אך חסר במסמך, או \
מידע במסמך שנראה מיושן/שגוי לאור קבצי הפרויקט.

עבור כל אי-התאמות שתמצא, קרא ל-report_findings עם רשימת הממצאים. אם לא נמצאו \
אי-התאמות, קרא לה עם רשימה ריקה. אל תדווח על ניסוחים שונים בלבד ללא הבדל עובדתי \
בפועל - רק על אי-התאמות מהותיות."""


def review(sotaf_documents: list[dict], uploaded_files: list[dict]) -> list[dict]:
    """sotaf_documents: [{'doc': 'A', 'rendered': '...'}, ...]
    uploaded_files: [{'filename': '...', 'text': '...'}, ...]
    Returns a list of finding dicts (possibly empty).
    """
    client = anthropic.Anthropic()

    docs_text = "\n\n".join(
        f"--- מסמך {d['doc']} ---\n{d['rendered']}" for d in sotaf_documents
    )
    files_text = "\n\n".join(
        f"--- קובץ שהועלה: {f['filename']} ---\n{f['text']}" for f in uploaded_files
    )

    user_message = (
        f"מסמכי SOTAF נוכחיים:\n\n{docs_text}\n\n"
        f"קבצי הפרויקט שהועלו:\n\n{files_text}\n\n"
        "מצא אי-התאמות ודווח באמצעות report_findings."
    )

    response = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        system=SYSTEM_PROMPT,
        tools=[REPORT_TOOL],
        tool_choice={"type": "tool", "name": "report_findings"},
        messages=[{"role": "user", "content": user_message}],
    )

    for block in response.content:
        if block.type == "tool_use" and block.name == "report_findings":
            return block.input.get("findings", [])
    return []

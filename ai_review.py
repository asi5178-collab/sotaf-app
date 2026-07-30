#!/usr/bin/env python3
"""Use Claude to compare uploaded project files against the filled-in SOTAF
documents and produce findings shaped like the course's real Doc H table
(מסמך בדיקת רציפות מסמכים): document/section, the SOTAF info, the conflicting
info, and the required fix.
"""
import anthropic

MODEL = "claude-opus-5"

REPORT_TOOL = {
    "name": "report_findings",
    "description": (
        "Report inconsistencies found between the uploaded project files and the "
        "SOTAF documents, shaped like the course's Doc H (מסמך בדיקת רציפות מסמכים) table."
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
                            "enum": ["0", "A", "B", "C1", "D", "E", "F", "G", "H"],
                            "description": "Which SOTAF document this finding applies to.",
                        },
                        "section": {
                            "type": "string",
                            "description": "Which section within that document, in Hebrew (e.g. 'בעלי עניין', 'מיפוי שירותי ניידות').",
                        },
                        "sotaf_info": {
                            "type": "string",
                            "description": "The information as currently stated in the SOTAF document, in Hebrew.",
                        },
                        "conflicting_info": {
                            "type": "string",
                            "description": "The conflicting or missing information found in the uploaded project files, with the source filename, in Hebrew.",
                        },
                        "recommendation": {
                            "type": "string",
                            "description": "A concrete recommended fix to the SOTAF document, in Hebrew.",
                        },
                    },
                    "required": ["doc", "section", "sotaf_info", "conflicting_info", "recommendation"],
                },
            }
        },
        "required": ["findings"],
    },
}

SYSTEM_PROMPT = """\
אתה עוזר בהכנת מסמך H (מסמך בדיקת רציפות מסמכים) בשיטת SOTAF - מסמך שמטרתו "איתור \
נקודות אי-התאמה בין מסמכי A-G" של פרויקט הנדסת מערכות.

תקבל את תוכן מסמכי ה-SOTAF שהמשתמש מילא (0, A, B, C1, D, E, F, G) וקבצי פרויקט \
שהועלו (מצגות, דוחות, מסמכי דרישות). המשימה שלך: למצוא אי-התאמות עובדתיות בין \
תוכן קבצי הפרויקט לבין מסמכי ה-SOTAF - מידע שסותר את מה שכתוב במסמך, מידע חשוב \
שמופיע בקבצי הפרויקט אך חסר במסמך, או מידע במסמך שנראה מיושן/שגוי לאור קבצי הפרויקט.

עבור כל אי-התאמה, קרא ל-report_findings עם שורה בפורמט הזהה לטבלת H2 הרשמית: \
מסמך + סעיף, המידע כפי שמופיע במסמך ה-SOTAF, המידע הסותר/חסר מהקובץ שהועלה (עם שם \
הקובץ), והתיקון הנדרש. אם לא נמצאו אי-התאמות, קרא לה עם רשימה ריקה. אל תדווח על \
ניסוחים שונים בלבד ללא הבדל עובדתי בפועל - רק על אי-התאמות מהותיות."""


def review(sotaf_documents: list[dict], uploaded_files: list[dict]) -> list[dict]:
    """sotaf_documents: [{'doc': 'A', 'rendered': '...'}, ...]
    uploaded_files: [{'filename': '...', 'text': '...'}, ...]
    Returns a list of finding dicts shaped like Doc H rows.
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
        "מצא אי-התאמות ודווח באמצעות report_findings, בפורמט טבלת H2."
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

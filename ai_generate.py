#!/usr/bin/env python3
"""Auto-generate a full draft of all 9 SOTAF documents from a short user
description, using Claude with structured tool calls built from the real
SOTAF schema (sotaf_schema.py) — so the output shape matches the app's
storage format exactly and lands directly in the editable document editor.

Generating all 9 documents in a single call is slow enough to blow past
reasonable HTTP timeouts, so the work is split into three groups and run
concurrently; wall-clock time is roughly the slowest single group instead
of the sum of all nine documents.
"""
from concurrent.futures import ThreadPoolExecutor

import anthropic

from sotaf_schema import DOCUMENTS, DOC_META

MODEL = "claude-opus-5"

GROUPS = [
    ["0", "A", "B"],
    ["C1", "D", "E"],
    ["F", "G", "H"],
]

SYSTEM_PROMPT = """\
אתה עוזר בהכנת ערכת מסמכי SOTAF (Socio-Technological Architecture Framework) \
מלאה - מתודולוגיה הנדסת מערכות הנלמדת בקורס "מידול מערכות" באוניברסיטת אריאל, \
לתיעוד אתגרים מערכתיים (בעיקר בתחום הניידות/תחבורה קמפוסית, אך גם תחומים אחרים).

תקבל תיאור קצר של אתגר מערכתי מהמשתמש. המשימה שלך: לחולל טיוטה מלאה וסבירה \
של קבוצת מסמכי SOTAF שתתבקש, על בסיס התיאור, בעברית.

הנחיות:
- כתוב תוכן קונקרטי, ספציפי לאתגר שתואר - לא ניסוחים גנריים. אם התיאור חסר פרטים \
מסוימים, הסק בצורה סבירה מהקשר האתגר (לדוגמה: אם האתגר הוא ניידות קמפוסית, \
בעלי העניין, השירותים והתרחישים צריכים להתאים לסביבה קמפוסית).
- מלא את כל הטבלאות בשורות רלוונטיות (בעלי עניין, שירותים, תרחישים, ממשקים, \
Use Cases וכו') - לא להשאיר טבלאות ריקות, אך שמור על תמציתיות (2-5 שורות לטבלה \
מספיקות).
- שדות טקסט חופשי: 2-4 משפטים לכל שדה, ממוקדים וספציפיים - לא חיבורים ארוכים.
- מסמך H (בדיקת רציפות מסמכים), אם מבוקש - במקום למצוא אי-התאמות אמיתיות (שעדיין \
לא קיימות בטיוטה ראשונית), מלא אותו עם 1-2 שורות לדוגמה שממחישות את סוג הבדיקה \
שהמסמך אמור לבצע בהמשך הפרויקט, ופסקת תהליך בדיקה כללית.
- קרא לכלי המבוקש עם כל המסמכים שהתבקשו, מלאים."""


def _section_schema(section: dict) -> dict:
    if section["type"] == "text":
        return {"type": "string", "description": section["label"]}

    if section["type"] == "table":
        columns = section["columns"]
    else:
        columns = [f["label"] for f in section["fields"]]

    return {
        "type": "array",
        "description": f"טבלה: {section['label']}",
        "items": {
            "type": "object",
            "properties": {c: {"type": "string"} for c in columns},
            "required": columns,
        },
    }


def _doc_schema(letter: str) -> dict:
    sections = DOCUMENTS[letter]
    return {
        "type": "object",
        "description": f"{DOC_META[letter]['title']} ({DOC_META[letter]['subtitle']})",
        "properties": {s["id"]: _section_schema(s) for s in sections},
        "required": [s["id"] for s in sections],
    }


def _build_tool(letters: list[str]) -> dict:
    return {
        "name": "generate_sotaf_documents",
        "description": "Generate full draft content for the requested SOTAF documents based on the user's challenge description.",
        "input_schema": {
            "type": "object",
            "properties": {letter: _doc_schema(letter) for letter in letters},
            "required": letters,
        },
    }


def _generate_group(client: anthropic.Anthropic, letters: list[str], user_message: str) -> dict:
    tool = _build_tool(letters)
    with client.messages.stream(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "tool", "name": "generate_sotaf_documents"},
        output_config={"effort": "medium"},
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        response = stream.get_final_message()

    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_sotaf_documents":
            return block.input
    return {}


def generate_all_documents(description: str, project_name: str, author: str) -> dict:
    """Returns a dict shaped like {letter: {section_id: value}}, matching the
    per-document portion of blank_metadata(). Runs the 3 document groups
    concurrently so wall-clock time stays well under the slowest single call."""
    client = anthropic.Anthropic()
    user_message = (
        f"שם הפרויקט/האתגר: {project_name}\n"
        f"צוות: {author}\n\n"
        f"תיאור האתגר המערכתי:\n{description}"
    )

    result: dict = {}
    with ThreadPoolExecutor(max_workers=len(GROUPS)) as executor:
        futures = [
            executor.submit(_generate_group, client, letters, user_message)
            for letters in GROUPS
        ]
        for future in futures:
            result.update(future.result())
    return result

#!/usr/bin/env python3
"""Auto-generate a full draft of all 9 SOTAF documents from a short user
description, using Claude with a structured tool call built from the real
SOTAF schema (sotaf_schema.py) — so the output shape matches the app's
storage format exactly and lands directly in the editable document editor.
"""
import anthropic

from sotaf_schema import DOCUMENTS, DOC_ORDER, DOC_META

MODEL = "claude-opus-5"

SYSTEM_PROMPT = """\
אתה עוזר בהכנת ערכת מסמכי SOTAF (Socio-Technological Architecture Framework) \
מלאה - מתודולוגיה הנדסת מערכות הנלמדת בקורס "מידול מערכות" באוניברסיטת אריאל, \
לתיעוד אתגרים מערכתיים (בעיקר בתחום הניידות/תחבורה קמפוסית, אך גם תחומים אחרים).

תקבל תיאור קצר של אתגר מערכתי מהמשתמש. המשימה שלך: לחולל טיוטה מלאה וסבירה \
של כל 9 מסמכי ה-SOTAF (0, A, B, C1, D, E, F, G, H), על בסיס התיאור, בעברית.

הנחיות:
- כתוב תוכן קונקרטי, ספציפי לאתגר שתואר - לא ניסוחים גנריים. אם התיאור חסר פרטים \
מסוימים, הסק בצורה סבירה מהקשר האתגר (לדוגמה: אם האתגר הוא ניידות קמפוסית, \
בעלי העניין, השירותים והתרחישים צריכים להתאים לסביבה קמפוסית).
- מלא את כל הטבלאות בשורות רלוונטיות (בעלי עניין, שירותים, תרחישים, ממשקים, \
Use Cases וכו') - לא להשאיר טבלאות ריקות. אפשר ורצוי להשתמש בקבוצות/שירותים \
הסטנדרטיים כשמתאימים (למשל קבוצות בעלי עניין: מפעיל השירות, רשויות מקומיות, \
סטודנטים וכו'), אך התאם אותם ואת התוכן שלהם לאתגר הספציפי.
- מסמך H (בדיקת רציפות מסמכים) - במקום למצוא אי-התאמות אמיתיות (שעדיין לא קיימות \
בטיוטה ראשונית), מלא אותו עם 1-2 שורות לדוגמה שממחישות את סוג הבדיקה שהמסמך אמור \
לבצע בהמשך הפרויקט, ופסקת תהליך בדיקה כללית.
- קרא לכלי generate_sotaf_documents עם כל 9 המסמכים מלאים."""


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


def _build_tool() -> dict:
    return {
        "name": "generate_sotaf_documents",
        "description": "Generate full draft content for all 9 SOTAF documents based on the user's challenge description.",
        "input_schema": {
            "type": "object",
            "properties": {letter: _doc_schema(letter) for letter in DOC_ORDER},
            "required": DOC_ORDER,
        },
    }


def generate_all_documents(description: str, project_name: str, author: str) -> dict:
    """Returns a dict shaped like {letter: {section_id: value}}, matching the
    per-document portion of blank_metadata()."""
    client = anthropic.Anthropic()
    tool = _build_tool()

    user_message = (
        f"שם הפרויקט/האתגר: {project_name}\n"
        f"צוות: {author}\n\n"
        f"תיאור האתגר המערכתי:\n{description}"
    )

    with client.messages.stream(
        model=MODEL,
        max_tokens=16000,
        system=SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "tool", "name": "generate_sotaf_documents"},
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        response = stream.get_final_message()

    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_sotaf_documents":
            return block.input
    return {}

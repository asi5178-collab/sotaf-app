#!/usr/bin/env python3
"""Auto-generate a full draft of all 9 SOTAF documents from a short user
description, using Claude with structured tool calls built from the real
SOTAF schema (sotaf_schema.py) — so the output shape matches the app's
storage format exactly and lands directly in the editable document editor.

Generating all 9 documents in a single call (or even grouped 3-at-a-time)
took anywhere from 3 to 5 minutes and had a habit of truncating the later
documents in a group before it finished. One call per document keeps each
call's output small and predictable, and all 9 run concurrently so
wall-clock time is roughly the slowest single document, not the sum.
"""
from concurrent.futures import ThreadPoolExecutor

import anthropic

from sotaf_schema import DOCUMENTS, DOC_ORDER, DOC_META

MODEL = "claude-opus-5"

SYSTEM_PROMPT = """\
אתה עוזר בהכנת ערכת מסמכי SOTAF (Socio-Technological Architecture Framework) \
מלאה - מתודולוגיה הנדסת מערכות הנלמדת בקורס "מידול מערכות" באוניברסיטת אריאל, \
לתיעוד אתגרים מערכתיים (בעיקר בתחום הניידות/תחבורה קמפוסית, אך גם תחומים אחרים).

תקבל תיאור קצר של אתגר מערכתי מהמשתמש, וכן את שם מסמך ה-SOTAF הספציפי שנדרש. \
לעיתים תקבל גם קבצי פרויקט קיימים (מצגות, דוחות, מסמכי דרישות) שהמשתמש כבר העלה. \
המשימה שלך: לחולל טיוטה מלאה וסבירה של אותו מסמך, על בסיס התיאור, בעברית.

הנחיות:
- אם סופקו קבצי פרויקט - התוכן שלהם הוא המקור הכי אמין למידע. שאב מהם עובדות, \
מספרים, שמות ופרטים קונקרטיים במקום להמציא אותם, וודא שהמסמך שתחולל תואם למה \
שכתוב בהם. השתמש בהנחות סבירות רק למילוי פערים שהקבצים לא מכסים.
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
- קרא לכלי generate_sotaf_document עם המסמך המבוקש, מלא."""


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


def _build_tool(letter: str) -> dict:
    return {
        "name": "generate_sotaf_document",
        "description": "Generate full draft content for one SOTAF document based on the user's challenge description.",
        "input_schema": _doc_schema(letter),
    }


def _generate_one(client: anthropic.Anthropic, letter: str, user_message: str) -> dict:
    tool = _build_tool(letter)
    with client.messages.stream(
        model=MODEL,
        max_tokens=6000,
        system=SYSTEM_PROMPT,
        tools=[tool],
        tool_choice={"type": "tool", "name": "generate_sotaf_document"},
        output_config={"effort": "low"},
        messages=[{"role": "user", "content": f"מסמך מבוקש: {letter}\n\n{user_message}"}],
    ) as stream:
        response = stream.get_final_message()

    for block in response.content:
        if block.type == "tool_use" and block.name == "generate_sotaf_document":
            return {letter: block.input}
    return {}


def generate_all_documents(
    description: str, project_name: str, author: str, reference_files: list[dict] | None = None
) -> dict:
    """Returns a dict shaped like {letter: {section_id: value}}, matching the
    per-document portion of blank_metadata(). One Claude call per document,
    run concurrently, so wall-clock time is roughly the slowest single
    document instead of the sum of all nine.

    reference_files: optional [{'filename': ..., 'text': ...}, ...] - existing
    project material to ground the generated content in, instead of inventing
    everything from the short description alone.
    """
    client = anthropic.Anthropic()
    user_message = (
        f"שם הפרויקט/האתגר: {project_name}\n"
        f"צוות: {author}\n\n"
        f"תיאור האתגר המערכתי:\n{description}"
    )
    if reference_files:
        files_text = "\n\n".join(
            f"--- קובץ פרויקט: {f['filename']} ---\n{f['text']}" for f in reference_files
        )
        user_message += f"\n\nקבצי פרויקט קיימים שהועלו:\n\n{files_text}"

    result: dict = {}
    with ThreadPoolExecutor(max_workers=len(DOC_ORDER)) as executor:
        futures = [
            executor.submit(_generate_one, client, letter, user_message)
            for letter in DOC_ORDER
        ]
        for future in futures:
            result.update(future.result())
    return result

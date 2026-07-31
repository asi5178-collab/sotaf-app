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
        "Report inconsistencies, gaps, and missing/incomplete content found between the "
        "uploaded project files and the SOTAF documents, shaped like the course's Doc H "
        "(מסמך בדיקת רציפות מסמכים) table."
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
                        "category": {
                            "type": "string",
                            "enum": ["contradiction", "missing_document", "missing_content", "vague_or_generic"],
                            "description": (
                                "contradiction = SOTAF text conflicts with an uploaded file; "
                                "missing_document = the whole SOTAF document is empty/unfilled but the "
                                "uploaded files contain relevant info for it; "
                                "missing_content = the document exists but a specific fact/section from the "
                                "uploaded files is absent from it; "
                                "vague_or_generic = the SOTAF text lacks the concrete numbers/specifics that "
                                "the uploaded files actually provide."
                            ),
                        },
                        "section": {
                            "type": "string",
                            "description": "Which section within that document, in Hebrew (e.g. 'בעלי עניין', 'מיפוי שירותי ניידות'). If the whole document is missing, name the most relevant section for the info found.",
                        },
                        "sotaf_info": {
                            "type": "string",
                            "description": "The information as currently stated in the SOTAF document, in Hebrew. If the document/section is empty, say so explicitly (e.g. 'הסעיף ריק').",
                        },
                        "conflicting_info": {
                            "type": "string",
                            "description": "The conflicting, missing, or more-specific information found in the uploaded project files, with the source filename, in Hebrew.",
                        },
                        "recommendation": {
                            "type": "string",
                            "description": "A concrete recommended fix to the SOTAF document, in Hebrew.",
                        },
                    },
                    "required": ["doc", "category", "section", "sotaf_info", "conflicting_info", "recommendation"],
                },
            }
        },
        "required": ["findings"],
    },
}

SYSTEM_PROMPT = """\
אתה עוזר בהכנת מסמך H (מסמך בדיקת רציפות מסמכים) בשיטת SOTAF - מסמך שמטרתו "איתור \
נקודות אי-התאמה בין מסמכי A-G" של פרויקט הנדסת מערכות. זו בדיקת איכות/טיוב נתונים \
יסודית, לא רק חיפוש סתירות בוטות.

תקבל את תוכן מסמכי ה-SOTAF שהמשתמש מילא (0, A, B, C1, D, E, F, G) - כולל מסמכים \
וסעיפים ריקים המסומנים במפורש - וקבצי פרויקט שהועלו (מצגות, דוחות, מסמכי דרישות, \
לעיתים כמה קבצים). עבור על כל מסמך וכל קובץ שיטתית, אחד-אחד, ודווח על כל אחד \
מסוגי הממצאים הבאים (השתמש בשדה category המתאים):

1. **contradiction** - מידע בקובץ שהועלה סותר במפורש מידע במסמך ה-SOTAF (למשל \
מספרים שונים, תיאורים סותרים).
2. **missing_document** - מסמך SOTAF שלם מסומן כ"ריק לחלוטין - טרם מולא כלל", \
אך הקבצים שהועלו מכילים מידע רלוונטי לאותו מסמך. חובה לדווח על כל מקרה כזה בנפרד \
- זהו אחד הממצאים החשובים ביותר בבדיקת רציפות מסמכים.
3. **missing_content** - המסמך קיים וממולא חלקית, אבל עובדה/פרט קונקרטי שמופיע \
בקבצים שהועלו (או שסעיף מסומן כ"טרם מולא") חסר ממנו.
4. **vague_or_generic** - הטקסט במסמך ה-SOTAF כללי/גנרי, בעוד שהקבצים שהועלו \
מספקים נתונים כמותיים/ספציפיים (מספרים, תאריכים, תקציבים, יעדים) שראוי לשלב במסמך.

הנחיות חשובות:
- אל תסתפק בסריקה שטחית אחר סתירות בולטות בלבד. עבור במפורש על כל אחד מהמסמכים \
0, A, B, C1, D, E, F, G מול כל קובץ שהועלה, ובדוק גם השלמה/דיוק, לא רק סתירה.
- אם מסמך מסומן כריק לחלוטין, וקבצי הפרויקט מכילים ולו פיסת מידע רלוונטית אליו - \
זה תמיד ממצא (category: missing_document). אל תדלג על כך.
- כאשר יש כמה קבצים שהועלו, ציין בכל ממצא באיזה קובץ (או קבצים) מדובר.
- דיווח על רשימה ריקה (אין ממצאים) הוא חריג ולא ברירת המחדל - קורה רק כאשר כל \
המסמכים כבר מלאים, ספציפיים, ותואמים לחלוטין את כל מה שמופיע בקבצים שהועלו. \
אם יש ספק, עדיף לדווח ולתת למשתמש להחליט אם הממצא רלוונטי.
- קרא ל-report_findings עם כל הממצאים, בפורמט הזהה לטבלת H2 הרשמית."""


def review(sotaf_documents: list[dict], uploaded_files: list[dict]) -> list[dict]:
    """sotaf_documents: [{'doc': 'A', 'rendered': '...'}, ...] — includes ALL
    documents, even empty ones, explicitly marked as such.
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
        f"מסמכי SOTAF נוכחיים ({len(sotaf_documents)} מסמכים, כולל ריקים):\n\n{docs_text}\n\n"
        f"קבצי הפרויקט שהועלו ({len(uploaded_files)} קבצים):\n\n{files_text}\n\n"
        "עבור שיטתית על כל מסמך מול כל קובץ ודווח באמצעות report_findings, בפורמט טבלת H2."
    )

    with client.messages.stream(
        model=MODEL,
        max_tokens=8000,
        system=SYSTEM_PROMPT,
        tools=[REPORT_TOOL],
        tool_choice={"type": "tool", "name": "report_findings"},
        output_config={"effort": "high"},
        messages=[{"role": "user", "content": user_message}],
    ) as stream:
        response = stream.get_final_message()

    for block in response.content:
        if block.type == "tool_use" and block.name == "report_findings":
            return block.input.get("findings", [])
    return []

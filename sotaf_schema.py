#!/usr/bin/env python3
"""The real SOTAF document schema, extracted from the actual course materials
(SOTAF architectureframwork.pdf, the official templates under 'תבניות מסמכים
הנדסיים', and real student submissions under 'הגשות'). Not invented.

Each document is a list of sections. A section is one of:
  - {"type": "text", "id", "label"}                         -> free-text paragraph
  - {"type": "table", "id", "label", "table_id", "columns", "seed"} -> repeatable rows
  - {"type": "repeat_group", "id", "label", "fields", "seed"}       -> repeatable multi-field cards
"""

DOC_ORDER = ["0", "A", "B", "C1", "D", "E", "F", "G", "H"]

DOC_META = {
    "0": {"title": "מסמך הגדרת האתגר המערכתי", "subtitle": "System Challenge Definition"},
    "A": {"title": "מסמך תפיסת מערכת", "subtitle": "System Concept"},
    "B": {"title": "מסמך טכנולוגיות", "subtitle": "Technology Mapping"},
    "C1": {"title": "מסמך דרישות הקישוריות", "subtitle": "Connectivity Requirements"},
    "D": {"title": "מסמך תפיסת הפעלה", "subtitle": "Operational Concept"},
    "E": {"title": "מסמך התפיסה העסקית", "subtitle": "Business Concept"},
    "F": {"title": "מסמך התפיסה הניהולית", "subtitle": "Management Concept"},
    "G": {"title": "מסמך מדיניות תמריצים וכללי משחוק", "subtitle": "Incentives & Gamification"},
    "H": {"title": "מסמך בדיקת רציפות מסמכים", "subtitle": "Document Consistency Check"},
}

# --- Canonical seed data (pre-seeded in the real course templates) ---

STAKEHOLDER_GROUPS_SEED = [
    "מפעיל השירות", "רשויות מקומיות", "יזמים/סטארטאפים",
    "קהילות משתמשים", "סטודנטים", "מרצים", "אורחים", "ספקים",
]

SCENARIOS_SEED = [
    {"קוד": "A", "שם התרחיש": "יום / עומס", "תיאור": "", "אירוע התחלה": "", "אירוע סיום": "", "רשות אחראית": ""},
    {"קוד": "B", "שם התרחיש": "לילה", "תיאור": "", "אירוע התחלה": "", "אירוע סיום": "", "רשות אחראית": ""},
    {"קוד": "C", "שם התרחיש": "חופשות סמסטר", "תיאור": "", "אירוע התחלה": "", "אירוע סיום": "", "רשות אחראית": ""},
    {"קוד": "D", "שם התרחיש": "אירוע המונים", "תיאור": "", "אירוע התחלה": "", "אירוע סיום": "", "רשות אחראית": ""},
    {"קוד": "E", "שם התרחיש": "אירוע אסון", "תיאור": "", "אירוע התחלה": "", "אירוע סיום": "", "רשות אחראית": ""},
]

SERVICES_SEED = [
    "מיקרומוביליטי", "קווי אוטובוס", "שאטלים", "שיתוף נסיעות", "חניה חכמה",
    "MaaS", "היסעי אירועי המונים", "פינוי בחירום", "תגמול ותמרוץ", "מוקד בקרת ניידות",
]

BUSINESS_MODELS_SEED = [
    "רכש מוצרי מדף", "פיתוח ואינטגרציה", "הפעלה ותחזוקה", "מכרז למפעיל",
    "מכרז זכיינות", "תקציב ממשלה", "סובסידיה ממשלתית", "קרן פיתוח", "מודל BOT",
]

REVENUE_CATEGORIES_SEED = [
    "הכנסות ממכירת השירות למשתמשים", "הכנסות מעמלת זיכיון למפעילים",
    "הכנסות מפרסום", "הכנסות ממכירת ידע הנדסי/תפעולי/ניהולי", "הכנסות מתמלוגים",
]

COST_CATEGORIES_SEED = [
    "פיתוח (NRE)", "רכש (RE)", "מימון", "ניהול", "תפעול",
    "תחזוקה", "סביבה", "פרסום והטמעה", "תמריצים",
]


def _stakeholder_table(table_id, columns, extra_seed_cols=None):
    seed = []
    for group in STAKEHOLDER_GROUPS_SEED:
        row = {columns[0]: group}
        for c in columns[1:]:
            row[c] = ""
        seed.append(row)
    return {
        "type": "table", "id": "stakeholders", "label": "בעלי עניין",
        "table_id": table_id, "columns": columns, "seed": seed,
    }


def _text(id_, label):
    return {"type": "text", "id": id_, "label": label}


def _table(id_, label, table_id, columns, seed=None):
    return {"type": "table", "id": id_, "label": label, "table_id": table_id,
            "columns": columns, "seed": seed or []}


DOCUMENTS = {
    "0": [
        _text("vision", "תמונת חזון"),
        _text("goals", "מטרות ויעדים"),
        _text("ecosystem", "תיאור מרחב המחיה (Ecosystem)"),
        _text("challenge", "הגדרת האתגר"),
        _stakeholder_table("01", ["קבוצת בעלי ענין", "ארגון", "אינטרסים", "הערות"]),
        _text("initiatives", "מארג היוזמות"),
        _text("mvp", "תכנון MVP"),
        _text("rollout_scope", "תיחום מרחב ההטמעה"),
        _text("transition", "תהליך השינוי (Transition)"),
        _text("sources", "מקורות (יוזמות דומות, מחקרים, מוצרים קיימים)"),
    ],
    "A": [
        _text("intro", "מבוא"),
        _text("purpose", "מטרות המסמך"),
        _text("service_concept", "תפיסת השירות החדש שיפותח"),
        _stakeholder_table("A1", ["קבוצת בעלי ענין", "ארגון", "אינטרסים", "הערות"]),
        _text("applicable_docs", "מסמכים ישימים"),
        _text("assumptions", "הנחות יסוד"),
        _table("services_map", "מיפוי שירותי ניידות (קיימים וחדשים)", "A2",
               ["תיאור השירות", "חדש/קיים", "מפעיל השירות", "הערות"],
               seed=[{"תיאור השירות": s, "חדש/קיים": "", "מפעיל השירות": "", "הערות": ""} for s in SERVICES_SEED]),
        _table("structure", "מבנה המערכת / המערכות המשולבות בפתרון", "A3",
               ["שם המערכת", "רכיב במערכת (Module)", "תיאור", "באחריות/ספק"]),
        _text("deployment", "פריסה מערכתית בזירת ההפעלה"),
        _table("capabilities", "יכולות מערכת", "A4", ["מערכת", "יכולת", "פרוט הדרישות"]),
        _table("interfaces", "ממשקים", "A5", ["ממערכת", "אל מערכת", "פרוט הממשק/ערוץ הנתונים"]),
        _table("specs", "דרישות מפרטיות", "A6", ["מערכת", "תת מערכת", "הפרמטר", "הדרישה כמותית"]),
        _text("glossary", "מונחים והגדרות"),
    ],
    "B": [
        _text("intro", "מבוא — RFI ודיאלוג מול ספקי טכנולוגיה"),
        {
            "type": "repeat_group", "id": "technologies", "label": "טכנולוגיות",
            "fields": [
                {"id": "name", "label": "שם הטכנולוגיה", "kind": "text"},
                {"id": "description", "label": "תיאור הטכנולוגיה", "kind": "textarea"},
                {"id": "products", "label": "דוגמאות למוצרים המבוססים על טכנולוגיה זו", "kind": "textarea"},
                {"id": "vendors", "label": "שמות יצרנים ומוצרים קיימים בשוק", "kind": "textarea"},
                {"id": "alternatives", "label": "טכנולוגיות חלופיות/מתחרות", "kind": "textarea"},
                {"id": "pros_cons", "label": "יתרונות/חסרונות מול טכנולוגיות חלופיות", "kind": "textarea"},
                {"id": "research", "label": "מחקרים, פרסומים וכתבות", "kind": "textarea"},
                {"id": "reviews", "label": "חוות דעת משתמשים", "kind": "textarea"},
            ],
            "seed": [],
        },
    ],
    "C1": [
        _text("intro", "מבוא"),
        _text("purpose", "מטרות המסמך"),
        _text("service_concept", "שם ותאור מילולי קצר של הפתרון המערכתי שיפותח"),
        _stakeholder_table("C1-1", ["קבוצת בעלי ענין", "ארגון", "אינטרסים", "הערות"]),
        _text("applicable_docs", "מסמכים ישימים"),
        _text("assumptions", "הנחות יסוד"),
        _table("scenarios", "תרחישים", "C1-2",
               ["קוד", "שם התרחיש", "תיאור", "אירוע התחלה", "אירוע סיום", "רשות אחראית"],
               seed=SCENARIOS_SEED),
        _table("systems_map", "מיפוי קשרים בין תתי מערכות/מערכות", "C1-3",
               ["שם המערכת", "תיאור", "באחריות/ספק"]),
        _text("backbone", "תצורת שלד הקישוריות (Backbone) — תיאור"),
        _table("interfaces", "ממשקים", "C1-4",
               ["קוד מערכת", "ממערכת", "אל מערכת", "תיאור", "פרטי הממשק/ערוץ הנתונים"]),
        _text("sequence_diagram", "Sequence Diagram — תיאור מילולי של רצף הפעולות"),
        _text("glossary", "מונחים והגדרות"),
    ],
    "D": [
        _text("intro", "מבוא"),
        _text("purpose", "מטרות המסמך"),
        _text("service_concept", "תפיסת השירות החדש שיפותח"),
        _table("stakeholders", "בעלי עניין", "D1",
               ["קבוצת בעלי ענין", "מאפייני השימוש", "עמדות/אינטרסים ביחס להפעלת השירות החדש"],
               seed=[{"קבוצת בעלי ענין": g, "מאפייני השימוש": "", "עמדות/אינטרסים ביחס להפעלת השירות החדש": ""} for g in STAKEHOLDER_GROUPS_SEED]),
        _text("applicable_docs", "מסמכים ישימים"),
        _text("assumptions", "הנחות יסוד"),
        _table("scenarios", "תרחישים", "D2",
               ["קוד", "שם התרחיש", "תיאור", "אירוע התחלה", "אירוע סיום", "רשות אחראית"],
               seed=SCENARIOS_SEED),
        _table("services_by_scenario", "פירוט שירותי ניידות (לפי תרחישים)", "D3",
               ["השירות", "שלב בתהליך", "המשתמש", "יעד ביצוע"]),
        _table("use_cases_map", "מיפוי מקרי שימוש (Use Cases)", "D4",
               ["התרחיש", "שירות/שלב", "בעל ענין", "UC#", "שם Use Case", "תיאור מילולי"]),
        {
            "type": "repeat_group", "id": "use_case_specs", "label": "הכנת מפרטי Use Case",
            "fields": [
                {"id": "uc_id", "label": "UC# / שם Use Case", "kind": "text"},
                {"id": "goal", "label": "מטרה / תיאור מילולי", "kind": "textarea"},
                {"id": "stakeholders", "label": "בעלי עניין ואינטרסים", "kind": "textarea"},
                {"id": "current", "label": "התהליך במצב הנוכחי", "kind": "textarea"},
                {"id": "desired", "label": "התהליך במצב הרצוי", "kind": "textarea"},
                {"id": "critical", "label": "Critical Use Case? (האם ממיר משתמשים לשירות החדש)", "kind": "text"},
                {"id": "negative_branch", "label": "הסתעפות שלילית (כשלים/סטיות)", "kind": "textarea"},
                {"id": "notes", "label": "הערות", "kind": "textarea"},
            ],
            "seed": [],
        },
        _text("risk_safety", "ניתוח סיכונים/בטיחות משתמש"),
        _text("glossary", "מונחים והגדרות"),
    ],
    "E": [
        _text("intro", "מבוא"),
        _text("purpose", "מטרות המסמך"),
        _text("audience", "קהל היעד של המסמך"),
        _text("glossary", "מונחים והגדרות"),
        _text("applicable_docs", "מסמכים ישימים (0, A, B, C, D)"),
        _table("business_models", "סקירת מודלים עסקיים", "E1",
               ["מודל עסקי", "מאפיינים", "הערות"],
               seed=[{"מודל עסקי": m, "מאפיינים": "", "הערות": ""} for m in BUSINESS_MODELS_SEED]),
        _table("users_estimate", "הערכת כמות משתמשים", "E2",
               ["השירות", "היקף משתמשים במצב הנוכחי", "היקף משתמשים צפוי", "סימולציה/סקר/תחזית", "פיילוט/MVP"]),
        _table("revenues", "ניתוח הכנסות לאורך מחזור חיים", "E3",
               ["קטגוריית הכנסה", "תיאור", "סכום שנתי משוער (₪)"],
               seed=[{"קטגוריית הכנסה": r, "תיאור": "", "סכום שנתי משוער (₪)": ""} for r in REVENUE_CATEGORIES_SEED]),
        _table("costs", "עלויות מחזור חיים", "E4",
               ["קטגוריית עלות", "תיאור", "סכום שנתי משוער (₪)"],
               seed=[{"קטגוריית עלות": c, "תיאור": "", "סכום שנתי משוער (₪)": ""} for c in COST_CATEGORIES_SEED]),
        _text("conclusions", "מסקנות והמלצות (מודל מומלץ, שנת איזון, מקורות מימון)"),
    ],
    "F": [
        _text("intro", "מבוא"),
        _text("purpose", "מטרות המסמך"),
        _text("audience", "קהל היעד של המסמך"),
        _text("glossary", "מונחים והגדרות"),
        _text("applicable_docs", "מסמכים ישימים (0, A, C, D, E)"),
        _stakeholder_table("F1", ["קבוצת בעלי ענין", "ארגון", "תחום אחריות", "הערות"]),
        _table("engineering_framework", "מבנה המסגרת ההנדסית", "F2",
               ["מחלקה", "יכולת ארגונית", "הערות"],
               seed=[{"מחלקה": m, "יכולת ארגונית": "", "הערות": ""} for m in ["הנדסת מערכות", "טכנולוגיות", "אינטגרציה", "בדיקות מערכת"]]),
        _table("operational_framework", "מבנה המסגרת התפעולית", "F3",
               ["מחלקה", "יכולת ארגונית", "הערות"],
               seed=[{"מחלקה": m, "יכולת ארגונית": "", "הערות": ""} for m in ["תפעול", "בקרת LOS", "מדדי שירות", "מדדי ניידות"]]),
        _table("management_framework", "מבנה המסגרת הניהולית", "F4",
               ["מחלקה", "יכולת ארגונית", "הערות"],
               seed=[{"מחלקה": m, "יכולת ארגונית": "", "הערות": ""} for m in ["מדיניות ניידות", "פרסום ותמריצים", "ניהול פרויקטים", "תחקיר ושיפור"]]),
        _table("risks", "ניהול סיכונים", "F5",
               ["תחום", "פירוט הסיכון", "פעולות לצמצום הסיכון", "חומרה", "שכיחות"]),
    ],
    "G": [
        _text("intro", "מבוא"),
        _text("purpose", "מטרות המסמך"),
        _text("glossary", "מונחים והגדרות"),
        _text("applicable_docs", "מסמכים ישימים"),
        _stakeholder_table("G1", ["קבוצת בעלי ענין", "ארגון", "אינטרסים", "הערות"]),
        _table("services_map", "מיפוי שירותי ניידות", "G2",
               ["תיאור השירות", "חדש/קיים", "מפעיל השירות", "הערות"],
               seed=[{"תיאור השירות": s, "חדש/קיים": "", "מפעיל השירות": "", "הערות": ""} for s in SERVICES_SEED]),
        _text("service_goals", "תיאור השירות החדש והתכלית, יעדי שירות כמותיים"),
        _table("incentive_planning", "תכנון תמריצים", "G3",
               ["השירות", "קהל יעד", "מנגנון תמריץ / משחוק", "מדד הצלחה"]),
    ],
    "H": [
        _text("intro", "מבוא"),
        _text("purpose", "מטרות המסמך — איתור נקודות אי-התאמה בין מסמכי A-G"),
        _text("glossary", "מונחים והגדרות"),
        _text("applicable_docs", "מסמכים ישימים (A-G)"),
        _stakeholder_table("H1", ["קבוצת בעלי ענין", "ארגון", "תפקיד בתהליך הבדיקה", "הערות"]),
        _text("process", "תאור תהליך בדיקת המסמכים"),
        _table("findings", "ממצאי אי-התאמה", "H2",
               ["מסמך הנדסי / סעיף", "מידע הנדסי", "לא תואם מידע במסמך", "מידע הנדסי סותר", "תיקון נדרש"]),
    ],
}


def blank_metadata() -> dict:
    """An empty metadata dict shaped like the schema, ready to be filled in."""
    metadata = {"project_name": "", "author": "", "version": "0.1"}
    for doc in DOC_ORDER:
        doc_data = {}
        for section in DOCUMENTS[doc]:
            if section["type"] == "text":
                doc_data[section["id"]] = ""
            else:
                doc_data[section["id"]] = list(section.get("seed") or [])
        metadata[doc] = doc_data
    return metadata


def doc_progress(metadata: dict, doc: str) -> tuple[int, int]:
    """(filled, total) section count for a document, to show progress on the hub."""
    sections = DOCUMENTS[doc]
    filled = 0
    for section in sections:
        value = metadata.get(doc, {}).get(section["id"])
        if section["type"] == "text":
            if value and value.strip():
                filled += 1
        else:
            if value and any(any((v or "").strip() for v in row.values()) for row in value):
                filled += 1
    return filled, len(sections)

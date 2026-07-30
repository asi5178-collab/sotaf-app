#!/usr/bin/env python3
"""Reference library of real past SOTAF projects from the course, for
inspiration when describing a new system. Descriptions only — not the
original files (those live outside the repo, on the course owner's disk)."""

EXAMPLE_PROJECTS = [
    {
        "id": "public-transport",
        "name": "MaaS קמפוסי — תחבורה ציבורית",
        "topic": "Public Transportation",
        "description": (
            "פלטפורמת MaaS קמפוסית המאחדת אוטובוסים, שיתוף נסיעות, מיקרומוביליטי "
            "(קורקינטים) ורכבים אוטונומיים לאפליקציה אחת, במטרה לצמצם עומסי תנועה "
            "וזיהום ולשפר נגישות."
        ),
        "docs": ["A", "B", "C1", "F"],
    },
    {
        "id": "share-rides",
        "name": "GreenShare — הרחבת נסיעות שיתופיות",
        "topic": "Scaling Up Share Rides",
        "description": (
            "פלטפורמה דיגיטלית להגברת האימוץ של נסיעות שיתופיות בקמפוס, עם שידוך "
            "מסלולים מבוסס AI ומנגנוני תמריצים, בשילוב עם תחבורה ציבורית. יעד: 70% "
            "מהנסיעות בשיתוף/תחבורה ציבורית עד 2050."
        ),
        "docs": ["A", "C1", "D", "E"],
    },
    {
        "id": "backbone",
        "name": "Backbone — שדרת קישוריות קמפוסית",
        "topic": "Campus Mobility Backbone",
        "description": (
            "לא שירות ניידות בודד אלא שכבת אינטגרציה/תשתית המחברת את כלל פרויקטי "
            "הניידות בקמפוס (מיקרומוביליטי, תחבורה ציבורית, נסיעות שיתופיות, חניה "
            "חכמה, MaaS, מוקד ניהול ניידות) לכדי אקוסיסטם מתואם אחד, מבוסס API."
        ),
        "docs": ["0", "C1", "D"],
    },
    {
        "id": "micromobility",
        "name": "שירותי מיקרומוביליטי קמפוסיים",
        "topic": "Campus Micromobility Services",
        "description": (
            "שירות שיתוף קורקינטים חשמליים לתנועה בין הקמפוס העליון והתחתון "
            "(כ-18,000 סטודנטים, 500+ סגל), שמטרתו לצמצם תלות ברכב פרטי ועומסי "
            "תנועה באזור הקמפוס."
        ),
        "docs": ["0", "A", "B", "C1", "D", "E"],
    },
    {
        "id": "emergency-evacuation",
        "name": "פינוי בחירום מבוסס תחבורה ציבורית",
        "topic": "Emergency Evacuation",
        "description": (
            "שימוש במערכת התחבורה הציבורית הקיימת כשדרת גב לפינוי המוני של הקמפוס "
            "במצב חירום, עם תכנון עד שנת 2031. דוגמה לתחום שונה לגמרי מאשכול הניידות/MaaS."
        ),
        "docs": ["A", "B", "C1", "E"],
    },
    {
        "id": "mobility-management-center",
        "name": "מוקד ניהול ניידות חכם",
        "topic": "Campus Mobility Management Center",
        "description": (
            "מוקד בקרה מרכזי המרכז נתונים בזמן אמת מאפליקציה ייעודית, חיישני חניה "
            "חכמה וצי שאטלים, בשאיפה ל-30% שימוש בתחבורה ציבורית/שאטלים. משלים "
            "טבעי לפרויקט ה-Backbone כצרכן הנתונים המרכזי שלו."
        ),
        "docs": ["A", "D"],
    },
]

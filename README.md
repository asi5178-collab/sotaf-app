# SOTAF App (templates A–G)

כלי קטן ליצירת מסמכי SOTAF A–G מבוססי תבניות Markdown ובדיקת אי‑התאמות בסיסית בין המסמכים.

## שימוש כ-CLI

1. עדכן `sample_metadata.json` עם שדות הפרויקט.
2. הרץ:

```bash
python generate.py sample_metadata.json
python checker.py output/summaries
```

## שימוש כאפליקציית Web

```bash
pip install -r requirements.txt
python app.py
```

פותח שרת Flask מקומי (ברירת מחדל פורט 5000) עם טופס להדבקה/העלאת metadata JSON, שמציג את המסמכים המלאים ואת דוח העקביות בדפדפן — בלי לכתוב קבצים לדיסק.

## פריסה ל-Railway

הפרויקט כולל `Procfile` ו-`railway.json` שמריצים `gunicorn app:app`. לפריסה:

```bash
railway up
```

קבצים חשובים:
- `templates/` — תבניות A..G למילוי (משמשות גם CLI וגם Web)
- `templates_web/` — תבנית ה-HTML של ממשק ה-Web
- `generate.py` — ממלא תבניות (CLI: כותב ל-`output/`; מיוצא כפונקציה `generate_all` לשימוש ב-`app.py`)
- `checker.py` — בדיקות עקביות (CLI: קורא מ-`output/summaries`; מיוצא כפונקציה `analyze` לשימוש ב-`app.py`)
- `app.py` — ממשק Web (Flask)

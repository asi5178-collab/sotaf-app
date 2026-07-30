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
export ANTHROPIC_API_KEY=sk-ant-...   # נדרש לפיצ'ר הניתוח עם AI
python app.py
```

פותח שרת Flask מקומי (ברירת מחדל פורט 5000) עם זרימה בת שני שלבים:

1. **טופס מונחה** — הזנת פרטי הפרויקט ותוכן כל אחד ממסמכי SOTAF A–G בשדות נפרדים. בשליחה, המערכת יוצרת את 7 המסמכים ומריצה דוח עקביות בין המסמכים עצמם.
2. **סקירה + ניתוח AI** — מציג את המסמכים שנוצרו ומאפשר להעלות קבצי פרויקט קיימים (PDF/Word). Claude (`claude-opus-5`) משווה את תוכן הקבצים למסמכי ה-SOTAF, מאתר אי-התאמות עובדתיות וממליץ על תיקון קונקרטי לכל מסמך.

מצב הסשן (metadata + מסמכים) נשמר בזיכרון השרת (לא בקובץ ולא בעוגייה) — מתאים לפריסה של worker יחיד.

## פריסה ל-Railway

הפרויקט כולל `Procfile` ו-`railway.json` שמריצים `gunicorn app:app`. יש להגדיר את משתנה הסביבה `ANTHROPIC_API_KEY` בפרויקט ב-Railway (`railway variable set ANTHROPIC_API_KEY --stdin`). לפריסה:

```bash
railway up
```

קבצים חשובים:
- `templates/` — תבניות A..G למילוי (משמשות גם CLI וגם Web)
- `templates_web/` — תבניות ה-HTML של ממשק ה-Web (`form.html`, `review.html`, `base.html`)
- `generate.py` — ממלא תבניות (CLI: כותב ל-`output/`; מיוצא כפונקציה `generate_all` לשימוש ב-`app.py`)
- `checker.py` — בדיקות עקביות (CLI: קורא מ-`output/summaries`; מיוצא כפונקציה `analyze` לשימוש ב-`app.py`)
- `extract.py` — חילוץ טקסט מקבצי PDF/DOCX שהועלו
- `ai_review.py` — קריאה ל-Claude API להשוואת קבצי הפרויקט מול מסמכי ה-SOTAF
- `app.py` — ממשק Web (Flask) — טופס מונחה, סקירה, והעלאת קבצים לניתוח

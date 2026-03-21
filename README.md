# 🛒 מערכת ניהול רשימת קניות

אפליקציית Streamlit לניהול רשימות קניות מבוססת סלולאר.

## ✨ תכונות
- 📋 **ניהול מרובה רשימות** — צור רשימות שונות לאירועים שונים
- 🗂️ **מיון אוטומטי לפי קטגוריות** — הפריטים מסודרים אוטומטית (חלב, בשר, ירקות...)
- 📊 **מד התקדמות** — רואים בדיוק כמה פריטים נאספו
- 📜 **היסטוריה** — כל קנייה נשמרת ואפשר לשחזר רשימות ישנות
- 🎯 **תבניות מהירות** — קניות שבועיות, מסיבה, בריאות
- 📱 **ממשק מותאם לנייד** — RTL עברית מלאה

## 🚀 התקנה והפעלה מקומית

```bash
# 1. שכפל את הריפוזיטורי
git clone https://github.com/YOUR_USERNAME/shopping-list.git
cd shopping-list

# 2. התקן תלויות
pip install -r requirements.txt

# 3. הפעל
streamlit run app.py
```

## ☁️ פריסה ל-Streamlit Cloud

### שלב 1 — העלה ל-GitHub
```bash
git init
git add .
git commit -m "Initial commit: Shopping List App"
git remote add origin https://github.com/YOUR_USERNAME/shopping-list.git
git push -u origin main
```

### שלב 2 — פרוס ב-Streamlit Cloud
1. היכנס ל-[share.streamlit.io](https://share.streamlit.io)
2. לחץ **"New app"**
3. בחר את הריפוזיטורי: `YOUR_USERNAME/shopping-list`
4. Branch: `main`
5. Main file: `app.py`
6. לחץ **"Deploy!"**

### שלב 3 — שיתוף
- קבל קישור בצורת: `https://YOUR_USERNAME-shopping-list.streamlit.app`
- שתף עם בני משפחה!

## 📁 מבנה הקבצים

```
shopping-list/
├── app.py                  # האפליקציה הראשית
├── requirements.txt        # תלויות Python
├── .streamlit/
│   └── config.toml        # הגדרות עיצוב
├── shopping_data.json      # נוצר אוטומטית — נתוני הרשימות
└── README.md
```

## ⚠️ הערה על שמירת נתונים
- בסביבה המקומית: הנתונים נשמרים ב-`shopping_data.json`
- ב-Streamlit Cloud: הנתונים **לא נשמרים** בין deployments
- לשמירה קבועה: מומלץ לחבר Google Sheets או Supabase

## 🔧 הוספת שמירה קבועה (אופציונלי)
להוסיף Google Sheets כ-backend — צור issue בריפוזיטורי.

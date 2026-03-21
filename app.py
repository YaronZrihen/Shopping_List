import streamlit as st
import json
import os
from datetime import datetime
import uuid

st.set_page_config(
    page_title="🛒 רשימת קניות",
    page_icon="🛒",
    layout="centered",
    initial_sidebar_state="collapsed",
)

CATEGORIES = {
    "🥦 ירקות ופירות": ["ירקות", "פירות", "עגבניה", "מלפפון", "חסה", "תפוח", "בננה", "לימון"],
    "🥛 מוצרי חלב": ["חלב", "גבינה", "יוגורט", "חמאה", "שמנת", "קוטג"],
    "🥩 בשר ודגים": ["בשר", "עוף", "דגים", "נקניק", "המבורגר"],
    "🍞 לחם ומאפים": ["לחם", "חלה", "פיתה", "קרוואסון", "בייגל"],
    "🥫 שימורים ויבשים": ["שימור", "פסטה", "אורז", "קטניות", "דגנים", "קמח", "סוכר"],
    "🧃 משקאות": ["מיץ", "מים", "סודה", "קפה", "תה", "שתייה"],
    "🧹 ניקיון ובית": ["סבון", "אבקה", "ניקיון", "נייר", "שקיות"],
    "🍬 חטיפים וממתקים": ["שוקולד", "ביסקוויט", "חטיף", "ממתק", "עוגה", "גלידה"],
    "🧴 טיפוח ובריאות": ["שמפו", "קרם", "ויטמין", "תרופה", "מברשת"],
    "🌿 תבלינים ורטבים": ["מלח", "פלפל", "שמן", "חומץ", "רוטב", "תבלין"],
    "❄️ קפואים": ["קפוא", "פיצה קפואה", "ירקות קפואים"],
    "🐾 מוצרי חיות": ["חתול", "כלב", "מזון לחיות"],
    "🛒 שונות": [],
}

DATA_FILE = "shopping_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"lists": {}, "history": [], "current_list": None}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def guess_category(item_name):
    name_lower = item_name.lower()
    for cat, keywords in CATEGORIES.items():
        for kw in keywords:
            if kw in name_lower:
                return cat
    return "🛒 שונות"

def get_list_stats(items):
    total = len(items)
    checked = sum(1 for i in items if i.get("checked"))
    return total, checked

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap');
  html, body, [class*="css"] { font-family: 'Heebo', sans-serif; direction: rtl; }
  .stApp { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 50%, #f0f9ff 100%); }
  #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
  .main-header {
    background: linear-gradient(135deg, #16a34a, #15803d);
    color: white; padding: 1.2rem 1.5rem; border-radius: 16px;
    margin-bottom: 1rem; text-align: center;
    box-shadow: 0 4px 20px rgba(22,163,74,0.3);
  }
  .main-header h1 { margin: 0; font-size: 1.8rem; font-weight: 900; }
  .main-header p { margin: 0.2rem 0 0; font-size: 0.9rem; opacity: 0.85; }
  .progress-container {
    background: white; border-radius: 12px; padding: 0.8rem 1rem;
    margin-bottom: 0.8rem; box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  }
  .cat-header {
    background: white; border-radius: 10px; padding: 0.5rem 0.9rem;
    margin: 0.7rem 0 0.3rem; font-weight: 700; font-size: 0.95rem;
    color: #166534; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    border-right: 4px solid #16a34a;
  }
  .history-item {
    background: white; border-radius: 10px; padding: 0.7rem 1rem;
    margin-bottom: 0.4rem; box-shadow: 0 1px 4px rgba(0,0,0,0.05);
    border-right: 3px solid #86efac;
  }
  .block-container { padding: 0.5rem 0.8rem 2rem !important; max-width: 520px !important; }
  .stButton button {
    border-radius: 10px !important; font-family: 'Heebo', sans-serif !important;
    font-weight: 600 !important;
  }
  .stTextInput input, .stSelectbox select, .stNumberInput input {
    border-radius: 10px !important; direction: rtl !important;
    font-family: 'Heebo', sans-serif !important;
  }
  .stTabs [data-baseweb="tab"] { font-family: 'Heebo', sans-serif !important; font-weight: 600 !important; }
</style>
""", unsafe_allow_html=True)

if "data" not in st.session_state:
    st.session_state.data = load_data()

data = st.session_state.data

st.markdown('<div class="main-header"><h1>🛒 רשימת קניות</h1><p>ניהול חכם לסל הקניות שלך</p></div>', unsafe_allow_html=True)

tab_list, tab_manage, tab_history = st.tabs(["📋 רשימה פעילה", "📂 ניהול רשימות", "📜 היסטוריה"])

# ── TAB 1: Active List ──────────────────────────────────────────────────────────
with tab_list:
    lists = data.get("lists", {})
    if not lists:
        st.info("⬅️ עבור ל'ניהול רשימות' כדי ליצור רשימה חדשה")
    else:
        list_names = list(lists.keys())
        current = data.get("current_list") or list_names[0]
        if current not in list_names:
            current = list_names[0]

        selected = st.selectbox("📋 בחר רשימה", list_names, index=list_names.index(current))
        data["current_list"] = selected
        save_data(data)

        items = lists[selected]
        total, checked = get_list_stats(items)
        pct = int(checked / total * 100) if total > 0 else 0

        st.markdown(f"""
        <div class="progress-container">
          <div style="display:flex;justify-content:space-between;font-size:0.82rem;color:#4b5563;margin-bottom:0.4rem">
            <span>✅ {checked} מתוך {total} פריטים</span><span>{pct}%</span>
          </div>
          <div style="background:#e5e7eb;border-radius:99px;height:10px;overflow:hidden">
            <div style="background:linear-gradient(90deg,#16a34a,#4ade80);height:100%;width:{pct}%;border-radius:99px;transition:width 0.4s"></div>
          </div>
        </div>""", unsafe_allow_html=True)

        with st.expander("➕ הוסף פריט", expanded=False):
            c1, c2 = st.columns([3, 1])
            new_name = c1.text_input("שם המוצר", key="nin", placeholder="חלב, לחם, עגבניות...")
            new_qty = c2.number_input("כמות", min_value=1, max_value=99, value=1, key="nqty")
            cat_options = list(CATEGORIES.keys())
            auto_cat = guess_category(new_name) if new_name else "🛒 שונות"
            new_cat = st.selectbox("קטגוריה", cat_options, index=cat_options.index(auto_cat), key="ncat")
            note = st.text_input("הערה", key="nnote", placeholder="מותג, גודל, כמות...")
            if st.button("➕ הוסף לרשימה", use_container_width=True, type="primary"):
                if new_name.strip():
                    lists[selected].append({
                        "id": str(uuid.uuid4()),
                        "name": new_name.strip(),
                        "qty": new_qty,
                        "category": new_cat,
                        "note": note.strip(),
                        "checked": False,
                        "added": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    })
                    save_data(data)
                    st.rerun()

        by_cat = {}
        for item in items:
            cat = item.get("category", "🛒 שונות")
            by_cat.setdefault(cat, []).append(item)

        for cat, cat_items in sorted(by_cat.items(), key=lambda x: all(i.get("checked") for i in x[1])):
            st.markdown(f'<div class="cat-header">{cat} <span style="color:#86efac;font-weight:400;font-size:0.82rem">({len(cat_items)})</span></div>', unsafe_allow_html=True)
            for item in cat_items:
                col_check, col_info, col_del = st.columns([1, 7, 1])
                with col_check:
                    new_check = st.checkbox("", value=item.get("checked", False), key=f"chk_{item['id']}")
                    if new_check != item.get("checked"):
                        item["checked"] = new_check
                        save_data(data)
                        st.rerun()
                with col_info:
                    style = "text-decoration:line-through;opacity:0.5" if item.get("checked") else ""
                    qty = f" <span style='background:#dcfce7;color:#166534;border-radius:99px;padding:0.1rem 0.5rem;font-size:0.75rem;font-weight:700'>×{item['qty']}</span>" if item['qty'] > 1 else ""
                    note_html = f"<br><span style='font-size:0.73rem;color:#9ca3af'>{item['note']}</span>" if item.get("note") else ""
                    st.markdown(f'<div style="padding:0.5rem 0;{style}"><span style="font-weight:500">{item["name"]}</span>{qty}{note_html}</div>', unsafe_allow_html=True)
                with col_del:
                    if st.button("🗑", key=f"del_{item['id']}"):
                        lists[selected] = [i for i in lists[selected] if i["id"] != item["id"]]
                        save_data(data)
                        st.rerun()

        st.markdown("---")
        c1, c2 = st.columns(2)
        with c1:
            if st.button("🗑️ נקה מסומנים", use_container_width=True):
                lists[selected] = [i for i in lists[selected] if not i.get("checked")]
                save_data(data)
                st.rerun()
        with c2:
            if st.button("✅ סמן הכל", use_container_width=True):
                for item in lists[selected]:
                    item["checked"] = True
                save_data(data)
                st.rerun()

        if st.button("📦 סיים ושמור בהיסטוריה", use_container_width=True, type="primary"):
            if lists[selected]:
                data.setdefault("history", []).insert(0, {
                    "id": str(uuid.uuid4()),
                    "list_name": selected,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "items": lists[selected].copy(),
                    "total": total, "checked": checked,
                })
                lists[selected] = []
                save_data(data)
                st.success("✅ הרשימה נשמרה בהיסטוריה!")
                st.rerun()

# ── TAB 2: Manage Lists ────────────────────────────────────────────────────────
with tab_manage:
    st.markdown("#### 📂 הרשימות שלי")
    lists = data.get("lists", {})

    for list_name, items in list(lists.items()):
        total, checked = get_list_stats(items)
        pct = int(checked / total * 100) if total > 0 else 0
        is_active = list_name == data.get("current_list")
        icon = "🟢" if is_active else "⚪"
        c1, c2 = st.columns([8, 1])
        with c1:
            if st.button(f"{icon} {list_name}  •  {total} פריטים  •  {pct}%", key=f"sel_{list_name}", use_container_width=True):
                data["current_list"] = list_name
                save_data(data)
                st.rerun()
        with c2:
            if st.button("❌", key=f"rm_{list_name}"):
                del data["lists"][list_name]
                remaining = list(data["lists"].keys())
                data["current_list"] = remaining[0] if remaining else None
                save_data(data)
                st.rerun()

    st.markdown("---")
    st.markdown("#### ➕ צור רשימה חדשה")
    new_list_name = st.text_input("שם הרשימה", placeholder="קניות שבועיות, יום שישי...", key="new_list_nm")

    TEMPLATES = {
        "🏠 שבועי": [("חלב 3%",2,"🥛 מוצרי חלב","1 ליטר"),("לחם",1,"🍞 לחם ומאפים",""),("עגבניות",1,"🥦 ירקות ופירות",""),("מלפפונים",1,"🥦 ירקות ופירות",""),("ביצים",1,"🥛 מוצרי חלב","12 יח'"),("עוף",1,"🥩 בשר ודגים","חזה")],
        "🎉 מסיבה": [("שתייה קלה",4,"🧃 משקאות",""),("חטיפים",3,"🍬 חטיפים וממתקים",""),("לחמניות",2,"🍞 לחם ומאפים",""),("נקניקיות",2,"🥩 בשר ודגים","")],
        "🥗 בריאות": [("ירקות מעורבים",1,"🥦 ירקות ופירות",""),("קינואה",1,"🥫 שימורים ויבשים",""),("חזה עוף",2,"🥩 בשר ודגים",""),("יוגורט 0%",3,"🥛 מוצרי חלב","")],
    }

    st.markdown("**תבניות מהירות:**")
    cols = st.columns(3)
    for col, (tname, titems) in zip(cols, TEMPLATES.items()):
        with col:
            if st.button(tname, use_container_width=True, key=f"t_{tname}"):
                base = tname.split(" ", 1)[1]
                lkey = f"{base} {datetime.now().strftime('%d/%m')}"
                data["lists"][lkey] = [{"id": str(uuid.uuid4()), "name": n, "qty": q, "category": c, "note": nt, "checked": False, "added": datetime.now().strftime("%d/%m/%Y %H:%M")} for n,q,c,nt in titems]
                data["current_list"] = lkey
                save_data(data)
                st.success(f"✅ רשימת '{lkey}' נוצרה!")
                st.rerun()

    if st.button("➕ צור רשימה ריקה", use_container_width=True, type="primary"):
        if new_list_name.strip():
            if new_list_name.strip() not in data["lists"]:
                data["lists"][new_list_name.strip()] = []
                data["current_list"] = new_list_name.strip()
                save_data(data)
                st.success(f"✅ הרשימה '{new_list_name}' נוצרה!")
                st.rerun()
            else:
                st.warning("⚠️ רשימה בשם זה כבר קיימת")
        else:
            st.warning("⚠️ הכנס שם לרשימה")

# ── TAB 3: History ─────────────────────────────────────────────────────────────
with tab_history:
    history = data.get("history", [])
    if not history:
        st.info("📭 אין היסטוריה עדיין. סיים רשימת קניות כדי לשמור אותה כאן.")
    else:
        st.markdown(f"#### 📜 {len(history)} קניות קודמות")
        if st.button("🗑️ נקה היסטוריה"):
            data["history"] = []
            save_data(data)
            st.rerun()

        for entry in history:
            with st.expander(f"🛍️ {entry['list_name']} — {entry['date']} ({entry['total']} פריטים)"):
                by_cat = {}
                for item in entry["items"]:
                    by_cat.setdefault(item.get("category", "🛒 שונות"), []).append(item)
                for cat, citems in by_cat.items():
                    st.markdown(f"**{cat}**")
                    for item in citems:
                        chk = "✅" if item.get("checked") else "⬜"
                        qty = f" ×{item['qty']}" if item["qty"] > 1 else ""
                        nt = f" _({item['note']})_" if item.get("note") else ""
                        st.markdown(f"{chk} {item['name']}{qty}{nt}")
                st.markdown("---")
                if st.button("♻️ שחזר רשימה זו", key=f"restore_{entry['id']}"):
                    rname = f"{entry['list_name']} (שוחזר)"
                    data["lists"][rname] = [{**i, "id": str(uuid.uuid4()), "checked": False} for i in entry["items"]]
                    data["current_list"] = rname
                    save_data(data)
                    st.success(f"✅ הרשימה שוחזרה!")
                    st.rerun()

import streamlit as st
import json, os, uuid
from datetime import datetime

st.set_page_config(page_title="🛒 קניות", page_icon="🛒", layout="centered", initial_sidebar_state="collapsed")

CATEGORIES = {
    "🥛 מוצרי חלב":       ["חלב","גבינה","יוגורט","חמאה","שמנת","קוטג","ביצ"],
    "🥦 ירקות ופירות":     ["ירק","פרי","עגבני","מלפפ","חסה","תפוח","בננה","לימון","פלפל","גזר","בצל","תפוח אדמה"],
    "🥩 בשר ודגים":        ["בשר","עוף","דג","נקניק","המבורגר","שניצל","כבש"],
    "🍞 לחם ומאפים":       ["לחם","חלה","פיתה","קרואס","בייגל","לחמני"],
    "🥫 שימורים ויבשים":   ["שימור","פסט","אורז","קטנית","דגן","קמח","סוכר","עדשים"],
    "🧃 משקאות":           ["מיץ","מים","סודה","קפה","תה","שתייה","ענב","תפוז"],
    "🧹 ניקיון ובית":      ["סבון","אבקה","ניקיון","נייר","שקית","מגבת","כלים"],
    "🍬 חטיפים וממתקים":   ["שוקולד","ביסקוויט","חטיף","ממתק","עוגה","גלידה","בונבון"],
    "🧴 טיפוח ובריאות":    ["שמפו","קרם","ויטמין","תרופה","מברשת","סבון פנים"],
    "🌿 תבלינים ורטבים":   ["מלח","פלפל שחור","שמן","חומץ","רוטב","תבלין","כורכום"],
    "❄️ קפואים":           ["קפוא","פיצה קפו","ירקות קפו"],
    "🐾 מוצרי חיות":       ["חתול","כלב","מזון לחי"],
    "🛒 שונות":            [],
}

DATA_FILE = "shopping_data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE,"r",encoding="utf-8") as f: return json.load(f)
    return {"lists":{},"history":[],"current_list":None}

def save_data(d):
    with open(DATA_FILE,"w",encoding="utf-8") as f: json.dump(d,f,ensure_ascii=False,indent=2)

def guess_cat(name):
    n = name.lower()
    for cat,kws in CATEGORIES.items():
        for kw in kws:
            if kw in n: return cat
    return "🛒 שונות"

def stats(items): 
    t=len(items); c=sum(1 for i in items if i.get("checked")); return t,c

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"], [data-testid] { font-family: 'Heebo', sans-serif !important; direction: rtl; }

.stApp { background: #f7faf8 !important; }
#MainMenu,footer,header,[data-testid="stToolbar"] { visibility:hidden !important; display:none !important; }
.block-container { padding: 0 !important; max-width: 430px !important; margin: 0 auto; }

/* ── Top bar ── */
.topbar {
  background: #1c7a42;
  padding: 22px 20px 14px;
  margin-bottom: 0;
}
.topbar h1 { color:#fff; font-size:20px; font-weight:700; margin:0 0 3px; }
.topbar .sub { color:rgba(255,255,255,0.72); font-size:13px; }
.prog-wrap { background:rgba(255,255,255,0.25); border-radius:99px; height:5px; margin-top:10px; }
.prog-fill { background:#7de8a4; height:5px; border-radius:99px; transition:width .4s; }
.prog-row { display:flex; justify-content:space-between; font-size:12px; color:rgba(255,255,255,0.75); margin-top:4px; }

/* ── Category header ── */
.cat-label {
  font-size:11px; font-weight:500; color:#5f6f68;
  padding:14px 18px 5px;
  text-transform:uppercase; letter-spacing:.06em;
}

/* ── Item row ── */
.item-card {
  display:flex; align-items:center; gap:12px;
  padding:11px 18px;
  border-bottom:1px solid #f0f0ef;
  background:#fff;
  transition: background .15s;
}
.item-card:hover { background:#fafffe; }
.item-name { font-size:15px; color:#1a2e22; font-weight:400; }
.item-note { font-size:12px; color:#92a89a; margin-top:1px; }
.item-card.done .item-name { text-decoration:line-through; color:#b0bdb5; }
.check-circle {
  width:24px; height:24px; border-radius:50%;
  border:1.5px solid #1c7a42;
  flex-shrink:0; display:flex; align-items:center; justify-content:center;
  cursor:pointer; transition:all .15s;
}
.check-circle.checked { background:#1c7a42; border-color:#1c7a42; }
.qty-pill { background:#eaf7f0; color:#1c7a42; font-size:11px; font-weight:500; padding:2px 9px; border-radius:99px; white-space:nowrap; }

/* ── Empty state ── */
.empty-state { text-align:center; padding:50px 20px; color:#92a89a; }
.empty-state .icon { font-size:40px; margin-bottom:12px; }
.empty-state p { font-size:15px; }

/* ── History card ── */
.hist-card { background:#fff; border-radius:14px; margin:10px 14px; padding:14px 16px; border:1px solid #eef0ed; }
.hist-title { font-size:15px; font-weight:500; color:#1a2e22; }
.hist-meta { font-size:12px; color:#92a89a; margin-top:2px; }

/* ── Streamlit widgets override ── */
.stTabs { margin:0 !important; }
.stTabs [data-baseweb="tab-list"] {
  background:#fff !important; border-bottom:1px solid #e8ede9 !important;
  gap:0 !important; padding:0 !important;
}
.stTabs [data-baseweb="tab"] {
  font-family:'Heebo',sans-serif !important; font-size:13px !important;
  font-weight:500 !important; color:#7a8f82 !important;
  padding:10px 0 !important; flex:1 !important; text-align:center !important;
  border-bottom:2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
  color:#1c7a42 !important; border-bottom-color:#1c7a42 !important;
  background:transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding:0 !important; }

div[data-testid="stVerticalBlock"] > div { gap:0 !important; }

.stButton button {
  font-family:'Heebo',sans-serif !important; font-weight:500 !important;
  border-radius:12px !important;
}
button[kind="primary"] {
  background:#1c7a42 !important; border-color:#1c7a42 !important; color:#fff !important;
}
button[kind="primary"]:hover { background:#155e33 !important; }

.stTextInput input, .stNumberInput input, .stSelectbox > div > div {
  direction:rtl !important; font-family:'Heebo',sans-serif !important;
  border-radius:12px !important; font-size:15px !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label {
  font-family:'Heebo',sans-serif !important; font-size:13px !important; color:#5f6f68 !important;
}
[data-testid="stExpander"] { border:none !important; background:#fff !important; border-radius:14px !important; margin:10px 12px 6px !important; box-shadow:0 1px 4px rgba(0,0,0,.06) !important; }
[data-testid="stExpanderDetails"] { padding:0 14px 14px !important; }
[data-testid="stCheckbox"] { display:none !important; }

.stSelectbox [data-baseweb="select"] { direction:rtl; }
</style>
""", unsafe_allow_html=True)

if "data" not in st.session_state:
    st.session_state.data = load_data()
data = st.session_state.data

# ═══ TOPBAR ═══════════════════════════════════════════════════════════════════
lists = data.get("lists", {})
current = data.get("current_list")
if lists:
    if current not in lists: current = list(lists.keys())[0]
    items = lists.get(current, [])
    total, checked = stats(items)
    pct = int(checked/total*100) if total else 0
    date_str = datetime.now().strftime("%A, %-d ב%B").replace("Monday","שני").replace("Tuesday","שלישי").replace("Wednesday","רביעי").replace("Thursday","חמישי").replace("Friday","שישי").replace("Saturday","שבת").replace("Sunday","ראשון").replace("January","ינואר").replace("February","פברואר").replace("March","מרץ").replace("April","אפריל").replace("May","מאי").replace("June","יוני").replace("July","יולי").replace("August","אוגוסט").replace("September","ספטמבר").replace("October","אוקטובר").replace("November","נובמבר").replace("December","דצמבר")
    st.markdown(f"""
    <div class="topbar">
      <h1>{current}</h1>
      <div class="sub">יום {date_str}</div>
      <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
      <div class="prog-row"><span>{checked} מתוך {total} פריטים</span><span>{pct}%</span></div>
    </div>
    """, unsafe_allow_html=True)
else:
    st.markdown('<div class="topbar"><h1>🛒 רשימת קניות</h1><div class="sub">ניהול חכם לסל הקניות שלך</div></div>', unsafe_allow_html=True)

# ═══ TABS ══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3 = st.tabs(["📋  רשימה", "📂  ניהול", "📜  היסטוריה"])

# ── TAB 1: Active list ────────────────────────────────────────────────────────
with tab1:
    if not lists:
        st.markdown('<div class="empty-state"><div class="icon">🛒</div><p>עבור ל"ניהול" כדי ליצור רשימה ראשונה</p></div>', unsafe_allow_html=True)
    else:
        # List selector (compact pills row)
        list_names = list(lists.keys())
        if len(list_names) > 1:
            sel = st.selectbox("", list_names, index=list_names.index(current), key="sel", label_visibility="collapsed")
            if sel != current:
                data["current_list"] = sel; save_data(data); st.rerun()

        items = lists[current]

        # Add item
        with st.expander("✚  הוסף פריט"):
            c1,c2 = st.columns([4,1])
            nm = c1.text_input("שם המוצר","",key="add_nm",placeholder="חלב, לחם, עגבניות...")
            qty = c2.number_input("כמות",1,99,1,key="add_qty")
            cat_opts = list(CATEGORIES.keys())
            auto = guess_cat(nm) if nm else "🛒 שונות"
            cat = st.selectbox("קטגוריה", cat_opts, index=cat_opts.index(auto), key="add_cat")
            note = st.text_input("הערה","",key="add_note",placeholder="מותג, גודל...")
            if st.button("הוסף לרשימה ✚", use_container_width=True, type="primary"):
                if nm.strip():
                    items.append({"id":str(uuid.uuid4()),"name":nm.strip(),"qty":qty,"category":cat,"note":note.strip(),"checked":False,"added":datetime.now().strftime("%d/%m/%Y %H:%M")})
                    save_data(data); st.rerun()

        # Items grouped by category — unchecked first
        by_cat = {}
        for item in items:
            by_cat.setdefault(item.get("category","🛒 שונות"),[]).append(item)

        for cat, citems in sorted(by_cat.items(), key=lambda x: all(i.get("checked") for i in x[1])):
            st.markdown(f'<div class="cat-label">{cat}</div>', unsafe_allow_html=True)
            for item in citems:
                done = item.get("checked",False)
                done_cls = "done" if done else ""
                chk_cls = "checked" if done else ""
                qty_html = f'<span class="qty-pill">×{item["qty"]}</span>' if item["qty"]>1 else ""
                note_html = f'<div class="item-note">{item["note"]}</div>' if item.get("note") else ""
                chk_svg = '<svg width="12" height="10" viewBox="0 0 12 10" fill="none"><polyline points="1,5 4.5,8.5 11,1" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>' if done else ""

                col_main, col_del = st.columns([11,1])
                with col_main:
                    st.markdown(f"""
                    <div class="item-card {done_cls}">
                      <div class="check-circle {chk_cls}">{chk_svg}</div>
                      <div style="flex:1">
                        <div class="item-name">{item["name"]}</div>
                        {note_html}
                      </div>
                      {qty_html}
                    </div>""", unsafe_allow_html=True)
                    # Invisible checkbox for toggle
                    new_val = st.checkbox("", value=done, key=f"c_{item['id']}", label_visibility="hidden")
                    if new_val != done:
                        item["checked"] = new_val; save_data(data); st.rerun()
                with col_del:
                    st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
                    if st.button("✕", key=f"d_{item['id']}", help="מחק"):
                        lists[current] = [i for i in items if i["id"]!=item["id"]]
                        save_data(data); st.rerun()

        if items:
            st.markdown("<div style='height:12px'></div>",unsafe_allow_html=True)
            c1,c2 = st.columns(2)
            with c1:
                if st.button("נקה מסומנים 🗑️", use_container_width=True):
                    lists[current]=[i for i in items if not i.get("checked")]; save_data(data); st.rerun()
            with c2:
                if st.button("סמן הכל ✅", use_container_width=True):
                    for i in items: i["checked"]=True
                    save_data(data); st.rerun()

            st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
            if st.button("📦  סיים ושמור בהיסטוריה", use_container_width=True, type="primary"):
                t,c = stats(items)
                data.setdefault("history",[]).insert(0,{"id":str(uuid.uuid4()),"list_name":current,"date":datetime.now().strftime("%d/%m/%Y %H:%M"),"items":items.copy(),"total":t,"checked":c})
                lists[current]=[]; save_data(data); st.success("✅ נשמר!"); st.rerun()

# ── TAB 2: Manage lists ───────────────────────────────────────────────────────
with tab2:
    st.markdown("<div style='height:10px'></div>",unsafe_allow_html=True)
    for lname, litems in list(lists.items()):
        t,c = stats(litems); pct = int(c/t*100) if t else 0
        icon = "🟢" if lname==current else "⚪"
        col_b, col_x = st.columns([9,1])
        with col_b:
            if st.button(f"{icon}  {lname}   •   {t} פריטים   {pct}%", key=f"sl_{lname}", use_container_width=True):
                data["current_list"]=lname; save_data(data); st.rerun()
        with col_x:
            st.markdown("<div style='height:6px'></div>",unsafe_allow_html=True)
            if st.button("✕",key=f"rl_{lname}"):
                del data["lists"][lname]
                rem=list(data["lists"].keys()); data["current_list"]=rem[0] if rem else None
                save_data(data); st.rerun()

    st.markdown("---")
    st.markdown("**צור רשימה חדשה**")
    new_nm = st.text_input("שם הרשימה","",key="new_lnm",placeholder="קניות שבועיות, יום שישי...")

    TMPL = {
        "🏠 שבועי": [("חלב 3%",2,"🥛 מוצרי חלב","1 ליטר"),("לחם",1,"🍞 לחם ומאפים",""),("עגבניות",1,"🥦 ירקות ופירות",""),("מלפפונים",1,"🥦 ירקות ופירות",""),("ביצים",1,"🥛 מוצרי חלב","12 יח'"),("עוף",1,"🥩 בשר ודגים","חזה")],
        "🎉 מסיבה": [("שתייה קלה",4,"🧃 משקאות",""),("חטיפים",3,"🍬 חטיפים וממתקים",""),("לחמניות",2,"🍞 לחם ומאפים",""),("נקניקיות",2,"🥩 בשר ודגים","")],
        "🥗 בריאות": [("ירקות מעורבים",1,"🥦 ירקות ופירות",""),("קינואה",1,"🥫 שימורים ויבשים",""),("חזה עוף",2,"🥩 בשר ודגים",""),("יוגורט 0%",3,"🥛 מוצרי חלב","")],
    }
    cols = st.columns(3)
    for col,(tn,ti) in zip(cols,TMPL.items()):
        with col:
            if st.button(tn,use_container_width=True,key=f"t_{tn}"):
                base=tn.split(" ",1)[1]; lkey=f"{base} {datetime.now().strftime('%d/%m')}"
                data["lists"][lkey]=[{"id":str(uuid.uuid4()),"name":n,"qty":q,"category":c,"note":nt,"checked":False,"added":datetime.now().strftime("%d/%m/%Y %H:%M")} for n,q,c,nt in ti]
                data["current_list"]=lkey; save_data(data); st.success(f"✅ '{lkey}' נוצרה!"); st.rerun()

    if st.button("✚  צור רשימה ריקה", use_container_width=True, type="primary"):
        if new_nm.strip():
            if new_nm.strip() not in data["lists"]:
                data["lists"][new_nm.strip()]=[]; data["current_list"]=new_nm.strip()
                save_data(data); st.success(f"✅ '{new_nm}' נוצרה!"); st.rerun()
            else: st.warning("⚠️ שם כבר קיים")
        else: st.warning("⚠️ הכנס שם")

# ── TAB 3: History ────────────────────────────────────────────────────────────
with tab3:
    history = data.get("history",[])
    if not history:
        st.markdown('<div class="empty-state"><div class="icon">📭</div><p>אין היסטוריה עדיין</p></div>', unsafe_allow_html=True)
    else:
        c1,c2 = st.columns([6,1])
        c1.markdown(f"**{len(history)} קניות קודמות**")
        if c2.button("נקה"):
            data["history"]=[]; save_data(data); st.rerun()
        for entry in history:
            with st.expander(f"🛍️  {entry['list_name']}  —  {entry['date']}  ({entry['total']} פריטים)"):
                by = {}
                for item in entry["items"]: by.setdefault(item.get("category","שונות"),[]).append(item)
                for cat,ci in by.items():
                    st.markdown(f"**{cat}**")
                    for item in ci:
                        c="✅" if item.get("checked") else "⬜"
                        q=f" ×{item['qty']}" if item["qty"]>1 else ""
                        n=f" _{item['note']}_" if item.get("note") else ""
                        st.markdown(f"{c} {item['name']}{q}{n}")
                st.markdown("---")
                if st.button("♻️ שחזר רשימה זו",key=f"r_{entry['id']}"):
                    rn=f"{entry['list_name']} (שוחזר)"
                    data["lists"][rn]=[{**i,"id":str(uuid.uuid4()),"checked":False} for i in entry["items"]]
                    data["current_list"]=rn; save_data(data); st.success("✅ שוחזר!"); st.rerun()

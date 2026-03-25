import streamlit as st
import json, os, uuid
from datetime import datetime
from catalog import CATALOG

st.set_page_config(page_title="🛒 קניות", page_icon="🛒", layout="centered", initial_sidebar_state="collapsed")

CATEGORIES = {
    "🥛 מוצרי חלב":       ["חלב","גבינה","יוגורט","חמאה","שמנת","קוטג","ביצ"],
    "🥦 ירקות ופירות":     ["ירק","פרי","עגבני","מלפפ","חסה","תפוח","בננה","לימון","פלפל","גזר","בצל","אדמה","אבוקד","תות","ענב","מנגו","קישוא","חציל","ברוקולי"],
    "🥩 בשר ודגים":        ["בשר","עוף","דג","נקניק","המבורגר","שניצל","כבש","סלמון","טונה","אנטריקוט"],
    "🍞 לחם ומאפים":       ["לחם","חלה","פיתה","קרואס","בייגל","לחמני","טורטייה"],
    "🥫 שימורים ויבשים":   ["שימור","פסט","אורז","קטנית","דגן","קמח","סוכר","עדשים","חומוס","רסק","תירס","שיבולת","קינואה","שעועית"],
    "🧃 משקאות":           ["מיץ","מים","סודה","קפה","תה","שתייה","אנרגיה"],
    "🧹 ניקיון ובית":      ["סבון","אבקה","ניקיון","נייר","שקית","מגבת","כלים","ספוג","מרכך"],
    "🍬 חטיפים וממתקים":   ["שוקולד","ביסקוויט","חטיף","ממתק","עוגה","גלידה","פופקורן","במבה","ביסלי","גומי","עוגיות"],
    "🧴 טיפוח ובריאות":    ["שמפו","קרם","ויטמין","תרופה","מברשת","דאודורנט","משחת","טישו","מגנ"],
    "🌿 תבלינים ורטבים":   ["מלח","פלפל שחור","שמן","חומץ","רוטב","תבלין","פפריקה","חרדל","מיונז","קטשופ","סויה","דבש","כורכום"],
    "🍷 אלכוהול ויין":     ["יין","בירה","וויסקי","אלכוהול"],
    "❄️ קפואים":           ["קפוא","פיצה קפו","ירקות קפו","אדממה"],
    "🐾 מוצרי חיות":       ["חתול","כלב","מזון לחי","חול"],
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

# ── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700&display=swap');

*, *::before, *::after { box-sizing: border-box; }

/* Force RTL everywhere */
html, body { direction: rtl !important; }
[class*="css"], [data-testid], .stApp, .main, section, div {
    font-family: 'Heebo', sans-serif !important;
    direction: rtl !important;
}

.stApp { background: #f7faf8 !important; }
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"], [data-testid="stStatusWidget"] {
    visibility: hidden !important; display: none !important;
}
.block-container {
    padding: 0 !important;
    max-width: 430px !important;
    margin: 0 auto !important;
}

/* Topbar */
.topbar { background: #1c7a42; padding: 22px 20px 14px; }
.topbar h1 { color:#fff; font-size:20px; font-weight:700; margin:0 0 3px; text-align:right; }
.topbar .sub { color:rgba(255,255,255,0.72); font-size:13px; text-align:right; }
.prog-wrap { background:rgba(255,255,255,0.25); border-radius:99px; height:5px; margin-top:10px; }
.prog-fill { background:#7de8a4; height:5px; border-radius:99px; transition:width .4s; }
.prog-row { display:flex; justify-content:space-between; font-size:12px; color:rgba(255,255,255,0.75); margin-top:4px; }

/* Section label */
.cat-label {
    font-size:11px; font-weight:600; color:#5f6f68;
    padding:14px 18px 5px; letter-spacing:.06em;
    text-align:right;
}

/* Active list item */
.item-card {
    display:flex; align-items:center; gap:12px;
    padding:12px 18px; border-bottom:1px solid #f0f0ef;
    background:#fff; direction:rtl;
}
.item-name { font-size:15px; color:#1a2e22; text-align:right; }
.item-note { font-size:12px; color:#92a89a; margin-top:1px; text-align:right; }
.item-card.done .item-name { text-decoration:line-through; color:#b0bdb5; }
.chk-circle {
    width:26px; height:26px; min-width:26px; border-radius:50%;
    border:1.5px solid #1c7a42; display:flex; align-items:center;
    justify-content:center;
}
.chk-circle.on { background:#1c7a42; }
.qty-pill {
    background:#eaf7f0; color:#1c7a42; font-size:11px;
    font-weight:600; padding:3px 10px; border-radius:99px; white-space:nowrap;
}

/* Catalog item — full row is the button */
.cat-item-btn {
    width:100%; background:#fff; border:none; border-bottom:1px solid #f0f0ef;
    padding:12px 18px; display:flex; align-items:center; gap:12px;
    cursor:pointer; direction:rtl; text-align:right;
    transition: background .12s;
}
.cat-item-btn:active { background:#f0fdf4; }
.cat-item-btn.sel { background:#eaf7f0; }
.cat-chk {
    width:24px; height:24px; min-width:24px; border-radius:6px;
    border:1.5px solid #c8d9cc; display:flex; align-items:center; justify-content:center;
    transition:all .15s;
}
.cat-chk.on { background:#1c7a42; border-color:#1c7a42; }
.cat-item-name { font-size:15px; color:#1a2e22; flex:1; text-align:right; }
.cat-item-note { font-size:12px; color:#9aab9e; }

.sel-bar {
    background:#1c7a42; color:#fff; padding:11px 18px;
    display:flex; align-items:center; justify-content:space-between;
    font-size:14px; font-weight:500; direction:rtl;
}

.empty-state { text-align:center; padding:50px 20px; color:#92a89a; direction:rtl; }
.empty-state .big { font-size:40px; margin-bottom:12px; }

/* Tabs */
.stTabs { margin:0 !important; }
.stTabs [data-baseweb="tab-list"] {
    background:#fff !important; border-bottom:1px solid #e8ede9 !important;
    gap:0 !important; padding:0 !important; direction:rtl !important;
}
.stTabs [data-baseweb="tab"] {
    font-family:'Heebo',sans-serif !important; font-size:12px !important;
    font-weight:500 !important; color:#7a8f82 !important;
    padding:11px 2px !important; flex:1 !important; text-align:center !important;
    border-bottom:2px solid transparent !important;
}
.stTabs [aria-selected="true"] {
    color:#1c7a42 !important; border-bottom-color:#1c7a42 !important;
    background:transparent !important;
}
.stTabs [data-baseweb="tab-panel"] { padding:0 !important; }

div[data-testid="stVerticalBlock"] > div { gap:0 !important; }

/* All inputs RTL */
.stTextInput input, .stNumberInput input {
    direction:rtl !important; text-align:right !important;
    font-family:'Heebo',sans-serif !important;
    border-radius:12px !important; font-size:15px !important;
}
.stSelectbox > div > div {
    direction:rtl !important;
    font-family:'Heebo',sans-serif !important;
    border-radius:12px !important;
}
.stTextInput label, .stNumberInput label, .stSelectbox label,
.stRadio label, [data-testid="stWidgetLabel"] {
    font-family:'Heebo',sans-serif !important; font-size:13px !important;
    color:#5f6f68 !important; direction:rtl !important; text-align:right !important;
}
.stRadio [data-testid="stMarkdownContainer"] p { direction:rtl !important; }

/* Buttons */
.stButton button {
    font-family:'Heebo',sans-serif !important; font-weight:500 !important;
    border-radius:12px !important; direction:rtl !important;
}
button[kind="primary"] {
    background:#1c7a42 !important; border-color:#1c7a42 !important; color:#fff !important;
}

/* Expander */
[data-testid="stExpander"] {
    border:none !important; background:#fff !important;
    border-radius:14px !important; margin:10px 12px 4px !important;
    box-shadow:0 1px 6px rgba(0,0,0,.07) !important;
}
[data-testid="stExpanderDetails"] { padding:0 14px 14px !important; }

/* Hide native checkboxes used as triggers */
.hidden-cb { position:absolute; opacity:0; pointer-events:none; height:0; }
</style>
""", unsafe_allow_html=True)

# ── Session state ──────────────────────────────────────────────────────────────
if "data" not in st.session_state:
    st.session_state.data = load_data()
if "sel" not in st.session_state:
    # key -> {name, note, category, qty}
    st.session_state.sel = {}

data   = st.session_state.data
sel    = st.session_state.sel
lists  = data.get("lists", {})
current = data.get("current_list")
if lists and current not in lists:
    current = list(lists.keys())[0]

# ── Topbar ─────────────────────────────────────────────────────────────────────
if lists and current:
    items = lists[current]
    total, checked = stats(items)
    pct = int(checked/total*100) if total else 0
    st.markdown(f"""
    <div class="topbar">
      <h1>{current}</h1>
      <div class="sub">{total} פריטים ברשימה</div>
      <div class="prog-wrap"><div class="prog-fill" style="width:{pct}%"></div></div>
      <div class="prog-row"><span>{checked} מתוך {total} נרכשו</span><span>{pct}%</span></div>
    </div>""", unsafe_allow_html=True)
else:
    st.markdown('<div class="topbar"><h1>🛒 רשימת קניות</h1><div class="sub">בחר מהקטלוג או צור רשימה חדשה</div></div>', unsafe_allow_html=True)

# ── Tabs ───────────────────────────────────────────────────────────────────────
tab_active, tab_catalog, tab_manage, tab_history = st.tabs(["📋 רשימה", "🗂️ קטלוג", "📂 ניהול", "📜 היסטוריה"])

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Active list
# ══════════════════════════════════════════════════════════════════════════════
with tab_active:
    if not lists:
        st.markdown('<div class="empty-state"><div class="big">🛒</div><p>עבור לקטלוג כדי לבחור פריטים</p></div>', unsafe_allow_html=True)
    else:
        list_names = list(lists.keys())
        if len(list_names) > 1:
            idx = list_names.index(current) if current in list_names else 0
            sel_list = st.selectbox("", list_names, index=idx, key="sel_active", label_visibility="collapsed")
            if sel_list != current:
                data["current_list"] = sel_list; save_data(data); st.rerun()

        items = lists[current]

        with st.expander("✚  הוסף פריט ידנית"):
            c1, c2 = st.columns([4,1])
            nm   = c1.text_input("שם המוצר", "", key="add_nm", placeholder="חלב, לחם...")
            qty  = c2.number_input("כמות", 1, 99, 1, key="add_qty")
            cat_opts = list(CATEGORIES.keys())
            auto     = guess_cat(nm) if nm else "🛒 שונות"
            cat  = st.selectbox("קטגוריה", cat_opts, index=cat_opts.index(auto), key="add_cat")
            note = st.text_input("הערה", "", key="add_note", placeholder="מותג, גודל...")
            if st.button("הוסף ✚", use_container_width=True, type="primary"):
                if nm.strip():
                    items.append({"id":str(uuid.uuid4()),"name":nm.strip(),"qty":qty,
                                  "category":cat,"note":note.strip(),"checked":False,
                                  "added":datetime.now().strftime("%d/%m/%Y %H:%M")})
                    save_data(data); st.rerun()

        by_cat = {}
        for item in items:
            by_cat.setdefault(item.get("category","🛒 שונות"),[]).append(item)

        for cat_name, citems in sorted(by_cat.items(), key=lambda x: all(i.get("checked") for i in x[1])):
            st.markdown(f'<div class="cat-label">{cat_name}</div>', unsafe_allow_html=True)
            for item in citems:
                done     = item.get("checked", False)
                done_cls = "done" if done else ""
                chk_cls  = "on"   if done else ""
                qty_html = f'<span class="qty-pill">×{item["qty"]}</span>' if item["qty"]>1 else ""
                note_html= f'<div class="item-note">{item["note"]}</div>' if item.get("note") else ""
                tick     = '<svg width="12" height="10" viewBox="0 0 12 10" fill="none"><polyline points="1,5 4.5,8.5 11,1" stroke="#fff" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/></svg>' if done else ""

                col_chk, col_info, col_del = st.columns([1, 9, 1])

                with col_chk:
                    # Real Streamlit button styled as circle
                    if st.button("✓" if done else " ", key=f"chk_{item['id']}",
                                 help="סמן/בטל", use_container_width=True):
                        item["checked"] = not done
                        save_data(data); st.rerun()

                with col_info:
                    st.markdown(f"""<div class="item-card {done_cls}" style="padding:8px 4px;border:none">
                      <div style="flex:1">
                        <div class="item-name">{item["name"]}</div>{note_html}
                      </div>{qty_html}</div>""", unsafe_allow_html=True)

                with col_del:
                    if st.button("✕", key=f"del_{item['id']}", use_container_width=True):
                        lists[current] = [i for i in items if i["id"]!=item["id"]]
                        save_data(data); st.rerun()

        if items:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            with c1:
                if st.button("🗑️ נקה מסומנים", use_container_width=True):
                    lists[current]=[i for i in items if not i.get("checked")]; save_data(data); st.rerun()
            with c2:
                if st.button("✅ סמן הכל", use_container_width=True):
                    for i in items: i["checked"]=True
                    save_data(data); st.rerun()
            st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)
            if st.button("📦  סיים ושמור בהיסטוריה", use_container_width=True, type="primary"):
                t, c = stats(items)
                data.setdefault("history",[]).insert(0,{
                    "id":str(uuid.uuid4()), "list_name":current,
                    "date":datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "items":items.copy(), "total":t, "checked":c})
                lists[current]=[]; save_data(data); st.success("✅ נשמר!"); st.rerun()

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Catalog  (pure Streamlit buttons — no hidden checkboxes)
# ══════════════════════════════════════════════════════════════════════════════
with tab_catalog:
    n_sel = len(sel)

    if n_sel > 0:
        st.markdown(f'<div class="sel-bar"><span>✓ {n_sel} פריטים נבחרו</span></div>', unsafe_allow_html=True)

    search = st.text_input("", key="cat_search", placeholder="🔍  חיפוש מוצר...", label_visibility="collapsed")

    # Save controls
    if n_sel > 0:
        with st.container():
            save_mode = st.radio("שמור ל:", ["רשימה חדשה", "רשימה קיימת"], horizontal=True, key="save_mode")
            if save_mode == "רשימה חדשה":
                new_list_name = st.text_input("", key="cat_new_nm", placeholder="שם הרשימה...", label_visibility="collapsed")
            else:
                existing = list(lists.keys())
                if existing:
                    new_list_name = st.selectbox("", existing, key="cat_existing", label_visibility="collapsed")
                else:
                    st.caption("אין רשימות קיימות")
                    new_list_name = ""

            c1, c2 = st.columns([3,1])
            with c1:
                if st.button(f"💾  הוסף {n_sel} פריטים לרשימה", use_container_width=True, type="primary"):
                    nm_clean = new_list_name.strip() if new_list_name else ""
                    if not nm_clean:
                        st.warning("⚠️ הכנס שם לרשימה")
                    else:
                        if nm_clean not in data["lists"]:
                            data["lists"][nm_clean] = []
                        for key, itm in sel.items():
                            data["lists"][nm_clean].append({
                                "id":str(uuid.uuid4()), "name":itm["name"],
                                "qty":itm.get("qty",1), "category":itm["category"],
                                "note":itm.get("note",""), "checked":False,
                                "added":datetime.now().strftime("%d/%m/%Y %H:%M"),
                            })
                        data["current_list"] = nm_clean
                        st.session_state.sel = {}
                        save_data(data)
                        st.success(f"✅ {n_sel} פריטים נוספו ל'{nm_clean}'!")
                        st.rerun()
            with c2:
                if st.button("נקה", use_container_width=True):
                    st.session_state.sel = {}; st.rerun()

    st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

    # Catalog items — each row is a real st.button
    for cat_name, cat_items in CATALOG.items():
        filtered = [i for i in cat_items
                    if not search or search in i["name"] or search.lower() in i["name"].lower()]
        if not filtered:
            continue

        all_keys     = [f"{cat_name}|{i['name']}" for i in filtered]
        all_selected = all(k in sel for k in all_keys)

        hdr_c, sel_c = st.columns([7, 2])
        with hdr_c:
            st.markdown(f'<div class="cat-label">{cat_name}</div>', unsafe_allow_html=True)
        with sel_c:
            label = "בטל הכל" if all_selected else "בחר הכל"
            if st.button(label, key=f"all_{cat_name}", use_container_width=True):
                if all_selected:
                    for k in all_keys: sel.pop(k, None)
                else:
                    for itm in filtered:
                        k = f"{cat_name}|{itm['name']}"
                        sel[k] = {**itm, "category": cat_name, "qty": 1}
                st.rerun()

        for itm in filtered:
            key    = f"{cat_name}|{itm['name']}"
            is_sel = key in sel
            tick   = "✓ " if is_sel else "   "
            note_str = f"  —  {itm['note']}" if itm.get("note") else ""
            bg     = "#eaf7f0" if is_sel else "#ffffff"
            fw     = "600"     if is_sel else "400"
            clr    = "#1c7a42" if is_sel else "#1a2e22"

            col_btn, col_qty = st.columns([8, 2])
            with col_btn:
                btn_label = f"{tick}{itm['name']}{note_str}"
                if st.button(btn_label, key=f"tog_{key}", use_container_width=True):
                    if is_sel:
                        sel.pop(key, None)
                    else:
                        sel[key] = {**itm, "category": cat_name, "qty": 1}
                    st.rerun()
                # Style the button to look like a list row
                st.markdown(f"""<style>
                  div[data-testid="stButton"]:has(button[kind="secondary"][key="tog_{key}"]) button,
                  button[data-testid="baseButton-secondary"][aria-label="{btn_label}"] {{
                    background:{bg} !important; color:{clr} !important;
                    font-weight:{fw} !important; border-radius:0 !important;
                    border:none !important; border-bottom:1px solid #f0f0ef !important;
                    text-align:right !important; padding:12px 18px !important;
                    justify-content:flex-start !important;
                  }}
                </style>""", unsafe_allow_html=True)

            with col_qty:
                if is_sel:
                    q = st.number_input("", min_value=1, max_value=99,
                                        value=sel[key].get("qty",1),
                                        key=f"q_{key}", label_visibility="collapsed")
                    if q != sel[key].get("qty",1):
                        sel[key]["qty"] = q

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Manage
# ══════════════════════════════════════════════════════════════════════════════
with tab_manage:
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    for lname, litems in list(lists.items()):
        t, c = stats(litems)
        pct  = int(c/t*100) if t else 0
        icon = "🟢" if lname==current else "⚪"
        cb, cx = st.columns([9,1])
        with cb:
            if st.button(f"{icon}  {lname}   •   {t} פריטים   {pct}%", key=f"sl_{lname}", use_container_width=True):
                data["current_list"]=lname; save_data(data); st.rerun()
        with cx:
            st.markdown("<div style='height:6px'></div>", unsafe_allow_html=True)
            if st.button("✕", key=f"rl_{lname}"):
                del data["lists"][lname]
                rem=list(data["lists"].keys()); data["current_list"]=rem[0] if rem else None
                save_data(data); st.rerun()

    st.markdown("---")
    st.markdown("**צור רשימה ריקה**")
    new_nm = st.text_input("", "", key="new_lnm", placeholder="שם הרשימה...", label_visibility="collapsed")

    TMPL = {
        "🏠 שבועי": [("חלב 3%",2,"🥛 מוצרי חלב","1 ליטר"),("לחם",1,"🍞 לחם ומאפים",""),("עגבניות",1,"🥦 ירקות ופירות",""),("מלפפונים",1,"🥦 ירקות ופירות",""),("ביצים",1,"🥛 מוצרי חלב","12 יח'"),("עוף",1,"🥩 בשר ודגים","חזה")],
        "🎉 מסיבה": [("שתייה קלה",4,"🧃 משקאות",""),("חטיפים",3,"🍬 חטיפים וממתקים",""),("לחמניות",2,"🍞 לחם ומאפים",""),("נקניקיות",2,"🥩 בשר ודגים","")],
        "🥗 בריאות": [("ירקות מעורבים",1,"🥦 ירקות ופירות",""),("קינואה",1,"🥫 שימורים ויבשים",""),("חזה עוף",2,"🥩 בשר ודגים",""),("יוגורט 0%",3,"🥛 מוצרי חלב","")],
    }
    cols = st.columns(3)
    for col,(tn,ti) in zip(cols,TMPL.items()):
        with col:
            if st.button(tn, use_container_width=True, key=f"t_{tn}"):
                base = tn.split(" ",1)[1]
                lkey = f"{base} {datetime.now().strftime('%d/%m')}"
                data["lists"][lkey]=[{"id":str(uuid.uuid4()),"name":n,"qty":q,"category":c,"note":nt,
                                       "checked":False,"added":datetime.now().strftime("%d/%m/%Y %H:%M")}
                                      for n,q,c,nt in ti]
                data["current_list"]=lkey; save_data(data); st.success(f"✅ '{lkey}' נוצרה!"); st.rerun()

    if st.button("✚  צור רשימה ריקה", use_container_width=True, type="primary"):
        if new_nm.strip():
            if new_nm.strip() not in data["lists"]:
                data["lists"][new_nm.strip()]=[]; data["current_list"]=new_nm.strip()
                save_data(data); st.success(f"✅ '{new_nm}' נוצרה!"); st.rerun()
            else: st.warning("⚠️ שם כבר קיים")
        else: st.warning("⚠️ הכנס שם")

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — History
# ══════════════════════════════════════════════════════════════════════════════
with tab_history:
    history = data.get("history",[])
    if not history:
        st.markdown('<div class="empty-state"><div class="big">📭</div><p>אין היסטוריה עדיין</p></div>', unsafe_allow_html=True)
    else:
        c1,c2 = st.columns([7,2])
        c1.markdown(f"<div style='padding:12px 0 6px;font-weight:500;direction:rtl'>{len(history)} קניות קודמות</div>", unsafe_allow_html=True)
        with c2:
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            if st.button("נקה הכל"):
                data["history"]=[]; save_data(data); st.rerun()
        for entry in history:
            with st.expander(f"🛍️  {entry['list_name']}  —  {entry['date']}  ({entry['total']} פריטים)"):
                by={}
                for item in entry["items"]: by.setdefault(item.get("category","שונות"),[]).append(item)
                for cat,ci in by.items():
                    st.markdown(f"**{cat}**")
                    for item in ci:
                        c = "✅" if item.get("checked") else "⬜"
                        q = f" ×{item['qty']}" if item["qty"]>1 else ""
                        n = f" _{item['note']}_" if item.get("note") else ""
                        st.markdown(f"{c} {item['name']}{q}{n}")
                st.markdown("---")
                if st.button("♻️ שחזר", key=f"r_{entry['id']}"):
                    rn = f"{entry['list_name']} (שוחזר)"
                    data["lists"][rn]=[{**i,"id":str(uuid.uuid4()),"checked":False} for i in entry["items"]]
                    data["current_list"]=rn; save_data(data); st.success("✅ שוחזר!"); st.rerun()

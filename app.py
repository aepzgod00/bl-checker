import streamlit as st
from google import genai
from google.genai import types
import io
import os
import json
import pandas as pd
from datetime import datetime
import xlsxwriter

# ─────────────────────────────────────────────
# 1. PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="VerifyHub v2 - Document Verification System",
    page_icon="🌿",
    layout="wide"
)

# ─────────────────────────────────────────────
# 2. CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');

    .stApp {
        background: linear-gradient(180deg, #FAF8F5 0%, #F4F2EE 100%);
        font-family: 'Bai Jamjuree', sans-serif;
        background-attachment: fixed;
    }
    div[data-testid="stMarkdownContainer"] p,
    div[data-testid="stMarkdownContainer"] li {
        color: #4A5A4E !important;
        line-height: 1.625;
        font-size: 14.5px;
    }
    div[data-testid="stMarkdownContainer"] h1,
    div[data-testid="stMarkdownContainer"] h2,
    div[data-testid="stMarkdownContainer"] h3,
    div[data-testid="stMarkdownContainer"] h4 {
        color: #2D3531 !important;
        font-family: 'Manrope', sans-serif;
        font-weight: 700;
        margin-top: 25px;
        margin-bottom: 12px;
    }
    div[data-testid="stMarkdownContainer"] table {
        color: #4A5A4E !important;
        background-color: #FDFCFA !important;
        border-collapse: collapse !important;
        border-radius: 14px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 20px rgba(141,137,120,0.04) !important;
        margin: 20px 0 !important;
        width: 100% !important;
        border: none !important;
    }
    div[data-testid="stMarkdownContainer"] th {
        background-color: #F0EDE6 !important;
        color: #2D3531 !important;
        font-weight: 600 !important;
        padding: 14px 16px !important;
        border: none !important;
        border-bottom: 2px solid #E4E1D6 !important;
        font-size: 13.5px;
        text-align: left;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMarkdownContainer"] td {
        color: #4A5A4E !important;
        padding: 14px 16px !important;
        border: none !important;
        border-bottom: 1px solid #EAE8DF !important;
        background-color: #FDFCFA !important;
        font-size: 13.5px;
        vertical-align: top;
    }
    div[data-testid="stMarkdownContainer"] tr:nth-child(even) td {
        background-color: #FAF8F4 !important;
    }

    /* ── Badges ── */
    .badge-match    { color:#3B664B!important;background:#E6F0EA;padding:3px 8px;border-radius:6px;font-weight:700;font-size:12px;letter-spacing:.5px; }
    .badge-mismatch { color:#A65252!important;background:#FAEAEA;padding:3px 8px;border-radius:6px;font-weight:700;font-size:12px;letter-spacing:.5px; }
    .badge-warn     { color:#8A6A00!important;background:#FFF8DF;padding:3px 8px;border-radius:6px;font-weight:700;font-size:12px;letter-spacing:.5px; }

    /* ── Brand ── */
    .brand-header { font-family:'Manrope',sans-serif;color:#3A443E;font-weight:800;font-size:32px;letter-spacing:.5px;margin:0;line-height:1.2;background:linear-gradient(180deg,#3A443E 0%,#222825 100%);-webkit-background-clip:text;-webkit-text-fill-color:transparent; }
    .brand-subtitle { font-family:'Bai Jamjuree',sans-serif;color:#8C968E;font-size:12px;font-weight:500;letter-spacing:1px;text-transform:uppercase;margin-top:2px; }

    .user-profile-box { display:flex;align-items:center;justify-content:flex-end;gap:12px;background:#FFF;padding:10px 18px;border-radius:14px;border:1px solid #EAE8DF;box-shadow:0 4px 12px rgba(141,137,120,.02);margin-top:10px; }
    .user-avatar { font-size:22px;color:#557A61; }
    .user-info-text { font-size:12px;color:#4A5A4E;line-height:1.4;text-align:right; }
    .user-name { font-weight:700;color:#2D3531; }

    .workspace-title    { font-family:'Manrope',sans-serif;font-size:22px;font-weight:700;color:#2D3531;margin-bottom:2px; }
    .workspace-subtitle { font-size:14px;color:#7A857D;margin-bottom:35px; }

    .cozy-portal-card { background:#FFF;padding:30px 24px;border-radius:22px;border:1px solid #EAE8DF;text-align:center;box-shadow:0 10px 30px rgba(141,137,120,.05);transition:all .4s cubic-bezier(.16,1,.3,1);margin-bottom:15px; }
    .cozy-portal-card:hover { transform:translateY(-5px);border-color:#557A61;box-shadow:0 20px 40px rgba(85,122,97,.10); }

    .icon-wrapper { background:#F4F6F4;width:54px;height:54px;border-radius:50%;display:flex;align-items:center;justify-content:center;margin:0 auto 16px auto;color:#4A5A4E;transition:all .4s cubic-bezier(.16,1,.3,1); }
    .cozy-portal-card:hover .icon-wrapper { transform:scale(1.05);background:#EDF3EE;color:#557A61; }

    .card-title-text { color:#3A443E;font-weight:700;font-size:19px;margin-bottom:8px; }
    .card-desc-text  { color:#7A857D;font-size:13.5px;line-height:1.45;margin-bottom:0; }

    .custom-code-box { background:#FAF8F5!important;border:1px solid #EAE8DF!important;border-radius:14px!important;padding:16px 20px!important;margin-top:15px!important;text-align:left!important;box-shadow:inset 0 2px 4px rgba(141,137,120,.02)!important; }
    .checklist-item  { font-size:13.5px;color:#5A665E;margin-bottom:8px;display:flex;align-items:center;gap:10px; }
    .checklist-item-check { color:#557A61;font-weight:700; }

    div[data-testid="stFileUploader"] { background:#FAF8F5!important;border:1.5px dashed #DCD9CD!important;border-radius:16px!important;padding:25px 20px!important;transition:all .3s cubic-bezier(.16,1,.3,1); }
    div[data-testid="stFileUploader"]:hover { border-color:#557A61!important;background:#F3F5F2!important; }

    div.stButton > button { border-radius:12px!important;border:1px solid #557A61!important;background:#FFF!important;color:#557A61!important;font-family:'Bai Jamjuree',sans-serif!important;font-weight:600!important;font-size:14.5px!important;padding:10px 24px!important;transition:all .3s ease;box-shadow:0 4px 12px rgba(85,122,97,.05); }
    div.stButton > button:hover { background:#557A61!important;color:#FFF!important;transform:translateY(-2px)!important;box-shadow:0 8px 20px rgba(85,122,97,.18)!important; }

    .inner-header-container { display:flex;align-items:flex-start;gap:20px;margin-top:5px;margin-bottom:25px; }
    .inner-title-block  { text-align:left; }
    .inner-main-title   { font-family:'Bai Jamjuree',sans-serif;font-size:24px;font-weight:700;color:#2D3531;line-height:1.3; }
    .inner-sub-title    { font-family:'Bai Jamjuree',sans-serif;font-size:14px;color:#7A857D;margin-top:5px; }

    .output-header-box   { display:flex;align-items:center;gap:10px;margin-top:32px;margin-bottom:-5px;color:#2D3531; }
    .output-header-title { font-size:17px;font-weight:700;font-family:'Manrope',sans-serif;letter-spacing:.2px; }

    /* ── Progress Steps ── */
    .step-bar { display:flex;gap:0;margin-bottom:28px;border-radius:12px;overflow:hidden;border:1px solid #EAE8DF; }
    .step-item { flex:1;padding:10px 0;text-align:center;font-size:13px;font-weight:600;background:#FAF8F5;color:#A0ADA2;transition:all .3s; }
    .step-item.active   { background:#557A61;color:#FFF; }
    .step-item.done     { background:#EDF3EE;color:#3B664B; }

    /* ── Confidence Gauge ── */
    .conf-gauge-wrap { background:#F4F2EE;border-radius:14px;padding:16px 20px;border:1px solid #EAE8DF;margin-bottom:18px; }
    .conf-label { font-size:12px;font-weight:600;color:#7A857D;text-transform:uppercase;letter-spacing:.5px;margin-bottom:8px; }
    .conf-bar-bg { background:#E4E1D6;border-radius:99px;height:10px;width:100%; }
    .conf-bar-fill { height:10px;border-radius:99px;transition:width .6s ease; }

    /* ── History log ── */
    .hist-row { display:flex;justify-content:space-between;align-items:center;padding:10px 14px;border-bottom:1px solid #EAE8DF;font-size:13.5px;color:#4A5A4E; }
    .hist-row:last-child { border-bottom:none; }
    .hist-time { font-size:11px;color:#A0ADA2; }

    /* ── Toast ── */
    .toast-success { background:#E6F0EA;border-left:4px solid #557A61;border-radius:10px;padding:12px 18px;font-size:14px;color:#3B664B;font-weight:600;margin-bottom:16px; }
    .toast-error   { background:#FAEAEA;border-left:4px solid #C0524E;border-radius:10px;padding:12px 18px;font-size:14px;color:#A65252;font-weight:600;margin-bottom:16px; }

    /* ── Stats card ── */
    .stat-card { background:#FFF;border:1px solid #EAE8DF;border-radius:16px;padding:18px 22px;text-align:center;box-shadow:0 4px 16px rgba(141,137,120,.04); }
    .stat-num { font-family:'Manrope',sans-serif;font-size:30px;font-weight:800;color:#2D3531; }
    .stat-lbl { font-size:12px;color:#7A857D;margin-top:3px;font-weight:500; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 3. CONFIG
# ─────────────────────────────────────────────
API_KEY   = "AQ.Ab8RN6I6laxWePmvYG1jGjbMflb4GtDkCcF3mnrBBe2nDb5SYw"   # ← ใส่ key ตรงนี้
EXCEL_FILE = "do_database_records.xlsx"
AUDIT_LOG_FILE = "audit_history.json"

# ─────────────────────────────────────────────
# 4. HELPERS
# ─────────────────────────────────────────────
def load_do_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame(columns=["เลขที่ B/L", "ชื่อ Consignee", "วันที่รับ D/O", "บันทึกโดย"])

def save_do_data(df: pd.DataFrame):
    df.to_excel(EXCEL_FILE, index=False)

def load_audit_log():
    if os.path.exists(AUDIT_LOG_FILE):
        with open(AUDIT_LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_audit_log(log: list):
    with open(AUDIT_LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(log, f, ensure_ascii=False, indent=2)

def file_to_gemini_part(file_obj):
    if file_obj:
        return types.Part.from_bytes(data=file_obj.getvalue(), mime_type=file_obj.type)
    return None

def export_do_excel(df: pd.DataFrame) -> bytes:
    """Export DO database to styled Excel."""
    buf = io.BytesIO()
    with xlsxwriter.Workbook(buf) as wb:
        ws = wb.add_worksheet("D/O Records")
        hdr_fmt = wb.add_format({"bold": True, "bg_color": "#557A61", "font_color": "#FFFFFF",
                                  "border": 1, "align": "center", "valign": "vcenter", "font_size": 12})
        cell_fmt = wb.add_format({"border": 1, "align": "left", "valign": "vcenter", "font_size": 11})
        alt_fmt  = wb.add_format({"border": 1, "align": "left", "valign": "vcenter",
                                   "font_size": 11, "bg_color": "#F4F6F4"})
        headers = list(df.columns)
        col_widths = [22, 35, 18, 20]
        for ci, (h, w) in enumerate(zip(headers, col_widths)):
            ws.write(0, ci, h, hdr_fmt)
            ws.set_column(ci, ci, w)
        ws.set_row(0, 28)
        for ri, row in df.iterrows():
            fmt = alt_fmt if ri % 2 else cell_fmt
            for ci, val in enumerate(row):
                ws.write(ri + 1, ci, str(val), fmt)
            ws.set_row(ri + 1, 22)
    buf.seek(0)
    return buf.read()

def export_audit_excel(audit_result_text: str, bl_names: list, amend_names: list) -> bytes:
    """Export audit result summary to Excel."""
    buf = io.BytesIO()
    with xlsxwriter.Workbook(buf) as wb:
        ws = wb.add_worksheet("Audit Report")
        title_fmt = wb.add_format({"bold": True, "font_size": 14, "font_color": "#2D3531"})
        sub_fmt   = wb.add_format({"font_size": 11, "font_color": "#7A857D"})
        ws.write(0, 0, "VerifyHub — Audit Report", title_fmt)
        ws.write(1, 0, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", sub_fmt)
        ws.write(3, 0, "B/L Files:", sub_fmt)
        ws.write(3, 1, ", ".join(bl_names))
        ws.write(4, 0, "Amendment Files:", sub_fmt)
        ws.write(4, 1, ", ".join(amend_names))
        ws.write(6, 0, "AI Analysis Output (Raw):", sub_fmt)
        ws.write(7, 0, audit_result_text)
        ws.set_column(0, 0, 22)
        ws.set_column(1, 1, 60)
    buf.seek(0)
    return buf.read()

# ─────────────────────────────────────────────
# 5. SESSION STATE
# ─────────────────────────────────────────────
for key, default in {
    "current_page": "portal",
    "audit_step": 0,
    "audit_result": None,
    "audit_confidence": 0,
    "audit_summary_stats": {},
    "audit_bl_names": [],
    "audit_amend_names": [],
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ─────────────────────────────────────────────
# 6. HEADER
# ─────────────────────────────────────────────
nav1, nav2 = st.columns([7, 3])
with nav1:
    st.markdown("""
        <div>
            <div class='brand-header'>VERIFYHUB</div>
            <div class='brand-subtitle'>ระบบตรวจเอกสารและจัดการสถานะส่งมอบ D/O อัจฉริยะ — v2.0</div>
        </div>""", unsafe_allow_html=True)
with nav2:
    st.markdown(f"""
        <div class='user-profile-box'>
            <div class='user-avatar'>👤</div>
            <div class='user-info-text'>
                <div class='user-name'>Seabra Team</div>
                <div style='color:#7A857D;'>Import-Export Dept &bull; {datetime.now().strftime('%d %b %Y')}</div>
            </div>
        </div>""", unsafe_allow_html=True)

st.markdown("<hr style='border:0;border-top:1px solid #EAE8DF;margin:18px 0 25px 0;'>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 7. API CLIENT
# ─────────────────────────────────────────────
if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่ Gemini API Key ที่ถูกต้องในตัวแปร API_KEY")
    st.stop()

client = genai.Client(api_key=API_KEY)

# ─────────────────────────────────────────────
# 8. PORTAL
# ─────────────────────────────────────────────
if st.session_state.current_page == "portal":
    st.markdown("<div class='workspace-title'>ยินดีต้อนรับกลับมาค่ะ</div>", unsafe_allow_html=True)
    st.markdown("<div class='workspace-subtitle'>กรุณาเลือกพื้นที่ทำงานที่ต้องการจัดการข้อมูลเพื่อดำเนินการต่อ</div>", unsafe_allow_html=True)

    # ── Mini stats bar ──
    df_tmp = load_do_data()
    log_tmp = load_audit_log()
    today_count = sum(1 for r in log_tmp if r.get("date","").startswith(datetime.now().strftime("%Y-%m-%d")))

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{len(df_tmp)}</div><div class='stat-lbl'>D/O ทั้งหมดในระบบ</div></div>", unsafe_allow_html=True)
    with sc2:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{len(log_tmp)}</div><div class='stat-lbl'>ครั้งที่ตรวจเอกสาร</div></div>", unsafe_allow_html=True)
    with sc3:
        st.markdown(f"<div class='stat-card'><div class='stat-num'>{today_count}</div><div class='stat-lbl'>ตรวจวันนี้</div></div>", unsafe_allow_html=True)
    with sc4:
        recent_do = df_tmp["วันที่รับ D/O"].max() if not df_tmp.empty else "—"
        st.markdown(f"<div class='stat-card'><div class='stat-num' style='font-size:18px;margin-top:6px;'>{recent_do}</div><div class='stat-lbl'>วันที่รับ D/O ล่าสุด</div></div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    p_col1, space_col, p_col2 = st.columns([4, 0.6, 4])
    with p_col1:
        st.markdown("""
            <div class='cozy-portal-card'>
                <div class='icon-wrapper'><span class="material-symbols-outlined" style="font-size:26px;">pageview</span></div>
                <div class='card-title-text'>ตรวจสอบเอกสาร</div>
                <p class='card-desc-text'>เปรียบเทียบข้อมูลไฟล์สแกนและประมวลผลความถูกต้องข้ามเอกสารอัตโนมัติ</p>
                <div class='custom-code-box'>
                    <div class='checklist-item'><span class='checklist-item-check'>✓</span> Bill of Lading (B/L)</div>
                    <div class='checklist-item'><span class='checklist-item-check'>✓</span> Amendment Notice</div>
                    <div class='checklist-item'><span class='checklist-item-check'>✓</span> Confidence Score + Export Excel</div>
                </div>
            </div>""", unsafe_allow_html=True)
        if st.button("เริ่มการตรวจสอบเอกสาร  →", key="go_audit", use_container_width=True):
            st.session_state.current_page = "audit_page"
            st.session_state.audit_step = 0
            st.session_state.audit_result = None
            st.rerun()

    with p_col2:
        st.markdown("""
            <div class='cozy-portal-card'>
                <div class='icon-wrapper'><span class="material-symbols-outlined" style="font-size:26px;">archive</span></div>
                <div class='card-title-text'>ระบบจัดการสถานะ D/O</div>
                <p class='card-desc-text'>บันทึกการปล่อยเอกสารหน้าเคาน์เตอร์ และค้นหาข้อมูลประวัติแบบเรียลไทม์</p>
                <div class='custom-code-box'>
                    <div class='checklist-item'><span class='checklist-item-check'>✓</span> บันทึกการรับ D/O หน้างาน</div>
                    <div class='checklist-item'><span class='checklist-item-check'>✓</span> ระบบสืบค้นด่วนแบบ Real-time</div>
                    <div class='checklist-item'><span class='checklist-item-check'>✓</span> Export Excel พร้อม Format สวยงาม</div>
                </div>
            </div>""", unsafe_allow_html=True)
        if st.button("เปิดพื้นที่จัดการสถานะ  →", key="go_tracking", use_container_width=True):
            st.session_state.current_page = "tracking_page"
            st.rerun()

# ─────────────────────────────────────────────
# 9. AUDIT PAGE
# ─────────────────────────────────────────────
elif st.session_state.current_page == "audit_page":
    if st.button("⬅   กลับหน้าเมนูหลัก", key="back_audit"):
        st.session_state.current_page = "portal"
        st.rerun()

    st.markdown("""
        <div class='inner-header-container'>
            <div class='icon-wrapper' style='margin:0;min-width:54px;'>
                <span class="material-symbols-outlined" style="font-size:26px;">pageview</span>
            </div>
            <div class='inner-title-block'>
                <div class='inner-main-title'>ระบบตรวจสอบความสอดคล้องของข้อมูลเอกสารขนส่งอัตโนมัติ</div>
                <div class='inner-sub-title'>เปรียบเทียบข้อมูลสำคัญระหว่างไฟล์ B/L, Amendment และ Attached Sheet พร้อม Confidence Score</div>
            </div>
        </div>""", unsafe_allow_html=True)

    # ── Progress Steps ──
    steps = ["① อัปโหลดเอกสาร", "② ประมวลผล AI", "③ ผลการตรวจสอบ"]
    step_html = "<div class='step-bar'>"
    for i, s in enumerate(steps):
        cls = "active" if i == st.session_state.audit_step else ("done" if i < st.session_state.audit_step else "")
        step_html += f"<div class='step-item {cls}'>{s}</div>"
    step_html += "</div>"
    st.markdown(step_html, unsafe_allow_html=True)

    # ── Step 0: Upload ──
    if st.session_state.audit_step == 0:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='background:#EDF3EE;padding:12px 20px;border-radius:12px;color:#4A5A4E;font-size:14px;margin-bottom:14px;font-weight:600;'>📄 เอกสารต้นฉบับ B/L</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("ลากไฟล์ B/L มาวาง (หลายไฟล์ได้)", type=["pdf","png","jpg","jpeg"],
                                         accept_multiple_files=True, key="bl_up")
        with col2:
            st.markdown("<div style='background:#FAF2F2;padding:12px 20px;border-radius:12px;color:#A66E6E;font-size:14px;margin-bottom:14px;font-weight:600;'>✏️ ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("ลากไฟล์ Amend และ Attached Sheet", type=["pdf","png","jpg","jpeg"],
                                            accept_multiple_files=True, key="amend_up")

        if bl_files and amend_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูล", use_container_width=True):
                st.session_state.audit_step = 1
                st.session_state["_bl_files"]    = bl_files
                st.session_state["_amend_files"] = amend_files
                st.session_state.audit_bl_names    = [f.name for f in bl_files]
                st.session_state.audit_amend_names = [f.name for f in amend_files]
                st.rerun()

    # ── Step 1: AI Processing ──
    elif st.session_state.audit_step == 1:
        bl_files    = st.session_state.get("_bl_files", [])
        amend_files = st.session_state.get("_amend_files", [])

        with st.spinner("🤖 กำลังวิเคราะห์เอกสารด้วย Gemini AI..."):
            try:
                payload = []
                for f in bl_files:
                    p = file_to_gemini_part(f)
                    if p: payload.append(p)
                for f in amend_files:
                    p = file_to_gemini_part(f)
                    if p: payload.append(p)

                prompt = (
                    "You are an automated Document Audit System for Seabra Trans Freight Forwarding.\n\n"
                    "TASK: Compare the provided Bill of Lading (B/L) files against the Amendment Notices and Attached Sheets.\n\n"
                    "OUTPUT FORMAT RULES (STRICT):\n"
                    "- No greetings, no AI introductions, no casual language.\n"
                    "- Start DIRECTLY with the HTML/Markdown output below.\n"
                    "- Use <span class='badge-match'>MATCH</span> or <span class='badge-mismatch'>MISMATCH</span> or <span class='badge-warn'>MINOR DIFF</span> in the Status column.\n"
                    "- After the tables, output a JSON block (wrapped in ```json ... ```) with this structure:\n"
                    "  { \"confidence\": <0-100 integer>, \"total_fields\": <int>, \"match_count\": <int>, \"mismatch_count\": <int>, \"warn_count\": <int>, \"summary\": \"<one-line Thai summary>\" }\n\n"
                    "FLEXIBLE MATCHING: Minor spacing or text-wrap differences on 'Description of Goods' = MATCH if specs/volume/weight equivalent.\n\n"
                    "SECTION 1 — Detailed Discrepancy Report:\n"
                    "<div class='output-header-box'><span class='material-symbols-outlined' style='font-size:22px;color:#557A61;'>analytics</span>"
                    "<span class='output-header-title'>Detailed Discrepancy & Verification Report</span></div>\n\n"
                    "| B/L No. / D/O Ref | Audit Field | Original B/L | Amendment / Attached Sheet | Status | Remarks |\n"
                    "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                    "| **[BL_NO]** | Consignee | ... | ... | <span class='badge-match'>MATCH</span> | ... |\n"
                    "| **[BL_NO]** | Shipping Marks | ... | ... | <span class='badge-mismatch'>MISMATCH</span> | ... |\n"
                    "| **[BL_NO]** | Description of Goods | ... | ... | <span class='badge-match'>MATCH</span> | ... |\n"
                    "| **[BL_NO]** | Gross Weight (G.W.) | ... | ... | <span class='badge-match'>MATCH</span> | ... |\n"
                    "| **[BL_NO]** | Measurement (CBM) | ... | ... | <span class='badge-warn'>MINOR DIFF</span> | ... |\n\n"
                    "SECTION 2 — Grand Totals Check:\n"
                    "<div class='output-header-box'><span class='material-symbols-outlined' style='font-size:22px;color:#557A61;'>calculate</span>"
                    "<span class='output-header-title'>Manifest Summary — Grand Totals Check</span></div>\n\n"
                    "| Parameter | B/L Total | Amendment Total | Result | Notes |\n"
                    "| :--- | :--- | :--- | :--- | :--- |\n"
                    "| **Total Gross Weight** | [val] | [val] | <span class='badge-match'>MATCH</span> | |\n"
                    "| **Total CBM** | [val] | [val] | <span class='badge-match'>MATCH</span> | |\n\n"
                    "Then output the JSON block.\n"
                )
                payload.append(prompt)

                response = client.models.generate_content(model="gemini-2.5-flash", contents=payload)
                raw_text = response.text

                # Parse confidence JSON
                conf_data = {"confidence": 0, "total_fields": 0, "match_count": 0,
                             "mismatch_count": 0, "warn_count": 0, "summary": ""}
                import re
                json_match = re.search(r"```json\s*(\{.*?\})\s*```", raw_text, re.DOTALL)
                if json_match:
                    try:
                        conf_data = json.loads(json_match.group(1))
                    except Exception:
                        pass
                    # Remove JSON block from display text
                    display_text = raw_text[:json_match.start()] + raw_text[json_match.end():]
                else:
                    display_text = raw_text

                st.session_state.audit_result     = display_text
                st.session_state.audit_confidence = conf_data.get("confidence", 75)
                st.session_state.audit_summary_stats = conf_data

                # Save to audit log
                log = load_audit_log()
                log.append({
                    "date": datetime.now().isoformat(),
                    "bl_files": st.session_state.audit_bl_names,
                    "amend_files": st.session_state.audit_amend_names,
                    "confidence": conf_data.get("confidence", 0),
                    "summary": conf_data.get("summary", ""),
                    "match": conf_data.get("match_count", 0),
                    "mismatch": conf_data.get("mismatch_count", 0),
                })
                save_audit_log(log)

                st.session_state.audit_step = 2
                st.rerun()

            except Exception as e:
                st.markdown(f"<div class='toast-error'>❌ ระบบขัดข้อง: {str(e)}</div>", unsafe_allow_html=True)
                st.session_state.audit_step = 0

    # ── Step 2: Results ──
    elif st.session_state.audit_step == 2:
        stats = st.session_state.audit_summary_stats
        conf  = st.session_state.audit_confidence
        conf_color = "#557A61" if conf >= 80 else ("#E6A817" if conf >= 60 else "#C0524E")

        st.markdown("<div class='toast-success'>✅ การตรวจสอบเสร็จสิ้น — ดูผลด้านล่างได้เลย</div>", unsafe_allow_html=True)

        # ── Stats row ──
        s1, s2, s3, s4 = st.columns(4)
        with s1:
            st.markdown(f"<div class='stat-card'><div class='stat-num' style='color:{conf_color}'>{conf}%</div><div class='stat-lbl'>Confidence Score</div></div>", unsafe_allow_html=True)
        with s2:
            st.markdown(f"<div class='stat-card'><div class='stat-num' style='color:#557A61'>{stats.get('match_count',0)}</div><div class='stat-lbl'>MATCH</div></div>", unsafe_allow_html=True)
        with s3:
            st.markdown(f"<div class='stat-card'><div class='stat-num' style='color:#C0524E'>{stats.get('mismatch_count',0)}</div><div class='stat-lbl'>MISMATCH</div></div>", unsafe_allow_html=True)
        with s4:
            st.markdown(f"<div class='stat-card'><div class='stat-num' style='color:#E6A817'>{stats.get('warn_count',0)}</div><div class='stat-lbl'>MINOR DIFF</div></div>", unsafe_allow_html=True)

        # ── Confidence gauge ──
        st.markdown(f"""
            <div class='conf-gauge-wrap' style='margin-top:20px;'>
                <div class='conf-label'>AI Confidence Level</div>
                <div class='conf-bar-bg'>
                    <div class='conf-bar-fill' style='width:{conf}%;background:{conf_color};'></div>
                </div>
                <div style='font-size:12px;color:#7A857D;margin-top:6px;'>{stats.get("summary","")}</div>
            </div>""", unsafe_allow_html=True)

        # ── Export buttons ──
        ex1, ex2, ex3 = st.columns([2, 2, 4])
        with ex1:
            audit_xlsx = export_audit_excel(
                st.session_state.audit_result or "",
                st.session_state.audit_bl_names,
                st.session_state.audit_amend_names
            )
            st.download_button(
                "📥 Export ผลตรวจ Excel",
                data=audit_xlsx,
                file_name=f"audit_report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with ex2:
            if st.button("🔄 ตรวจสอบชุดใหม่", use_container_width=True):
                st.session_state.audit_step = 0
                st.session_state.audit_result = None
                st.rerun()

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(st.session_state.audit_result or "", unsafe_allow_html=True)

        # ── Audit History ──
        st.markdown("<hr style='border:0;border-top:1px solid #EAE8DF;margin:30px 0 20px 0;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight:700;color:#2D3531;margin-bottom:14px;'>🕐 ประวัติการตรวจสอบล่าสุด</h4>", unsafe_allow_html=True)
        log_entries = load_audit_log()[-8:][::-1]
        if log_entries:
            hist_html = "<div style='background:#FFF;border:1px solid #EAE8DF;border-radius:14px;overflow:hidden;'>"
            for entry in log_entries:
                ts = entry.get("date","")[:16].replace("T"," ")
                bl = ", ".join(entry.get("bl_files",[]))
                conf_e = entry.get("confidence", 0)
                cc = "#557A61" if conf_e >= 80 else ("#E6A817" if conf_e >= 60 else "#C0524E")
                hist_html += f"""
                    <div class='hist-row'>
                        <div>
                            <div style='font-weight:600;color:#2D3531;'>{bl}</div>
                            <div style='font-size:12px;color:#7A857D;margin-top:2px;'>{entry.get("summary","")}</div>
                        </div>
                        <div style='text-align:right;'>
                            <span style='color:{cc};font-weight:700;font-size:15px;'>{conf_e}%</span>
                            <div class='hist-time'>{ts}</div>
                        </div>
                    </div>"""
            hist_html += "</div>"
            st.markdown(hist_html, unsafe_allow_html=True)
        else:
            st.markdown("<div style='color:#A0ADA2;font-size:13.5px;'>ยังไม่มีประวัติการตรวจสอบในระบบ</div>", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 10. TRACKING PAGE
# ─────────────────────────────────────────────
elif st.session_state.current_page == "tracking_page":
    if st.button("⬅   กลับหน้าเมนูหลัก", key="back_tracking"):
        st.session_state.current_page = "portal"
        st.rerun()

    st.markdown("""
        <div class='inner-header-container'>
            <div class='icon-wrapper' style='margin:0;min-width:54px;'>
                <span class="material-symbols-outlined" style="font-size:26px;">archive</span>
            </div>
            <div class='inner-title-block'>
                <div class='inner-main-title'>ระบบจัดการและตรวจสอบสถานะการส่งมอบ D/O</div>
                <div class='inner-sub-title'>บันทึกยืนยันวันที่มารับชุดเอกสาร และค้นหาข้อมูลประวัติเพื่อบริการตอบกลับหน้างานรวดเร็ว</div>
            </div>
        </div>""", unsafe_allow_html=True)

    df_current = load_do_data()

    # ── Entry Form ──
    st.markdown("<h4 style='font-weight:700;color:#2D3531;margin-top:0;'>✏️ บันทึกการรับ D/O หน้างาน</h4>", unsafe_allow_html=True)
    with st.form(key="do_form", clear_on_submit=True):
        cx1, cx2, cx3 = st.columns([3, 3, 2])
        with cx1:
            inp_bl = st.text_input("หมายเลข B/L", placeholder="เช่น PKELCH2660002")
        with cx2:
            inp_con = st.text_input("ชื่อ Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.")
        with cx3:
            inp_by = st.text_input("บันทึกโดย", placeholder="ชื่อผู้บันทึก")
        st.markdown("<br>", unsafe_allow_html=True)
        submitted = st.form_submit_button("💾 บันทึกวันรับ D/O", use_container_width=True)

        if submitted:
            if inp_bl.strip():
                bl_c  = inp_bl.strip()
                con_c = inp_con.strip() or "ลูกค้าหน้าเคาน์เตอร์"
                by_c  = inp_by.strip() or "Staff"
                today = datetime.now().strftime("%Y-%m-%d")
                df_current = df_current[df_current["เลขที่ B/L"] != bl_c]
                new_row = pd.DataFrame([{"เลขที่ B/L": bl_c, "ชื่อ Consignee": con_c,
                                          "วันที่รับ D/O": today, "บันทึกโดย": by_c}])
                df_current = pd.concat([df_current, new_row], ignore_index=True)
                try:
                    save_do_data(df_current)
                    st.markdown(f"<div class='toast-success'>✅ บันทึก {bl_c} เรียบร้อยแล้ว</div>", unsafe_allow_html=True)
                    st.rerun()
                except Exception as e:
                    st.markdown(f"<div class='toast-error'>❌ บันทึกไม่สำเร็จ: {e}</div>", unsafe_allow_html=True)
            else:
                st.warning("⚠️ กรุณากรอกหมายเลข B/L")

    st.markdown("<hr style='border:0;border-top:1px solid #EAE8DF;margin:24px 0;'>", unsafe_allow_html=True)

    # ── Search + Export ──
    srch1, srch2 = st.columns([5, 2])
    with srch1:
        st.markdown("<h4 style='font-weight:700;color:#2D3531;margin-top:0;'>🔍 ค้นหาด่วนประวัติ D/O</h4>", unsafe_allow_html=True)
        q = st.text_input("ค้นหาด้วย B/L หรือชื่อ Consignee", placeholder="พิมพ์คำค้นหา...", key="search_q")
    with srch2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        do_xlsx = export_do_excel(df_current)
        st.download_button(
            "📥 Export D/O Excel",
            data=do_xlsx,
            file_name=f"DO_records_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )

    if q.strip():
        mask = (df_current["เลขที่ B/L"].str.contains(q.strip(), case=False, na=False) |
                df_current["ชื่อ Consignee"].str.contains(q.strip(), case=False, na=False))
        df_show = df_current[mask]
    else:
        df_show = df_current

    if df_show.empty:
        st.markdown("<div style='color:#A0ADA2;font-size:13.5px;padding:20px 0;'>ไม่พบข้อมูลที่ค้นหา</div>", unsafe_allow_html=True)
    else:
        st.dataframe(df_show, use_container_width=True, hide_index=True)

    # ── Danger Zone ──
    st.markdown("<hr style='border:0;border-top:1px solid #EAE8DF;margin:30px 0 20px 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='color:#A66E6E;font-size:13px;font-weight:600;'>⚠️ โซนอันตรายสำหรับผู้ดูแลระบบ</p>", unsafe_allow_html=True)
    dz1, dz2 = st.columns(2)
    with dz1:
        if st.button("🗑️ ล้างฐานข้อมูล D/O ทั้งหมด", key="clear_do"):
            if os.path.exists(EXCEL_FILE):
                os.remove(EXCEL_FILE)
                st.success("รีเซ็ตฐานข้อมูล D/O เรียบร้อยแล้ว")
                st.rerun()
    with dz2:
        if st.button("🗑️ ล้างประวัติการตรวจสอบทั้งหมด", key="clear_log"):
            if os.path.exists(AUDIT_LOG_FILE):
                os.remove(AUDIT_LOG_FILE)
                st.success("ลบ Audit History เรียบร้อยแล้ว")
                st.rerun()

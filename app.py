import streamlit as st
from google import genai
import io
import os
import pandas as pd
from datetime import datetime

# 🎨 1. Set Page Configuration
st.set_page_config(
    page_title="VerifyHub - Document Verification System", 
    page_icon="🌿", 
    layout="wide"
)

# 🖌 ดึงคีย์จากระบบ Secrets ของ Streamlit
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = "AQ.Ab8RN6KfAAI3LV9KOfLxE7OFDtcqamABiIk3IY24OYGUkmZtHw"

# 🖌️ 2. Inject Custom CSS (Cozy Modern - Pure Light Mode Enforcement)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
        
        /* 💡 FORCE LIGHT THEME BASE & PREVENT DARK MODE OVERRIDES */
        html, body, [data-testid="stAppViewContainer"] {
            background-color: #FAF8F5 !important;
            color: #4A5A4E !important;
        }
        .stApp {
            background: #FAF8F5 !important;
            font-family: 'Bai Jamjuree', sans-serif;
        }
        
        /* Typography */
        div[data-testid="stMarkdownContainer"] p, 
        div[data-testid="stMarkdownContainer"] li,
        div[data-testid="stMarkdownContainer"] span {
            color: #5A665E !important;
            line-height: 1.65;
            font-size: 14.5px;
        }
        div[data-testid="stMarkdownContainer"] h1,
        div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3 {
            color: #2D3531 !important;
            font-family: 'Bai Jamjuree', sans-serif;
            font-weight: 700;
        }
        
        /* Navigation Header */
        .brand-block { text-align: left; }
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #2D3531 !important; 
            font-weight: 800; font-size: 24px; letter-spacing: -0.5px;
        }
        .brand-subtitle {
            font-family: 'Manrope', sans-serif;
            color: #8C968E !important; font-size: 12px; font-weight: 500; margin-top: -2px;
        }
        .user-profile-box {
            display: flex; align-items: center; justify-content: flex-end; gap: 12px;
            background-color: #FFFFFF !important; padding: 8px 16px; border-radius: 12px;
            border: 1px solid #EAE8DF !important;
        }
        .user-profile-box span, .user-profile-box div {
            color: #4A5A4E !important;
        }
        
        /* Top Horizontal Rule */
        .custom-hr {
            border: 0; border-top: 1px solid #EAE8DF; margin: 20px 0 15px 0;
        }
        
        /* Breadcrumb Bar */
        .breadcrumb-text { font-size: 13px; color: #8C968E !important; margin-bottom: 25px; }
        .breadcrumb-text b { color: #2D3531 !important; }

        /* ================= PORTAL PAGE CARDS (EXACT MATCH) ================= */
        .main-portal-container {
            margin-top: 10px;
        }
        .portal-meta-line {
            font-size: 13px; color: #8C968E !important; font-weight: 500; margin-bottom: 6px;
        }
        .portal-title-headline {
            font-size: 42px; font-weight: 700; color: #2D3531 !important; letter-spacing: -0.8px; margin-bottom: 12px;
        }
        .portal-subtitle-headline {
            font-size: 16px; color: #5A665E !important; margin-bottom: 45px;
        }
        .section-divider-title {
            font-size: 11px; font-weight: 700; color: #A4ABA5 !important; letter-spacing: 1.5px; text-transform: uppercase;
            border-bottom: 1px solid #EAE8DF; padding-bottom: 10px; margin-bottom: 30px;
        }
        
        .workspace-card-grid {
            background: #FFFFFF !important;
            border: 1px solid #EAE8DF !important;
            border-radius: 24px !important;
            padding: 35px 30px !important;
            box-shadow: 0 4px 24px rgba(141, 137, 120, 0.02) !important;
            text-align: center;
            display: flex; flex-direction: column; justify-content: space-between;
            min-height: 500px;
        }
        .card-top-meta {
            display: flex; justify-content: space-between; align-items: center; width: 100%; margin-bottom: 15px;
        }
        .card-icon-box {
            width: 48px; height: 48px; border-radius: 50%; border: 1px solid #EAE8DF !important;
            background: #FFFFFF !important; display: flex; align-items: center; justify-content: center;
            color: #5F7464 !important;
        }
        .card-badge-tag {
            background: #F4F3EE !important; color: #7A857D !important; font-size: 11px; font-weight: 600;
            padding: 5px 14px; border-radius: 20px;
        }
        .card-title-text {
            font-size: 22px; font-weight: 700; color: #2D3531 !important; margin-top: 15px; margin-bottom: 12px;
        }
        .card-desc-text {
            font-size: 14px; color: #7A857D !important; line-height: 1.5; margin-bottom: 25px; padding: 0 10px;
        }
        .card-inner-checklist-box {
            background: #F7F5F0 !important; border-radius: 16px; padding: 20px 22px; text-align: left; margin-bottom: 30px;
        }
        .card-checklist-item {
            font-size: 13.5px; color: #4A5A4E !important; margin-bottom: 10px; display: flex; align-items: center; gap: 12px;
        }
        .card-checklist-item:last-child { margin-bottom: 0; }
        .card-checklist-icon { color: #5F7464 !important; font-weight: 800; }

        /* ================= AUDIT WORKSPACE HEADER ================= */
        .workspace-header-card { display: flex; align-items: center; justify-content: space-between; margin-bottom: 35px; }
        .header-left-zone { display: flex; align-items: center; gap: 20px; }
        .search-icon-circle {
            width: 54px; height: 54px; border-radius: 50%; border: 1px solid #EAE8DF !important;
            background: #FFFFFF !important; display: flex; align-items: center; justify-content: center; color: #5F7464 !important;
        }
        .workspace-title-main { font-size: 24px; font-weight: 700; color: #2D3531 !important; letter-spacing: -0.3px; }
        .workspace-subtitle-main { font-size: 14px; color: #8C968E !important; margin-top: 2px; }
        
        /* ================= FIXED FILE UPLOADER (ANTI-DARK MODE) ================= */
        .uploader-header-tab {
            font-size: 13.5px; font-weight: 600; padding: 10px 16px; border-radius: 8px 8px 0 0; margin-bottom: -2px; display: inline-flex; align-items: center; gap: 8px;
        }
        .tab-bl { background-color: #EEF3EF !important; color: #3E5C47 !important; }
        .tab-amend { background-color: #FAF1F1 !important; color: #A45353 !important; }
        
        /* Strict Overrides to guarantee White Background and Dark Text even in dark mode */
        div[data-testid="stFileUploader"] {
            background-color: #FFFFFF !important; 
            border: 1.5px dashed #D3CFC4 !important;
            border-radius: 20px !important; 
            padding: 40px 20px !important;
            text-align: center !important;
            box-shadow: 0 4px 16px rgba(141, 137, 120, 0.01) !important;
        }
        div[data-testid="stFileUploader"] * {
            color: #4A5A4E !important; /* Force all internal text to be dark grey/green */
            background-color: transparent !important;
        }
        div[data-testid="stFileUploader"] section button {
            color: #5F7464 !important;
            text-decoration: underline !important;
            font-weight: 600 !important;
            display: inline !important;
        }
        div[data-testid="stFileUploader"] section p {
            color: #8C968E !important;
            font-size: 13px !important;
        }
        /* Style the 'No files uploaded' text container below uploader */
        div[data-testid="stFileUploaderDropzone"] + div {
            color: #8C968E !important;
            text-align: center !important;
        }

        /* ================= OVERRIDE STREAMLIT BUTTONS ================= */
        /* 1. Global/Outline Action Buttons (Card Action Links) */
        div.stButton > button {
            border-radius: 24px !important; 
            border: 1px solid #EAE8DF !important;
            background-color: #FFFFFF !important; 
            color: #2D3531 !important;
            font-family: 'Bai Jamjuree', sans-serif !important; 
            font-weight: 600 !important; font-size: 14px !important;
            padding: 10px 24px !important;
            transition: all 0.2s ease;
            width: 100% !important;
        }
        div.stButton > button:hover {
            border-color: #5F7464 !important;
            background-color: #5F7464 !important;
            color: #FFFFFF !important;
        }
        
        /* 2. Specific Back button overriding layout positioning */
        div.stButton > button[key*="back_from_audit"],
        div.stButton > button[key*="back_from_tracking"] {
            border-radius: 20px !important; border: 1px solid #EAE8DF !important;
            background-color: #FFFFFF !important; color: #2D3531 !important;
            font-size: 13.5px !important; padding: 8px 20px !important; font-weight: 500 !important;
            width: auto !important;
        }
        div.stButton > button[key*="back_from_audit"]:hover,
        div.stButton > button[key*="back_from_tracking"]:hover {
            border-color: #5F7464 !important; background-color: #F5F3EF !important; color: #5F7464 !important;
        }
        
        /* 3. Main Audit Process Action Button (Solid Sage Green #5F7464) */
        div.stButton > button[key*="process_audit"] {
            background-color: #5F7464 !important;
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 24px !important;
            padding: 14px 45px !important;
            font-size: 15px !important; font-weight: 600 !important;
            box-shadow: 0 4px 15px rgba(95, 116, 100, 0.15) !important;
            display: block; margin: 35px auto 0 auto !important;
            width: auto !important; min-width: 290px;
        }
        div.stButton > button[key*="process_audit"]:hover {
            background-color: #4D5E51 !important;
            color: #FFFFFF !important;
        }
        
        /* Data Tables Styling */
        div[data-testid="stMarkdownContainer"] table {
            color: #4A5A4E !important; background-color: #FFFFFF !important; border-collapse: collapse !important;
            border-radius: 16px !important; overflow: hidden !important; box-shadow: 0 4px 20px rgba(141, 137, 120, 0.01) !important;
            margin: 20px 0 !important; width: 100% !important; border: 1px solid #EAE8DF !important;
        }
        div[data-testid="stMarkdownContainer"] th {
            background-color: #F5F3EF !important; color: #2D3531 !important; font-weight: 600 !important;
            padding: 14px 16px !important; border-bottom: 1.5px solid #EAE8DF !important; font-size: 14px;
        }
        div[data-testid="stMarkdownContainer"] td { padding: 14px 16px !important; border-bottom: 1px solid #F0EDE8 !important; font-size: 13.5px; }
        .status-badge-match { color: #2E593A !important; background-color: #E8F2EA; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px; display: inline-block; }
        .status-badge-mismatch { color: #9C4141 !important; background-color: #FCEAEA; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px; display: inline-block; }
        .output-header-box { display: flex; align-items: center; gap: 10px; margin-top: 35px; margin-bottom: 10px; color: #2D3531 !important; }
        .output-header-title { font-size: 16px; font-weight: 700; letter-spacing: -0.2px; }
    </style>
""", unsafe_allow_html=True)

# 🧠 ⚙️ CORE DATABASE
EXCEL_FILE = "do_database_records.xlsx"

def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=["เลขที่ B/L", "ชื่อ Consignee", "วันที่รับ D/O"])

if "current_page" not in st.session_state:
    st.session_state.current_page = "portal"

# 🏢 TOP NAVIGATION HEADER
nav_col1, nav_col2 = st.columns([7, 3])
with nav_col1:
    st.markdown("""
        <div class='brand-block'>
            <div class='brand-header'>VERIFYHUB</div>
            <div class='brand-subtitle'>Freight Document Operations Platform</div>
        </div>
    """, unsafe_allow_html=True)
with nav_col2:
    st.markdown(f"""
        <div class='user-profile-box'>
            <div style='font-size: 13px; color: #7A857D;'>📅 Mon, 29 Jun 2026</div>
            <div style='border-left: 1px solid #EAE8DF; height: 18px;'></div>
            <div style='font-size:13px; color:#4A5A4E; text-align:right;'>
                <span style='font-weight:700; color:#2D3531;'>Seabra Team</span>
                <span style='color:#7A857D; font-size:11.5px;'> (Import-Export Dept.)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<div class='custom-hr'></div>", unsafe_allow_html=True)

# 🔐 เช็คและเปิดใช้งานโมเดล
if not API_KEY or API_KEY == "":
    st.error("⚠️ ไม่พบรหัสผ่าน API Key ในระบบ")
else:
    client = genai.Client(api_key=API_KEY)
    
    # 🚪 ================== [หน้าหลัก Menu Portal - EXACT REPLICA] ==================
    if st.session_state.current_page == "portal":
        st.markdown("""
            <div class='main-portal-container'>
                <div class='portal-meta-line'>● 2 Workspaces Available · 29 มิ.ย. 2569</div>
                <div class='portal-title-headline'>Welcome back.</div>
                <div class='portal-subtitle-headline'>Ready to verify your shipping documents.</div>
                <div class='section-divider-title'>Workspaces</div>
            </div>
        """, unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4.6, 0.8, 4.6])
        with p_col1:
            st.markdown("""
                <div class='workspace-card-grid'>
                    <div class='card-top-meta'>
                        <div class='card-icon-box'>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                        </div>
                        <div class='card-badge-tag'>Document Audit</div>
                    </div>
                    <div>
                        <div class='card-title-text'>ตรวจสอบเอกสาร</div>
                        <div class='card-desc-text'>เปรียบเทียบข้อมูล B/L กับ Amendment อัตโนมัติ พร้อมรายงานผลแบบ field-by-field</div>
                    </div>
                    <div class='card-inner-checklist-box'>
                        <div class='card-checklist-item'><span class='card-checklist-icon'>✓</span> Bill of Lading (B/L)</div>
                        <div class='card-checklist-item'><span class='card-checklist-icon'>✓</span> Amendment Notice</div>
                        <div class='card-checklist-item'><span class='card-checklist-icon'>✓</span> Attached Sheet & ไฟล์แนบ</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เริ่มตรวจสอบเอกสาร →", key="go_audit"):
                st.session_state.current_page = "audit_page"
                st.rerun()
                
        with p_col2:
            st.markdown("""
                <div class='workspace-card-grid'>
                    <div class='card-top-meta'>
                        <div class='card-icon-box'>
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M21 8V21H3V8"></path><path d="M23 3H1V8H23V3Z"></path><path d="M10 12H14"></path></svg>
                        </div>
                        <div class='card-badge-tag'>D/O Management</div>
                    </div>
                    <div>
                        <div class='card-title-text'>บันทึกรับ D/O</div>
                        <div class='card-desc-text'>บันทึกและค้นหาประวัติการรับมอบเอกสาร D/O หน้าเคาน์เตอร์ พร้อมระบบ search realtime</div>
                    </div>
                    <div class='card-inner-checklist-box'>
                        <div class='card-checklist-item'><span class='card-checklist-icon'>✓</span> D/O Release Logging</div>
                        <div class='card-checklist-item'><span class='card-checklist-icon'>✓</span> Consignee Tracking</div>
                        <div class='card-checklist-item'><span class='card-checklist-icon'>✓</span> Quick Search History</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เปิดพื้นที่จัดการ D/O →", key="go_tracking"):
                st.session_state.current_page = "tracking_page"
                st.rerun()

    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร - REPLICA FROM IMAGE] ==================
    elif st.session_state.current_page == "audit_page":
        st.markdown("<div class='breadcrumb-text'>Home › <b>Document Audit</b></div>", unsafe_allow_html=True)
        
        head_col1, head_col2 = st.columns([8, 2])
        with head_col1:
            st.markdown("""
                <div class='header-left-zone'>
                    <div class='search-icon-circle'>
                        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    </div>
                    <div>
                        <div class='workspace-title-main'>Document Audit Workspace</div>
                        <div class='workspace-subtitle-main'>อัปโหลดเอกสารเพื่อเปรียบเทียบข้อมูลจำเพาะ</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        with head_col2:
            st.markdown("<div style='text-align: right; margin-top: 5px;'>", unsafe_allow_html=True)
            if st.button("🏠 กลับหน้าหลัก", key="back_from_audit"):
                st.session_state.current_page = "portal"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='uploader-header-tab tab-bl'>📄 1. ไฟล์เอกสาร B/L ตัวหลัก</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("ลากไฟล์มาวางตรงนี้ หรือ เลือกไฟล์จากเครื่อง", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<div class='uploader-header-tab tab-amend'>📄 2. ไฟล์ใบแก้ไข AMENDMENT NOTICE</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("ลากไฟล์มาวางตรงนี้ หรือ เลือกไฟล์จากเครื่อง", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        process_clicked = st.button("เริ่มกระบวนการตรวจสอบเอกสาร", key="process_audit")

        if process_clicked:
            if bl_files and amend_files:
                with st.spinner("กำลังใช้โมเดลวิเคราะห์ข้อมูลเอกสารคู่ขนาน..."):
                    try:
                        prompt_instruction = (
                            "You are an automated Data Compliance Audit Engine configured specifically for Seabra Trans Freight Forwarding Operations. "
                            "Your task is to analyze and compare logistics manifests (B/L) with requested adjustments (Amendments & Attached Sheets).\n"
                            "CRITICAL REQUIREMENT: There are multiple Bill of Lading (B/L) documents inside the payload. You must scan ALL of them and generate verification report rows for EVERY SINGLE B/L number found. Do not drop or miss any B/L numbers.\n\n"
                            "📢 STRICT OUTPUT CONSTRAINT:\n"
                            "- DO NOT include any conversational text, chat introductions, greetings, summaries, or post-analysis notes.\n"
                            "- Start rendering the structural output directly from the HTML code segments below.\n"
                            "- Absolutely no emojis are allowed in the text output.\n\n"
                            "🎨 FORMAT STRUCTURES TO RENDER:\n"
                            "<div class='output-header-box'><span class='output-header-title'>รายงานผลการตรวจสอบเปรียบเทียบข้อมูลเอกสารรายฉบับ</span></div>\n\n"
                            "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลต้นฉบับบนใบ B/L | ข้อมูลบนใบ Amend + Attached Sheet | ผลการตรวจสอบ | หมายเหตุคำวิเคราะห์ / เกณฑ์การอนุโลม |\n"
                            "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                            "| **[B/L Number]** | ผู้รับสินค้า (Consignee) | ... | ... | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | ... |\n"
                            "| **[B/L Number]** | จำนวนสินค้า (Quantity) | ... | ... | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | ... |\n\n"
                            "<div class='output-header-box'><span class='output-header-title'>ตารางสรุปการกระทบยอดน้ำหนักและปริมาตรสุทธิ</span></div>\n\n"
                            "| พารามิเตอร์ที่ตรวจสอบ | ผลรวมคำนวณจาก B/L ทุกฉบับ | ยอดรวมสุทธิบนใบขอแก้ไข (Amend) | สถานะความถูกต้อง | รายละเอียดประกอบการคำนวณ |\n"
                            "| :--- | :--- | :--- | :--- | :--- |\n"
                            "| **น้ำหนักมวลรวมสะสม (Total G.W.)** | [Value] | [Value] | <span class='status-badge-match'>MATCH</span> | [สูตรการบวกเลข] |\n"
                        )

                        contents_payload = [prompt_instruction]
                        for bl in bl_files:
                            contents_payload.append(genai.types.Part.from_bytes(data=bl.getvalue(), mime_type=bl.type))
                        for amend in amend_files:
                            contents_payload.append(genai.types.Part.from_bytes(data=amend.getvalue(), mime_type=amend.type))
                        
                        response = client.models.generate_content(
                            model='gemini-2.5-flash', 
                            contents=contents_payload
                        )
                        st.balloons()
                        st.markdown(response.text, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"ระบบขัดข้องในการส่งข้อมูลชุดเอกสาร: {str(e)}")
            else:
                st.warning("⚠️ กรุณาอัปโหลดเอกสารให้ครบทั้งสองฝั่งก่อนเริ่มกระบวนการตรวจสอบ")

    # 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O] ==================
    elif st.session_state.current_page == "tracking_page":
        st.markdown("<div class='breadcrumb-text'>Home › <b>D/O Management</b></div>", unsafe_allow_html=True)
        
        track_col1, track_col2 = st.columns([8, 2])
        with track_col1:
            st.markdown("<div style='font-size: 24px; font-weight: 700; color: #2D3531;'>ระบบจัดการและตรวจสอบสถานะการส่งมอบ D/O</div>", unsafe_allow_html=True)
        with track_col2:
            st.markdown("<div style='text-align: right;'>", unsafe_allow_html=True)
            if st.button("🏠 กลับหน้าหลัก", key="back_from_tracking"):
                st.session_state.current_page = "portal"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        df_current = load_data()
        
        with st.form(key="do_entry_form", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1: input_bl = st.text_input("หมายเลข Bill of Lading (B/L)")
            with cx2: input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee")
            st.markdown("<div style='margin-top:10px;'></div>", unsafe_allow_html=True)
            submit_save = st.form_submit_button("บันทึกข้อมูลการรับมอบเอกสาร", use_container_width=True)
            
            if submit_save and input_bl:
                today_str = datetime.now().strftime("%Y-%m-%d")
                new_row = pd.DataFrame([{"เลขที่ B/L": input_bl.strip(), "ชื่อ Consignee": input_consignee.strip(), "วันที่รับ D/O": today_str}])
                df_current = pd.concat([df_current, new_row], ignore_index=True)
                df_current.to_excel(EXCEL_FILE, index=False)
                st.success("บันทึกประวัติเสร็จสิ้น")
                st.rerun()
                
        st.markdown("<div style='margin-top:25px; font-weight:600; color:#2D3531; font-size:15px;'>📋 ประวัติรายการรับมอบเอกสารล่าสุด</div>", unsafe_allow_html=True)
        st.table(df_current)

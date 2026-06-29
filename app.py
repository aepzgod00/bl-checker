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

# 🖌️ 2. Inject Custom CSS (Cozy Modern Style - Exactly matching the image)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;600;700;800&display=swap');
        
        /* Global App Styling */
        .stApp {
            background: #FAF8F5 !important;
            font-family: 'Bai Jamjuree', sans-serif;
        }
        
        /* Typography */
        div[data-testid="stMarkdownContainer"] p, 
        div[data-testid="stMarkdownContainer"] li {
            color: #5A665E !important;
            line-height: 1.65;
            font-size: 14.5px;
        }
        
        /* Main Navigation Header */
        .brand-block { text-align: left; }
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #2D3531; 
            font-weight: 800;
            font-size: 24px;
            letter-spacing: -0.5px;
        }
        .brand-subtitle {
            font-family: 'Manrope', sans-serif;
            color: #8C968E;
            font-size: 12px;
            font-weight: 500;
            margin-top: -2px;
        }
        .user-profile-box {
            display: flex; align-items: center; justify-content: flex-end; gap: 12px;
            background-color: #FFFFFF; padding: 8px 16px; border-radius: 12px;
            border: 1px solid #EAE8DF;
        }
        
        /* Breadcrumb Bar */
        .breadcrumb-text {
            font-size: 13px;
            color: #8C968E;
            margin-bottom: 25px;
        }
        
        /* Workspace Header Section (Matching the Image) */
        .workspace-header-card {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 35px;
            background: transparent;
        }
        .header-left-zone {
            display: flex;
            align-items: center;
            gap: 20px;
        }
        .search-icon-circle {
            width: 54px; height: 54px;
            border-radius: 50%;
            border: 1px solid #EAE8DF;
            background: #FFFFFF;
            display: flex; align-items: center; justify-content: center;
            color: #2D3531;
            box-shadow: 0 4px 12px rgba(0,0,0,0.01);
        }
        .workspace-title-main {
            font-size: 24px; font-weight: 700; color: #2D3531; letter-spacing: -0.3px;
        }
        .workspace-subtitle-main {
            font-size: 14px; color: #8C968E; margin-top: 2px;
        }
        
        /* ================= UI CUSTOM FILE UPLOADER ================= */
        /* Header tabs above uploader */
        .uploader-header-tab {
            font-size: 13.5px;
            font-weight: 600;
            padding: 10px 16px;
            border-radius: 8px 8px 0 0;
            margin-bottom: -2px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
        }
        .tab-bl { background-color: #EEF3EF; color: #3E5C47; }
        .tab-amend { background-color: #FAF1F1; color: #A45353; }
        
        /* Seamlessly override Streamlit File Uploader Box to match the exact image look */
        div[data-testid="stFileUploader"] {
            background-color: #FFFFFF !important; 
            border: 1.5px dashed #D3CFC4 !important;
            border-radius: 20px !important; 
            padding: 40px 20px !important;
            text-align: center !important;
            box-shadow: 0 4px 16px rgba(141, 137, 120, 0.02) !important;
            transition: all 0.2s ease;
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #2D3531 !important;
        }
        /* Hide default streamlit icon & text styling to let it look cozy */
        div[data-testid="stFileUploader"] section button {
            background-color: transparent !important;
            border: none !important;
            color: #4A5A4E !important;
            text-decoration: underline !important;
            font-weight: 500 !important;
            padding: 0 !important;
            display: inline !important;
        }
        div[data-testid="stFileUploader"] section p {
            color: #8C968E !important;
            font-size: 13px !important;
        }
        
        /* ================= BUTTONS DESIGN ================= */
        /* 1. Back button (Upper Right) */
        div.stButton > button[key*="back_from_audit"] {
            border-radius: 20px !important; 
            border: 1px solid #EAE8DF !important;
            background-color: #FFFFFF !important; 
            color: #2D3531 !important;
            font-size: 13.5px !important;
            padding: 8px 20px !important;
            font-weight: 500 !important;
        }
        div.stButton > button[key*="back_from_audit"]:hover {
            background-color: #F5F3EF !important;
            border-color: #2D3531 !important;
        }
        
        /* 2. Primary Audit Action Button (Centered Bottom - Solid Sage Green color in image) */
        div.stButton > button[key*="process_audit"] {
            background-color: #A9B3A7 !important; /* Sage green muted tint from the image */
            color: #FFFFFF !important;
            border: none !important;
            border-radius: 24px !important;
            padding: 14px 40px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            letter-spacing: 0.2px;
            box-shadow: 0 4px 15px rgba(169, 179, 167, 0.2) !important;
            display: block;
            margin: 30px auto 0 auto !important;
            width: auto !important;
            min-width: 280px;
        }
        div.stButton > button[key*="process_audit"]:hover {
            background-color: #8F9A8D !important;
            color: #FFFFFF !important;
        }
        
        /* Portal Card Layout Overrides */
        .workspace-container {
            background: #FFFFFF; border: 1px solid #EAE8DF; border-radius: 24px;
            padding: 40px 32px; box-shadow: 0 4px 24px rgba(141, 137, 120, 0.03);
            text-align: center; height: 100%; display: flex; flex-direction: column; justify-content: space-between;
        }
        .workspace-badge {
            background: #F4F3EE; color: #7A857D; font-size: 11px; font-weight: 600;
            padding: 4px 12px; border-radius: 20px; display: inline-block; align-self: flex-end; margin-top: -15px;
        }
        .workspace-icon-circle {
            width: 56px; height: 56px; border-radius: 50%; border: 1px solid #EAE8DF;
            display: flex; align-items: center; justify-content: center; margin: 10px auto 24px auto; color: #2D3531;
        }
        .workspace-title { font-size: 22px; font-weight: 700; color: #2D3531; margin-bottom: 12px; }
        .workspace-desc { font-size: 14px; color: #7A857D; line-height: 1.5; margin-bottom: 24px; }
        .workspace-checklist { background: #FAF9F5; border-radius: 16px; padding: 20px; text-align: left; margin-bottom: 30px; }
        .checklist-line { font-size: 13.5px; color: #4A5A4E; margin-bottom: 10px; display: flex; align-items: center; gap: 10px; }
        .checklist-icon { color: #607366; font-weight: bold; }
        
        /* Data Tables Styling */
        div[data-testid="stMarkdownContainer"] table {
            color: #4A5A4E !important; background-color: #FFFFFF !important; border-collapse: collapse !important;
            border-radius: 16px !important; overflow: hidden !important; box-shadow: 0 4px 20px rgba(141, 137, 120, 0.02) !important;
            margin: 20px 0 !important; width: 100% !important; border: 1px solid #EAE8DF !important;
        }
        div[data-testid="stMarkdownContainer"] th {
            background-color: #F5F3EF !important; color: #2D3531 !important; font-weight: 600 !important;
            padding: 14px 16px !important; border-bottom: 1.5px solid #EAE8DF !important; font-size: 14px;
        }
        div[data-testid="stMarkdownContainer"] td { padding: 14px 16px !important; border-bottom: 1px solid #F0EDE8 !important; font-size: 13.5px; }
        .status-badge-match { color: #2E593A !important; background-color: #E8F2EA; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px; display: inline-block; }
        .status-badge-mismatch { color: #9C4141 !important; background-color: #FCEAEA; padding: 4px 10px; border-radius: 6px; font-weight: 700; font-size: 12px; display: inline-block; }
        .output-header-box { display: flex; align-items: center; gap: 10px; margin-top: 35px; margin-bottom: 10px; color: #2D3531; }
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
            <div style='font-size: 13px; color: #7A857D;'>📅 {datetime.now().strftime('%a, %d %b %Y')}</div>
            <div style='border-left: 1px solid #EAE8DF; height: 18px;'></div>
            <div style='font-size:13px; color:#4A5A4E; text-align:right;'>
                <span style='font-weight:700; color:#2D3531;'>Seabra Team</span>
                <span style='color:#7A857D; font-size:11.5px;'> (Import-Export Dept.)</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 20px 0 15px 0;'>", unsafe_allow_html=True)

# 🔐 เช็คและเปิดใช้งานโมเดล
if not API_KEY or API_KEY == "":
    st.error("⚠️ ไม่พบรหัสผ่าน API Key ในระบบ")
else:
    client = genai.Client(api_key=API_KEY)
    
    # 🚪 ================== [หน้าหลัก Menu Portal] ==================
    if st.session_state.current_page == "portal":
        st.markdown("<div style='font-size:13px; color:#7A857D; margin-bottom:2px; font-weight:500;'>● 2 Workspaces Available</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:36px; font-weight:700; color:#2D3531; letter-spacing:-0.5px; margin-bottom:8px;'>Welcome back.</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:15px; color:#5A665E; margin-bottom:40px;'>Ready to verify your shipping documents.</div>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4.5, 1, 4.5])
        with p_col1:
            st.markdown("""
                <div class='workspace-container'>
                    <div class='workspace-badge'>Document Audit</div>
                    <div class='workspace-icon-circle'>
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                    </div>
                    <div class='workspace-title'>ตรวจสอบเอกสาร</div>
                    <div class='workspace-desc'>เปรียบเทียบข้อมูล B/L กับ Amendment อัตโนมัติ พร้อมรายงานผลแบบ field-by-field</div>
                    <div class='workspace-checklist'>
                        <div class='checklist-line'><span class='checklist-icon'>✓</span> Bill of Lading (B/L)</div>
                        <div class='checklist-line'><span class='checklist-icon'>✓</span> Amendment Notice</div>
                        <div class='checklist-line'><span class='checklist-icon'>✓</span> Attached Sheet & ไฟล์แนบ</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เริ่มตรวจสอบเอกสาร →", key="go_audit", use_container_width=True):
                st.session_state.current_page = "audit_page"
                st.rerun()
                
        with p_col2:
            st.markdown("""
                <div class='workspace-container'>
                    <div class='workspace-badge'>D/O Management</div>
                    <div class='workspace-icon-circle'>
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 8V21H3V8"></path><path d="M23 3H1V8H23V3Z"></path><path d="M10 12H14"></path></svg>
                    </div>
                    <div class='workspace-title'>บันทึกรับ D/O</div>
                    <div class='workspace-desc'>บันทึกและค้นหาประวัติการรับมอบเอกสาร D/O หน้าเคาน์เตอร์ พร้อมระบบ search realtime</div>
                    <div class='workspace-checklist'>
                        <div class='checklist-line'><span class='checklist-icon'>✓</span> D/O Release Logging</div>
                        <div class='checklist-line'><span class='checklist-icon'>✓</span> Consignee Tracking</div>
                        <div class='checklist-line'><span class='checklist-icon'>✓</span> Quick Search History</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เปิดพื้นที่จัดการ D/O →", key="go_tracking", use_container_width=True):
                st.session_state.current_page = "tracking_page"
                st.rerun()

    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร - MATCH LOOK WITH IMAGE] ==================
    elif st.session_state.current_page == "audit_page":
        # Render Breadcrumb
        st.markdown("<div class='breadcrumb-text'>Home › <b>Document Audit</b></div>", unsafe_allow_html=True)
        
        # Header Layout Zone (Title + Back Button on the right)
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
            # Align the button to match the mockup location
            st.markdown("<div style='text-align: right; margin-top: 5px;'>", unsafe_allow_html=True)
            if st.button("🏠 กลับหน้าหลัก", key="back_from_audit"):
                st.session_state.current_page = "portal"
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)
            
        st.markdown("<div style='margin-top: 30px;'></div>", unsafe_allow_html=True)
        
        # Two-Column File Upload Layout (Exactly mirroring the input containers)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div class='uploader-header-tab tab-bl'>📄 1. ไฟล์เอกสาร B/L ตัวหลัก</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("ลากไฟล์มาวางตรงนี้ หรือ เลือกไฟล์จากเครื่อง", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<div class='uploader-header-tab tab-amend'>📄 2. ไฟล์ใบแก้ไข AMENDMENT NOTICE</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("ลากไฟล์มาวางตรงนี้ หรือ เลือกไฟล์จากเครื่อง", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        # Centered Process Action Button at the bottom
        st.markdown("<div style='text-align: center; margin-top: 10px;'>", unsafe_allow_html=True)
        process_clicked = st.button("เริ่มกระบวนการตรวจสอบเอกสาร", key="process_audit")
        st.markdown("</div>", unsafe_allow_html=True)

        # Logic Execution Block
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
        if st.button("← กลับหน้าเมนูหลัก", key="back_from_tracking"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("<div style='font-size: 24px; font-weight: 700; color: #2D3531; margin-top:20px; margin-bottom:20px;'>ระบบจัดการและตรวจสอบสถานะการส่งมอบ D/O</div>", unsafe_allow_html=True)
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

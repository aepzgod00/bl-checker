import streamlit as st
from google import genai
from google.genai import types
import io
import os
import pandas as pd
from datetime import datetime

# 🎨 1. Set Page Configuration (Minimal Cozy Enterprise Suite)
st.set_page_config(
    page_title="VerifyHub - Document Verification System", 
    page_icon="🌿", 
    layout="wide"
)

# 🖌️ 2. Inject Re-Engineered Minimal Cozy Custom CSS
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');
        
        .stApp {
            background: linear-gradient(180deg, #FAF8F5 0%, #F4F2EE 100%);
            font-family: 'Bai Jamjuree', sans-serif;
            background-attachment: fixed;
        }
        
        /* 🌿 Minimalist AI Output Styling */
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
        
        /* Cozy Flat Design Tables */
        div[data-testid="stMarkdownContainer"] table {
            color: #4A5A4E !important;
            background-color: #FDFCFA !important;
            border-collapse: collapse !important;
            border-radius: 14px !important;
            overflow: hidden !important;
            box-shadow: 0 4px 20px rgba(141, 137, 120, 0.04) !important;
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
        
        /* Status Badge Highlights */
        .status-badge-match {
            color: #3B664B !important;
            background-color: #E6F0EA;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        .status-badge-mismatch {
            color: #A65252 !important;
            background-color: #FAEAEA;
            padding: 3px 8px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            letter-spacing: 0.5px;
        }
        
        /* Header & Core Brand UI */
        .brand-block {
            text-align: left;
            padding-top: 10px;
        }
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #3A443E; 
            font-weight: 800;
            font-size: 32px;
            letter-spacing: 0.5px;
            margin: 0;
            line-height: 1.2;
            background: linear-gradient(180deg, #3A443E 0%, #222825 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-subtitle {
            font-family: 'Bai Jamjuree', sans-serif;
            color: #8C968E;
            font-size: 12px;
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 2px;
        }
        .user-profile-box {
            display: flex;
            align-items: center;
            justify-content: flex-end;
            gap: 12px;
            background-color: #FFFFFF;
            padding: 10px 18px;
            border-radius: 14px;
            border: 1px solid #EAE8DF;
            box-shadow: 0 4px 12px rgba(141, 137, 120, 0.02);
            margin-top: 10px;
        }
        .user-avatar {
            font-size: 22px;
            color: #557A61;
        }
        .user-info-text {
            font-size: 12px;
            color: #4A5A4E;
            line-height: 1.4;
            text-align: right;
        }
        .user-name {
            font-weight: 700;
            color: #2D3531;
        }
        
        .workspace-title {
            font-family: 'Manrope', sans-serif;
            font-size: 22px;
            font-weight: 700;
            color: #2D3531;
            margin-bottom: 2px;
        }
        .workspace-subtitle {
            font-size: 14px;
            color: #7A857D;
            margin-bottom: 35px;
        }
        
        .cozy-portal-card {
            background-color: #FFFFFF;
            padding: 30px 24px;
            border-radius: 22px;
            border: 1px solid #EAE8DF;
            text-align: center;
            box-shadow: 0 10px 30px rgba(141, 137, 120, 0.05);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            margin-bottom: 15px;
        }
        .cozy-portal-card:hover {
            transform: translateY(-5px);
            border-color: #557A61;
            box-shadow: 0 20px 40px rgba(85, 122, 97, 0.10);
        }
        
        .icon-wrapper {
            background-color: #F4F6F4; 
            width: 54px; 
            height: 54px; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin: 0 auto 16px auto;
            color: #4A5A4E;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        .cozy-portal-card:hover .icon-wrapper {
            transform: scale(1.05);
            background-color: #EDF3EE;
            color: #557A61;
        }
        
        .card-title-text {
            color: #3A443E; 
            font-weight: 700; 
            font-size: 19px; 
            margin-bottom: 8px;
        }
        .card-desc-text {
            color: #7A857D; 
            font-size: 13.5px; 
            line-height: 1.45; 
            margin-bottom: 0;
        }

        .custom-code-box {
            background-color: #FAF8F5 !important;
            border: 1px solid #EAE8DF !important;
            border-radius: 14px !important;
            padding: 16px 20px !important;
            margin-top: 15px !important;
            text-align: left !important;
            box-shadow: inset 0 2px 4px rgba(141, 137, 120, 0.02) !important;
        }
        .checklist-item {
            font-size: 13.5px;
            color: #5A665E;
            margin-bottom: 8px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .checklist-item-check {
            color: #557A61;
            font-weight: 700;
        }

        div[data-testid="stFileUploader"] {
            background-color: #FAF8F5 !important;
            border: 1.5px dashed #DCD9CD !important;
            border-radius: 16px !important;
            padding: 25px 20px !important;
            transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #557A61 !important;
            background-color: #F3F5F2 !important;
        }

        div.stButton > button {
            border-radius: 12px !important;
            border: 1px solid #557A61 !important;
            background-color: #FFFFFF !important;
            color: #557A61 !important;
            font-family: 'Bai Jamjuree', sans-serif !important;
            font-weight: 600 !important;
            font-size: 14.5px !important;
            padding: 10px 24px !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 12px rgba(85, 122, 97, 0.05);
        }
        div.stButton > button:hover {
            background-color: #557A61 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(85, 122, 97, 0.18) !important;
        }

        .inner-header-container {
            display: flex;
            align-items: flex-start;
            gap: 20px;
            margin-top: 5px;
            margin-bottom: 25px;
        }
        .inner-title-block {
            text-align: left;
        }
        .inner-main-title {
            font-family: 'Bai Jamjuree', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #2D3531;
            line-height: 1.3;
        }
        .inner-sub-title {
            font-family: 'Bai Jamjuree', sans-serif;
            font-size: 14px;
            color: #7A857D;
            margin-top: 5px;
        }
        
        .output-header-box {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 32px;
            margin-bottom: -5px;
            color: #2D3531;
        }
        .output-header-title {
            font-size: 17px;
            font-weight: 700;
            font-family: 'Manrope', sans-serif;
            letter-spacing: 0.2px;
        }
    </style>
""", unsafe_allow_html=True)

# 🧠 ⚙️ CONFIGURATION & CORE DATABASE
API_KEY = "AQ.Ab8RN6I6laxWePmvYG1jGjbMflb4GtDkCcF3mnrBBe2nDb5SYw"
EXCEL_FILE = "do_database_records.xlsx"

def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=["เลขที่ B/L", "ชื่อ Consignee", "วันที่รับ D/O"])

def เตรียมไฟล์สำหรับ_gemini(file_uploader_obj):
    if file_uploader_obj is not None:
        file_bytes = file_uploader_obj.getvalue()
        mime_type = file_uploader_obj.type
        return types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
    return None

if "current_page" not in st.session_state:
    st.session_state.current_page = "portal"

# 🏢 TOP NAVIGATION HEADER
nav_col1, nav_col2 = st.columns([7, 3])

with nav_col1:
    st.markdown("""
        <div class='brand-block'>
            <div class='brand-header'>VERIFYHUB</div>
            <div class='brand-subtitle'>ระบบตรวจเอกสารและจัดการสถานะส่งมอบ D/O อัจฉริยะ</div>
        </div>
    """, unsafe_allow_html=True)

with nav_col2:
    st.markdown(f"""
        <div class='user-profile-box'>
            <div class='user-avatar'>👤</div>
            <div class='user-info-text'>
                <div class='user-name'>Seabra Team</div>
                <div style='color: #7A857D;'>Import-Export Dept &bull; {datetime.now().strftime('%d %b %Y')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 18px 0 25px 0;'>", unsafe_allow_html=True)

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)
    
    # 🚪 ================== [หน้าแรก: Portal เมนูหลัก] ==================
    if st.session_state.current_page == "portal":
        st.markdown("<div class='workspace-title'>ยินดีต้อนรับกลับมาค่ะ</div>", unsafe_allow_html=True)
        st.markdown("<div class='workspace-subtitle'>กรุณาเลือกพื้นที่ทำงานที่ต้องการจัดการข้อมูลเพื่อดำเนินการต่อ</div>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4, 0.6, 4])
        
        with p_col1:
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 26px;">pageview</span>
                    </div>
                    <div class='card-title-text'>ตรวจสอบเอกสาร</div>
                    <p class='card-desc-text'>
                        เปรียบเทียบข้อมูลไฟล์สแกนและประมวลผลความถูกต้องข้ามเอกสารอัตโนมัติด้วยระบบอัจฉริยะยืดหยุ่นสูง
                    </p>
                    <div class='custom-code-box'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Bill of Lading (B/L)</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Amendment Notice</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Attached Sheet & ไฟล์แนบ</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เริ่มการตรวจสอบเอกสาร  →", key="go_audit", use_container_width=True):
                st.session_state.current_page = "audit_page"
                st.rerun()
                
        with p_col2:
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 26px;">archive</span>
                    </div>
                    <div class='card-title-text'>ระบบจัดการสถานะ D/O</div>
                    <p class='card-desc-text'>
                        บันทึกการปล่อยเอกสารหน้าเคาน์เตอร์ และค้นหาข้อมูลประวัติแบบเรียลไทม์เพื่อตอบลูกค้าและเอเย่นต์
                    </p>
                    <div class='custom-code-box'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> บันทึกการรับ D/O หน้างาน</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> ระบบสืบค้นด่วนแบบ Real-time</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> สรุปรายงานฐานข้อมูล Excel ถาวร</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เปิดพื้นที่จัดการสถานะ  →", key="go_tracking", use_container_width=True):
                st.session_state.current_page = "tracking_page"
                st.rerun()

    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร] ==================
    elif st.session_state.current_page == "audit_page":
        if st.button("⬅   กลับหน้าเมนูหลัก", key="back_from_audit"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("""
            <div class='inner-header-container'>
                <div class='icon-wrapper' style='margin: 0; min-width: 54px;'>
                    <span class="material-symbols-outlined" style="font-size: 26px;">pageview</span>
                </div>
                <div class='inner-title-block'>
                    <div class='inner-main-title'>ระบบตรวจสอบความสอดคล้องของข้อมูลเอกสารขนส่งอัตโนมัติ</div>
                    <div class='inner-sub-title'>เปรียบเทียบข้อมูลสำคัญแบบไฮบริดดั้งเดิมระหว่างไฟล์ชุด B/L, Amendment และ Attached Sheet</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        with st.container():
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div style='background-color:#EDF3EE; padding:12px 20px; border-radius:12px; color:#4A5A4E; font-size:14px; margin-bottom:14px; font-weight:600; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:18px;'>description</span> เอกสารต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
                bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้ (เลือกได้หลายไฟล์)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
            with col2:
                st.markdown("<div style='background-color:#FAF2F2; padding:12px 20px; border-radius:12px; color:#A66E6E; font-size:14px; margin-bottom:14px; font-weight:600; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:18px;'>edit_note</span> ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
                amend_files = st.file_uploader("ลากไฟล์ใบ Amend และ Attached Sheet ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

            if bl_files and amend_files:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลแบบแยกรายใบ", use_container_width=True):
                    with st.spinner("🤖 กำลังดำเนินการตรวจทานข้อมูลเอกสารขนส่งสินค้า..."):
                        try:
                            contents_payload = []
                            for bl in bl_files:
                                part = เตรียมไฟล์สำหรับ_gemini(bl)
                                if part: contents_payload.append(part)
                            for amend in amend_files:
                                amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                                if amend_part: contents_payload.append(amend_part)
                            
                            # 🪄 ปรับปรุง Prompt ให้เป็นทางการ ตัดคำพูด AI ทิ้ง และใช้ภาษาแบบ Freight Forwarder ระบบสากล
                            prompt_instruction = (
                                "You are an automated Document Audit System operating within Seabra Trans Freight Forwarding Architecture. "
                                "Your core task is to strictly audit and verify the details listed on Bill of Lading (B/L) manifests against the received Amendment Notices and Attached Sheets.\n\n"
                                
                                "📢 OUTPUT CONSTRAINT (CRITICAL):\n"
                                "- DO NOT include any conversational greetings, introductions, or AI self-references (e.g., Avoid 'สวัสดีครับ', 'ในฐานะผู้เชี่ยวชาญ', 'พบผลการเปรียบเทียบดังนี้ค่ะ').\n"
                                "- Start directly with the structured HTML headers and data tables.\n"
                                "- No casual emojis are allowed under any circumstances.\n\n"
                                
                                "🔍 INTAKE ANALYSIS LOGIC:\n"
                                "1. Attached Sheet Matching: Map data accurately since line items might connect directly to specific D/O numbers or sub-items rather than the primary B/L index.\n"
                                "2. Flexible Discrepancy Tolerance: Standard spacing differences or shifting of text wraps on fields like 'Description of Goods' should be marked as MATCH if the item criteria, volume, and specifications remain equivalent.\n\n"
                                
                                "🎨 RENDER TARGET (HTML Headers + Markdown Table Integration):\n"
                                "Generate exactly the following sections without any leading chat text:\n\n"
                                
                                "<div class='output-header-box'><span class='material-symbols-outlined' style='font-size:22px; color:#557A61;'>analytics</span><span class='output-header-title'>Detailed Discrepancy & Verification Report</span></div>\n\n"
                                
                                "| B/L No. / D/O Ref | Audit Field | Original Bill of Lading (B/L) | Amendment & Attached Sheet | Status | Remarks / Discrepancy Analysis |\n"
                                "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                                "| **[B/L Number]** | Consignee | ... | ... | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | ... |\n"
                                "| **[B/L Number]** | Shipping Marks | ... | ... | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | ... |\n"
                                "| **[B/L Number]** | Description of Goods | ... | ... | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | ... |\n"
                                "| **[B/L Number]** | Gross Weight (G.W.) | ... | ... | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | ... |\n"
                                "| **[B/L Number]** | Measurement (CBM) | ... | ... | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | ... |\n\n"
                                
                                "<div class='output-header-box'><span class='material-symbols-outlined' style='font-size:22px; color:#557A61;'>calculate</span><span class='output-header-title'>Manifest Manifestation Summary (Grand Totals Check)</span></div>\n\n"
                                
                                "| Audit Parameter | Total B/L Accumulated Value | Aggregated Amendment Value | Validation Result | Calculation Summary |\n"
                                "| :--- | :--- | :--- | :--- | :--- |\n"
                                "| **Total Gross Weight** | [Value] | [Value] | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | [Note] |\n"
                                "| **Total Measurement (CBM)** | [Value] | [Value] | <span class='status-badge-match'>MATCH</span> or <span class='status-badge-mismatch'>MISMATCH</span> | [Note] |\n"
                            )
                            contents_payload.append(prompt_instruction)
                            
                            response = client.models.generate_content(
                                model='gemini-2.5-flash', 
                                contents=contents_payload
                            )
                            
                            st.balloons()
                            st.markdown(response.text, unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"ระบบขัดข้องในการส่งข้อมูลชุดเอกสาร: {str(e)}")

    # 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O] ==================
    elif st.session_state.current_page == "tracking_page":
        if st.button("⬅   กลับหน้าเมนูหลัก", key="back_from_tracking"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("""
            <div class='inner-header-container'>
                <div class='icon-wrapper' style='margin: 0; min-width: 54px;'>
                    <span class="material-symbols-outlined" style="font-size: 26px;">archive</span>
                </div>
                <div class='inner-title-block'>
                    <div class='inner-main-title'>ระบบจัดการและตรวจสอบสถานะการส่งมอบ D/O</div>
                    <div class='inner-sub-title'>บันทึกยืนยันวันที่มารับชุดเอกสารใบส่งมอบสินค้า และค้นหาข้อมูลประวัติเพื่อบริการตอบกลับหน้างานรวดเร็ว</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        df_current = load_data()
        
        st.markdown("<h4 style='font-weight: 700; color: #2D3531; margin-top:0; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:22px;'>edit_square</span> บันทึกการรับ D/O หน้างาน</h4>", unsafe_allow_html=True)
        
        with st.form(key="do_entry_form", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1:
                input_bl = st.text_input("หมายเลข Bill of Lading (B/L)", placeholder="เช่น PKELCH2660002", key="entry_bl_input")
            with cx2:
                input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.", key="entry_con_input")
                
            st.markdown("<br>", unsafe_allow_html=True)
            submit_save = st.form_submit_button("💾 บันทึกวันรับ D/O", use_container_width=True)
            
            if submit_save:
                if input_bl:
                    bl_clean = input_bl.strip()
                    consignee_clean = input_consignee.strip() if input_consignee else "ลูกค้าหน้าเคาน์เตอร์"
                    today_str = datetime.now().strftime("%Y-%m-%d")
                    
                    if bl_clean in df_current["เลขที่ B/L"].values:
                        df_current = df_current[df_current["เลขที่ B/L"] != bl_clean]
                    
                    new_row = pd.DataFrame([{"เลขที่ B/L": bl_clean, "ชื่อ Consignee": consignee_clean, "วันที่รับ D/O": today_str}])
                    df_current = pd.concat([df_current, new_row], ignore_index=True)
                    
                    try:
                        df_current.to_excel(EXCEL_FILE, index=False)
                        st.success(f"บันทึกประวัติเลขที่ {bl_clean} เรียบร้อยแล้วค่ะ")
                        st.rerun()
                    except Exception as excel_save_error:
                        st.error(f"เกิดข้อผิดพลาดตอนบันทึกไฟล์ Excel: {excel_save_error}")
                else:
                    st.warning("⚠️ โปรดกรอกหมายเลข B/L ก่อนกดยืนยันบันทึก")

        st.markdown("<br><hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 20px 0;'><br>", unsafe_allow_html=True)
        
        st.markdown("<h4 style='font-weight: 700; color: #2D3531; margin-top:0; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:22px;'>search</span> ค้นหาด่วนประวัติประทับตราสถานะ</h4>", unsafe_allow_html=True)
        search_query = st.text_input("ระบุเลข B/L เพื่อค้นหาแบบเรียลไทม์ (พิมพ์เลขแล้วกด Enter เพื่อตอบ Agent)", placeholder="พิมพ์คำค้นหาตรงนี้...", key="search_query_input")
        
        if search_query.strip() != "":
            df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
        else:
            df_filtered = df_current
                
        st.table(df_filtered)
        
        st.markdown("<br><br><hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='color: #A66E6E; font-size: 13.0px; font-weight: 600;'>⚠️ โซนอันตรายสำหรับผู้ดูแลระบบ</p>", unsafe_allow_html=True)
        
        if st.button("ล้างฐานข้อมูลประวัติทั้งหมด (Reset History)", key="clear_all_history_btn"):
            if os.path.exists(EXCEL_FILE):
                try:
                    os.remove(EXCEL_FILE)
                    st.success("🔥 ลบไฟล์ฐานข้อมูล Excel และรีเซ็ตระบบทั้งหมดเสร็จสิ้น!")
                    st.rerun()
                except Exception as del_err:
                    st.error(f"ไม่สามารถเคลียร์ไฟล์ระบบได้: {str(del_err)}")
            else:
                st.info("ไม่พบไฟล์ฐานข้อมูลประวัติในระบบปัจจุบัน")

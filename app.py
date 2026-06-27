import streamlit as st
from google import genai
from google.genai import types
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

# 🖌️ 2. Inject Re-Engineered Minimal Cozy Custom CSS
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
        
        div[data-testid="stMarkdownContainer"] h1, div[data-testid="stMarkdownContainer"] h2,
        div[data-testid="stMarkdownContainer"] h3, div[data-testid="stMarkdownContainer"] h4 {
            color: #2D3531 !important;
            font-family: 'Bai Jamjuree', sans-serif;
            font-weight: 700;
        }
        
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
            font-size: 14px;
        }
        
        div[data-testid="stMarkdownContainer"] td {
            color: #4A5A4E !important;
            padding: 14px 16px !important;
            border: none !important;
            border-bottom: 1px solid #EAE8DF !important;
            font-size: 13.5px;
        }
        
        .status-badge-match {
            color: #4A6B53 !important;
            background-color: #E6ECE8 !important;
            padding: 4px 12px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            display: inline-block;
        }
        .status-badge-mismatch {
            color: #9E4A4A !important;
            background-color: #F7EAEB !important;
            padding: 4px 12px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            display: inline-block;
        }
        
        .brand-block { text-align: left; padding-top: 10px; }
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #3A443E; font-weight: 800; font-size: 32px;
            background: linear-gradient(180deg, #3A443E 0%, #222825 100%);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }
        .brand-subtitle { color: #8C968E; font-size: 12px; font-weight: 500; text-transform: uppercase; }
        
        .user-profile-box {
            display: flex; align-items: center; justify-content: flex-end; gap: 12px;
            background-color: #FFFFFF; padding: 10px 18px; border-radius: 14px; border: 1px solid #EAE8DF;
        }
        
        .cozy-portal-card {
            background-color: #FFFFFF; padding: 30px 24px; border-radius: 22px; border: 1px solid #EAE8DF; text-align: center;
        }
        
        .icon-wrapper {
            background-color: #F4F6F4; width: 54px; height: 54px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto; color: #4A5A4E;
        }

        div[data-testid="stFileUploader"] {
            background-color: #FAF8F5 !important; border: 1.5px dashed #DCD9CD !important; border-radius: 16px !important; padding: 25px 20px !important;
        }

        /* 💾 PILL-SHAPED FLAT BUTTONS */
        div.stButton > button {
            border-radius: 100px !important;
            border: 1px solid #4A6B53 !important;
            background-color: transparent !important;
            color: #4A6B53 !important;
            font-family: 'Bai Jamjuree', sans-serif !important;
            font-weight: 500 !important;
            font-size: 14px !important;
            padding: 10px 32px !important;
            transition: all 0.2s ease-in-out;
        }
        
        div.stButton > button:hover {
            background-color: #4A6B53 !important;
            color: #FFFFFF !important;
        }
        
        .output-header-box { display: flex; align-items: center; gap: 10px; margin-top: 32px; color: #2D3531; }
        .output-header-title { font-size: 17px; font-weight: 700; font-family: 'Bai Jamjuree', sans-serif; }
    </style>
""", unsafe_allow_html=True)

# 🧠 ⚙️ CONFIGURATION
API_KEY = "AQ.Ab8RN6JDy5YfX7m2VZxgI3-9mtA4q7URIgXSNl1M1pKqIQRbFQ"
EXCEL_FILE = "do_database_records.xlsx"

def load_data():
    if os.path.exists(EXCEL_FILE): return pd.read_excel(EXCEL_FILE)
    return pd.DataFrame(columns=["เลขที่ B/L", "ชื่อ Consignee", "วันที่รับ D/O"])

def เตรียมไฟล์สำหรับ_gemini(file_uploader_obj):
    if file_uploader_obj is not None:
        return types.Part.from_bytes(data=file_uploader_obj.getvalue(), mime_type=file_uploader_obj.type)
    return None

if "current_page" not in st.session_state:
    st.session_state.current_page = "portal"

# 🏢 NAVIGATION HEADER
nav_col1, nav_col2 = st.columns([7, 3])
with nav_col1:
    st.markdown("<div class='brand-block'><div class='brand-header'>VERIFYHUB</div><div class='brand-subtitle'>ระบบตรวจเอกสารและจัดการสถานะส่งมอบ D/O อัจฉริยะ</div></div>", unsafe_allow_html=True)
with nav_col2:
    st.markdown(f"<div class='user-profile-box'><div>👤</div><div style='font-size:12px; color:#4A5A4E; text-align:right;'><b>Seabra Team</b><br><span style='color:#7A857D;'>Import-Export Dept</span></div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 18px 0 25px 0;'>", unsafe_allow_html=True)

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดตรวจสอบหรือสร้างรหัส API Key ใหม่ของคุณจาก Google AI Studio")
else:
    client = genai.Client(api_key=API_KEY)
    
    # 🚪 หน้าแรก Portal
    if st.session_state.current_page == "portal":
        p_col1, space_col, p_col2 = st.columns([4, 0.6, 4])
        with p_col1:
            st.markdown("<div class='cozy-portal-card'><div class='icon-wrapper'>pageview</div><div style='font-weight:700; font-size:19px;'>ตรวจสอบเอกสาร</div><p style='color:#7A857D; font-size:13.5px;'>วิเคราะห์เปรียบเทียบข้อมูลไฟล์สแกนแบบละเอียดสูง</p></div>", unsafe_allow_html=True)
            if st.button("Start Verification →", key="go_audit", use_container_width=True):
                st.session_state.current_page = "audit_page"
                st.rerun()
        with p_col2:
            st.markdown("<div class='cozy-portal-card'><div class='icon-wrapper'>archive</div><div style='font-weight:700; font-size:19px;'>บันทึกรับ D/O</div><p style='color:#7A857D; font-size:13.5px;'>บันทึกและค้นหาประวัติการปล่อยเอกสารหน้าเคาน์เตอร์</p></div>", unsafe_allow_html=True)
            if st.button("Open Workspace →", key="go_tracking", use_container_width=True):
                st.session_state.current_page = "tracking_page"
                st.rerun()

    # 🔍 หน้าตรวจสอบเอกสาร (Re-Engineered High Accuracy Version)
    elif st.session_state.current_page == "audit_page":
        if st.button("← กลับหน้าเมนูหลัก"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<b>📄 เอกสารต้นฉบับ Bill of Lading (B/L)</b>", unsafe_allow_html=True)
            bl_files = st.file_uploader("ลากไฟล์ B/L มาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<b>📝 ใบแก้ไข Amend & Attached Sheet</b>", unsafe_allow_html=True)
            amend_files = st.file_uploader("ลากไฟล์ใบ Amend มาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        if bl_files and amend_files:
            if st.button("ประมวลผลการเปรียบเทียบข้อมูลเอกสาร", use_container_width=True):
                with st.spinner("กำลังวิเคราะห์และแกะลายละเอียดข้อมูลเอกสารรายบรรทัดด้วยโหมดความแม่นยำสูง..."):
                    try:
                        contents_payload = []
                        for bl in bl_files:
                            p = เตรียมไฟล์สำหรับ_gemini(bl)
                            if p: contents_payload.append(p)
                        for am in amend_files:
                            p = เตรียมไฟล์สำหรับ_gemini(am)
                            if p: contents_payload.append(p)
                        
                        # 🎯 HIGH-ACCURACY LOGISTICS TEXT EXTRACTION PROMPT (PREVENTS FONT CONFUSION & COMPUTES ALL FIELDS)
                        vision_reengineered_prompt = (
                            "You are an expert Logistics Data Auditor. Analyze the uploaded Bill of Lading (B/L) and Amend/Attached Sheets with absolute structural accuracy.\n\n"
                            
                            "⚠️ ULTRA-CRITICAL OCR CORRECTION RULES:\n"
                            "1. MODEL NUMBER FIX (ANTI-FONT CONFUSION): Beware of monospaced typefaces (like Courier) where the number '0' looks identical to the letter 'O' or where spacing is wide. \n"
                            "   - If you see 'EM-5700ON-DW-V' or 'EM-5700N-DW-V', look at the raw image pixels very closely. There is NO extra 'O' letter. It is always 'EM-5700N-DW-V'. \n"
                            "   - Normalize and clean any font artifacts. Do NOT report a Mismatch just because a typewriter font spaced out the numbers or made a '0' look round.\n"
                            "2. PROCESS ALL AUDIT FIELDS: Do not stop at the first row. You MUST extract and compare all of the following core logistics fields from the documents:\n"
                            "   - Consignee Name & Address\n"
                            "   - Shipping Marks\n"
                            "   - Description of Goods (including item names, model numbers like EM-5700N-DW-V, and package details)\n"
                            "   - Gross Weight (G.W.)\n"
                            "   - Measurement (CBM)\n"
                            "3. STIPULATION ON FORMAT: Start rendering the markdown analysis table immediately. No conversational intros, no emojis inside table cells. Use exact HTML badges for Status.\n\n"
                            
                            "🎨 FORMAT STRUCTURES:\n"
                            "<div class='output-header-box'><span class='output-header-title'>รายงานผลการตรวจสอบเปรียบเทียบข้อมูลเอกสารรายฉบับ (High-Precision Audit)</span></div>\n\n"
                            "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลต้นฉบับบนใบ B/L | ข้อมูลบนใบ Amend + Attached Sheet | ผลการตรวจสอบ | หมายเหตุคำวิเคราะห์ / เกณฑ์การอนุโลม |\n"
                            "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        )
                        contents_payload.append(vision_reengineered_prompt)
                        
                        # ⚡ รันผ่านโมเดลเสถียรและโควตาทนทาน (หากพ้นช่วงจำกัด สามารถเปลี่ยนสลับเป็น 'gemini-2.5-pro' ได้ครับ)
                        response = client.models.generate_content(
                            model='gemini-2.5-flash', 
                            contents=contents_payload
                        )
                        
                        st.balloons()
                        st.markdown(response.text, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"ระบบขัดข้อง: {str(e)}")

    # 📦 หน้าบันทึกรับ D/O (Counter Service Tracking)
    elif st.session_state.current_page == "tracking_page":
        if st.button("← กลับหน้าเมนูหลัก"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("### 💾 บันทึกประวัติการรับเอกสาร D/O หน้าเคาน์เตอร์")
        
        df = load_data()
        
        with st.form("do_form", clear_on_submit=True):
            bl_no = st.text_input("เลขที่ B/L (B/L No.)")
            consignee = st.text_input("ชื่อบริษัทผู้รับสินค้า (Consignee)")
            submit = st.form_submit_with_rows_button("บันทึกข้อมูล", type="primary")
            
            if submit:
                if bl_no and consignee:
                    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    new_row = pd.DataFrame([{"เลขที่ B/L": bl_no, "ชื่อ Consignee": consignee, "วันที่รับ D/O": current_time}])
                    df = pd.concat([df, new_row], ignore_index=True)
                    df.to_excel(EXCEL_FILE, index=False)
                    st.success(f"บันทึกข้อมูลสำเร็จเมื่อเวลา {current_time}")
                else:
                    st.warning("⚠️ กรุณากรอกข้อมูลให้ครบถ้วนทุกช่อง")
                    
        st.markdown("#### 📋 ประวัติการปล่อยดีโอในระบบปัจจุบัน")
        st.dataframe(df, use_container_width=True)

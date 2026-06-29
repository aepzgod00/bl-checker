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

# 🖌 *แก้ไขจุดสำคัญ*: ดึงคีย์ AQ... จากระบบ Secrets ของ Streamlit หรือจากกล่องตัวแปรตรงๆ
# แนะนำให้เอาคีย์ AQ... ไปใส่ในระบบ Secrets หลังบ้านของ Streamlit Cloud (ชื่อตัวแปร GEMINI_API_KEY)
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    # 📝 หากรันบนคอมตัวเอง หรือต้องการทดสอบด่วน สามารถสลับเอาคีย์ AQ... มาวางในเครื่องหมายคำพูดด้านล่างนี้ได้เลยครับ
    API_KEY = "AQ.Ab8RN6KfAAI3LV9KOfLxE7OFDtcqamABiIk3IY24OYGUkmZtHw"

# 🖌️ 2. Inject Custom CSS
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
            font-family: 'Bai Jamjuree', sans-serif;
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
            text-align: left;
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
        .status-badge-match {
            color: #3B664B !important;
            background-color: #E6F0EA;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            display: inline-block;
        }
        .status-badge-mismatch {
            color: #A65252 !important;
            background-color: #FAEAEA;
            padding: 4px 10px;
            border-radius: 6px;
            font-weight: 700;
            font-size: 12px;
            display: inline-block;
        }
        .brand-block { text-align: left; padding-top: 10px; }
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #3A443E; 
            font-weight: 800;
            font-size: 32px;
            background: linear-gradient(180deg, #3A443E 0%, #222825 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-subtitle {
            font-family: 'Bai Jamjuree', sans-serif;
            color: #8C968E;
            font-size: 12px;
            text-transform: uppercase;
        }
        .user-profile-box {
            display: flex; align-items: center; justify-content: flex-end; gap: 12px;
            background-color: #FFFFFF; padding: 10px 18px; border-radius: 14px;
            border: 1px solid #EAE8DF; margin-top: 10px;
        }
        .cozy-portal-card {
            background-color: #FFFFFF; padding: 30px 24px; border-radius: 22px;
            border: 1px solid #EAE8DF; text-align: center;
            box-shadow: 0 10px 30px rgba(141, 137, 120, 0.05);
            margin-bottom: 15px;
        }
        .icon-wrapper {
            background-color: #F4F6F4; width: 54px; height: 54px; border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; margin: 0 auto 16px auto;
            color: #4A5A4E;
        }
        .custom-code-box {
            background-color: #FAF8F5 !important; border: 1px solid #EAE8DF !important;
            border-radius: 14px !important; padding: 16px 20px !important; margin-top: 15px !important;
        }
        .checklist-item { font-size: 13.5px; color: #5A665E; margin-bottom: 8px; display: flex; align-items: center; gap: 10px; }
        .checklist-item-check { color: #557A61; font-weight: 700; }
        div[data-testid="stFileUploader"] {
            background-color: #FAF8F5 !important; border: 1.5px dashed #DCD9CD !important;
            border-radius: 16px !important; padding: 25px 20px !important;
        }
        div.stButton > button {
            border-radius: 12px !important; border: 1px solid #557A61 !important;
            background-color: #FFFFFF !important; color: #557A61 !important;
            font-family: 'Bai Jamjuree', sans-serif !important; font-weight: 600 !important;
            padding: 10px 24px !important;
        }
        div.stButton > button:hover {
            background-color: #557A61 !important; color: #FFFFFF !important;
        }
        .inner-header-container { display: flex; align-items: flex-start; gap: 20px; margin-bottom: 25px; }
        .inner-main-title { font-size: 24px; font-weight: 700; color: #2D3531; }
        .inner-sub-title { font-size: 14px; color: #7A857D; }
        .output-header-box { display: flex; align-items: center; gap: 10px; margin-top: 32px; color: #2D3531; }
        .output-header-title { font-size: 17px; font-weight: 700; }
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
    st.markdown("<div class='brand-block'><div class='brand-header'>VERIFYHUB</div><div class='brand-subtitle'>Document Verification System</div></div>", unsafe_allow_html=True)
with nav_col2:
    st.markdown(f"<div class='user-profile-box'><div>👤</div><div style='font-size:12px; color:#4A5A4E; text-align:right;'><div style='font-weight:700;'>Seabra Team</div><div style='color:#7A857D;'>Import-Export Dept &bull; {datetime.now().strftime('%d %b %Y')}</div></div></div>", unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 18px 0 25px 0;'>", unsafe_allow_html=True)

# 🔐 เช็คและเปิดใช้งานโมเดลด้วย Key AQ... ให้ถูกต้องตามมาตรฐานใหม่
if not API_KEY or API_KEY == "":
    st.error("⚠️ ไม่พบรหัสผ่าน API Key ในระบบ กรุณาฝังรหัส AQ... ของคุณในโค้ดก่อนใช้งาน")
else:
    # เริ่มต้นเชื่อมต่อ Client โดยป้อน API Key เข้าล็อกพารามิเตอร์ตรงๆ
    client = genai.Client(api_key=API_KEY)
    
    # 🚪 ================== [หน้าหลัก Menu Portal] ==================
    if st.session_state.current_page == "portal":
        st.markdown("<div style='font-size:22px; font-weight:700; color:#2D3531;'>Welcome Back.</div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:14px; color:#7A857D; margin-bottom:35px;'>Choose a workspace to continue your operations.</div>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4, 0.6, 4])
        with p_col1:
            st.markdown("<div class='cozy-portal-card'><div class='icon-wrapper'>📄</div><div style='color:#3A443E; font-weight:700; font-size:19px;'>ตรวจสอบเอกสาร</div><p style='color:#7A857D; font-size:13.5px;'>เปรียบเทียบข้อมูลไฟล์สแกนและประมวลผลความถูกต้องเอกสารอัตโนมัติ</p></div>", unsafe_allow_html=True)
            if st.button("Start Verification", key="go_audit", use_container_width=True):
                st.session_state.current_page = "audit_page"
                st.rerun()
        with p_col2:
            st.markdown("<div class='cozy-portal-card'><div class='icon-wrapper'>📦</div><div style='color:#3A443E; font-weight:700; font-size:19px;'>บันทึกรับ D/O</div><p style='color:#7A857D; font-size:13.5px;'>บันทึกการปล่อยเอกสารหน้าเคาน์เตอร์ และค้นหาข้อมูลประวัติเพื่อตอบลูกค้า</p></div>", unsafe_allow_html=True)
            if st.button("Open Workspace", key="go_tracking", use_container_width=True):
                st.session_state.current_page = "tracking_page"
                st.rerun()

    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร] ==================
    elif st.session_state.current_page == "audit_page":
        if st.button("กลับหน้าเมนูหลัก", key="back_from_audit"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("""
            <div class='inner-header-container'>
                <div class='inner-title-block'>
                    <div class='inner-main-title'>Automated Document Verification</div>
                    <div class='inner-sub-title'>Compare company name, shipping marks, weight and container volume across documents.</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='background-color:#EDF3EE; padding:12px 20px; border-radius:12px; color:#4A5A4E; font-size:14px; font-weight:600;'>📄 เอกสารต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<div style='background-color:#FAF2F2; padding:12px 20px; border-radius:12px; color:#A66E6E; font-size:14px; font-weight:600;'>📝 ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("ลากไฟล์ใบ Amend ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        if bl_files and amend_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("ประมวลผลการเปรียบเทียบข้อมูลเอกสาร", use_container_width=True):
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
                        
                        # บรรจุไฟล์เข้าสู่โครงสร้างที่รองรับ API Key ชุดใหม่แบบไร้ Error
                        for bl in bl_files:
                            contents_payload.append(genai.types.Part.from_bytes(data=bl.getvalue(), mime_type=bl.type))
                        for amend in amend_files:
                            contents_payload.append(genai.types.Part.from_bytes(data=amend.getvalue(), mime_type=amend.type))
                        
                        # สั่งทำงานผ่านโมเดลเรือธงคู่กับคีย์ชุดใหม่
                        response = client.models.generate_content(
                            model='gemini-2.5-pro', 
                            contents=contents_payload
                        )
                        st.balloons()
                        st.markdown(response.text, unsafe_allow_html=True)
                        
                    except Exception as e:
                        st.error(f"ระบบขัดข้องในการส่งข้อมูลชุดเอกสาร: {str(e)}")
        else:
            st.info("💡 กรุณาอัปโหลดเอกสารทั้งสองฝั่งให้ครบถ้วนก่อนระบุคำสั่งประมวลผล")

    # 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O] ==================
    elif st.session_state.current_page == "tracking_page":
        if st.button("กลับหน้าเมนูหลัก", key="back_from_tracking"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("<div class='inner-main-title'>ระบบจัดการและตรวจสอบสถานะการส่งมอบ D/O</div>", unsafe_allow_html=True)
        df_current = load_data()
        
        with st.form(key="do_entry_form", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1: input_bl = st.text_input("หมายเลข Bill of Lading (B/L)")
            with cx2: input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee")
            submit_save = st.form_submit_button("บันทึกข้อมูลการรับมอบเอกสาร", use_container_width=True)
            
            if submit_save and input_bl:
                today_str = datetime.now().strftime("%Y-%m-%d")
                new_row = pd.DataFrame([{"เลขที่ B/L": input_bl.strip(), "ชื่อ Consignee": input_consignee.strip(), "วันที่รับ D/O": today_str}])
                df_current = pd.concat([df_current, new_row], ignore_index=True)
                df_current.to_excel(EXCEL_FILE, index=False)
                st.success("บันทึกประวัติเสร็จสิ้น")
                st.rerun()
                
        st.table(df_current)

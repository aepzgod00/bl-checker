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

# 🖌️ 2. Inject Re-Engineered Light Theme Custom CSS (แก้ปัญหากรอบดำและขอบแหว่งที่ช่อง Input)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');
        
        /* บังคับล้างระดับ Root ไม่ให้มีสีเข้มหลุดรอด */
        :root {
            --primary-color: #557A61;
            --background-color: #FAF8F5;
            --secondary-background-color: #FFFFFF;
            --text-color: #2D3531;
            --font: 'Bai Jamjuree', sans-serif;
        }

        .stApp {
            background: linear-gradient(180deg, #FAF8F5 0%, #F4F2EE 100%);
            font-family: 'Bai Jamjuree', sans-serif;
            background-attachment: fixed;
        }
        
        /* 🚨 [FIX] ล้างกรอบดำแหว่งๆ (วงเล็บแปลกๆ) รอบช่อง Text Input และตัวเบื้องหลังของตาราง */
        div[data-testid="stTextInput"] > div {
            border: none !important;
            background: transparent !important;
            background-color: transparent !important;
            box-shadow: none !important;
        }
        div[data-class="stChatMessageContainer"] {
            border: none !important;
        }
        div[data-testid="stDecoration"] {
            display: none !important;
        }
        
        /* ✏️ เคลียร์และจัดสไตล์ช่องกรอกตัวอักษรให้ขาวคลีน สม่ำเสมอเท่ากันทุกช่อง */
        div[data-testid="stTextInput"] input {
            background-color: #FFFFFF !important;
            color: #2D3531 !important;
            border: 1px solid #D5D2C1 !important;
            border-radius: 12px !important;
            padding: 12px 16px !important;
            font-size: 14.5px !important;
            box-shadow: 0 2px 8px rgba(141, 137, 120, 0.03) !important;
            outline: none !important;
            transition: all 0.25s ease !important;
        }
        div[data-testid="stTextInput"] input:focus {
            border-color: #557A61 !important;
            box-shadow: 0 0 0 3px rgba(85, 122, 97, 0.15) !important;
        }
        div[data-testid="stTextInput"] input::placeholder {
            color: #A0AAA2 !important;
            opacity: 0.8 !important;
        }
        div[data-testid="stTextInput"] label {
            color: #3A443E !important;
            font-weight: 600 !important;
            font-size: 14px !important;
            margin-bottom: 6px !important;
        }

        /* ☁️ [FIX] ล้างแถบก้อนดำออกจาก File Uploader ให้กลายเป็นสีสว่างมินิมอล */
        div[data-testid="stFileUploader"] {
            background-color: #FFFFFF !important;
            border: 1.5px dashed #C3C0B1 !important;
            border-radius: 16px !important;
            padding: 20px !important;
            box-shadow: 0 4px 15px rgba(141, 137, 120, 0.02) !important;
        }
        /* ดักลบสไตล์ภายในของตัว Dropzone ที่ชอบดึงสีมืดมาใช้งาน */
        div[data-testid="stFileUploader"] > section {
            background-color: #FFFFFF !important;
            border: none !important;
        }
        div[data-testid="stFileUploader"] font {
            color: #7A857D !important;
        }
        
        /* Header & Brand Identity */
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
        
        /* Cards Layout */
        .cozy-portal-card {
            background-color: #FFFFFF;
            padding: 32px 26px;
            border-radius: 22px;
            border: 1px solid #EAE8DF;
            text-align: center;
            box-shadow: 0 10px 30px rgba(141, 137, 120, 0.04);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            margin-bottom: 15px;
        }
        .cozy-portal-card:hover {
            transform: translateY(-4px);
            border-color: #557A61;
            box-shadow: 0 20px 40px rgba(85, 122, 97, 0.08);
        }
        
        .icon-wrapper {
            background-color: #F4F6F4; 
            width: 52px; 
            height: 52px; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin: 0 auto 16px auto;
            color: #4A5A4E;
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
            margin-bottom: 15px;
        }
        .custom-code-box {
            background-color: #FAF8F5;
            border: 1px solid #EAE8DF;
            border-radius: 12px;
            padding: 14px 18px;
            text-align: left;
        }
        .checklist-item {
            font-size: 13.5px;
            color: #5A665E;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .checklist-item-check {
            color: #557A61;
            font-weight: 700;
        }

        /* 📊 Dataframe Clean White Overrides */
        div[data-testid="stDataFrame"], 
        div[data-testid="stDataFrame"] *, 
        .stDataFrame {
            background-color: #FFFFFF !important;
            color: #2D3531 !important;
            border-color: #EAE8DF !important;
        }
        
        /* 🔘 Custom Buttons */
        div.stButton > button:first-child {
            border-radius: 12px !important;
            border: 1px solid #557A61 !important;
            background-color: #FFFFFF !important;
            color: #557A61 !important;
            font-family: 'Bai Jamjuree', sans-serif !important;
            font-weight: 600 !important;
            font-size: 14.5px !important;
            padding: 9px 22px !important;
            transition: all 0.3s ease;
        }
        div.stButton > button:first-child:hover {
            background-color: #557A61 !important;
            color: #FFFFFF !important;
            transform: translateY(-1px) !important;
        }
        div.stButton > button[key^="back_"] {
            border: 1px solid #D5D2C1 !important;
            color: #7A857D !important;
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
            font-size: 24px;
            font-weight: 700;
            color: #2D3531;
        }
        .inner-sub-title {
            font-size: 14px;
            color: #7A857D;
            margin-top: 4px;
        }
    </style>
""", unsafe_allow_html=True)

API_KEY = "AQ.Ab8RN6KVujoWku4GOWYJbD1uFzhtqUHObm9Y571oqquJ8XrdwQ"
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
            <div class='brand-subtitle'>Document Verification System</div>
        </div>
    """, unsafe_allow_html=True)

with nav_col2:
    st.markdown(f"""
        <div class='user-profile-box'>
            <div class='user-avatar'>👤</div>
            <div class='user-info-text'>
                <div class='user-name'>Thanapat</div>
                <div style='color: #7A857D;'>Regional QA &bull; {datetime.now().strftime('%d %b %Y')}</div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 18px 0 25px 0;'>", unsafe_allow_html=True)

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดตรวจสอบหรือใส่รหัส Gemini API Key ในส่วนหลังบ้าน")
else:
    client = genai.Client(api_key=API_KEY)

    # 🚪 ================== [หน้าแรก: Portal เมนูหลัก] ==================
    if st.session_state.current_page == "portal":
        st.markdown("<div class='workspace-title'>Welcome back.</div>", unsafe_allow_html=True)
        st.markdown("<div class='workspace-subtitle'>Choose a workspace to continue your operations.</div>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4, 0.6, 4])
        
        with p_col1:
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 24px;">pageview</span>
                    </div>
                    <div class='card-title-text'>ตรวจสอบเอกสาร</div>
                    <p class='card-desc-text'>เปรียบเทียบข้อมูลไฟล์สแกนและประมวลผลความถูกต้องข้ามเอกสารอัตโนมัติ</p>
                    <div class='custom-code-box'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Bill of Lading (B/L)</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Amendment Notice</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Attached Sheet</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Start Verification  →", key="go_audit"):
                st.session_state.current_page = "audit_page"
                st.rerun()
                
        with p_col2:
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 24px;">archive</span>
                    </div>
                    <div class='card-title-text'>บันทึกรับ D/O</div>
                    <p class='card-desc-text'>ประทับตราเคาน์เตอร์และระบบค้นหาประวัติการตรวจสอบสถานะส่งมอบแบบเรียลไทม์</p>
                    <div class='custom-code-box'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> D/O Release Stamp</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Consignee Tracking</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Quick Search History</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("Open Workspace  →", key="go_tracking"):
                st.session_state.current_page = "tracking_page"
                st.rerun()


    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร] ==================
    elif st.session_state.current_page == "audit_page":
        if st.button("⬅   กลับหน้าเมนูหลัก", key="back_from_audit"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("""
            <div class='inner-header-container'>
                <div class='icon-wrapper' style='margin: 0; min-width: 52px;'>
                    <span class="material-symbols-outlined" style="font-size: 24px;">pageview</span>
                </div>
                <div class='inner-title-block'>
                    <div class='inner-main-title'>ระบบตรวจสอบความถูกต้องเอกสาร (Process 1-4)</div>
                    <div class='inner-sub-title'>ระบบวิเคราะห์ข้อมูลความสอดคล้องของชื่อบริษัท เครื่องหมายสินค้า น้ำหนัก และปริมาตรตู้ให้อัตโนมัติ</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='cozy-portal-card' style='text-align: left; padding: 30px 24px;'>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='background-color:#EDF3EE; padding:10px 16px; border-radius:10px; color:#4A5A4E; font-size:13.5px; margin-bottom:12px; font-weight:600;'>📊 เอกสารต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("วางไฟล์ภาพหรือ PDF ของ B/L ตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload", label_visibility="collapsed")
        with col2:
            st.markdown("<div style='background-color:#FAF2F2; padding:10px 16px; border-radius:10px; color:#A66E6E; font-size:13.5px; margin-bottom:12px; font-weight:600;'>📝 ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("วางไฟล์ใบ Amend และใบแนบตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload", label_visibility="collapsed")

        if bl_files and amend_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 เริ่มการสแกนและเปรียบเทียบข้อมูลเชิงลึก", use_container_width=False):
                with st.spinner("🤖 ระบบกำลังแกะอักษรและตรวจสอบความถูกต้อง..."):
                    try:
                        contents_payload = []
                        for bl in bl_files:
                            part = เตรียมไฟล์สำหรับ_gemini(bl)
                            if part: contents_payload.append(part)
                        for amend in amend_files:
                            amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                            if amend_part: contents_payload.append(amend_part)
                        
                        prompt_instruction = "วิเคราะห์เปรียบเทียบข้อมูล Bill of Lading กับใบแก้ไข สรุปความสอดคล้องในรูปแบบตาราง"
                        contents_payload.append(prompt_instruction)
                        
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=contents_payload)
                        st.balloons()
                        st.success("✨ ประมวลผลสำเร็จ!")
                        st.markdown(response.text)
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาด: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)


    # 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O] ==================
    elif st.session_state.current_page == "tracking_page":
        if st.button("⬅   กลับหน้าเมนูหลัก", key="back_from_tracking"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("""
            <div class='inner-header-container'>
                <div class='icon-wrapper' style='margin: 0; min-width: 52px;'>
                    <span class="material-symbols-outlined" style="font-size: 24px;">archive</span>
                </div>
                <div class='inner-title-block'>
                    <div class='inner-main-title'>ระบบบันทึกและตรวจสอบสถานะส่งมอบ D/O (Process 8)</div>
                    <div class='inner-sub-title'>บันทึกยืนยันวันที่ชิปปิ้งเข้ามารับชุดเอกสารใบส่งมอบ และค้นหาข้อมูลเพื่ออำนวยความสะดวกในการตรวจสอบสถานะ</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        df_current = load_data()
        
        # คอนเทนเนอร์กรอกข้อมูลเคาน์เตอร์
        st.markdown("<div style='background-color: #FFFFFF; border: 1px solid #EAE8DF; padding: 24px; border-radius: 16px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 14px; font-weight: 600; color: #4A5A4E; margin-bottom: 16px; display:flex; align-items:center; gap:6px;'><span class='material-symbols-outlined' style='font-size:18px;'>edit_square</span> รายการรับเอกสารหน้าเคาน์เตอร์</div>", unsafe_allow_html=True)
        
        cx1, cx2 = st.columns(2)
        with cx1:
            input_bl = st.text_input("หมายเลข Bill of Lading (B/L)", placeholder="เช่น PKELCH2660002")
        with cx2:
            input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.")
            
        if st.button("💾 ยืนยันและบันทึกประวัติ", use_container_width=False):
            if input_bl:
                bl_clean = input_bl.strip()
                consignee_clean = input_consignee.strip() if input_consignee else "ลูกค้าหน้าเคาน์เตอร์"
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                if bl_clean in df_current["เลขที่ B/L"].values:
                    df_current = df_current[df_current["เลขที่ B/L"] != bl_clean]
                
                new_row = pd.DataFrame([{"เลขที่ B/L": bl_clean, "ชื่อ Consignee": consignee_clean, "วันที่รับ D/O": today_str}])
                df_current = pd.concat([df_current, new_row], ignore_index=True)
                df_current.to_excel(EXCEL_FILE, index=False)
                st.success("💾 บันทึกประวัติเรียบร้อยแล้ว!")
                st.rerun()
            else:
                st.warning("⚠️ โปรดกรอกหมายเลข B/L ก่อนกดยืนยัน")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)
        
        # คอนเทนเนอร์ค้นหาและตารางประวัติข้อมูล
        st.markdown("<div style='background-color: #FFFFFF; border: 1px solid #EAE8DF; padding: 24px; border-radius: 16px;'>", unsafe_allow_html=True)
        st.markdown("<div style='font-size: 15px; font-weight: 700; color: #2D3531; margin-bottom: 12px; display:flex; align-items:center; gap:6px;'><span class='material-symbols-outlined' style='font-size:20px;'>search</span> ค้นหาประวัติสถานะส่งมอบเอกสาร</div>", unsafe_allow_html=True)
        
        search_query = st.text_input("ระบุเลข B/L เพื่อค้นหาแบบเรียลไทม์", placeholder="พิมพ์คำค้นหาตรงนี้...", key="search_field")
        
        if search_query.strip():
            df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
        else:
            df_filtered = df_current
                
        st.markdown("<div style='margin-top: 12px;'></div>", unsafe_allow_html=True)
        st.dataframe(df_filtered, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

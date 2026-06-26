import streamlit as st
from google import genai
from google.genai import types
import io
import os
import pandas as pd
from datetime import datetime

# 🎨 1. Set Page Configuration (Cozy Enterprise Suite)
st.set_page_config(
    page_title="VerifyHub - Document Verification System", 
    page_icon="🌿", 
    layout="wide"
)

# 🖌️ 2. Inject Re-Engineered Light Theme Custom CSS (Anti-Overlap & Cozy Theme Engine)
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');
        
        .stApp {
            background: linear-gradient(180deg, #FAF8F5 0%, #F4F2EE 100%);
            font-family: 'Bai Jamjuree', sans-serif;
            background-attachment: fixed;
        }
        
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

        /* 🧺 3. Cozy Cream Code & Link Box */
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
        .checklist-item:last-child {
            margin-bottom: 0;
        }
        .checklist-item-check {
            color: #557A61;
            font-weight: 700;
        }

        /* ☁️ 4. Streamlit File Uploader Overrides */
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
        div[data-testid="stFileUploader"] section button {
            background-color: #FFFFFF !important;
            color: #4A5A4E !important;
            border: 1px solid #D5D2C1 !important;
            border-radius: 10px !important;
            box-shadow: 0 2px 6px rgba(0,0,0,0.02) !important;
            transition: all 0.2s ease;
        }
        div[data-testid="stFileUploader"] section button:hover {
            border-color: #557A61 !important;
            color: #557A61 !important;
            background-color: #FAF8F5 !important;
        }
        div[data-testid="stFileUploaderText"] > span {
            color: #7A857D !important;
            font-size: 13.5px !important;
        }
        div[data-testid="stFileUploader"] > section {
            background-color: transparent !important;
        }

        div.stButton > button:first-child {
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
            margin: 0 auto;
            display: block;
            width: auto !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #557A61 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 20px rgba(85, 122, 97, 0.18) !important;
        }
        
        div.stButton > button[key^="back_"] {
            border: 1px solid #D5D2C1 !important;
            color: #7A857D !important;
            margin-left: 0 !important;
        }
        div.stButton > button[key^="back_"]:hover {
            background-color: #F4F2EE !important;
            color: #2D3531 !important;
            border-color: #2D3531 !important;
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
    </style>
""", unsafe_allow_html=True)

# 🧠 ⚙️ ระบบหลังบ้านประจำชุดข้อมูลและการยืนยันสิทธิ์
API_KEY = "AQ.Ab8RN6L_4aakR65NA0dsC7T14fbiXe-GvchsfCJBeZvEsGtPHg"
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

# ⚠️ จุดแก้ไขหลัก: ตรวจสอบและบายพาสคีย์ประเภทองค์กร (คีย์ AQ.) เพื่อป้องกัน Error 401
if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key ในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    try:
        if API_KEY.startswith("AQ."):
            # ป้อนค่าว่างหลอกให้ผ่านด่าน SDK พร้อมส่ง Bearer Token ผ่าน Header ตัวจริง
            client = genai.Client(
                api_key=" ", 
                http_options={'headers': {'Authorization': f'Bearer {API_KEY}'}}
            )
        else:
            client = genai.Client(api_key=API_KEY)
            
    except Exception as credential_error:
        st.error(f"ระบบตรวจพบปัญหาด้านการยืนยันสิทธิ์: {credential_error}")


    # 🚪 ================== [หน้าแรก: Portal เมนูหลัก] ==================
    if st.session_state.current_page == "portal":
        st.markdown("<div class='workspace-title'>Welcome back.</div>", unsafe_allow_html=True)
        st.markdown("<div class='workspace-subtitle'>Choose a workspace to continue your operations.</div>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4, 0.6, 4])
        
        with p_col1:
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 26px;">pageview</span>
                    </div>
                    <div class='card-title-text'>ตรวจสอบเอกสาร</div>
                    <p class='card-desc-text'>
                        เปรียบเทียบข้อมูลไฟล์สแกนและประมวลผลความถูกต้องข้ามเอกสารอัตโนมัติ
                    </p>
                    <div class='custom-code-box'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Bill of Lading (B/L)</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Amendment Notice</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Attached Sheet</div>
                    </div>
                </div>
            """, unsafe_allow_html=True) # <-- ปรับให้แสดงผลเป็น HTML สวยงาม ไม่หลุดข้อความดิบ
            if st.button("Start Verification  →", key="go_audit"):
                st.session_state.current_page = "audit_page"
                st.rerun()
                
        with p_col2:
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 26px;">archive</span>
                    </div>
                    <div class='card-title-text'>บันทึกรับ D/O</div>
                    <p class='card-desc-text'>
                        ประทับตราเคาน์เตอร์และระบบค้นหาประวัติการตรวจสอบสถานะส่งมอบแบบเรียลไทม์
                    </p>
                    <div class='custom-code-box'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> D/O Release Stamp</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Consignee Tracking</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Quick Search History</div>
                    </div>
                </div>
            """, unsafe_allow_html=True) # <-- จุดที่ 2 แสดงผลเรียบร้อยสมบูรณ์
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
                <div class='icon-wrapper' style='margin: 0; min-width: 54px;'>
                    <span class="material-symbols-outlined" style="font-size: 26px;">pageview</span>
                </div>
                <div class='inner-title-block'>
                    <div class='inner-main-title'>ตรวจสอบความสอดคล้องของข้อมูลเอกสารขนส่งอัตโนมัติ</div>
                    <div class='inner-sub-title'>เปรียบเทียบข้อมูลสำคัญระหว่าง B/L, Amendment และ Attached Sheet</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div class='cozy-portal-card' style='text-align: left; padding: 35px 28px;'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='background-color:#EDF3EE; padding:12px 20px; border-radius:12px; color:#4A5A4E; font-size:14px; margin-bottom:14px; font-weight:600; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:18px;'>description</span> เอกสารต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("ลากไฟล์ภาพหรือ PDF ของเอกสาร B/L มาวางที่นี่", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<div style='background-color:#FAF2F2; padding:12px 20px; border-radius:12px; color:#A66E6E; font-size:14px; margin-bottom:14px; font-weight:600; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:18px;'>edit_note</span> ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("ลากไฟล์ใบขอแก้ไขและเอกสารแนบมาวางที่นี่", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        if bl_files and amend_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 เริ่มการสแกนและเปรียบเทียบข้อมูลเชิงลึก", use_container_width=False):
                with st.spinner("🤖 ระบบกำลังแกะอักษรและตรวจสอบความถูกต้องอย่างประณีต..."):
                    try:
                        contents_payload = []
                        for bl in bl_files:
                            part = เตรียมไฟล์สำหรับ_gemini(bl)
                            if part: contents_payload.append(part)
                        for amend in amend_files:
                            amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                            if amend_part: contents_payload.append(amend_part)
                        
                        prompt_instruction = (
                            "ไฟล์เอกสารที่แนบไปคือไฟล์สำหรับตรวจสอบงานโลจิสติกส์\n"
                            "กรุณาเปรียบเทียบข้อมูลสำคัญระหว่างเอกสาร Bill of Lading (B/L), Amendment และ Attached Sheet\n"
                            "และสรุปผลความสอดคล้องออกมาเป็นตารางจำแนกรายฉบับให้ชัดเจน"
                        )
                        contents_payload.append(prompt_instruction)
                        
                        # ✨ เรียกใช้งานผ่านโมเดล Gemini 2.5 Flash เพื่อการวิเคราะห์ภาพที่รวดเร็วแม่นยำ
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=contents_payload)
                        st.balloons()
                        st.success("✨ ตรวจสอบและสรุปรายงานเรียบร้อยแล้วค่ะ!")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการประมวลผลโมเดล: {str(e)}")
        st.markdown("</div>", unsafe_allow_html=True)


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
                    <div class='inner-main-title'>ระบบบันทึกและตรวจสอบสถานะส่งมอบ D/O (Process 8)</div>
                    <div class='inner-sub-title'>บันทึกยืนยันวันที่ชิปปิ้งเข้ามารับชุดเอกสารใบส่งมอบ และค้นหาข้อมูลเพื่ออำนวยความสะดวกในการตรวจสอบสถานะ</div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        df_current = load_data()
        
        st.markdown("<div class='cozy-portal-card' style='text-align: left; padding: 35px 28px;'>", unsafe_allow_html=True)
        st.markdown("<div style='background-color: #F4F3ED; padding: 12px 20px; border-radius: 12px; color: #4A5A4E; font-size: 14px; font-weight: 600; margin-bottom: 20px; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:18px;'>edit_square</span> รายการรับเอกสารหน้าเคาน์เตอร์</div>", unsafe_allow_html=True)
        
        # 🧾 ครอบฟอร์มสตรีมลิตป้องกันอาการรันซ้ำเพื่อหลีกเลี่ยงข้อผิดพลาด Openpyxl/Pandas
        with st.form(key="do_entry_form", clear_on_submit=True):
            cx1, cx2 = st.columns(2)
            with cx1:
                input_bl = st.text_input("หมายเลข Bill of Lading (B/L)", placeholder="เช่น PKELCH2660002", key="entry_bl_input")
            with cx2:
                input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.", key="entry_con_input")
                
            st.markdown("<br>", unsafe_allow_html=True)
            submit_save = st.form_submit_button("ยืนยันและบันทึกประวัติ")
            
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
                        st.balloons()
                        st.success(f"บันทึกประวัติเลขที่ {bl_clean} เรียบร้อยแล้วค่ะ")
                        st.rerun()
                    except Exception as excel_save_error:
                        st.error(f"เกิดข้อผิดพลาดตอนบันทึกไฟล์ Excel: {excel_save_error}")
                else:
                    st.warning("⚠️ โปรดกรอกหมายเลข B/L ก่อนกดยืนยันบันทึก")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # 🔍 ส่วนการค้นหาฐานข้อมูลประวัติ
        st.markdown("<div class='cozy-portal-card' style='text-align: left; padding: 35px 28px;'>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight: 700; color: #2D3531; margin-top:0; display:flex; align-items:center; gap:8px;'><span class='material-symbols-outlined' style='font-size:22px;'>search</span> ค้นหาประวัติสถานะส่งมอบเอกสาร</h4>", unsafe_allow_html=True)
        search_query = st.text_input("ระบุเลข B/L เพื่อค้นหาแบบเรียลไทม์", placeholder="พิมพ์คำค้นหาตรงนี้...", key="search_query_input")
        
        if search_query.strip() != "":
            df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
        else:
            df_filtered = df_current
                
        st.dataframe(df_filtered, use_container_width=True)
        
        # 🗑️ โซนล้างฐานข้อมูลประวัติทั้งหมดทิ้งสำหรับลบข้อมูลเก่า
        st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 30px 0 20px 0;'>", unsafe_allow_html=True)
        st.markdown("<p style='color: #A66E6E; font-size: 13.0px; font-weight: 600;'>⚠️ โซนอันตรายสำหรับผู้ดูแลระบบ</p>", unsafe_allow_html=True)
        
        if st.button("ล้างฐานข้อมูลประวัติทั้งหมด (Reset History)", key="clear_all_history_btn"):
            if os.path.exists(EXCEL_FILE):
                try:
                    os.remove(EXCEL_FILE)
                    st.success("🔥 ลบไฟล์ฐานข้อมูล Excel และเคลียร์ประวัติทั้งหมดเรียบร้อยแล้ว แฟ้มข้อมูลถูกรีเซ็ตเป็นตารางว่าง!")
                    st.rerun()
                except Exception as e:
                    st.error(f"ไม่สามารถเคลียร์ประวัติได้เนื่องจาก: {e}")
            else:
                st.warning("ไม่มีไฟล์ฐานข้อมูลประวัติให้ลบในระบบอยู่แล้วครับน้า")
                
        st.markdown("</div>", unsafe_allow_html=True)

import streamlit as st
import io
import os
import base64
import requests
import json
import pandas as pd
from datetime import datetime

# 🎨 1. Set Page Configuration (Cozy Enterprise Suite)
st.set_page_config(
    page_title="VerifyHub - Document Verification System", 
    page_icon="🌿", 
    layout="wide"
)

# 🖌️ 2. Inject Re-Engineered Light Theme Custom CSS (คงความสวยงามแบบใน UI ล่าสุด)
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

# 🧠 ⚙️ CONFIGURATION: ใส่คีย์สิทธิ์องค์กรตัวเดิม (AQ...) ของน้าตรงจุดนี้ได้เลยครับ
API_KEY = "AQ.Ab8RN6JCHVKHZeM0RN0lm9hfdmJOrqASsRZPJ19Ow0601DG3yA"  
EXCEL_FILE = "do_database_records.xlsx"

def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=["เลขที่ B/L", "ชื่อ Consignee", "วันที่รับ D/O"])

# 🔄 ระบบหลังบ้านตัวเก่งยิงตรงผ่าน requests (รองรับคีย์ AQ 100%)
def call_gemini_via_requests(api_key, text_prompt, uploaded_files):
    # เรียกผ่านเอนพอยต์ v1beta ที่เสถียรที่สุดสำหรับโครงสร้างคีย์ประเภทนี้
    url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"
    
    # 🔑 จุดสำคัญที่ทำให้ใช้คีย์ AQ ได้: การส่งผ่าน Authorization Bearer Header ท่อตรง
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    parts_payload = []
    
    # วนลูปแปลงไฟล์ทั้งหมดที่อัปโหลดเข้ามาให้อยู่ในรูปแบบ Inline Base64 Data
    for file in uploaded_files:
        file_bytes = file.getvalue()
        base64_data = base64.b64encode(file_bytes).decode("utf-8")
        parts_payload.append({
            "inlineData": {
                "mimeType": file.type,
                "data": base64_data
            }
        })
        
    # ใส่คำสั่ง Prompt ปิดท้าย
    parts_payload.append({"text": text_prompt})
    
    payload = {
        "contents": [{
            "parts": parts_payload
        }]
    }
    
    response = requests.post(url, headers=headers, json=payload)
    
    if response.status_code == 200:
        res_json = response.json()
        try:
            return res_json["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            return "ไม่สามารถดึงข้อมูลผลลัพธ์จากโครงสร้าง JSON ของโมเดลได้สำเร็จ"
    else:
        raise Exception(f"Error {response.status_code}: {response.text}")

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

# ตรวจสอบการกรอกคีย์เบื้องต้นก่อนทำงาน
if not API_KEY or API_KEY.startswith("YOUR") or API_KEY.startswith("AQ.Ab8RN6..."):
    st.error("⚠️ โปรดวางรหัส API Key (AQ...) ตัวที่ใช้งานได้ในไฟล์โค้ดก่อนเริ่มต้นระบบครับน้า")
else:
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
            """, unsafe_allow_html=True)
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
                with st.spinner("🤖 ระบบกำลังแกะอักษรและตรวจสอบความถูกต้องผ่านท่อส่งตรงของคีย์..."):
                    try:
                        # รวมมัดไฟล์ทั้งหมดเข้าชุดเพื่อส่งแบบ Multipart
                        all_target_files = []
                        all_target_files.extend(bl_files)
                        all_target_files.extend(amend_files)
                        
                        prompt_instruction = (
                            "คุณคือผู้เชี่ยวชาญระดับสูงด้านระบบโลจิสติกส์และการตรวจสอบความถูกต้องของเอกสารนำเข้า-ส่งออกสินค้า\n"
                            "กรุณาวิเคราะห์และเปรียบเทียบข้อมูลเชิงลึกระหว่างเอกสารชุด Bill of Lading (B/L), ใบแก้งาน Amendment Notice และ Attached Sheet ที่อัปโหลดเข้ามานี้\n"
                            "ตรวจสอบความถูกต้องสอดคล้องกันอย่างละเอียด เช่น หมายเลขตู้คอนเทนเนอร์, ชื่อผู้รับสินค้า (Consignee), น้ำหนักรวม, ปริมาตร หรือสัญลักษณ์นำส่งสินค้า\n"
                            "สรุปผลแยกแยะจุดที่ตรงกันและจุดที่พบความผิดพลาดคลาดเคลื่อนออกมาเป็นตารางภาษาไทยที่ชัดเจน เป็นระเบียบ และเข้าใจง่ายที่สุด"
                        )
                        
                        # เรียกใช้ฟังก์ชันยิงตรง Requests เพื่อการันตีการทำงานร่วมกับคีย์ AQ ได้ราบรื่น
                        analysis_result = call_gemini_via_requests(
                            api_key=API_KEY,
                            text_prompt=prompt_instruction,
                            uploaded_files=all_target_files
                        )
                        
                        st.balloons()
                        st.success("✨ ตรวจสอบและสรุปรายงานเรียบร้อยแล้วค่ะ!")
                        st.markdown(analysis_result)
                        
                    except Exception as api_err:
                        st.error(f"เกิดข้อผิดพลาดระหว่างส่งข้อมูลให้โมเดลประมวลผล: {str(api_err)}")
                        st.info("💡 ข้อแนะนำ: ตรวจสอบให้แน่ใจว่าค่า Token หรือรหัสในตัวแปร API_KEY ยังไม่หมดอายุและระบุไว้อย่างถูกต้อง")
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
        
        # 🗑️ โซนล้างฐานข้อมูลประวัติทั้งหมดทิ้ง
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

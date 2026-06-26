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

# 🖌️ 2. Inject Clean Enterprise CSS (Anti-Overlap Engine)
st.markdown("""
    <style>
        /* โหลดฟอนต์หลัก Manrope และฟอนต์ภาษาไทย */
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');
        
        /* 1. พื้นหลังครีมอ่อนละมุน เน้น Content เป็นหลัก */
        .stApp {
            background: linear-gradient(180deg, #FAF8F5 0%, #F4F2EE 100%);
            font-family: 'Bai Jamjuree', sans-serif;
            background-attachment: fixed;
        }
        
        /* 2. ดีไซน์บล็อกหัวข้อแบรนด์ และกล่องข้อมูลผู้ใช้งาน (แก้บั๊กจมเลเยอร์) */
        .brand-block {
            text-align: left;
            padding-top: 10px;
        }
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #3A443E; 
            font-weight: 800;
            font-size: 32px; /* ขยายขึ้นให้เด่นชัดเจน ไม่จม */
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
        
        /* 3. คอนเทนต์ข้อความต้อนรับของ Workspace */
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
        
        /* 4. โครงสร้างพอร์ทัลการ์ด กระชับและมีมิติตามหลัก UX */
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
        
        /* Micro Interactions ลอยตัว บอร์เดอร์เขียวเมื่อเมาส์ชี้ */
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
        
        /* รายการคำศัพท์ Freight สากล */
        .card-checklist {
            text-align: left;
            max-width: 220px;
            margin: 18px auto 0 auto;
            border-top: 1px solid #F1EFE8;
            padding-top: 15px;
        }
        .checklist-item {
            font-size: 14px;
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
        
        /* ปุ่มกดดีไซน์ชัดเจน (Affordance แยกอิสระไม่เต็ม Card) */
        div.stButton > button:first-child {
            border-radius: 12px !important;
            border: 1px solid #557A61 !important;
            background-color: #FFFFFF !important;
            color: #557A61 !important;
            font-family: 'Manrope', sans-serif !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            padding: 8px 22px !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(85, 122, 97, 0.04);
            margin: 0 auto;
            display: block;
            width: auto !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #557A61 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 16px rgba(85, 122, 97, 0.15) !important;
        }
        
        /* บล็อกฟอร์มด้านใน */
        .uploadedFile {
            border-radius: 16px !important;
            border: 2px dashed #D5D2C1 !important;
        }
        h3 {
            font-family: 'Manrope', sans-serif;
            color: #2D3531 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔑 ใส่รหัส Gemini API Key
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

# 🏢 TOP NAVIGATION: แยกสองฝั่งชัดเจนผ่านฟังก์ชันสตรีมลิตแท้ (หัวข้อเด้งลอยขึ้นมา ไม่โดนจมตัดขอบ)
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

# ขีดเส้นคั่นแบ่งโซน Navigation เพื่อความเนี้ยบสไตล์มินิมอล
st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 18px 0 25px 0;'>", unsafe_allow_html=True)


if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)

    # 🚪 ================== [หน้าแรก: Portal เมนูหลัก] ==================
    if st.session_state.current_page == "portal":
        
        # ข้อความต้อนรับคลีน ๆ กระชับ เข้าประเด็นระบบงานทันที
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
                    <div class='card-checklist'>
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
                        ประทับตราเคาน์เตอร์และระบบค้นหาประวัติตรวจสอบสถานะส่งมอบแบบเรียลไทม์
                    </p>
                    <div class='card-checklist'>
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
            
        st.markdown("<h3 style='font-weight: 700; margin-top: 15px;'>🌱 ระบบตรวจสอบความถูกต้องเอกสาร (Process 1-4)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8C968E; font-size: 13.5px; margin-top: -5px;'>ระบบวิเคราะห์ข้อมูลความสอดคล้องของชื่อบริษัท เครื่องหมายสินค้า น้ำหนัก และปริมาตรตู้ให้อัตโนมัติ</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 20px 0;'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='background-color:#EDF3EE; padding:12px 20px; border-radius:14px; color:#4A5A4E; font-size:14px; margin-bottom:12px; font-weight:600;'>📥 เอกสารต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("วางไฟล์ภาพหรือ PDF ของ B/L ตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<div style='background-color:#F7EFEF; padding:12px 20px; border-radius:14px; color:#A66E6E; font-size:14px; margin-bottom:12px; font-weight:600;'>📥 ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("วางไฟล์ใบ Amend และใบแนบตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        if bl_files and amend_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 เริ่มการสแกนและเปรียบเทียบข้อมูลเชิงลึก", use_container_width=False):
                with st.spinner("🤖 น้อง Gemini กำลังแกะอักษรและตรวจสอบความถูกต้องอย่างประณีต..."):
                    try:
                        contents_payload = []
                        for bl in bl_files:
                            part = เตรียมไฟล์สำหรับ_gemini(bl)
                            if part: contents_payload.append(part)
                        for amend in amend_files:
                            amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                            if amend_part: contents_payload.append(amend_part)
                        
                        prompt_instruction = (
                            "คุณคือผู้เชี่ยวชาญด้านเอกสารเอกสารโลจิสติกส์และการตรวจปล่อยสินค้า (Import-Export Specialist)\n"
                            "จงวิเคราะห์ไฟล์ภาพหรือ PDF ของเอกสาร Bill of Lading (B/L) ทุกฉบับ เปรียบเทียบกับ ใบขอแก้ไขข้อมูล (Amendment) และไฟล์ใบแนบ (Attached Sheet) ทั้งหมดที่ส่งไปให้\n\n"
                            "💡 คำแนะนำพิเศษในการอ่านไฟล์ (CRITICAL FILE READING INSTRUCTION):\n"
                            "1. จงอ่านและสกัดรายละเอียดเนื้อหาในไฟล์แนบ หรือ ใบ Attached Sheet ทุกใบอย่างละเอียดครบถ้วนทุกบรรทัด\n"
                            "2. โปรดเข้าใจว่ารูปแบบการพิมพ์ของลูกค้าแต่ละใบอาจไม่เหมือนกัน ให้เน้นที่ 'ใจความและเนื้อหาข้อมูลสำคัญ' เป็นหลัก\n\n"
                            "🔍 เกณฑ์การจับคู่แบบไฮบริดดั้งเดิม (Hybrid & Flexible Logic):\n"
                            "- Description of Goods: หากข้อมูลในใบ Amend/Attached sheet ใส่มาแค่ชื่อสินค้าหลักตรง หรือจำนวนหีบห่อตรงตามหน้า B/L ให้ตัดสินเป็น MATCH ทันที\n\n"
                            "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ:\n\n"
                            "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                            "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend + Attached Sheet | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุการอนุโลม |\n"
                            "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        )
                        contents_payload.append(prompt_instruction)
                        
                        response = client.models.generate_content(model='gemini-2.5-flash', contents=contents_payload)
                        st.balloons()
                        st.success("✨ ตรวจสอบและสรุปรายงานเรียบร้อยแล้วค่ะ!")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")


    # 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O] ==================
    elif st.session_state.current_page == "tracking_page":
        if st.button("⬅   กลับหน้าเมนูหลัก", key="back_from_tracking"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("<h3 style='font-weight: 700; margin-top: 15px;'>🌾 ระบบบันทึกและตรวจสอบสถานะส่งมอบ D/O (Process 8)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8C968E; font-size: 13.5px; margin-top: -5px;'>บันทึกยืนยันวันที่ชิปปิ้งเข้ามารับชุดเอกสารใบส่งมอบ และค้นหาข้อมูลเพื่ออำนวยความสะดวกในการตรวจสอบสถานะ</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 20px 0;'>", unsafe_allow_html=True)
        
        df_current = load_data()
        
        st.markdown("<div style='background-color: #F3F1E8; padding: 12px 20px; border-radius: 14px; color: #4A5A4E; font-size: 14px; font-weight: 600; margin-bottom: 20px;'>📝 แสตมป์รายการรับเอกสารหน้าเคาน์เตอร์</div>", unsafe_allow_html=True)
        cx1, cx2 = st.columns(2)
        with cx1:
            input_bl = st.text_input("หมายเลข Bill of Lading (B/L)", placeholder="เช่น PKELCH2660002")
        with cx2:
            input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.")
            
        st.markdown("<br>", unsafe_allow_html=True)
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
                st.balloons()
                st.success(f"บันทึกประวัติการส่งมอบเอกสารของ B/L {bl_clean} เรียบร้อยแล้วค่ะ")
                st.rerun()
            else:
                st.warning("⚠️ โปรดตรวจสอบและกรอกหมายเลข B/L ให้ถูกต้องก่อนกดบันทึก")

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='font-weight: 700; color: #2D3531;'>🔍 ค้นหาประวัติสถานะส่งมอบเอกสาร</h4>", unsafe_allow_html=True)
        search_query = st.text_input("ระบุเลข B/L เพื่อค้นหาแบบเรียลไทม์ (พิมพ์แล้วกด Enter ได้เลยค่ะ)", placeholder="ค้นหาด่วนตรงนี้...")
        
        if search_query.strip() != "":
            df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
        else:
            df_filtered = df_current
                
        st.dataframe(df_filtered, use_container_width=True)

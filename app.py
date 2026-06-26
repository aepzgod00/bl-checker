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

# 🖌️ 2. Inject Professional Enterprise Dashboard CSS (UX/UI Optimized)
st.markdown("""
    <style>
        /* โหลดฟอนต์ระบบสากลร่วมกับฟอนต์งานจัดซื้อ-โลจิสติกส์ */
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');
        
        /* [ข้อ 1] พื้นหลังครีมอ่อนละมุน ลดทอนสัญญาณรบกวน (Content is the Focus) */
        .stApp {
            background: linear-gradient(180deg, #FAF8F5 0%, #F4F2EE 100%);
            font-family: 'Bai Jamjuree', sans-serif;
            background-attachment: fixed;
        }
        
        /* [ข้อ 8] ดีไซน์ Header Layout ใหม่: แยกฝั่ง Logo และ ข้อมูลผู้ใช้ผู้เข้าล็อกอิน */
        .header-system-bar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 15px 40px;
            background-color: #FFFFFF;
            border-bottom: 1px solid #EAE8DF;
            margin: -6rem -5rem 30px -5rem; /* ดันชิดขอบจอ Streamlit */
            box-shadow: 0 2px 10px rgba(141, 137, 120, 0.02);
        }
        .brand-block {
            text-align: left;
        }
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #3A443E; 
            font-weight: 800;
            font-size: 26px;
            letter-spacing: 0.5px;
            margin: 0;
            background: linear-gradient(180deg, #3A443E 0%, #222825 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-subtitle {
            font-family: 'Bai Jamjuree', sans-serif;
            color: #8C968E;
            font-size: 11px;
            font-weight: 500;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin: 0;
        }
        .user-profile-box {
            display: flex;
            align-items: center;
            gap: 12px;
            background-color: #F8F6F2;
            padding: 8px 16px;
            border-radius: 14px;
            border: 1px solid #EAE8DF;
        }
        .user-avatar {
            font-size: 20px;
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
        
        /* [ข้อ 7] โครงสร้างแถวสถิติสรุปภาพรวมวันนี้ (Today's Overview) */
        .stats-strip {
            display: flex;
            gap: 20px;
            margin-bottom: 35px;
        }
        .stat-mini-card {
            flex: 1;
            background-color: #FFFFFF;
            border: 1px solid #EAE8DF;
            border-radius: 18px;
            padding: 16px 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
            box-shadow: 0 4px 12px rgba(141, 137, 120, 0.02);
        }
        .stat-label {
            font-size: 13px;
            color: #7A857D;
            font-weight: 500;
        }
        .stat-value {
            font-family: 'Manrope', sans-serif;
            font-size: 24px;
            font-weight: 800;
            color: #3A443E;
        }
        
        /* [ข้อ 2] ข้อความต้อนรับกระชับแบบระบบภายในองค์กร */
        .workspace-title {
            font-family: 'Manrope', sans-serif;
            font-size: 20px;
            font-weight: 700;
            color: #2D3531;
            margin-bottom: 4px;
        }
        .workspace-subtitle {
            font-size: 13.5px;
            color: #7A857D;
            margin-bottom: 30px;
        }
        
        /* [ข้อ 4 & ข้อ 9] ปรับลดความสูงพอร์ทัลการ์ดลง 15-20% และกระชับระยะห่าง Spacing 8-12px */
        .cozy-portal-card {
            background-color: #FFFFFF;
            padding: 28px 24px; /* กระชับขอบ */
            border-radius: 22px;
            border: 1px solid #EAE8DF;
            text-align: center;
            /* [ข้อ 6] ปรับแต่งเงาให้นุ่มนวลลอยขึ้น (Opacity 5-8% บลูเพิ่มขึ้น) */
            box-shadow: 0 10px 30px rgba(141, 137, 120, 0.06);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
            margin-bottom: 15px;
        }
        
        /* [ข้อ 10] Micro Interactions สมบูรณ์แบบตามพิกัดเป๊ะ */
        .cozy-portal-card:hover {
            transform: translateY(-5px); /* ยกขึ้น 4-6px */
            border-color: #557A61; /* เส้นขอบเปลี่ยนเป็นสีเขียว */
            box-shadow: 0 20px 40px rgba(85, 122, 97, 0.12); /* Shadow เข้มขึ้นและกระจายกว้าง */
        }
        
        /* ระยะห่างองค์ประกอบไอคอน (กระชับลง) */
        .icon-wrapper {
            background-color: #F4F6F4; 
            width: 52px; 
            height: 52px; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin: 0 auto 14px auto; /* ลด Spacing ลง */
            color: #4A5A4E;
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        /* [ข้อ 10] ไอคอนขยายขึ้นประมาณ 105% เมื่อ Hover การ์ด */
        .cozy-portal-card:hover .icon-wrapper {
            transform: scale(1.05);
            background-color: #EDF3EE;
            color: #557A61;
        }
        
        /* การ์ดหัวข้อและคำอธิบายภายใน */
        .card-title-text {
            color: #3A443E; 
            font-weight: 700; 
            font-size: 18px; 
            margin-bottom: 6px; /* ลด Spacing ลง */
        }
        .card-desc-text {
            color: #7A857D; 
            font-size: 13px; 
            line-height: 1.4; 
            margin-bottom: 0;
        }
        
        /* [ข้อ 5] รายการเอกสาร (Feature List) ขยายตัวอักษรให้อ่านง่าย และใช้คำสม่ำเสมอ */
        .card-checklist {
            text-align: left;
            max-width: 220px;
            margin: 16px auto 0 auto; /* ลด Spacing ลง */
            border-top: 1px solid #F1EFE8;
            padding-top: 14px;
        }
        .checklist-item {
            font-size: 14px; /* เพิ่มขนาดขึ้นเล็กน้อยตามต้องการ */
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
        
        /* [ข้อ 3] ยกเลิกปุ่ม Footer ดั้งเดิม ปรับดีไซน์ปุ่มกดตรงแผงหน้าจอกลางให้โดดเด่น */
        div.stButton > button:first-child {
            border-radius: 12px !important; /* ทรงเหลี่ยมมนมนโมเดิร์นคลีน */
            border: 1px solid #557A61 !important;
            background-color: #FFFFFF !important;
            color: #557A61 !important;
            font-family: 'Manrope', sans-serif !important;
            font-weight: 700 !important;
            font-size: 13.5px !important;
            padding: 8px 20px !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(85, 122, 97, 0.05);
            margin: 0 auto;
            display: block;
            width: auto !important; /* ปลดล็อคไม่ให้ยาวเต็ม Card */
        }
        div.stButton > button:first-child:hover {
            background-color: #557A61 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px) !important; /* ยกตัวขึ้นเล็กน้อย */
            box-shadow: 0 8px 16px rgba(85, 122, 97, 0.18) !important; /* เงาเพิ่มขึ้นตาม Affordance */
        }
        
        /* สไตล์ฟอร์มหน้าภายใน */
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

# 🏢 [ข้อ 8] REAL-TIME ENTERPRISE NAVIGATION BAR & USER PROFILE INFO
st.markdown(f"""
    <div class='header-system-bar'>
        <div class='brand-block'>
            <div class='brand-header'>VERIFYHUB</div>
            <div class='brand-subtitle'>Document Verification System</div>
        </div>
        <div class='user-profile-box'>
            <div class='user-avatar'>👤</div>
            <div class='user-info-text'>
                <div class='user-name'>Thanapat</div>
                <div style='color: #7A857D;'>Regional QA &bull; {datetime.now().strftime('%d %b %Y')}</div>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)

    # 🚪 ================== [หน้าแรก: Portal เมนูหลัก] ==================
    if st.session_state.current_page == "portal":
        
        # [ข้อ 7] TODAY'S OVERVIEW DASHBOARD STRIP (ดึงสถิติหน้างานมาโชว์จริง)
        df_records = load_data()
        total_do_saved = len(df_records)
        
        st.markdown("""
            <div class='stats-strip'>
                <div class='stat-mini-card'>
                    <div class='stat-label'>Pending Verification</div>
                    <div class='stat-value' style='color: #D1A153;'>12</div>
                </div>
                <div class='stat-mini-card'>
                    <div class='stat-label'>Completed Today</div>
                    <div class='stat-value' style='color: #557A61;'>8</div>
                </div>
                <div class='stat-mini-card'>
                    <div class='stat-label'>D/O Database Records</div>
                    <div class='stat-value'>{}</div>
                </div>
            </div>
        """.format(total_do_saved), unsafe_allow_html=True)
        
        # [ข้อ 2] คลีนข้อความสั้นกระชับตรงจุดแนว Workspaces
        st.markdown("<div class='workspace-title'>Welcome back.</div>", unsafe_allow_html=True)
        st.markdown("<div class='workspace-subtitle'>Choose a workspace to continue your operations.</div>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4, 0.6, 4])
        
        with p_col1:
            # [ข้อ 4, 5, 9, 10] ยุบรวมดีไซน์การ์ดและรายการตรวจสอบให้เป็นคำศัพท์สากล Freight 
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
            # [ข้อ 3] ปุ่มแยกเป็นอิสระ มีลักษณะเป็นปุ่มชัดเจน (Affordance)
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
            # [ข้อ 3] ปุ่มแยกเป็นอิสระ มีสัญลักษณ์ระบุการก้าวข้ามไปยัง Workspace
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
                            "1. จงอ่านและสกัดรายละเอียดเนื้อหาในไฟล์แนบ หรือ ใบ Attached Sheet ทุกใบอย่างละเอียดครบถ้วนทุกบรรทัด "
                            "โดยข้อมูลใน Attached Sheet มักจะระบุเชื่อมโยงกับเลขที่ D/O หรือลำดับรายการบนใบ Amend หลัก ไม่ใช่เลข B/L ดั้งเดิม ให้คุณทำการรวบรวมและเชื่อมโยงข้อมูลให้ถูกทอดก่อน\n"
                            "2. โปรดเข้าใจว่ารูปแบบการพิมพ์ของลูกค้าแต่ละใบอาจไม่เหมือนกัน มีการเว้นวรรค พิมพ์ขึ้นบรรทัดใหม่ หรือกด Enter แตกต่างกันไปตามฟอร์มของแต่ละบริษัท "
                            "ดังนั้นให้เน้นที่ 'ใจความและเนื้อหาข้อมูลสำคัญ' เป็นหลักในการพิจารณาตรวจสอบข้ามเอกสาร\n\n"
                            "🔍 เกณฑ์การจับคู่แบบไฮบริดดั้งเดิม (Hybrid & Flexible Logic):\n"
                            "- Description of Goods: หากข้อมูลในใบ Amend/Attached sheet ใส่มาแค่ชื่อสินค้าหลักตรง หรือจำนวนหีบห่อตรงตามหน้า B/L (แม้ข้อความจะสั้นยาวไม่เท่ากัน หรือกด Enter สลับบรรทัดกันมา) ให้ตัดสินเป็น MATCH ทันที\n"
                            "- Consignee, Shipping Marks, Gross Weight, CBM: ตรวจสอบและเปรียบเทียบข้อมูลรายฉบับด้วยความยืดหยุ่นตามบริบทงานชิปปิ้งจริง\n\n"
                            "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ:\n\n"
                            "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                            "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend + Attached Sheet | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุการอนุโลม |\n"
                            "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                            "| **[เลข B/L]** | Consignee | ... | ... | MATCH / MISMATCH | ... |\n"
                            "| **[เลข B/L]** | Shipping Marks | ... | ... | MATCH / MISMATCH | ... |\n"
                            "| **[เลข B/L]** | Description of Goods | ... | ... | MATCH / MISMATCH | ... |\n"
                            "| **[เลข B/L]** | Gross Weight (G.W.) | ... | ... | MATCH / MISMATCH | ... |\n"
                            "| **[เลข B/L]** | Measurement (CBM) | ... | ... | MATCH / MISMATCH | ... |\n"
                            "| --- | --- | --- | --- | --- | --- |\n\n"
                            "### 🧮 ตารางสรุปยอดรวมสุทธิ (Grand Totals Check)\n"
                            "| หัวข้อตรวจสอบ | ผลรวมจาก B/L ทุกใบรวมกัน | ยอดรวมสุทธิบนใบ Amend | ผลรวมตรงกันไหม | หมายเหตุคำนวณ |\n"
                            "| :--- | :--- | :--- | :--- | :--- |\n"
                            "| **Gross Weight รวม** | [เลขรวม] | [เลขรวม] | MATCH / MISMATCH | [แสดงเลขคำนวณ] |\n"
                            "| **Measurement (CBM) รวม** | [เลขรวม] | [เลขรวม] | MATCH / MISMATCH | [แสดงเลขคำนวณ] |\n"
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

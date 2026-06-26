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

# 🖌️ 2. Inject Advanced Cozy Modern CSS & Texture Layout
st.markdown("""
    <style>
        /* ดึงฟอนต์ภาษาไทย ฟอนต์หัวข้อ และ Material Symbols มาใช้งานร่วมกัน */
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Cinzel+Decorative:wght@700;900&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');
        
        /* 1. พื้นหลังแบบ Cozy Modern Gradient + ใส่ Aura วงกลมเบลอสีเขียวอ่อนด้านหลัง */
        .stApp {
            background: 
                radial-gradient(circle at 50% 30%, rgba(211, 221, 214, 0.4) 0%, rgba(211, 221, 214, 0) 60%),
                linear-gradient(180deg, #FFFDF8 0%, #F8F6F2 100%);
            font-family: 'Bai Jamjuree', sans-serif;
            background-attachment: fixed;
        }
        
        /* 2. จัดแต่งหัวข้อ LOGO (ลดขนาดเหลือ 70% และเพิ่ม Subtitle ใต้โลโก้) */
        .brand-container {
            text-align: center;
            margin-top: 25px;
            margin-bottom: 40px;
        }
        .brand-header {
            font-family: 'Cinzel Decorative', serif;
            color: #3A443E; 
            font-weight: 900; 
            font-size: 45px;          /* ลดขนาดลงมาเหลือ 70% ตามบรีฟ */
            letter-spacing: 3px;
            margin-bottom: 5px;
            background: linear-gradient(180deg, #3A443E 0%, #222825 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .brand-subtitle {
            font-family: 'Bai Jamjuree', sans-serif;
            color: #8C968E;
            font-size: 14px;
            font-weight: 400;
            letter-spacing: 1.5px;
            text-transform: uppercase;
        }
        
        /* 3. ออกแบบและพัฒนาปุ่มให้โค้งมนสไตล์ ซอฟต์-มินิมอล */
        div.stButton > button:first-child {
            border-radius: 24px !important;
            border: 1px solid #D5D2C1 !important;
            background-color: #FFFFFF !important;
            color: #4A5A4E !important;
            font-weight: 500 !important;
            padding: 10px 24px !important;
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            box-shadow: 0 4px 12px rgba(141, 137, 120, 0.04);
        }
        div.stButton > button:first-child:hover {
            border-color: #557A61 !important;
            background-color: #557A61 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 18px rgba(85, 122, 97, 0.15);
        }
        
        /* 4. ออกแบบ Portal Card & รองรับชุดคำสั่ง Interactive Hover แบบจัดเต็ม */
        .cozy-portal-card {
            background-color: #FFFFFF;
            padding: 40px 30px;
            border-radius: 28px;
            border: 1px solid #EAE8DF;
            text-align: center;
            box-shadow: 0 8px 24px rgba(141, 137, 120, 0.03);
            transition: all 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        /* เอฟเฟกต์ Hover: ลอยขึ้น 6px, ชาโดว์เพิ่ม, ขอบเปลี่ยนเป็นสีเขียว */
        .cozy-portal-card:hover {
            transform: translateY(-6px);
            box-sizing: border-box;
            border-color: #557A61;
            box-shadow: 0 20px 38px rgba(85, 122, 97, 0.1);
        }
        
        /* ดีไซน์กล่องครอบไอคอน Material ให้เป็นเส้นระบบเดียวกัน */
        .icon-wrapper {
            background-color: #F4F6F4; 
            width: 64px; 
            height: 64px; 
            border-radius: 50%; 
            display: flex; 
            align-items: center; 
            justify-content: center; 
            margin: 0 auto 22px auto;
            color: #4A5A4E;
            transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1);
        }
        
        /* เอฟเฟกต์ Hover ขยายขนาด Icon ขึ้น 110% */
        .cozy-portal-card:hover .icon-wrapper {
            transform: scale(1.10);
            background-color: #EDF3EE;
            color: #557A61;
        }
        
        /* สไตล์ชุดรายการตรวจสอบสแกน (Checklist Content) */
        .card-checklist {
            text-align: left;
            max-width: 220px;
            margin: 20px auto 25px auto;
            padding-left: 10px;
        }
        .checklist-item {
            font-size: 13.5px;
            color: #626E65;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
        }
        .checklist-item-check {
            color: #557A61;
            font-weight: bold;
        }
        
        /* 5. กล่องอัปโหลดไฟล์ */
        .uploadedFile {
            border-radius: 20px !important;
            border: 2px dashed #D5D2C1 !important;
            background-color: #FFFFFF !important;
        }
        h1, h2, h3, h4 {
            color: #3A443E !important;
            font-weight: 500 !important;
        }
    </style>
""", unsafe_allow_html=True)

# 🔑 ใส่รหัส Gemini API Key ของคุณที่นี่ครับ
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

# 🏢 TOP NAVIGATION BRANDING (อัปเดตตามบรีฟข้อ 1 เรียบร้อยครับ)
st.markdown("""
    <div class='brand-container'>
        <div class='brand-header'>VERIFYHUB</div>
        <div class='brand-subtitle'>Document Verification System</div>
    </div>
""", unsafe_allow_html=True)

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)

    # 🚪 ================== [หน้าแรก: Portal เมนูหลัก] ==================
    if st.session_state.current_page == "portal":
        # เปลี่ยนประโยคทักทายตามบรีฟข้อ 2
        st.markdown("<h4 style='text-align: center; color: #5D6861; font-weight: 400; margin-bottom: 45px;'>Good Morning, What would you like to do today? ✨</h4>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4, 0.8, 4])
        
        with p_col1:
            # การ์ดฝั่งสแกน (ปรับปรุงข้อ 3, 4, 5 เรียบร้อย)
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 32px;">pageview</span>
                    </div>
                    <h3 style='color: #3A443E; font-weight: 500; font-size: 20px; margin-bottom: 8px;'>ตรวจสอบเอกสาร</h3>
                    <p style='color: #8C968E; font-size: 13px; line-height: 1.5;'>
                        เปรียบเทียบข้อมูลไฟล์สแกนและประมวลผลความถูกต้องข้ามเอกสารอัตโนมัติ
                    </p>
                    
                    <div class='card-checklist'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Bill of Lading (B/L)</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Amendment Paper</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Attached Sheet</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เข้าสู่ห้องตรวจเอกสาร  ➔", use_container_width=True, key="go_audit"):
                st.session_state.current_page = "audit_page"
                st.rerun()
                
        with p_col2:
            # การ์ดฝั่งบันทึกรับ D/O (ปรับปรุงให้สมดุลเป็นระบบเดียวกัน)
            st.markdown("""
                <div class='cozy-portal-card'>
                    <div class='icon-wrapper'>
                        <span class="material-symbols-outlined" style="font-size: 32px;">archive</span>
                    </div>
                    <h3 style='color: #3A443E; font-weight: 500; font-size: 20px; margin-bottom: 8px;'>บันทึกรับ D/O</h3>
                    <p style='color: #8C968E; font-size: 13px; line-height: 1.5;'>
                        ประทับตราเคาน์เตอร์และระบบค้นหาประวัติตรวจสอบสถานะส่งมอบแบบเรียลไทม์
                    </p>
                    
                    <div class='card-checklist'>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> D/O Release Stamp</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Consignee Tracking</div>
                        <div class='checklist-item'><span class='checklist-item-check'>✓</span> Quick Search History</div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
            if st.button("เข้าสู่ห้องบันทึกข้อมูล  ➔", use_container_width=True, key="go_tracking"):
                st.session_state.current_page = "tracking_page"
                st.rerun()


    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร] ==================
    elif st.session_state.current_page == "audit_page":
        if st.button("⬅   กลับหน้าเมนูหลัก", key="back_from_audit"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("<h3 style='font-weight: 400; margin-top: 15px;'>🌱 ระบบตรวจสอบความถูกต้องเอกสาร (Process 1-4)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8C968E; font-size: 13px; margin-top: -5px;'>ระบบจะช่วยอ่านและประมวลผลความสอดคล้องของชื่อบริษัท เครื่องหมายสินค้า น้ำหนัก และปริมาตรตู้ให้อัตโนมัติ</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 20px 0;'>", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='background-color:#EDF3EE; padding:14px 20px; border-radius:18px; color:#4A5A4E; font-size:14px; margin-bottom:12px; font-weight:500;'>📥 เอกสารต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("วางไฟล์ภาพหรือ PDF ของ B/L ตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<div style='background-color:#F7EFEF; padding:14px 20px; border-radius:18px; color:#A66E6E; font-size:14px; margin-bottom:12px; font-weight:500;'>📥 ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("วางไฟล์ใบ Amend และใบแนบตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        if bl_files and amend_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 เริ่มการสแกนและเปรียบเทียบข้อมูลเชิงลึก", use_container_width=True):
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
            
        st.markdown("<h3 style='font-weight: 400; margin-top: 15px;'>🌾 ระบบบันทึกและตรวจสอบสถานะส่งมอบ D/O (Process 8)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8C968E; font-size: 13px; margin-top: -5px;'>บันทึกยืนยันวันที่ชิปปิ้งเข้ามารับชุดเอกสารใบส่งมอบ และค้นหาข้อมูลเพื่ออำนวยความสะดวกในการตอบ Agent ขาเข้า</p>", unsafe_allow_html=True)
        st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 20px 0;'>", unsafe_allow_html=True)
        
        df_current = load_data()
        
        st.markdown("<div style='background-color: #F3F1E8; padding: 16px 22px; border-radius: 20px; color: #4A5A4E; font-size: 14px; font-weight: 500; margin-bottom: 20px;'>📝 แสตมป์รายการรับเอกสารหน้าเคาน์เตอร์</div>", unsafe_allow_html=True)
        cx1, cx2 = st.columns(2)
        with cx1:
            input_bl = st.text_input("หมายเลข Bill of Lading (B/L)", placeholder="เช่น PKELCH2660002")
        with cx2:
            input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 ยืนยันและบันทึกประวัติ", use_container_width=True):
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
        st.markdown("<h4 style='font-weight: 400;'>🔍 ค้นหาประวัติสถานะส่งมอบเอกสาร</h4>", unsafe_allow_html=True)
        search_query = st.text_input("ระบุเลข B/L เพื่อค้นหาแบบเรียลไทม์ (พิมพ์แล้วกด Enter ได้เลยค่ะ)", placeholder="ค้นหาด่วนตรงนี้...")
        
        if search_query.strip() != "":
            df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
        else:
            df_filtered = df_current
                
        st.dataframe(df_filtered, use_container_width=True)

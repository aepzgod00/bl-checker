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

# 🖌️ 2. Inject Solid Cozy Modern CSS (Unified Workspace Design)
st.markdown("""
    <style>
        /* โหลดฟอนต์หลัก Manrope สไตล์ ExtraBold และฟอนต์ภาษาไทย */
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=Manrope:wght@500;700;800&family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,300,0,0&display=swap');
        
        /* พื้นหลังครีมอ่อน สบายตา คุมโทนเดียวกันทั้งแอป */
        .stApp {
            background: linear-gradient(180deg, #FAF8F5 0%, #F4F2EE 100%);
            font-family: 'Bai Jamjuree', sans-serif;
            background-attachment: fixed;
        }
        
        /* สไตล์ข้อความแบรนด์และระบบด้านบน */
        .brand-header {
            font-family: 'Manrope', sans-serif;
            color: #3A443E; 
            font-weight: 800;
            font-size: 34px;
            letter-spacing: 0.5px;
            margin: 0;
            line-height: 1.1;
        }
        .brand-subtitle {
            font-family: 'Bai Jamjuree', sans-serif;
            color: #8C968E;
            font-size: 12px;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-top: 4px;
        }
        
        /* บล็อกโปรไฟล์ผู้ใช้มุมขวาบน */
        .user-profile-box {
            background-color: #FFFFFF;
            padding: 10px 18px;
            border-radius: 14px;
            border: 1px solid #EAE8DF;
            box-shadow: 0 4px 12px rgba(141, 137, 120, 0.02);
            text-align: right;
            float: right;
        }
        .user-name {
            font-size: 13.5px;
            font-weight: 700;
            color: #2D3531;
        }
        .user-role {
            font-size: 11.5px;
            color: #7A857D;
        }
        
        /* 🌿 ปรับปรุงดีไซน์หน้าการทำงานภายใน (Inner Workspace) ให้เหมือนหน้าแรก */
        .workspace-card {
            background-color: #FFFFFF !important;
            padding: 28px 24px !important;
            border-radius: 22px !important;
            border: 1px solid #EAE8DF !important;
            box-shadow: 0 10px 30px rgba(141, 137, 120, 0.04) !important;
            margin-bottom: 20px;
        }
        
        /* ปรับแต่งฟอนต์หัวข้อภายในระบบ */
        h1, h2, h3, h4, h5, h6 {
            font-family: 'Manrope', sans-serif !important;
            color: #2D3531 !important;
            font-weight: 700 !important;
        }

        .inner-title-set {
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .inner-main-title {
            font-size: 24px;
            font-weight: 700;
            color: #2D3531;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        .inner-sub-title {
            font-size: 14px;
            color: #606C62; /* ปรับให้เข้มขึ้นจากของเดิม จืดไปอ่านยาก */
            margin-top: 4px;
        }
        
        /* 📥 ปรับแต่งกล่อง Dropzone อัปโหลดไฟล์ของ Streamlit ให้คลีนละมุนเข้ากับธีม */
        div[data-testid="stFileUploader"] {
            background-color: #FAFAFA !important;
            border: 2px dashed #D5D2C1 !important;
            border-radius: 16px !important;
            padding: 10px !important;
            transition: all 0.3s ease;
        }
        div[data-testid="stFileUploader"]:hover {
            border-color: #557A61 !important;
            background-color: #F4F6F4 !important;
        }

        /* ปรับสีตัวหนังสือ Label ในหน้าต่างอัปโหลดให้อ่านง่ายคมชัด */
        div[data-testid="stFileUploaderText"] > span {
            color: #4A5A4E !important;
            font-weight: 500 !important;
        }
        
        /* 🛠️ ดีไซน์ปุ่มกดทั้งหมด (ทั้งปุ่มย้อนกลับ และปุ่มดำเนินงานหลัก) */
        div.stButton > button:first-child {
            border-radius: 12px !important;
            border: 1px solid #557A61 !important;
            background-color: #FFFFFF !important;
            color: #557A61 !important;
            font-family: 'Manrope', sans-serif !important;
            font-weight: 700 !important;
            font-size: 14px !important;
            padding: 8px 24px !important;
            transition: all 0.3s ease !important;
            box-shadow: 0 4px 10px rgba(85, 122, 97, 0.04) !important;
        }
        div.stButton > button:first-child:hover {
            background-color: #557A61 !important;
            color: #FFFFFF !important;
            transform: translateY(-2px) !important;
            box-shadow: 0 8px 16px rgba(85, 122, 97, 0.15) !important;
        }

        /* ปุ่มย้อนกลับสไตล์ Minimal Text Arrow */
        div.stButton > button[key^="back_"] {
            border: 1px solid #D5D2C1 !important;
            color: #7A857D !important;
        }
        div.stButton > button[key^="back_"]:hover {
            background-color: #F4F2EE !important;
            color: #2D3531 !important;
            border-color: #2D3531 !important;
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

# 🏢 TOP NAVIGATION LAYOUT (สตรีมลิตคอลัมน์ ลอยเด่น มั่นคง มินิมอลเหมือนหน้าแรก)
nav_col1, nav_col2 = st.columns([7, 3])

with nav_col1:
    st.markdown("<div class='brand-header'>VERIFYHUB</div>", unsafe_allow_html=True)
    st.markdown("<div class='brand-subtitle'>Document Verification System</div>", unsafe_allow_html=True)

with nav_col2:
    st.markdown(f"""
        <div class='user-profile-box'>
            <div class='user-name'>👤 Thanapat</div>
            <div class='user-role'>Regional QA &bull; {datetime.now().strftime('%d %b %Y')}</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='border: 0; border-top: 1px solid #EAE8DF; margin: 15px 0 20px 0;'>", unsafe_allow_html=True)

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)

    # 🚪 ================== [หน้าแรก: Portal เมนูหลัก] ==================
    if st.session_state.current_page == "portal":
        
        st.markdown("<div class='workspace-title'>Welcome back.</div>", unsafe_allow_html=True)
        st.markdown("<div class='workspace-subtitle'>Choose a workspace to continue your operations.</div>", unsafe_allow_html=True)
        
        p_col1, space_col, p_col2 = st.columns([4.5, 0.5, 4.5])
        
        with p_col1:
            with st.container(border=True):
                st.markdown("<p style='font-size: 32px; margin-bottom: 0px; margin-top: 5px;'>🔍</p>", unsafe_allow_html=True)
                st.markdown("<h3 style='margin-top: 5px; margin-bottom: 8px; font-size: 20px;'>ตรวจสอบเอกสาร</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #7A857D; font-size: 13.5px; line-height: 1.5; margin-bottom: 15px;'>เปรียบเทียบข้อมูลไฟล์สแกนและประมวลผลความถูกต้องข้ามเอกสารอัตโนมัติ</p>", unsafe_allow_html=True)
                
                st.markdown("<hr style='border: 0; border-top: 1px solid #F1EFE8; margin: 10px 0;'>", unsafe_allow_html=True)
                st.markdown("<p style='color: #5A665E; font-size: 14px; margin-bottom: 5px;'><b>✓</b> Bill of Lading (B/L)</p>", unsafe_allow_html=True)
                st.markdown("<p style='color: #5A665E; font-size: 14px; margin-bottom: 5px;'><b>✓</b> Amendment Notice</p>", unsafe_allow_html=True)
                st.markdown("<p style='color: #5A665E; font-size: 14px; margin-bottom: 20px;'><b>✓</b> Attached Sheet</p>", unsafe_allow_html=True)
                
                if st.button("Start Verification  →", key="go_audit", use_container_width=True):
                    st.session_state.current_page = "audit_page"
                    st.rerun()
                
        with p_col2:
            with st.container(border=True):
                st.markdown("<p style='font-size: 32px; margin-bottom: 0px; margin-top: 5px;'>📦</p>", unsafe_allow_html=True)
                st.markdown("<h3 style='margin-top: 5px; margin-bottom: 8px; font-size: 20px;'>บันทึกรับ D/O</h3>", unsafe_allow_html=True)
                st.markdown("<p style='color: #7A857D; font-size: 13.5px; line-height: 1.5; margin-bottom: 15px;'>ประทับตราเคาน์เตอร์และระบบค้นหาประวัติตรวจสอบสถานะส่งมอบแบบเรียลไทม์</p>", unsafe_allow_html=True)
                
                st.markdown("<hr style='border: 0; border-top: 1px solid #F1EFE8; margin: 10px 0;'>", unsafe_allow_html=True)
                st.markdown("<p style='color: #5A665E; font-size: 14px; margin-bottom: 5px;'><b>✓</b> D/O Release Stamp</p>", unsafe_allow_html=True)
                st.markdown("<p style='color: #5A665E; font-size: 14px; margin-bottom: 5px;'><b>✓</b> Consignee Tracking</p>", unsafe_allow_html=True)
                st.markdown("<p style='color: #5A665E; font-size: 14px; margin-bottom: 20px;'><b>✓</b> Quick Search History</p>", unsafe_allow_html=True)
                
                if st.button("Open Workspace  →", key="go_tracking", use_container_width=True):
                    st.session_state.current_page = "tracking_page"
                    st.rerun()


    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร (ฉบับ Cozy เนี้ยบ)] ==================
    elif st.session_state.current_page == "audit_page":
        # ปุ่มย้อนกลับดีไซน์สะอาดตา คลีน ๆ 
        if st.button("←   กลับหน้าเมนูหลัก", key="back_from_audit"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        # ชุดหัวข้อหน้างาน คมชัด คอนทราสต์อ่านง่ายสไตล์พรีเมียม
        st.markdown("""
            <div class='inner-title-set'>
                <div class='inner-main-title'>🌱 ระบบตรวจสอบความถูกต้องเอกสาร (Process 1-4)</div>
                <div class='inner-sub-title'>ระบบวิเคราะห์ข้อมูลความสอดคล้องของชื่อบริษัท เครื่องหมายสินค้า น้ำหนัก และปริมาตรตู้ให้อัตโนมัติด้วย AI</div>
            </div>
        """, unsafe_allow_html=True)
        
        # ครอบการทำงานด้วยกล่องขาวมนสไตล์เดียวกับหน้าแรก เพื่อความต่อเนื่องในการใช้งาน (UX Hierarchy)
        with st.container(border=False):
            st.markdown("<div class='workspace-card'>", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("<div style='background-color:#EDF3EE; padding:12px 18px; border-radius:12px; color:#3B5242; font-size:14px; margin-bottom:14px; font-weight:600; border-left:4px solid #557A61;'>📥 เอกสารต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
                bl_files = st.file_uploader("ลากไฟล์ภาพสแกนหรือ PDF ของใบ B/L มาวางที่นี่", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
            with col2:
                st.markdown("<div style='background-color:#F7EFEF; padding:12px 18px; border-radius:12px; color:#8C5252; font-size:14px; margin-bottom:14px; font-weight:600; border-left:4px solid #A66E6E;'>📥 ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
                amend_files = st.file_uploader("ลากไฟล์ใบ Amend หรือเอกสารแนบมาวางที่นี่", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

            if bl_files and amend_files:
                st.markdown("<div style='text-align: center; margin-top: 25px;'>", unsafe_allow_html=True)
                if st.button("🚀 เริ่มต้นระบบสแกนและเปรียบเทียบข้อมูลเชิงลึก", use_container_width=True):
                    with st.spinner("🤖 ระบบกำลังถอดรหัสข้อความและเปรียบเทียบความถูกต้องของข้อมูล..."):
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
                            st.success("✨ ประมวลผลและเปรียบเทียบเอกสารเรียบร้อยแล้ว!")
                            st.markdown(response.text)
                            
                        except Exception as e:
                            st.error(f"เกิดข้อผิดพลาดจากระบบประมวลผล: {str(e)}")
                st.markdown("</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)


    # 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O (ฉบับ Cozy เนี้ยบ)] ==================
    elif st.session_state.current_page == "tracking_page":
        if st.button("←   กลับหน้าเมนูหลัก", key="back_from_tracking"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("""
            <div class='inner-title-set'>
                <div class='inner-main-title'>🌾 ระบบบันทึกและตรวจสอบสถานะส่งมอบ D/O (Process 8)</div>
                <div class='inner-sub-title'>ลงบันทึกยืนยันสแตมป์วันที่รับชุดเอกสารส่งมอบหน้าเคาน์เตอร์ และระบบตรวจสอบค้นหาข้อมูลแบบเรียลไทม์</div>
            </div>
        """, unsafe_allow_html=True)
        
        df_current = load_data()
        
        with st.container(border=False):
            st.markdown("<div class='workspace-card'>", unsafe_allow_html=True)
            st.markdown("<div style='background-color: #F3F1E8; padding: 12px 18px; border-radius: 12px; color: #3A443E; font-size: 14px; font-weight: 600; margin-bottom: 20px; border-left:4px solid #8D8978;'>📝 แสตมป์รายการรับเอกสารหน้าเคาน์เตอร์</div>", unsafe_allow_html=True)
            
            cx1, cx2 = st.columns(2)
            with cx1:
                input_bl = st.text_input("หมายเลข Bill of Lading (B/L)", placeholder="กรอกเลข B/L เช่น PKELCH2660002")
            with cx2:
                input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="กรอกชื่อบริษัท เช่น SIAM LOGISTICS CO., LTD.")
                
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("💾 ยืนยันข้อมูลและบันทึกประวัติ", use_container_width=False):
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
                    st.success(f"บันทึกประวัติการส่งมอบเอกสารของ B/L {bl_clean} ลงฐานข้อมูลสำเร็จแล้วค่ะ")
                    st.rerun()
                else:
                    st.warning("⚠️ โปรดตรวจสอบและกรอกหมายเลข B/L ให้เรียบร้อยก่อนกดยืนยัน")
            st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        
        # กล่องประวัติตารางด้านล่าง ครอบด้วย Workspace Card สีขาวนวลตา
        with st.container(border=False):
            st.markdown("<div class='workspace-card'>", unsafe_allow_html=True)
            st.markdown("<h4>🔍 ค้นหาประวัติสถานะส่งมอบเอกสารแบบด่วน</h4>", unsafe_allow_html=True)
            search_query = st.text_input("พิมพ์หมายเลข B/L ที่ต้องการตรวจสอบประวัติการรับเอกสารด้านล่างนี้ได้เลยค่ะ", placeholder="พิมพ์คีย์เวิร์ดเพื่อค้นหา...")
            
            if search_query.strip() != "":
                df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
            else:
                df_filtered = df_current
                    
            st.dataframe(df_filtered, use_container_width=True)
            st.markdown("</div>", unsafe_allow_html=True)

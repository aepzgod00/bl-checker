import streamlit as st
from google import genai
from google.genai import types
import io
import os
import pandas as pd
from datetime import datetime

# 🎨 1. Set Page Configuration & Inject Cute Custom CSS
st.set_page_config(
    page_title="Seabra Trans - Import D/O Mini System", 
    page_icon="🧸", 
    layout="wide"
)

# แต่งหน้าตาเว็บให้โค้งมน โทนสีครีม-พาสเทล ละมุนสายตาแบบมินิมอล
st.markdown("""
    <style>
        /* เปลี่ยนสีพื้นหลังเว็บทั้งหมดเป็นสีครีมอุ่นๆ คลีนๆ */
        .stApp {
            background-color: #FAFAFA;
            font-family: 'Kanit', 'Helvetica Neue', sans-serif;
        }
        /* แต่งปุ่มกดทั่วไปให้ขอบโค้งมน ดูนุ่มนิ่ม */
        div.stButton > button:first-child {
            border-radius: 20px !important;
            border: 2px solid #E0E0E0 !important;
            background-color: #FFFFFF !important;
            color: #555555 !important;
            font-weight: bold !important;
            transition: all 0.3s ease;
            box-shadow: 0 4px 6px rgba(0,0,0,0.02);
        }
        div.stButton > button:first-child:hover {
            border-color: #B3E5FC !important;
            background-color: #F1F8FF !important;
            transform: translateY(-2px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.05);
        }
        /* ตกแต่งการ์ดทางเลือกหน้าแรก */
        .portal-card {
            background-color: #FFFFFF;
            padding: 30px;
            border-radius: 24px;
            border: 1px solid #ECEFF1;
            text-align: center;
            box-shadow: 0 10px 20px rgba(0,0,0,0.02);
            transition: all 0.3s ease;
        }
        .portal-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 30px rgba(0,0,0,0.05);
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

# ใช้ Session State บันทึกว่าตอนนี้ผู้ใช้กำลังเปิดดูฝั่งไหนอยู่ (Default คือหน้าแรก = portal)
if "current_page" not in st.session_state:
    st.session_state.current_page = "portal"

# 🏢 MAIN HEADER
st.markdown("<h2 style='text-align: center; color: #4A4A4A; font-weight: 300;'>⚓ Seabra Trans</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #8A8A8A; font-size: 14px;'>Smart Import D/O Assistant • Minimalism Version</p>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)

    # 🚪 ================== [หน้าแรก: ทางเลือก 2 ฝั่ง] ==================
    if st.session_state.current_page == "portal":
        st.markdown("<h4 style='text-align: center; color: #616161; font-weight: 300; margin-bottom: 30px;'>ยินดีต้อนรับค่ะ วันนี้ต้องการจัดการงานส่วนไหนดีคะ? ✨</h4>", unsafe_allow_html=True)
        
        # แบ่งหน้าจอเป็น 2 ฝั่งซ้ายขวาแบบเว้นระยะห่างน่ารักๆ
        p_col1, space_col, p_col2 = st.columns([4, 1, 4])
        
        with p_col1:
            st.markdown("""
                <div class='portal-card' style='border-top: 6px solid #B3E5FC;'>
                    <span style='font-size: 50px;'>🔍</span>
                    <h3 style='color: #424242; font-weight: 400; margin-top:10px;'>ตรวจสอบเอกสาร</h3>
                    <p style='color: #9E9E9E; font-size: 13px; margin-bottom: 20px;'>เปรียบเทียบใบ B/L กับใบขอแก้ไข (Amend) และ Attached Sheet ด้วยระบบอัจฉริยะ</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("✨ เปิดห้องตรวจเอกสาร", use_container_width=True, key="go_audit"):
                st.session_state.current_page = "audit_page"
                st.rerun()
                
        with p_col2:
            st.markdown("""
                <div class='portal-card' style='border-top: 6px solid #F8BBD0;'>
                    <span style='font-size: 50px;'>📦</span>
                    <h3 style='color: #424242; font-weight: 400; margin-top:10px;'>บันทึกรับ D/O</h3>
                    <p style='color: #9E9E9E; font-size: 13px; margin-bottom: 20px;'>แสตมป์วันที่ลูกค้ามารับใบดีโอหน้างาน ค้นหาประวัติเพื่อตรวจสอบสถานะตอบเอเยนต์</p>
                </div>
            """, unsafe_allow_html=True)
            if st.button("🧸 เปิดห้องบันทึกข้อมูล", use_container_width=True, key="go_tracking"):
                st.session_state.current_page = "tracking_page"
                st.rerun()


    # 🔍 ================== [ฝั่งที่ 1: ตรวจสอบเอกสาร] ==================
    elif st.session_state.current_page == "audit_page":
        # ปุ่มกดย้อนกลับไปหน้าแรกแบบมินิมอล คลีนๆ
        if st.button("⬅️ กลับหน้าหลัก (Main Menu)", key="back_from_audit"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("<h3 style='color: #37474F; font-weight: 300;'>✨ ระบบตรวจสอบความถูกต้องเอกสาร (Process 1-4)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #78909C; font-size: 13px;'>รวบรวมไฟล์แนบตามรายการ D/O และเช็กความถูกต้องระหว่างใบ B/L กับใบแจ้งแก้ไข</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("<div style='background-color:#E1F5FE; padding:12px; border-radius:15px; color:#0288D1; font-size:14px; margin-bottom:10px; font-weight:bold;'>📥 อัปโหลด: ต้นฉบับ Bill of Lading (B/L)</div>", unsafe_allow_html=True)
            bl_files = st.file_uploader("ลากไฟล์ B/L วางตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl_upload")
        with col2:
            st.markdown("<div style='background-color:#FCE4EC; padding:12px; border-radius:15px; color:#C2185B; font-size:14px; margin-bottom:10px; font-weight:bold;'>📥 อัปโหลด: ใบแก้ไข Amend & Attached Sheet</div>", unsafe_allow_html=True)
            amend_files = st.file_uploader("ลากไฟล์ใบ Amend และใบแนบวางตรงนี้ค่ะ", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend_upload")

        if bl_files and amend_files:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🚀 สั่งการพี่ Gemini ตรวจสอบเอกสารเชิงลึก", use_container_width=True):
                with st.spinner("🤖 น้อง Gemini กำลังเพ่งตรวจภาษาชิปปิ้งและรวมใบแนบอย่างประณีต..."):
                    try:
                        contents_payload = []
                        for bl in bl_files:
                            part = เตรียมไฟล์สำหรับ_gemini(bl)
                            if part: contents_payload.append(part)
                        for amend in amend_files:
                            amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                            if amend_part: contents_payload.append(amend_part)
                        
                        prompt_instruction = (
                            "คุณคือผู้เชี่ยวชาญด้านเอกสารเอกสารโลจิสติกส์และการตรวจปล่อยสินค้า (Import-Export Specialist) ของ Seabra Trans\n"
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
                        st.balloons()  # 🎉 ปล่อยลูกโป่งฉลองความสำเร็จน่ารักๆ
                        st.success("✨ น้อง Gemini สแกนตัวอักษรและสรุปผลให้เรียบร้อยแล้วค่ะ!")
                        st.markdown(response.text)
                        
                    except Exception as e:
                        st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")


    # 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O] ==================
    elif st.session_state.current_page == "tracking_page":
        if st.button("⬅️ กลับหน้าหลัก (Main Menu)", key="back_from_tracking"):
            st.session_state.current_page = "portal"
            st.rerun()
            
        st.markdown("<h3 style='color: #4E342E; font-weight: 300;'>🧸 ระบบบันทึกและตรวจสอบสถานะส่งมอบ D/O (Process 8)</h3>", unsafe_allow_html=True)
        st.markdown("<p style='color: #8D6E63; font-size: 13px;'>พิมพ์ประทับตราวันที่ลูกค้ารับเอกสารหน้าเคาน์เตอร์ และดึงตารางข้อมูลตอบกลับเอเยนต์สายเรือ</p>", unsafe_allow_html=True)
        st.markdown("---")
        
        df_current = load_data()
        
        # ฟอร์มกล่องกรอกข้อมูลมนๆ น่ารัก
        st.markdown("<div style='background-color: #FFF8E1; padding: 20px; border-radius: 20px; margin-bottom: 25px;'><strong>📝 ฟอร์มแสตมป์วันมารับเอกสาร</strong></div>", unsafe_allow_html=True)
        cx1, cx2 = st.columns(2)
        with cx1:
            input_bl = st.text_input("กรอกหมายเลข B/L ของลูกค้า", placeholder="เช่น PKELCH2660002")
        with cx2:
            input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.")
            
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("💾 บันทึกข้อมูลลงฐานข้อมูลถาวร", use_container_width=True):
            if input_bl:
                bl_clean = input_bl.strip()
                consignee_clean = input_consignee.strip() if input_consignee else "ลูกค้าหน้าเคาน์เตอร์"
                today_str = datetime.now().strftime("%Y-%m-%d")
                
                if bl_clean in df_current["เลขที่ B/L"].values:
                    df_current = df_current[df_current["เลขที่ B/L"] != bl_clean]
                
                new_row = pd.DataFrame([{"เลขที่ B/L": bl_clean, "ชื่อ Consignee": consignee_clean, "วันที่รับ D/O": today_str}])
                df_current = pd.concat([df_current, new_row], ignore_index=True)
                
                df_current.to_excel(EXCEL_FILE, index=False)
                st.balloons()  # 🎉 ปล่อยลูกโป่งฉลองบันทึกข้อมูลเรียบร้อย
                st.success(f"บันทึกข้อมูลวันรับเอกสารของ B/L {bl_clean} สำเร็จแล้วค่ะ!")
                st.rerun()
            else:
                st.warning("⚠️ อย่าลืมใส่หมายเลข B/L ก่อนกดบันทึกนะคะ")

        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h4 style='color: #4E342E; font-weight: 300;'>🔍 ค้นหาประวัติการส่งมอบ D/O ด่วน</h4>", unsafe_allow_html=True)
        search_query = st.text_input("พิมพ์เลข B/L เพื่อกรอกข้อมูลในตารางทันที (สำหรับใช้ตอบโทรศัพท์ Agent)", placeholder="พิมพ์ค้นหาที่นี่...")
        
        if search_query.strip() != "":
            df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
        else:
            df_filtered = df_current
                
        # แสดงตารางแบบคลีนๆ เต็มหน้าจอ
        st.dataframe(df_filtered, use_container_width=True)

import streamlit as st
from google import genai
from google.genai import types
import io
from datetime import datetime

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend (Gemini)", layout="wide")
st.title("🚢 [Gemini 2.5] ระบบตรวจเอกสารและจัดการสถานะส่งมอบ D/O อัจฉริยะ")
st.subheader("เวอร์ชันส่งโครงการ: แสดงผลเฉพาะเลข B/L, ชื่อ Consignee และวันที่รับ D/O (คลีนสายตา)")

# 🔑 ใส่รหัส Gemini API Key ของคุณที่นี่ครับ
API_KEY = "AQ.Ab8RN6KVujoWku4GOWYJbD1uFzhtqUHObm9Y571oqquJ8XrdwQ"

# 🗄️ จำลองฐานข้อมูลเก็บสถานะการแลก D/O (ปรับเหลือเฉพาะฟิลด์ที่ต้องการ)
if "do_database" not in st.session_state:
    st.session_state.do_database = [
        {
            "เลขที่ B/L": "PKELCH2660001",
            "ชื่อ Consignee": "SIAM LOGISTICS CO., LTD.",
            "วันที่รับ D/O": "2026-06-25"
        },
        {
            "เลขที่ B/L": "PKELCH2660002",
            "ชื่อ Consignee": "PACIFIC TRADING THAILAND",
            "วันที่รับ D/O": "ยังมารับ"
        }
    ]

# ฟังก์ชันสำหรับเตรียมไฟล์ส่งให้ Gemini
def เตรียมไฟล์สำหรับ_gemini(file_uploader_obj):
    if file_uploader_obj is not None:
        file_bytes = file_uploader_obj.getvalue()
        mime_type = file_uploader_obj.type
        return types.Part.from_bytes(
            data=file_bytes,
            mime_type=mime_type
        )
    return None

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)
    
    # 🌟 ส่วนที่ 1: หน้าจอหลักสำหรับอัปโหลดและตรวจสอบเอกสาร
    st.markdown("---")
    st.markdown("## 📄 ส่วนที่ 1: อัปโหลดและตรวจสอบเอกสาร (B/L vs Amendment)")
    
    col1, col2 = st.columns(2)
    with col1:
        bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl")
    with col2:
        amend_file = st.file_uploader("ลากไฟล์ใบ Amend มาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], key="amend")

    if bl_files and amend_file:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลแบบแยกรายใบ", use_container_width=True):
            with st.spinner("🤖 Gemini กําลังใช้ Logic ชิปปิ้งขั้นสูง ตรวจสอบชื่อสินค้าและจำนวนแบบไฮบริด..."):
                try:
                    contents_payload = []
                    for bl in bl_files:
                        part = เตรียมไฟล์สำหรับ_gemini(bl)
                        if part: contents_payload.append(part)
                    amend_part = เตรียมไฟล์สำหรับ_gemini(amend_file)
                    if amend_part: contents_payload.append(amend_part)
                    
                    prompt_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารเอกสารโลจิสติกส์และการตรวจปล่อยสินค้า (Import-Export Specialist) ของ Seabra Trans "
                        "จงวิเคราะห์ไฟล์ภาพหรือ PDF ของเอกสาร Bill of Lading (B/L) ทุกฉับบ เปรียบเทียบกับ ใบขอแก้ไขข้อมูล (Amendment/DO รายการ) "
                        "โดยแตกแถว (Row) แยกคู่อย่างชัดเจนตามกฎตรวจจับแบบไฮบริด (ชื่อสินค้าตรง หรือจำนวนหีบห่อตรง ให้ปัดเป็น MATCH ทันที)\n\n"
                        "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ (กรุณาแสดงผลแยกแถวให้ชัดเจน):\n\n"
                        "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                        "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุการอนุโลม |\n"
                        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        "| [แสดงผลตรวจให้ครบถ้วนตามเกณฑ์เดิม] | ... | ... | ... | ... | ... |\n"
                    )
                    contents_payload.append(prompt_instruction)
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=contents_payload)
                    
                    st.success("✨ Gemini ตรวจสอบข้อมูลเสสิ้น!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")

    # 🌟 ส่วนที่ 2: ระบบจัดการและบันทึกวันที่รับ D/O (ปรับแต่งตามรีเควส)
    st.markdown("---")
    st.markdown("## 📦 ส่วนที่ 2: ระบบตรวจสอบสถานะการส่งมอบ D/O (สำหรับตอบ Agent และลูกค้า)")
    
    # ส่วนฟอร์มบันทึกข้อมูล
    st.markdown("### 📝 บันทึกการรับ D/O หน้างาน")
    cx1, cx2 = st.columns(2)
    with cx1:
        input_bl = st.text_input("กรอกเลขที่ B/L ที่ลูกค้ามารับ", placeholder="เช่น PKELCH2660002")
    with cx2:
        input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.")
        
    if st.button("💾 บันทึกวันที่จ่าย D/O", use_container_width=True):
        if input_bl:
            found = False
            # ค้นหาและอัปเดตข้อมูลเดิมที่มีอยู่
            for item in st.session_state.do_database:
                if item["เลขที่ B/L"] == input_bl.strip():
                    item["วันที่รับ D/O"] = datetime.now().strftime("%Y-%m-%d") # บันทึกเฉพาะวันที่ ไม่เอาเวลา
                    if input_consignee:
                        item["ชื่อ Consignee"] = input_consignee.strip()
                    found = True
                    st.success(f"บันทึกวันที่รับ D/O ของเลข B/L {input_bl} สำเร็จ!")
                    break
            
            # ถ้าไม่เจอ ให้แอดเพิ่มแถวใหม่เข้าไปในตารางเลย
            if not found:
                new_record = {
                    "เลขที่ B/L": input_bl.strip(),
                    "ชื่อ Consignee": input_consignee.strip() if input_consignee else "ลูกค้าหน้าเคาน์เตอร์",
                    "วันที่รับ D/O": datetime.now().strftime("%Y-%m-%d") # บันทึกเฉพาะวันที่ ไม่เอาเวลา
                }
                st.session_state.do_database.append(new_record)
                st.success(f"บันทึกวันที่รับ D/O ของเลข B/L {input_bl} สำเร็จ!")
        else:
            st.warning("⚠️ โปรดระบุเลขที่ B/L ก่อนกดบันทึก")

    # ส่วนตารางมอนิเตอร์สถานะหลัก (ดึงช่องค้นหาและหัวตารางให้คลีนตามสั่ง)
    st.markdown("### 📊 ตารางประวัติการรับเอกสาร D/O")
    search_query = st.text_input("🔍 ค้นหาด่วนด้วยเลข B/L (พิมพ์เลขแล้วกด Enter เพื่อตอบ Agent)", placeholder="พิมพ์เลข B/L ที่ต้องการเช็กตรงนี้...")
    
    # ฟิลเตอร์กรองข้อมูลแสดงในตาราง
    table_data = []
    for item in st.session_state.do_database:
        if search_query.strip() == "" or search_query.strip().lower() in item["เลขที่ B/L"].lower():
            table_data.append(item)
            
    # แสดงตารางแบบคลีนๆ มีแค่ 3 คอลัมน์ตามสั่ง
    st.table(table_data)

import streamlit as st
from google import genai
from google.genai import types
import io
from datetime import datetime

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend (Gemini)", layout="wide")
st.title("🚢 [Gemini 2.5] ระบบตรวจเอกสารและจัดการสถานะส่งมอบ D/O อัจฉริยะ")
st.subheader("เวอร์ชันสำหรับส่งโครงการ: มีระบบแทร็กประวัติเวลารับ D/O สำหรับตอบ Agent ได้ทันที")

# 🔑 ใส่รหัส Gemini API Key ของคุณที่นี่ครับ
API_KEY = "AQ.Ab8RN6KVujoWku4GOWYJbD1uFzhtqUHObm9Y571oqquJ8XrdwQ"

# 🗄️ จำลองฐานข้อมูลเก็บสถานะการแลก D/O (ใช้ Session State)
if "do_database" not in st.session_state:
    st.session_state.do_database = [
        {
            "bl_no": "PKELCH2660001",
            "consignee": "SIAM LOGISTICS CO., LTD.",
            "status": "🟢 รับ D/O เรียบร้อยแล้ว",
            "pickup_time": "2026-06-25 14:30:15",
            "agent_remark": "Agent: OOCL / จ่ายเงินครบแล้ว"
        },
        {
            "bl_no": "PKELCH2660002",
            "consignee": "PACIFIC TRADING THAILAND",
            "status": "🟡 เอกสารผ่านแล้ว (รอเงินเข้า/รอรับ D/O)",
            "pickup_time": "-",
            "agent_remark": "Agent: ONE / รอยืนยัน Pay-in"
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
    
    # 🌟 ส่วนที่ 1: หน้าจอหลักสำหรับอัปโหลดและตรวจสอบเอกสาร (Process 1-4)
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
                        "จงวิเคราะห์ไฟล์ภาพหรือ PDF ของเอกสาร Bill of Lading (B/L) ทุกฉบับ เปรียบเทียบกับ ใบขอแก้ไขข้อมูล (Amendment/DO รายการ) "
                        "โดยแตกแถว (Row) แยกคู่อย่างชัดเจนตามกฎตรวจจับแบบไฮบริด (ชื่อสินค้าตรง หรือจำนวนหีบห่อตรง ให้ปัดเป็น MATCH ทันที)\n\n"
                        "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ (กรุณาแสดงผลแยกแถวให้ชัดเจน):\n\n"
                        "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                        "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุการอนุโลม |\n"
                        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        "| **PKELCH2660001** | Consignee | ... | ... | MATCH | ... |\n"
                        "| [แสดงผลตรวจให้ครบถ้วนตามเกณฑ์เดิม] | ... | ... | ... | ... | ... |\n"
                    )
                    contents_payload.append(prompt_instruction)
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=contents_payload)
                    
                    st.success("✨ Gemini ตรวจสอบข้อมูลเสร็จสิ้น!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")

    # 🌟 ส่วนที่ 2: ระบบจัดการและบันทึกเวลาการรับ D/O (Process 8)
    st.markdown("---")
    st.markdown("## 📦 ส่วนที่ 2: ระบบบริหารสถานะและการส่งมอบ D/O (สำหรับตอบ Agent และลูกค้า)")
    
    # ส่วนฟอร์มสำหรับอัปเดตเวลารับ D/O เมื่อลูกค้ามาถึงหน้าเคาน์เตอร์
    st.markdown("### 📝 บันทึกการรับ D/O หน้างาน (เมื่อลูกค้ามาแลกเอกสาร)")
    cx1, cx2, cx3 = st.columns([2, 2, 2])
    with cx1:
        input_bl = st.text_input("กรอกเลขที่ B/L ที่ลูกค้ามารับ", placeholder="เช่น PKELCH2660002")
    with cx2:
        input_agent = st.text_input("ชื่อ Agent / สายเรือ (ถ้ามีข้อมูล)", placeholder="เช่น OOCL, ONE, COSCO")
    with cx3:
        st.markdown("<br>", unsafe_allow_html=True) # จัดปุ่มให้ตรงบรรทัด
        if st.button("💾 บันทึกเวลาจ่าย D/O ทันที", use_container_width=True):
            if input_bl:
                found = False
                # วนลูปเช็กว่ามีเลข B/L นี้ในฐานข้อมูลจำลองไหม
                for item in st.session_state.do_database:
                    if item["bl_no"] == input_bl.strip():
                        item["status"] = "🟢 รับ D/O เรียบร้อยแล้ว"
                        item["pickup_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if input_agent:
                            item["agent_remark"] = f"Agent: {input_agent}"
                        found = True
                        st.success(f"บันทึกเวลารับ D/O ของเลข B/L {input_bl} สำเร็จ!")
                        break
                
                # ถ้าไม่เจอ เลข B/L เดิม ให้แอดเป็นรายการใหม่เข้าไปในตารางเลย
                if not found:
                    new_record = {
                        "bl_no": input_bl.strip(),
                        "consignee": "ลูกค้าหน้าเคาน์เตอร์",
                        "status": "🟢 รับ D/O เรียบร้อยแล้ว",
                        "pickup_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "agent_remark": f"Agent: {input_agent}" if input_agent else "-"
                    }
                    st.session_state.do_database.append(new_record)
                    st.success(f"สร้างรายการและบันทึกเวลารับ D/O ของเลข B/L {input_bl} สำเร็จ!")
            else:
                st.warning("⚠️ โปรดระบุเลขที่ B/L ก่อนกดบันทึก")

    # ส่วนตารางมอนิเตอร์สถานะหลัก (Dashboard) ที่เอาไว้เปิดดูเวลา Agent ถาม
    st.markdown("### 📊 ตารางตรวจสอบสถานะตู้สินค้า และ ประวัติเวลารับ D/O")
    
    # ปุ่มสำหรับเคลียร์ค่า หรือเพิ่มช่องค้นหาด่วน
    search_query = st.text_input("🔍 ค้นหาด่วนด้วยเลข B/L (พิมพ์เลขแล้วกด Enter เพื่อตอบ Agent)", placeholder="พิมพ์เลข B/L ที่ต้องการเช็กตรงนี้...")
    
    # แสดงตารางผลลัพธ์
    table_data = []
    for item in st.session_state.do_database:
        # ฟิลเตอร์กรองข้อมูลตามคำค้นหา
        if search_query.strip() == "" or search_query.strip().lower() in item["bl_no"].lower():
            table_data.append(item)
            
    st.table(table_data)

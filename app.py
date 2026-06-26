import streamlit as st
from google import genai
from google.genai import types
import io

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend (Gemini)", layout="wide")
st.title("🚢 [Gemini 2.5] ระบบตรวจเปรียบเทียบข้อมูล B/L แยกตามรายฉบับ และใบ Amend")
st.subheader("เวอร์ชันแก้ไข: แยกแถวตารางชัดเจน ไม่ยำรวมคอลัมน์ อ่านง่าย นำไปคีย์งานได้ทันที")

# 🔑 ใส่รหัส Gemini API Key ของคุณที่นี่ครับ
API_KEY = "AQ.Ab8RN6KVujoWku4GOWYJbD1uFzhtqUHObm9Y571oqquJ8XrdwQ"

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
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 1. ไฟล์ Bill of Lading (B/L) *อัปโหลดได้หลายไฟล์พร้อมกัน*")
        bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl")
    with col2:
        st.markdown("### 📝 2. ไฟล์ใบขอแก้ไข (Amendment)")
        amend_file = st.file_uploader("ลากไฟล์ใบ Amend มาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], key="amend")

    if bl_files and amend_file:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลแบบแยกรายใบ", use_container_width=True):
            with st.spinner("🤖 Gemini กําลังจัดตารางแยกแยะคู่ข้อมูล B/L และใบ Amend อย่างละเอียด..."):
                try:
                    contents_payload = []
                    
                    # วนลูปแอดไฟล์ B/L ทุกใบ
                    for idx, bl in enumerate(bl_files):
                        part = เตรียมไฟล์สำหรับ_gemini(bl)
                        if part:
                            contents_payload.append(part)
                            
                    # แอดไฟล์ใบ Amend ปิดท้าย
                    amend_part = เตรียมไฟล์สำหรับ_gemini(amend_file)
                    if amend_part:
                        contents_payload.append(amend_part)
                    
                    # 🧠 ออกแบบกฎการเจนเนอเรทตารางใหม่ บังคับแตก Row ห้ามยำรวมคอลัมน์
                    prompt_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารโลจิสติกส์การนำเข้าและส่งออก (Import-Export Specialist) "
                        "จงทำการวิเคราะห์ไฟล์ Bill of Lading (B/L) ทุกๆ ใบที่ส่งมา และนำมาจับคู่เปรียบเทียบกับข้อมูลบนใบขอแก้ไขเอกสาร (Amendment) "
                        "โดยห้ามนำข้อมูลของ B/L คนละเลข หรือ D/O คนละใบมายำรวมกันในแถวเดียวเด็ดขาด! ให้แยกแยะผลลัพธ์เป็นรายฉบับอย่างชัดเจนตามกฎต่อไปนี้:\n\n"
                        
                        "📋 กฎการจัดโครงสร้างตารางแสดงผล (CRITICAL TABLE STRUCTURE):\n"
                        "- สร้างตารางหลักที่แสดงการเปรียบเทียบทีละคู่ให้ชัดเจน โดย 1 แถว (Row) = 1 ฟิตเจอร์ตรวจสอบของ B/L ใบนั้นๆ\n"
                        "- ตัวอย่างเช่น หากมี B/L 3 ใบ (PKELCH2660001, PKELCH2660002, PKELCH2660003) และใบ Amend แยกเป็นรายรายการ (D/O 01, D/O 02, D/O 03) "
                        "ให้เขียนไล่ลำดับตารางให้เห็นชัดเจน ห้ามรวบยอดใส่เครื่องหมาย <br> เพื่อยำรวมกันในช่องเดียว\n\n"
                        
                        "🔍 5 ฟิลด์หลักที่ต้องระบุและตรวจจับรายใบ:\n"
                        "1. Consignee (เทียบชื่อบริษัทหลัก ไม่เอาจุดหรือคอมมา)\n"
                        "2. Shipping Marks & Numbers (เครื่องหมายหีบห่อสินค้า ไม่รวมเลขตู้คอนเทนเนอร์)\n"
                        "3. Description of Goods (รายละเอียดชื่อสินค้า)\n"
                        "4. Gross Weight (G.W.) (ตัวเลขน้ำหนักของ B/L ใบนั้นๆ เทียบกับคู่ Amend ของมัน)\n"
                        "5. Measurement (CBM) (ตัวเลขปริมาตรของ B/L ใบนั้นๆ เทียบกับคู่ Amend ของมัน)\n\n"
                        
                        "🧠 กฎเหล็กคาดการณ์ความเพี้ยนจากฟอนต์เบียด (Contextual Font Logic):\n"
                        "- ในฟิลด์ Description of Goods หากในเอกสารต้นฉบับฟอนต์เบียดจนเครื่องหมาย '#' เพี้ยนไป แต่พิจารณาบริบทแล้วในใบ Amend ระบุชัดเจนว่าต้องการแก้ไขเป็นคำเฉพาะ เช่น '#35S' หรือ '#22S' ให้คุณใช้ Logic คาดการณ์คำเพื่อตัดสินผลเป็น 'MATCH' ทันที และระบุในหมายเหตุสั้นๆ\n\n"
                        
                        "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ (กรุณาใช้ฟอร์แมตนี้เป๊ะๆ):\n\n"
                        "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                        "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุ |\n"
                        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        "| **PKELCH2660001** (D/O 01) | Consignee | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660001** (D/O 01) | Shipping Marks | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660001** (D/O 01) | Description of Goods | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660001** (D/O 01) | Gross Weight (G.W.) | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660001** (D/O 01) | Measurement (CBM) | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| --- | --- | --- | --- | --- | --- |\n"
                        "| **PKELCH2660002** (D/O 02) | Consignee | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660002** (D/O 02) | Shipping Marks | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| [ไล่เรียงให้ครบทุกใบ...] | ... | ... | ... | ... | ... |\n\n"
                        
                        "### 🧮 ตารางสรุปยอดรวมสุทธิ (Grand Totals Check)\n"
                        "| หัวข้อตรวจสอบ | ผลรวมจาก B/L ทุกใบรวมกัน | ยอดรวมสุทธิบนใบ Amend | ผลรวมตรงกันไหม | หมายเหตุคำนวณ |\n"
                        "| :--- | :--- | :--- | :--- | :--- |\n"
                        "| **Gross Weight รวม** | [เลขรวม] | [เลขรวม] | MATCH / MISMATCH | [คำนวณให้เห็น] |\n"
                        "| **Measurement (CBM) รวม** | [เลขรวม] | [เลขรวม] | MATCH / MISMATCH | [คำนวณให้เห็น] |\n\n"
                        "### 📢 สรุปข้อแนะนำการปฏิบัติงาน\n"
                        "**ข้อวิเคราะห์สรุป:** (เจาะลึกภาพรวมการตรวจปล่อยเอกสารชิปเม้นท์นี้)"
                    )
                    
                    contents_payload.append(prompt_instruction)
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents_payload
                    )
                    
                    st.success("✨ Gemini จัดระเบียบและคัดแยกตารางข้อมูลเสร็จสิ้น!")
                    st.markdown("### 📊 ผลการตรวจสอบเปรียบเทียบรายใบ (Clean View)")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")

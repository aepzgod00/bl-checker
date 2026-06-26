import streamlit as st
from google import genai
from google.genai import types
import io

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend (Gemini)", layout="wide")
st.title("🚢 [Gemini 2.5] ระบบตรวจเปรียบเทียบข้อมูล B/L หลายฉบับ กับ ใบ Amend")
st.subheader("เวอร์ชันเสถียรสูงสุด: อัปเกรดระบบ Prompt อัจฉริยะ คาดการณ์คำและสรุปผลแม่นยำ")

# 🔑 ใส่รหัส Gemini API Key ของคุณที่นี่ครับ (ใช้ง่าย ไม่ล็อก 401 วุ่นวาย)
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
    # เริ่มต้นเชื่อมต่อกับเซิร์ฟเวอร์ Google GenAI
    client = genai.Client(api_key=API_KEY)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 1. ไฟล์ Bill of Lading (B/L) *อัปโหลดได้หลายไฟล์พร้อมกัน*")
        bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl")
    with col2:
        st.markdown("### 📝 2. ไฟล์ใบขอแก้ไข (Amendment)")
        amend_file = st.file_uploader("ลากไฟล์ใบ Amend มาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], key="amend")

    if bl_files and amend_file:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลด้วย Gemini อัจฉริยะ", use_container_width=True):
            with st.spinner("🤖 Gemini กําลังวิเคราะห์โครงสร้างเอกสารและคำนวเนตัวเลขทั้งหมด..."):
                try:
                    # 1. รวบรวมชิ้นส่วนไฟล์ทั้งหมดส่งไปให้โมเดลประมวลผลพร้อมกันทีเดียว
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
                    
                    # 2. ข้อความสั่งงานระดับเซียนโลจิสติกส์ (Advanced Prompt Engineering)
                    prompt_instruction = (
                        "คุณคือผู้ตรวจสอบเอกสารฝ่ายขาเข้า-ขาออก (Import-Export Specialist) ที่มีความละเอียดรอบคอบระดับสูงสุด "
                        "จงทำการวิเคราะห์รูปภาพหรือไฟล์ PDF ของ Bill of Lading (B/L) ทุกๆ ใบที่อัปโหลดมา นำข้อมูลมารวมกัน "
                        "แล้วนำไปเปรียบเทียบกับเอกสารใบขอแก้ไขข้อมูล (Amendment) อย่างเข้มงวดตามหลักการดังนี้:\n\n"
                        
                        "🔍 ฟิลด์บังคับตรวจสอบเปรียบเทียบ (5 Core Fields):\n"
                        "1. Consignee: ตรวจสอบเฉพาะชื่อบริษัทหลัก (ตัดเครื่องหมายจุด, คอมมา หรือคำลงท้ายสร้อยออกเพื่อเทียบความถูกต้อง)\n"
                        "2. Shipping Marks & Numbers: ตรวจสอบเครื่องหมายบนหีบห่อตามที่ระบุในเอกสาร\n"
                        "3. Description of Goods: รายละเอียดสินค้าทั้งหมด\n"
                        "4. Gross Weight (G.W.): ทำการหาผลรวมตัวเลข Gross Weight จาก B/L ทุกใบที่ส่งมา แล้วนำยอดรวมนั้นไปเช็กว่าตรงกับค่าบนใบ Amend ไหม\n"
                        "5. Measurement (M3/CBM): ทำการหาผลรวมตัวเลข CBM จาก B/L ทุกใบที่ส่งมา แล้วนำยอดรวมนั้นไปเช็กว่าตรงกับค่าบนใบ Amend ไหม\n\n"
                        
                        "🧠 กฎเหล็ก Logic คาดการณ์บริบทคำผิด (Contextual Font Logic):\n"
                        "- หากในช่อง Description of Goods ของ B/L มีคำที่ฟอนต์เบียดหรือจาง เช่น ระบบอาจจะสแกนเห็นเป็นเลขอื่นแทนเครื่องหมาย '#' (เช่น 'Hi Alumina sand 35S' หรือเพี้ยนเป็นอักษรอื่น) แต่ในเอกสารใบ Amend เขียนระบุชัดเจนว่าต้องแก้ไขเป็น '#35S' หรือ '#22S' ให้คุณพิจารณาตามความน่าจะเป็นเชิงบริบท (Contextual Logic) ว่ามันคือตัวเดียวกัน และตัดสินผลการตรวจสอบช่องนั้นเป็น 'MATCH' ทันที! แต่ให้ระบุในหมายเหตุว่า 'ผ่านการปรับปรุงความเพี้ยนของฟอนต์ตัวอักษรเบียด'\n"
                        "- อย่างไรก็ตาม หากมีความแตกต่างด้านการสลับโครงสร้างคำที่มีผลต่อความหมาย เช่น 'MADE IN TAIWAN' กับ 'IN TAIWAN MADE' หรือการเว้นวรรคผิดจุดที่ส่งผลต่อรหัสสินค้า ให้ตัดสินเป็น 'MISMATCH'\n\n"
                        
                        "📋 รูปแบบการแสดงผล (ต้องแสดงเป็นตาราง Markdown แยกหัวข้อให้ชัดเจนและอ่านง่ายที่สุด):\n\n"
                        "### 📊 ตารางเปรียบเทียบข้อมูลเอกสาร B/L ทั้งหมด และ ใบ Amend\n"
                        "| หัวข้อตรวจสอบ | ข้อมูลรวมจาก B/L ทุกใบ | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุ |\n"
                        "| :--- | :--- | :--- | :--- | :--- |\n"
                        "| **Consignee** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [รายละเอียด] |\n"
                        "| **Shipping Marks** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [รายละเอียด] |\n"
                        "| **Description of Goods** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [วิเคราะห์เคสพิเศษฟอนต์เบียด] |\n"
                        "| **Gross Weight (G.W.)** | [ข้อมูลรวมคณิตศาสตร์] | [ข้อมูล] | MATCH หรือ MISMATCH | [แสดงเลขบวกกันให้เห็น] |\n"
                        "| **Measurement (CBM)** | [ข้อมูลรวมคณิตศาสตร์] | [ข้อมูล] | MATCH หรือ MISMATCH | [แสดงเลขบวกกันให้เห็น] |\n\n"
                        
                        "### 📢 สรุปข้อแนะนำการ Amend และจุดที่ต้องระวัง\n"
                        "**วิเคราะห์ภาพรวม:** (เขียนสรุปให้คำแนะนำในมุมมองผู้ตรวจปล่อยสินค้าอย่างมืออาชีพ)"
                    )
                    
                    contents_payload.append(prompt_instruction)
                    
                    # 3. ส่งคำสั่งไปประมวลผลที่โมเดลรุ่นเก่งและนิ่งที่สุด Gemini 2.5 Flash
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents_payload
                    )
                    
                    st.success("✨ Gemini ตรวจสอบและคำนวณข้อมูลให้เสร็จสิ้นเรียบร้อย!")
                    st.markdown("### 📊 ผลการตรวจสอบเปรียบเทียบเชิงลึก")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")

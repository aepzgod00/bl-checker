import streamlit as st
from anthropic import Anthropic
import base64
import io
import pdfplumber
from PIL import Image

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend", layout="wide")
st.title("🚢 [Claude 3.5 Sonnet] ระบบตรวจเปรียบเทียบข้อมูล B/L หลายฉบับ กับ ใบ Amend")
st.subheader("เวอร์ชันแก้ Error: บังคับแปลงเป็นรูปภาพคมชัดสูงก่อนส่งให้ Claude 3.5 สแกนสายตา")

# ⚠️ ใส่รหัส Claude API Key (sk-ant-...) ของคุณด้านล่างนี้ครับ
API_KEY = "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"

# ฟังก์ชันแปลงไฟล์ทุกประเภท (รวมถึง PDF) ให้กลายเป็นภาพ JPEG และทำเป็น Base64
def แปลงไฟล์เป็นภาพ_base64(file_uploader_obj):
    file_bytes = file_uploader_obj.getvalue()
    file_name = file_uploader_obj.name.lower()
    
    # 📄 เคสไฟล์ PDF: ใช้ pdfplumber ดึงหน้าแรกออกมาแปลงเป็นรูปภาพ
    if file_name.endswith('.pdf'):
        try:
            with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
                if pdf.pages:
                    # ดึงหน้าแรกของ PDF ออกมา (ส่วนใหญ่ B/L และ Amend มีหน้าเดียวหรืออยู่หน้าแรก)
                    first_page = pdf.pages[0]
                    # แปลงหน้านี้ให้กลายเป็นภาพออบเจกต์ของ PIL (ความละเอียดสูง)
                    pil_img = first_page.to_image(resolution=150).original
                    
                    # เซฟภาพลงหน่วยความจำบัฟเฟอร์ให้เป็น JPEG
                    img_byte_arr = io.BytesIO()
                    pil_img.convert('RGB').save(img_byte_arr, format='JPEG')
                    base64_data = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
                    return base64_data
        except Exception as e:
            st.error(f"ไม่สามารถอ่านไฟล์ PDF {file_uploader_obj.name} ได้: {str(e)}")
            return None
            
    # 🖼️ เคสไฟล์รูปภาพปกติ (PNG, JPG, JPEG)
    else:
        base64_data = base64.b64encode(file_bytes).decode("utf-8")
        return base64_data

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Claude API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = Anthropic(api_key=API_KEY)
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 1. ไฟล์ Bill of Lading (B/L) *อัปโหลดได้หลายไฟล์พร้อมกัน*")
        bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl")
    with col2:
        st.markdown("### 📝 2. ไฟล์ใบขอแก้ไข (Amendment)")
        amend_file = st.file_uploader("ลากไฟล์ใบ Amend มาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], key="amend")

    if bl_files and amend_file:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลด้วย Claude 3.5", use_container_width=True):
            with st.spinner("🤖 Claude 3.5 Sonnet กําลังใช้เลนส์สายตาแกะฟอนต์เอกสารอย่างละเอียด..."):
                try:
                    # ส่วนผสมคอนเทนต์ที่จะส่งให้ Claude (บังคับเป็น Image ชัดเจน)
                    message_content = []
                    
                    # 🔄 1. วนลูปแปลงไฟล์ B/L ทุกใบให้เป็นรูปภาพ และแอดเข้าสู่ระบบ
                    for bl_file in bl_files:
                        b64_img = แปลงไฟล์เป็นภาพ_base64(bl_file)
                        if b64_img:
                            message_content.append({
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": b64_img
                                }
                            })
                    
                    # 📝 2. แปลงไฟล์ใบ Amend ให้เป็นรูปภาพ และแอดเข้าสู่ระบบ
                    amend_b64 = แปลงไฟล์เป็นภาพ_base64(amend_file)
                    if amend_b64:
                        message_content.append({
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": amend_b64
                            }
                        })
                    
                    # 🧠 3. สั่ง Prompt กฎเหล็กโลจิสติกส์ปิดท้าย เพื่อให้มันวิเคราะห์ภาพด้านบนทั้งหมด
                    system_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารโลจิสติกส์ มีความแม่นยำสูงมากในการตรวจสอบเอกสาร Bill of Lading (B/L) หลายๆ ใบ เทียบกับใบขอแก้ไขข้อมูล (Amendment) ใบเดียว\n\n"
                        "ภารกิจของคุณ:\n"
                        "ให้เปรียบเทียบและตรวจสอบความถูกต้องจากภาพเอกสารด้านบนทั้งหมด โดยเน้น 5 ฟิลด์หลักดังนี้:\n"
                        "1. Consignee (เอาแค่ชื่อบริษัท ไม่เอาที่อยู่ ใช้ Logic ตัดคำพวก ., ออกเองเลย)\n"
                        "2. Shipping Marks & Numbers (เอาตามที่ลูกค้ากรอกหรือติ๊กเลือก)\n"
                        "3. Description of Goods (รายละเอียดสินค้าทั้งหมด)\n"
                        "4. Gross Weight (G.W.) (รวมมูลค่าตัวเลขจาก B/L ทุกใบมาเทียบกับใบ Amend ว่าตรงกันไหม)\n"
                        "5. Measurement (M3/CBM) (รวมมูลค่าตัวเลขจาก B/L ทุกใบมาเทียบกับใบ Amend ว่าตรงกันไหม)\n\n"
                        "⚠️ กฎเหล็กในการตรวจจับอักษร (CRITICAL LOGIC):\n"
                        "- ในช่อง Description of Goods หากคุณอ่านเจอคำว่า 'Hi Alumina sand #35S' หรือ '#22S' แล้วฟอนต์มันเบียดกันจนดูเพี้ยน แต่ในใบ Amend ระบุเป็น #35S ชัดเจน ให้คุณใช้ Logic คาดการณ์บริบทความน่าจะเป็น (Contextual Logic) ว่ามันคือตัวเดียวกัน และตัดสินผลเป็น 'MATCH' ทันที (แต่ให้เขียนหมายเหตุบอกสั้นๆ ว่าปรับปรุงจากฟอนต์เอกสารเบียดกัน)\n"
                        "- ต้องพิจารณาถึงความแตกต่างเล็กน้อย เช่น การเว้นวรรค (Spacing) หรือการสลับตำแหน่งของคำ (เช่น MADE IN TAIWAN vs IN TAIWAN MADE) โดยต้องมองว่าเป็นจุดที่ต้องแก้ไข (MISMATCH)\n\n"
                        "📋 รูปแบบการรายงานผลลัพธ์ (กรุณาแสดงผลเป็นตาราง Markdown แยกตามหัวข้ออย่างชัดเจน):\n\n"
                        "### 📊 ตารางเปรียบเทียบข้อมูลเอกสาร B/L ทั้งหมด และ ใบ Amend\n"
                        "| หัวข้อตรวจสอบ | ข้อมูลรวมจาก B/L ทุกใบ | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / สาเหตุที่ผิดพลาด |\n"
                        "| :--- | :--- | :--- | :--- | :--- |\n"
                        "| **Consignee** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [รายละเอียด] |\n"
                        "| **Shipping Marks** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [รายละเอียด] |\n"
                        "| **Description of Goods** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [รายละเอียดเคสพิเศษ] |\n"
                        "| **Gross Weight (G.W.)** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [คำนวณสรุป] |\n"
                        "| **Measurement (CBM)** | [ข้อมูล] | [ข้อมูล] | MATCH หรือ MISMATCH | [คำนวณสรุป] |\n\n"
                        "### 📢 สรุปข้อแนะนำการ Amend เอกสาร\n"
                        "**สรุปภาพรวม:** (วิเคราะห์ภาพรวมให้ชัดเจนแบบมืออาชีพ Import-Export)"
                    )
                    
                    # แอดคำสั่ง Text บรีฟงานเข้าไปเป็นส่วนสุดท้ายของกล่องคำสั่ง
                    message_content.append({"type": "text", "text": system_instruction})
                    
                    # ยิงข้อมูลเรียกใช้งาน Claude 3.5 Sonnet
                    response = client.messages.create(
                        model="claude-3-5-sonnet-20241022",
                        max_tokens=4000,
                        temperature=0.1,
                        messages=[{"role": "user", "content": message_content}]
                    )
                    
                    st.success("✨ Claude 3.5 ตรวจสอบข้อมูลเสร็จสิ้นเรียบร้อย!")
                    st.markdown("### 📊 ผลการตรวจสอบเปรียบเทียบเชิงลึก")
                    st.markdown(response.content[0].text)
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Claude: {str(e)}")

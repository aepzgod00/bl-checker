import streamlit as st
from anthropic import Anthropic
import base64
import io
from pypdf import PdfReader

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend", layout="wide")
st.title("🚢 [Claude 3.5 Sonnet] ระบบตรวจเปรียบเทียบข้อมูล B/L หลายฉบับ กับ ใบ Amend")
st.subheader("เวอร์ชันเสถียรสูงสุดบน Cloud: รองรับทั้งไฟล์ภาพและ PDF สแกน")

# ⚠️ ใส่รหัส Claude API Key (sk-ant-...) ของคุณด้านล่างนี้ครับ
API_KEY = "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"

# ฟังก์ชันสำหรับจัดการไฟล์เพื่อส่งให้ Claude
def ประมวลผลเอกสาร(file_uploader_obj):
    file_bytes = file_uploader_obj.getvalue()
    file_name = file_uploader_obj.name.lower()
    file_type = file_uploader_obj.type
    
    # เคสที่ 1: เป็นไฟล์ PDF -> สกัดข้อความออกมา
    if file_name.endswith('.pdf') or "pdf" in file_type:
        try:
            pdf_file = io.BytesIO(file_bytes)
            reader = PdfReader(pdf_file)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
            
            # ถ้าสกัดข้อความออกมาได้ ให้ส่งเป็นข้อความ Text
            if extracted_text.strip():
                return {"type": "text", "text": f"--- เนื้อหาข้อความจากไฟล์ {file_uploader_obj.name} ---\n{extracted_text}"}
        except Exception:
            pass
            
    # เคสที่ 2: เป็นไฟล์รูปภาพ หรือ PDF ที่สกัดตัวหนังสือไม่ได้ (เป็นภาพสแกนเพียวๆ)
    # ส่งข้อมูลแบบภาพ Base64 ให้ตาคอมพิวเตอร์ของ Claude สแกนโดยตรง
    # หมายเหตุ: หากระบบต้องการระบุมีเดียไทป์ บังคับเลือก image/jpeg หรือ image/png
    media_type = "image/png" if "png" in file_type else "image/jpeg"
    base64_data = base64.b64encode(file_bytes).decode("utf-8")
    return {
        "type": "image",
        "source": {
            "type": "base64",
            "media_type": media_type,
            "data": base64_data
        }
    }

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
            with st.spinner("🤖 Claude 3.5 Sonnet กําลังแกะฟอนต์และประมวลผลตารางอย่างละเอียด..."):
                try:
                    # โครงสร้างข้อความคอนเทนต์สำหรับส่งให้ Claude
                    message_content = []
                    
                    # ตัวแปรคุม Logic และ Prompt กฎเหล็กโลจิสติกส์
                    system_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารโลจิสติกส์ มีความแม่นยำสูงมากในการตรวจสอบเอกสาร Bill of Lading (B/L) หลายๆ ใบ เทียบกับใบขอแก้ไขข้อมูล (Amendment) ใบเดียว\n\n"
                        "ภารกิจของคุณ:\n"
                        "ให้ตรวจสอบความถูกต้องและเปรียบเทียบ 5 ฟิลด์หลักดังนี้:\n"
                        "1. Consignee (เอาแค่ชื่อบริษัท ไม่เอาที่อยู่ ใช้ Logic ตัดคำพวก ., ออกเองเลย)\n"
                        "2. Shipping Marks & Numbers (เอาตามที่ลูกค้ากรอกหรือติ๊กเลือก)\n"
                        "3. Description of Goods (รายละเอียดสินค้าทั้งหมด)\n"
                        "4. Gross Weight (G.W.) (รวมมูลค่าตัวเลขจาก B/L ทุกใบมาเทียบกับใบ Amend ว่าตรงกันไหม)\n"
                        "5. Measurement (M3/CBM) (รวมมูลค่าตัวเลขจาก B/L ทุกใบมาเทียบกับใบ Amend ว่าตรงกันไหม)\n\n"
                        "⚠️ กฎเหล็กในการตรวจจับอักษร (CRITICAL LOGIC):\n"
                        "- ในช่อง Description of Goods หากคุณอ่านเจอคำว่า 'Hi Alumina sand #35S' หรือ '#22S' แล้วระบบมองเห็นเครื่องหมาย '#' เพี้ยนเป็นเลขอื่นเนื่องจากฟอนต์เบียด แต่ในใบ Amend ระบุเป็น #35S ชัดเจน ให้คุณใช้ Logic คาดการณ์บริบทความน่าจะเป็น (Contextual Logic) ว่ามันคือตัวเดียวกัน และตัดสินผลเป็น 'MATCH' ทันที (แต่ให้เขียนหมายเหตุบอกสั้นๆ ว่าปรับปรุงจากฟอนต์เอกสารเบียดกัน)\n"
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
                    
                    message_content.append({"type": "text", "text": system_instruction})
                    
                    # 🔄 วนลูปประมวลผลไฟล์ B/L ทุกใบ
                    for bl in bl_files:
                        bl_part = ประมวลผลเอกสาร(bl)
                        if bl_part:
                            message_content.append(bl_part)
                    
                    # ประมวลผลไฟล์ใบ Amend
                    amend_part = ประมวลผลเอกสาร(amend_file)
                    if amend_part:
                        message_content.append(amend_part)
                    
                    # ยิงข้อมูลเรียกใช้งาน Claude 3.5 Sonnet ตัวท็อป
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
                    st.error(f"ระบบตรวจพบความล่าช้าทางเทคนิค: {str(e)}")

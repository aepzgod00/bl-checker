import streamlit as st
from anthropic import Anthropic
import base64
from pdf2image import convert_from_bytes
import io

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend", layout="wide")
st.title("🚢 [Claude 3.5 Sonnet] ระบบตรวจเปรียบเทียบข้อมูล B/L หลายฉบับ กับ ใบ Amend")
st.subheader("เวอร์ชันเสถียรสูงสุด: สแกนโครงสร้างพิกเซลและแก้อักษรเพี้ยนอย่างแม่นยำ")

# ⚠️ ใส่รหัส Claude API Key (sk-ant-...) ของคุณด้านล่างนี้ครับ
API_KEY = "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"

# ฟังก์ชันแปลงไฟล์ส่งให้ Claude
def เอกสารเป็นภาพ_base64(file_bytes, file_type):
    if "pdf" in file_type.lower():
        # ถ้าเป็น PDF ให้แปลงหน้าแรกเป็นรูปภาพก่อนส่งให้โมเดลมองเห็น
        images = convert_from_bytes(file_bytes, first_page=1, last_page=1)
        if images:
            img_byte_arr = io.BytesIO()
            images[0].save(img_byte_arr, format='JPEG')
            base64_data = base64.b64encode(img_byte_arr.getvalue()).decode("utf-8")
            return "image/jpeg", base64_data
    else:
        # ถ้าเป็นรูปภาพปกติอยู่แล้ว ส่งตรงได้เลย
        base64_data = base64.b64encode(file_bytes).decode("utf-8")
        return file_type, base64_data
    return None, None

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
                    # โครงสร้างข้อความสำหรับส่งให้ Claude
                    message_content = []
                    
                    # ตัวแปรคุม Logic และ Prompt กฎเหล็ก
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
                    
                    # 🔄 วนลูปโหลดไฟล์ B/L ทุกใบส่งเข้าสมองกล
                    for bl in bl_files:
                        m_type, b64_txt = เอกสารเป็นภาพ_base64(bl.getvalue(), bl.type)
                        if b64_txt:
                            message_content.append({
                                "type": "image",
                                "source": {"type": "base64", "media_type": "image/jpeg", "data": b64_txt}
                            })
                    
                    # โหลดไฟล์ใบ Amend ส่งเข้าสมองกล
                    am_type, am_b64 = เอกสารเป็นภาพ_base64(amend_file.getvalue(), amend_file.type)
                    if am_b64:
                        message_content.append({
                            "type": "image",
                            "source": {"type": "base64", "media_type": "image/jpeg", "data": am_b64}
                        })
                    
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

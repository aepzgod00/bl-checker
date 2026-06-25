import streamlit as st
import google.generativeai as genai

# ตั้งค่าหน้าตาของเว็บไซต์
st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend", layout="wide")
st.title("🚢 ระบบตรวจเปรียบเทียบข้อมูล B/L หลายฉบับ กับ ใบ Amend")
st.subheader("เวอร์ชันอัปเกรด: รองรับการลากไฟล์ B/L หลายใบพร้อมกันเพื่อตรวจกับใบ Amend")

# ⚠️ ใส่รหัส API Key จริงของคุณในเครื่องหมายคำพูดด้านล่างนี้ได้เลยครับ
API_KEY = "AQ.Ab8RN6KVujoWku4GOWYJbD1uFzhtqUHObm9Y571oqquJ8XrdwQ"

# เริ่มต้นระบบเชื่อมต่อ
if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
    st.error("⚠️ โปรดใส่รหัส API Key จริงในโค้ดหลังบ้านก่อนนำขึ้นระบบ Cloud")
else:
    genai.configure(api_key=API_KEY)
    
    # UI ช่องสำหรับลากไฟล์มาวางแยกฝั่งชัดเจน
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 📄 1. ไฟล์ Bill of Lading (B/L) *อัปโหลดได้มากกว่า 1 ไฟล์*")
        # 🔥 เพิ่ม accept_multiple_files=True เพื่อให้เลือกได้หลายไฟล์พร้อมกัน
        bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้ (PDF หรือ รูปภาพ)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl")
    with col2:
        st.markdown("### 📝 2. ไฟล์ใบขอแก้ไข (Amendment)")
        amend_file = st.file_uploader("ลากไฟล์ใบ Amend มาวางตรงนี้ (PDF หรือ รูปภาพ)", type=["pdf", "png", "jpg", "jpeg"], key="amend")

    # ปุ่มกดสั่งเริ่มงาน
    if bl_files and amend_file:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลเอกสารทั้งหมด", use_container_width=True):
            with st.spinner("🤖 สมองกลกำลังอ่านไฟล์ B/L ทุกใบ และคำนวณเปรียบเทียบข้อมูล..."):
                try:
                    # เตรียมลิสต์สำหรับใส่ข้อมูลไฟล์ส่งให้ AI
                    uploaded_parts = []
                    
                    # 🔄 วนลูปดึงข้อมูลจาก B/L ทุกใบที่ผู้ใช้อัปโหลดเข้ามา
                    for index, bl_file in enumerate(bl_files):
                        bl_data = bl_file.getvalue()
                        uploaded_parts.append({
                            "mime_type": bl_file.type, 
                            "data": bl_data
                        })
                    
                    # ดึงข้อมูลจากใบ Amend (มีใบเดียวเป็นตัวตั้งรับ)
                    amend_data = amend_file.getvalue()
                    uploaded_parts.append({
                        "mime_type": amend_file.type, 
                        "data": amend_data
                    })
                    
                    # ตั้งค่า Logic การตรวจ (ปรับคำสั่งให้ AI รองรับการแยกแยะข้อมูล B/L หลายใบ)
                    system_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารโลจิสติกส์ มีความแม่นยำสูงมากในการตรวจสอบเอกสาร Bill of Lading (B/L) หลายๆ ใบ เทียบกับใบขอแก้ไขข้อมูล (Amendment) ใบเดียว\n\n"
                        "ภารกิจของคุณ:\n"
                        "ฉันได้อัปโหลดไฟล์ B/L มาให้คุณหลายฉบับ และมีไฟล์ Amendment มาให้ 1 ฉบับ ให้คุณอ่านข้อมูลจาก B/L ทุกใบรวมกัน แล้วนำมาเปรียบเทียบความถูกต้องกับใบ Amendment โดยเน้นฟิลด์ดังนี้:\n"
                        "1. Consignee (เอาแค่ชื่อบริษัท ไม่เอาที่อยู่ ใช้ Logic ตัดคำพวก ., ออกเองเลย)\n"
                        "2. Shipping Marks & Numbers (เอาตามที่ลูกค้ากรอกหรือติ๊กเลือก)\n"
                        "3. Description of Goods (รายละเอียดสินค้าทั้งหมด)\n"
                        "4. Gross Weight (G.W.) (รวมมูลค่าตัวเลขจาก B/L ทุกใบมาเทียบกับใบ Amend ว่าตรงกันไหม ไม่สนทศนิยมหรือเลข 0 ตัวท้าย)\n"
                        "5. Measurement (M3/CBM) (รวมมูลค่าตัวเลขจาก B/L ทุกใบมาเทียบกับใบ Amend ว่าตรงกันไหม)\n\n"
                        "⚠️ กฎเหล็กในการตรวจจับอักษรเพี้ยน (CRITICAL OCR LOGIC):\n"
                        "- ในช่อง Description of Goods หากคุณอ่านเจอคำว่า 'Hi Alumina sand #35S' หรือ '#22S' แล้วระบบของคุณดันมองเห็นเครื่องหมาย '#' เพี้ยนเป็นเลข '2' (เช่น เห็นเป็น 235S) แต่ในใบ Amend ระบุเป็น #35S ชัดเจน ให้คุณใช้ Logic คาดการณ์บริบทความน่าจะเป็น ว่ามันคือตัวเดียวกัน และตัดสินผลลัพธ์เป็น 'MATCH' ทันที ห้ามตัดสินเป็น Mismatch เด็ดขาด\n"
                        "- ต้องพิจารณาถึงความแตกต่างเล็กน้อย เช่น การเว้นวรรค (Spacing) หรือการสลับตำแหน่งของคำ (เช่น MADE IN TAIWAN vs IN TAIWAN MADE) โดยต้องมองว่าเป็นจุดที่ต้องแก้ไข (MISMATCH)\n\n"
                        "📋 รูปแบบการรายงานผลลัพธ์ (กรุณาแสดงผลเป็นตารางแยกตามหัวข้อ ตรวจสอบเนื้อหาให้ครบทุก B/L):\n\n"
                        "### 📊 ตารางเปรียบเทียบข้อมูลเอกสาร B/L ทั้งหมด และ ใบ Amend\n"
                        "| หัวข้อตรวจสอบ | ข้อมูลรวมจาก B/L ทุกใบ | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / สาเหตุที่ผิดพลาด |\n"
                        "| :--- | :--- | :--- | :--- | :--- |\n"
                        "| **Consignee** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [ระบุชื่อบริษัทเทียบกัน] |\n"
                        "| **Shipping Marks** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [ระบุจุดต่างถ้ามี] |\n"
                        "| **Description of Goods** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [ระบุเคสพิเศษเรื่องฟอนต์เบียดหากตรวจเจอ] |\n"
                        "| **Gross Weight (G.W.)** | [สรุปยอดรวมน้ำหนักจากทุกตู้/ทุกใบ] | [น้ำหนักในใบ Amend] | MATCH หรือ MISMATCH | [คำนวณเลขให้ดูย่อๆ] |\n"
                        "| **Measurement (CBM)** | [สรุปยอดรวม CBM จากทุกตู้/ทุกใบ] | [CBM ในใบ Amend] | MATCH หรือ MISMATCH | [คำนวณเลขให้ดูย่อๆ] |\n\n"
                        "### 📢 สรุปข้อแนะนำการ Amend เอกสาร\n"
                        "**สรุปภาพรวม:** (วิเคราะห์ในมุมมองผู้เชี่ยวชาญโลจิสติกส์ Seabra Trans ว่าภาพรวม B/L ทั้งหมดนี้เมื่อเทียบกับใบ Amend แล้วถูกต้องหรือไม่ มี B/L ใบไหนที่ต้องส่งไปแก้เคลียร์กับสายเรือเพิ่มไหม สรุปเป็นข้อๆ ให้ชัดเจน)"
                    )
                    
                    # เรียกใช้โมเดลเวอร์ชันเสถียร
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        generation_config={
                            "temperature": 0.2,
                            "top_p": 0.95,
                            "max_output_tokens": 8192,
                        }
                    )
                    
                    # รวมร่างข้อมูลคำสั่งบรีฟ + ไฟล์ทั้งหมดส่งไปประมวลผลพร้อมกัน
                    prompt_data = [system_instruction] + uploaded_parts
                    response = model.generate_content(prompt_data)
                    
                    st.success("✨ ตรวจสอบเอกสารทั้งหมดเสร็จสิ้นเรียบร้อย!")
                    st.markdown("### 📊 ผลการตรวจสอบเปรียบเทียบแบบหลายไฟล์")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดความล่าช้าหรือข้อผิดพลาด: {str(e)}")

import streamlit as st
import google.generativeai as genai

# ตั้งค่าหน้าตาของเว็บไซต์
st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend", layout="wide")
st.title("🚢 ระบบตรวจเปรียบเทียบข้อมูล B/L กับ ใบ Amend")
st.subheader("เน้นตรวจสอบคุณภาพและความถูกต้องของข้อมูลตาม Logic ธุรกิจ")

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
        st.markdown("### 📄 1. ไฟล์ Bill of Lading (B/L)")
        bl_file = st.file_uploader("ลากไฟล์ B/L มาวางตรงนี้ (PDF หรือ รูปภาพ)", type=["pdf", "png", "jpg", "jpeg"], key="bl")
    with col2:
        st.markdown("### 📝 2. ไฟล์ใบขอแก้ไข (Amendment)")
        amend_file = st.file_uploader("ลากไฟล์ใบ Amend มาวางตรงนี้ (PDF หรือ รูปภาพ)", type=["pdf", "png", "jpg", "jpeg"], key="amend")

    # ปุ่มกดสั่งเริ่มงาน
    if bl_file and amend_file:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบคำสะกดอย่างละเอียด", use_container_width=True):
            with st.spinner("🤖 สมองกลกำลังวิเคราะห์ตารางและคำนวณมูลค่าตัวเลข..."):
                try:
                    # จัดเตรียมไฟล์เพื่อส่งให้โมเดล
                    bl_data = bl_file.getvalue()
                    amend_data = amend_file.getvalue()
                    
                    uploaded_parts = [
                        {"mime_type": bl_file.type, "data": bl_data},
                        {"mime_type": amend_file.type, "data": amend_data}
                    ]
                    
                    # ตั้งค่า Logic การตรวจ (ปรับปรุงให้เว้นวรรคถูกต้อง ไม่หลุดบรรทัด)
                    system_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารโลจิสติกส์ มีความแม่นยำสูงมากในการตรวจสอบเอกสาร Bill of Lading (B/L) และใบขอแก้ไขข้อมูล (Amendment)\n\n"
                        "ภารกิจของคุณ:\n"
                        "ให้เปรียบเทียบข้อมูลระหว่าง 'ภาพไฟล์ B/L' และ 'ภาพไฟล์ Amendment' ที่ฉันอัปโหลดให้ โดยเน้นตรวจสอบความถูกต้องของฟิลด์ดังนี้:\n"
                        "1. Consignee (เอาแค่ชื่อบริษัท ไม่เอาที่อยู่ ใช้ Logic ตัดคำพวก ., ออกเองเลย)\n"
                        "2. Shipping Marks & Numbers (เอาตามที่ลูกค้ากรอกหรือติ๊กเลือก)\n"
                        "3. Description of Goods (รายละเอียดสินค้าทั้งหมด)\n"
                        "4. Gross Weight (G.W.) (เช็กแค่มูลค่าตัวเลขว่าเท่ากันไหม ไม่สนทศนิยมหรือเลข 0 ตัวท้าย)\n"
                        "5. Measurement (M3/CBM) (เช็กแค่มูลค่าตัวเลขว่าเท่ากันไหม)\n\n"
                        "⚠️ กฎเหล็กในการตรวจจับอักษรเพี้ยน (CRITICAL OCR LOGIC):\n"
                        "- ในช่อง Description of Goods หากคุณอ่านเจอคำว่า 'Hi Alumina sand #35S' หรือ '#22S' แล้วระบบของคุณดันมองเห็นเครื่องหมาย '#' เพี้ยนเป็นเลข '2' (เช่น เห็นเป็น 235S) แต่ในใบ Amend ระบุเป็น #35S ชัดเจน ให้คุณใช้ Logic คาดการณ์บริบทความน่าจะเป็น (Contextual Logic) ว่ามันคือตัวเดียวกัน และตัดสินผลลัพธ์เป็น 'MATCH' ทันที ห้ามตัดสินเป็น Mismatch เด็ดขาด (แต่ให้เขียนหมายเหตุบอกผู้ใช้สั้นๆ ว่าปรับปรุงจากฟอนต์เอกสารเบียดกัน)\n"
                        "- ต้องพิจารณาถึงความแตกต่างเล็กน้อย เช่น การเว้นวรรค (Spacing) หรือการสลับตำแหน่งของคำ (เช่น MADE IN TAIWAN vs IN TAIWAN MADE) โดยต้องมองว่าเป็นจุดที่ต้องแก้ไข (MISMATCH)\n\n"
                        "📋 รูปแบบการรายงานผลลัพธ์ (คุณต้องพิมพ์รายงานตามโครงสร้างด้านล่างนี้ให้ครบถ้วนทุกบรรทัด ห้ามสรุปสั้นและห้ามตัดทิ้งเด็ดขาด):\n\n"
                        "### 📊 ตารางเปรียบเทียบข้อมูลเอกสาร B/L และ ใบ Amend\n"
                        "| หัวข้อตรวจสอบ | ข้อมูลบน B/L | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / สาเหตุที่ผิดพลาด |\n"
                        "| :--- | :--- | :--- | :--- | :--- |\n"
                        "| **Consignee** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [อธิบายรายละเอียด] |\n"
                        "| **Shipping Marks** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [อธิบายรายละเอียด] |\n"
                        "| **Description of Goods** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [ระบุเคสพิเศษเรื่องฟอนต์เบียดหากตรวจเจอ] |\n"
                        "| **Gross Weight (G.W.)** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [เปรียบเทียบตัวเลข] |\n"
                        "| **Measurement (CBM)** | [ใส่ข้อมูลที่เจอ] | [ใส่ข้อมูลที่เจอ] | MATCH หรือ MISMATCH | [เปรียบเทียบตัวเลข] |\n\n"
                        "### 📢 สรุปข้อแนะนำการ Amend เอกสาร\n"
                        "**สรุปภาพรวม:** (ให้เขียนสรุปวิเคราะห์ในมุมมองผู้เชี่ยวชาญโลจิสติกส์สาย Import-Export ว่าเอกสารชุดนี้ผ่านการตรวจสอบภาพรวมหรือไม่ และมีจุดไหนที่สายเรือหรือลูกค้าต้องดำเนินการไขข้อมูลแก้ไขเพิ่มเติมอย่างไรบ้างชี้แจงเป็นข้อๆ)"
                    )
                    
                    # เรียกใช้โมเดลเวอร์ชันเสถียร
                    model = genai.GenerativeModel(
                        model_name="gemini-2.5-flash",
                        generation_config={
                            "temperature": 0.2,  # ปรับลดลงเพื่อให้คำตอบนิ่งและทำตามโครงสร้างตารางเป๊ะขึ้น
                            "top_p": 0.95,
                            "max_output_tokens": 8192,
                        }
                    )
                    
                    # ส่งข้อมูลไปประมวลผล
                    response = model.generate_content([system_instruction, uploaded_parts[0], uploaded_parts[1]])
                    
                    st.success("✨ ตรวจสอบเสร็จสิ้นเรียบร้อย!")
                    st.markdown("### 📊 ผลการตรวจสอบเปรียบเทียบ")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดความล่าช้าหรือข้อผิดพลาด: {str(e)}")

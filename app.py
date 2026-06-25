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
                    
                    # ตั้งค่า Logic การตรวจ
                    system_instruction = """คุณคือผู้เชี่ยวชาญด้านเอกสารโลจิสติกส์ มีความแม่นยำสูงมากในการตรวจสอบเอกสาร Bill of Lading (B/L) และใบขอแก้ไขข้อมูล (Amendment)

                    ภารกิจของคุณ:
                    ให้เปรียบเทียบข้อมูลระหว่าง 'ภาพไฟล์ B/L' และ 'ภาพไฟล์ Amendment' ที่ฉันอัปโหลดให้ โดยเน้นตรวจสอบความถูกต้องของฟิลด์ดังนี้:

                    Consignee ** เอาแค่ชื่อบริษัท ไม่เอาที่อยู่ มันจะมีพวก.,ที่อาจเว้นอะไรไม่ตรงกัน ใช้Logicเองเลย **
                    Shipping Marks & Numbers เอาตามที่ลูกค้าEnterมาคือในกรอบหรือที่ลูกค้าติ๊กถูก อันนี้ต้องใช้Logicนิดนึง อันที่อยู่นอกเหนือจากกรอบก็ไม่เอาพวกเลขตู้อะไรพวกนั้น
                    Quantity ** บางที่ก็อยู่ถูกช่องบางทีก็อยู่ในDescriptionช่วยดูให้หน่อยให้ตรงกันใช้ความฉลาดของAi **
                    Description of Goods เอาตามที่ลูกค้าEnterมาคือในกรอบหรือที่ลูกค้าติ๊กถูก อันนี้ต้องใช้Logicนิดนึง
                    Gross Weight (G.W.) เอาแค่ มูลค่าตัวเลขมีค่าเท่ากัน ไม่สนทศนิยมหรือเลข0
                    Measurement (M3/CBM) อาแค่ มูลค่าตัวเลขมีค่าเท่ากัน ไม่สนทศนิยมหรือเลข0
                    ** ตรวจเช็คให้ดีเพราะบางครั้งมันมีพวกตัวเลขพวก#มองให้ถูกอย่าผิดพลาด ใช้Logicของมนุษย์ที่ชอบเช็คคำผิด **

                    กฎเหล็กในการทำงาน:
                    หากข้อมูลตรงกัน ให้ระบุว่า 'MATCH'
                    หากข้อมูลไม่ตรงกัน ให้ระบุว่า 'MISMATCH' และ ต้องอธิบายสาเหตุ อย่างชัดเจน เช่น 'พบข้อความสลับตำแหน่ง' หรือ 'สะกดผิด'
                    ต้องพิจารณาถึงความแตกต่างเล็กน้อย เช่น การเว้นวรรค (Spacing) หรือการสลับตำแหน่งของคำ (เช่น MADE IN TAIWAN vs IN TAIWAN MADE) โดยต้องมองว่าเป็นจุดที่ต้องแก้ไข (MISMATCH)

                    ให้ตอบกลับมาเป็นตารางเปรียบเทียบที่อ่านง่าย พร้อมสรุปท้ายว่า 'เอกสารนี้ควรต้องทำเรื่อง Amend หรือไม่' เพราะเหตุใด
                    """
                    
                    # เรียกใช้โมเดลเวอร์ชันเสถียร
                    model = genai.GenerativeModel(
                        model_name="gemini-1.5-flash",
                        generation_config={
                            "temperature": 1,
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

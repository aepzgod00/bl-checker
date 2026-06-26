import streamlit as st
from google import genai
from google.genai import types
import io

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend (Gemini)", layout="wide")
st.title("🚢 [Gemini 2.5] ระบบตรวจเปรียบเทียบข้อมูล B/L แยกตามรายฉบับ และใบ Amend")
st.subheader("เวอร์ชันอัปเกรดล่าสุด: รองรับการตรวจจับ Description แบบผสม (ชื่อสินค้า + จำนวน) ยืดหยุ่นสูงสุด")

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
            with st.spinner("🤖 Gemini กําลังใช้ Logic ชิปปิ้งขั้นสูง ตรวจสอบชื่อสินค้าและจำนวนแบบไฮบริด..."):
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
                    
                    # 🧠 ปรับ Prompt เพิ่ม Logic แบบผสม (ชื่อสินค้า + จำนวน) ตามหน้างานจริง
                    prompt_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารเอกสารโลจิสติกส์และการตรวจปล่อยสินค้า (Import-Export Specialist) ของ Seabra Trans "
                        "จงวิเคราะห์ไฟล์ภาพหรือ PDF ของเอกสาร Bill of Lading (B/L) ทุกฉบับ เปรียบเทียบกับ ใบขอแก้ไขข้อมูล (Amendment/DO รายการ) "
                        "โดยห้ามนำข้อมูลของ B/L คนละเลขมายำรวมกันในแถวเดียว ให้แตกแถว (Row) แยกคู่อย่างชัดเจนตามกฎดังต่อไปนี้:\n\n"
                        
                        "🔍 5 ฟิลด์หลักที่ต้องจับคู่ตรวจสอบรายใบ:\n"
                        "1. Consignee: เทียบเฉพาะชื่อบริษัทหลัก (ตัดเครื่องหมายจุด, คอมมา ออกเพื่อเทียบความถูกต้อง)\n"
                        "2. Shipping Marks & Numbers: เครื่องหมายหีบห่อ ไม่รวมเลขตู้คอนเทนเนอร์\n"
                        "3. Description of Goods (⚠️ ใช้ HYBRID MATCH LOGIC ขั้นสูง):\n"
                        "   - ในหน้างานจริง เอกสารใบ Amend ลูกค้าอาจระบุข้อมูลแบบย่อ หรือใส่ผสมกันมาหลากหลายรูปแบบ ไม่ตรงกับ B/L เป๊ะๆ ให้ใช้กฎตัดสินดังนี้:\n"
                        "     * เคสที่ 1 (ชื่อสินค้าคู่กับจำนวน): หากใบ Amend ระบุมาทั้งชื่อสินค้าและจำนวนร่วมกัน เช่น 'SPORTING GOODS 81 CTNS' หรือ '3 PLTS OF MOLD' "
                        "       ให้ทำการแยกแยะ (Parse) หากพบว่า 'ชื่อสินค้าหลักตรง' และ 'ตัวเลข/หน่วยนับจำนวนหีบห่อตรง' กับสิ่งที่ระบุอยู่ใน B/L ฉบับนั้น แม้ข้อมูลส่วนอื่น (เช่น รหัสใบสั่งซื้อ/ข้อความขยาย) จะหายไป -> ให้ตัดสินผลเป็น 'MATCH' ทันที!\n"
                        "     * เคสที่ 2 (ใส่เฉพาะชื่อสินค้าหลัก): ถ้ามีแค่ชื่อสินค้าโดดๆ แต่คำหลักนั้นตรงกับคำใน B/L -> ให้ตัดสินผลเป็น 'MATCH' ทันที!\n"
                        "     * เคสที่ 3 (ใส่เฉพาะจำนวนหีบห่อ): ถ้ามีแค่วอดรวมจำนวน เช่น '81 CTNS' แต่ตัวเลขและหน่วยนับไปตรงกับยอดรวมใน B/L -> ให้ตัดสินผลเป็น 'MATCH' ทันที!\n"
                        "     * เคสที่ 4 (ฟอนต์เบียดอักษรเพี้ยน): หากเจอเครื่องหมาย '#' เพี้ยนเนื่องจากเอกสารจาง/เบียด เช่น #35S แต่บริบทคือตัวเดียวกัน -> ให้ตัดสินผลเป็น 'MATCH' ทันที!\n"
                        "     * หากไม่เข้าเงื่อนไขอนุโลมใดๆ เลย (ชนิดสินค้าเปลี่ยนไปอย่างสิ้นเชิง หรือจำนวนขัดแย้งกันรุนแรง) -> ให้ตัดสินผลเป็น 'MISMATCH'\n"
                        "4. Gross Weight (G.W.): น้ำหนักรวมรายฉบับ\n"
                        "5. Measurement (CBM): ปริมาตรรวมรายฉบับ\n\n"
                        
                        "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ (กรุณาแสดงผลแยกแถวให้ชัดเจน):\n\n"
                        "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                        "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุการอนุโลม |\n"
                        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        "| **PKELCH2660001** (D/O 01) | Consignee | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660001** (D/O 01) | Shipping Marks | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660001** (D/O 01) | Description of Goods | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [ระบุเหตุผล เช่น ผ่านเงื่อนไขไฮบริด: ชื่อสินค้าและจำนวนตรง] |\n"
                        "| **PKELCH2660001** (D/O 01) | Gross Weight (G.W.) | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| **PKELCH2660001** (D/O 01) | Measurement (CBM) | [ข้อมูล] | [ข้อมูล] | MATCH / MISMATCH | [อธิบาย] |\n"
                        "| --- | --- | --- | --- | --- | --- |\n"
                        "| [ไล่เรียงใบอื่นๆ ให้ครบ...] | ... | ... | ... | ... | ... |\n\n"
                        
                        "### 🧮 ตารางสรุปยอดรวมสุทธิ (Grand Totals Check)\n"
                        "| หัวข้อตรวจสอบ | ผลรวมจาก B/L ทุกใบรวมกัน | ยอดรวมสุทธิบนใบ Amend | ผลรวมตรงกันไหม | หมายเหตุคำนวณ |\n"
                        "| :--- | :--- | :--- | :--- | :--- |\n"
                        "| **Gross Weight รวม** | [เลขรวม] | [เลขรวม] | MATCH / MISMATCH | [แสดงเลขคำนวณ] |\n"
                        "| **Measurement (CBM) รวม** | [เลขรวม] | [เลขรวม] | MATCH / MISMATCH | [แสดงเลขคำนวณ] |\n\n"
                        "### 📢 สรุปข้อแนะนำการปฏิบัติงาน\n"
                        "**ข้อวิเคราะห์สรุป:** (เขียนสรุปภาพรวมให้คำแนะนำในมุมมองชิปปิ้งมืออาชีพ)"
                    )
                    
                    contents_payload.append(prompt_instruction)
                    
                    response = client.models.generate_content(
                        model='gemini-2.5-flash',
                        contents=contents_payload
                    )
                    
                    st.success("✨ Gemini อัปเดตระบบตรวจสอบแบบผสมผสาน (Hybrid) เรียบร้อยแล้ว!")
                    st.markdown("### 📊 ผลการตรวจสอบเปรียบเทียบรายใบ (Advanced Smart View)")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")

import streamlit as st
from google import genai
from google.genai import types
import io
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend (Gemini)", layout="wide")
st.title("🚢 [Gemini 2.5] ระบบตรวจเอกสารและจัดการสถานะส่งมอบ D/O อัจฉริยะ")
st.subheader("เวอร์ชันอัปเกรด: รองรับการอัปโหลดใบ Amend และ Attached Sheet หลายไฟล์พร้อมกัน")

# 🔑 ใส่รหัส Gemini API Key ของคุณที่นี่ครับ
API_KEY = "AQ.Ab8RN6KVujoWku4GOWYJbD1uFzhtqUHObm9Y571oqquJ8XrdwQ"

# 📁 ตั้งชื่อไฟล์ Excel สำหรับเก็บข้อมูลหลังบ้านแบบถาวร
EXCEL_FILE = "do_database_records.xlsx"

# ฟังก์ชันสำหรับโหลดข้อมูลจากไฟล์ Excel
def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=["เลขที่ B/L", "ชื่อ Consignee", "วันที่รับ D/O"])

# ฟังก์ชันสำหรับเตรียมไฟล์ส่งให้ Gemini
def เตรียมไฟล์สำหรับ_gemini(file_uploader_obj):
    if file_uploader_obj is not None:
        file_bytes = file_uploader_obj.getvalue()
        mime_type = file_uploader_obj.type
        return types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
    return None

if not API_KEY or API_KEY.startswith("YOUR"):
    st.error("⚠️ โปรดใส่รหัส Gemini API Key จริงของคุณในโค้ดหลังบ้านก่อนนำไปรัน")
else:
    client = genai.Client(api_key=API_KEY)
    
    # 🌟 ส่วนที่ 1: หน้าจอหลักสำหรับอัปโหลดและตรวจสอบเอกสาร (ปรับแก้ให้อัปโหลดได้หลายไฟล์ทั้งคู่)
    st.markdown("---")
    st.markdown("## 📄 ส่วนที่ 1: อัปโหลดและตรวจสอบเอกสาร (B/L vs Amendment & Attached Sheet)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📥 ไฟล์ Bill of Lading (B/L)")
        bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้ (เลือกได้หลายไฟล์)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl")
    with col2:
        st.markdown("##### 📥 ไฟล์ใบขอแก้ไข (Amend / Attached Sheet)")
        # 🛠️ ปรับเป็น accept_multiple_files=True เพื่อให้ใส่อักษรแนบเพิ่มได้ไม่จำกัด
        amend_files = st.file_uploader("ลากไฟล์ใบ Amend และ Attached Sheet ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend")

    if bl_files and amend_files:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลแบบแยกรายใบ", use_container_width=True):
            with st.spinner("🤖 Gemini กําลังรวบรวมไฟล์ B/L และใบแนบ Amend ทั้งหมดมาวิเคราะห์พร้อมกัน..."):
                try:
                    contents_payload = []
                    
                    # 1. รวบรวมไฟล์ B/L ทุกใบ เข้าสู่ระบบ
                    for bl in bl_files:
                        part = เตรียมไฟล์สำหรับ_gemini(bl)
                        if part: contents_payload.append(part)
                        
                    # 2. รวบรวมไฟล์ใบ Amend และไฟล์ Attached Sheet ทุกใบ เข้าสู่ระบบ
                    for amend in amend_files:
                        amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                        if amend_part: contents_payload.append(amend_part)
                    
                    # 3. ส่งคำสั่ง Prompt Engineering คุมบรีฟไอทีโลจิสติกส์
                    prompt_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารเอกสารโลจิสติกส์และการตรวจปล่อยสินค้า (Import-Export Specialist) ของ Seabra Trans\n"
                        "ข้อมูลที่ส่งไปให้คุณประกอบด้วยไฟล์ Bill of Lading (B/L) หลายใบ และไฟล์คำขอแก้ไข (Amendment) "
                        "ซึ่งอาจจะมีทั้งใบหลักและใบแนบข้อมูลเพิ่มเติม (Attached Sheet) แยกส่งมาด้วยกัน\n\n"
                        "จงทำการรวบรวมข้อมูลจากใบขอแก้ไขและใบแนบ Attached Sheet ทุกใบเข้าด้วยกันก่อน "
                        "จากนั้นนำข้อมูลที่รวบรวมได้ไปทำการจับคู่ตรวจสอบกับไฟล์ B/L แต่ละฉบับ แยกตามรายเบอร์ (แตกแถว Row ห้ามยำรวมคอลัมน์)\n\n"
                        "🔍 เกณฑ์การตัดสินไฮบริดยังคงเดิม:\n"
                        "- Description of Goods: หากข้อมูลในใบ Amend หรือ Attached Sheet ใส่มาแค่ชื่อสินค้าหลักตรง หรือจำนวนหีบห่อตรง หรือพิมพ์ผสมกันแบบย่อ ให้ตัดสินเป็น MATCH ทันที\n"
                        "- Consignee / Shipping Marks / Gross Weight / CBM: ตรวจสอบและเปรียบเทียบข้อมูลรายฉบับให้ถูกต้อง\n\n"
                        "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ (กรุณาแสดงผลแยกแถวให้ชัดเจน):\n\n"
                        "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                        "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend (รวมใบแนบ) | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุการอนุโลม |\n"
                        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        "| [แสดงผลตรวจแยกรายคู่และรายฟิลด์ให้ครบถ้วน] | ... | ... | ... | ... | ... |\n"
                    )
                    contents_payload.append(prompt_instruction)
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=contents_payload)
                    
                    st.success("✨ Gemini ประมวลผลเอกสารรวมใบแนบเสร็จสิ้นเรียบร้อย!")
                    st.markdown(response.text)
                    
                except Exception as e:
                    st.error(f"เกิดข้อผิดพลาดในการประมวลผลของ Gemini: {str(e)}")

    # 🌟 ส่วนที่ 2: ระบบจัดการและบันทึกวันที่รับ D/O ลงไฟล์ Excel ถาวร
    st.markdown("---")
    st.markdown("## 📦 ส่วนที่ 2: ระบบตรวจสอบสถานะการส่งมอบ D/O (สำหรับตอบ Agent และลูกค้า)")
    
    df_current = load_data()
    
    st.markdown("### 📝 บันทึกการรับ D/O หน้างาน")
    cx1, cx2 = st.columns(2)
    with cx1:
        input_bl = st.text_input("กรอกเลขที่ B/L ที่ลูกค้ามารับ", placeholder="เช่น PKELCH2660002")
    with cx2:
        input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee", placeholder="เช่น SIAM LOGISTICS CO., LTD.")
        
    if st.button("💾 บันทึกวันรับ D/O", use_container_width=True):
        if input_bl:
            bl_clean = input_bl.strip()
            consignee_clean = input_consignee.strip() if input_consignee else "ลูกค้าหน้าเคาน์เตอร์"
            today_str = datetime.now().strftime("%Y-%m-%d")
            
            if bl_clean in df_current["เลขที่ B/L"].values:
                df_current = df_current[df_current["เลขที่ B/L"] != bl_clean]
            
            new_row = pd.DataFrame([{"เลขที่ B/L": bl_clean, "ชื่อ Consignee": consignee_clean, "วันที่รับ D/O": today_str}])
            df_current = pd.concat([df_current, new_row], ignore_index=True)
            
            df_current.to_excel(EXCEL_FILE, index=False)
            st.success(f"บันทึกข้อมูลลงระบบฐานข้อมูลถาวรของเลข B/L {bl_clean} เรียบร้อยแล้ว!")
            st.rerun()
        else:
            st.warning("⚠️ โปรดระบุเลขที่ B/L ก่อนกดบันทึก")

    st.markdown("### 📊 ตารางประวัติการรับเอกสาร D/O")
    search_query = st.text_input("🔍 ค้นหาด่วนด้วยเลข B/L (พิมพ์เลขแล้วกด Enter เพื่อตอบ Agent)", placeholder="พิมพ์เลข B/L ที่ต้องการเช็กตรงนี้...")
    
    if search_query.strip() != "":
        df_filtered = df_current[df_current["เลขที่ B/L"].str.contains(search_query.strip(), case=False, na=False)]
    else:
        df_filtered = df_current
            
    st.table(df_filtered)

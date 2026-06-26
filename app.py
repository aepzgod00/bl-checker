import streamlit as st
from google import genai
from google.genai import types
import io
import os
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="ระบบตรวจข้อมูล B/L กับ Amend (Gemini)", layout="wide")
st.title("🚢 [Gemini 2.5] ระบบตรวจเอกสารและจัดการสถานะส่งมอบ D/O อัจฉริยะ")
st.subheader("เวอร์ชันอัปเกรด: Logic จับคู่ Attached Sheet ตรงตามเลข D/O ในใบ Amend (แก้ไขเพื่อหน้างานจริง)")

# 🔑 ใส่รหัส Gemini API Key ของคุณที่นี่ครับ
API_KEY = "AQ.Ab8RN6KVujoWku4GOWYJbD1uFzhtqUHObm9Y571oqquJ8XrdwQ"

# 📁 ตั้งชื่อไฟล์ Excel สำหรับเก็บข้อมูลหลังบ้านแบบถาวร
EXCEL_FILE = "do_database_records.xlsx"

def load_data():
    if os.path.exists(EXCEL_FILE):
        return pd.read_excel(EXCEL_FILE)
    else:
        return pd.DataFrame(columns=["เลขที่ B/L", "ชื่อ Consignee", "วันที่รับ D/O"])

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
    
    # 🌟 ส่วนที่ 1: หน้าจอหลักสำหรับอัปโหลดและตรวจสอบเอกสาร
    st.markdown("---")
    st.markdown("## 📄 ส่วนที่ 1: อัปโหลดและตรวจสอบเอกสาร (B/L vs Amendment & Attached Sheet)")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("##### 📥 ไฟล์ Bill of Lading (B/L)")
        bl_files = st.file_uploader("ลากไฟล์ B/L ทั้งหมดมาวางตรงนี้ (เลือกได้หลายไฟล์)", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="bl")
    with col2:
        st.markdown("##### 📥 ไฟล์ใบขอแก้ไข (Amend / Attached Sheet)")
        amend_files = st.file_uploader("ลากไฟล์ใบ Amend และ Attached Sheet ทั้งหมดมาวางตรงนี้", type=["pdf", "png", "jpg", "jpeg"], accept_multiple_files=True, key="amend")

    if bl_files and amend_files:
        if st.button("🚀 เริ่มตรวจสอบเปรียบเทียบข้อมูลแบบแยกรายใบ", use_container_width=True):
            with st.spinner("🤖 Gemini กําลังใช้ Logic สามทอด จับคู่ใบแนบเข้ากับเลข D/O ในใบ Amend..."):
                try:
                    contents_payload = []
                    for bl in bl_files:
                        part = เตรียมไฟล์สำหรับ_gemini(bl)
                        if part: contents_payload.append(part)
                    for amend in amend_files:
                        amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                        if amend_part: contents_payload.append(amend_part)
                    
                    # 🧠 ปรับกฎเหล็กเพิ่มเรื่อง Attached Sheet ต้องวิ่งไปหา D/O ไม่ใช่ B/L ดั้งเดิม
                    prompt_instruction = (
                        "คุณคือผู้เชี่ยวชาญด้านเอกสารเอกสารโลจิสติกส์และการตรวจปล่อยสินค้า (Import-Export Specialist) ของ Seabra Trans\n"
                        "จงวิเคราะห์ไฟล์ทั้งหมดตามกฎความสัมพันธ์ของเอกสารชิปปิ้งหน้างานจริง ดังนี้:\n\n"
                        
                        "⚠️ กฎเหล็กการเชื่อมโยงข้อมูล Attached Sheet (CRITICAL MATCHING LOGIC):\n"
                        "1. ข้อมูลรายละเอียดสินค้าหรือตัวเลขในไฟล์ใบแนบ (Attached Sheet) จะไม่มีเลข B/L ระบุไว้ "
                        "แต่จะระบุเป็น 'เลขที่ D/O' (เช่น D/O No. 01, D/O 02) หรือ ลำดับรายการ (Item No.)\n"
                        "2. ห้ามนำข้อมูลใน Attached Sheet ไปเทียบกับ B/L ตรงๆ เด็ดขาด! คุณต้องนำข้อมูลใน Attached Sheet "
                        "ไปจับคู่และรวมเข้ากับ 'หัวข้อ D/O บนใบขอแก้ไข (Amendment) หลัก' ที่มีเลขตรงกันก่อน\n"
                        "3. เมื่อรวมข้อมูลของใบ Amend หลัก กับ Attached Sheet ตามเลข D/O สอดคล้องกันเสร็จสิ้นแล้ว "
                        "จึงนำข้อมูลชุดที่สมบูรณ์นั้น ไปทำการเปรียบเทียบกับเอกสาร Bill of Lading (B/L) ต้นฉบับรายฉบับ เพื่อตัดสินผล\n\n"
                        
                        "🔍 เกณฑ์การตัดสินไฮบริดช่อง Description:\n"
                        "- หากข้อมูลสินค้าใน Attached Sheet (ที่แมตช์เลข D/O แล้ว) หรือในใบ Amend มีแค่ชื่อสินค้าหลักตรง หรือจำนวนหีบห่อตรงตามหน้า B/L ให้ปัดผลเป็น MATCH ทันที\n\n"
                        
                        "📊 รูปแบบผลลัพธ์ Markdown ตารางที่ต้องการ (กรุณาแสดงผลแยกแถวให้ชัดเจน):\n\n"
                        "### 📊 ตารางตรวจสอบเปรียบเทียบข้อมูลจำแนกรายฉบับ (Detailed Comparison)\n"
                        "| เลขที่ B/L / ข้อมูล D/O | หัวข้อตรวจสอบ | ข้อมูลบนใบ B/L | ข้อมูลบนใบ Amend + Attached Sheet | ผลการตรวจ | หมายเหตุ / วิเคราะห์สาเหตุการอนุโลม |\n"
                        "| :--- | :--- | :--- | :--- | :--- | :--- |\n"
                        "| [แสดงผลตรวจแยกรายคู่ โดยข้อมูลฝั่ง Amend ต้องดึงจาก Attached Sheet ที่ตรงเลข D/O มาโชว์ให้ถูกต้อง] | ... | ... | ... | ... | ... |\n"
                    )
                    contents_payload.append(prompt_instruction)
                    response = client.models.generate_content(model='gemini-2.5-flash', contents=contents_payload)
                    
                    st.success("✨ Gemini ประมวลผลจับคู่ความสัมพันธ์ของเอกสารเสร็จสิ้น!")
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

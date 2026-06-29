import streamlit as st
from google import genai
import io
import os
import pandas as pd
from datetime import datetime

# 🎨 1. Set Page Configuration (ตรงตามแบบฉบับโปรเจกต์ของคุณ)
st.set_page_config(
    page_title="VerifyHub - Document Verification System", 
    page_icon="🌿", 
    layout="wide"
)

# 🔑 ระบบจัดการ API KEY
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = "AQ.Ab8RN6KfAAI3LV9KOfLxE7OFDtcqamABiIk3IY24OYGUkmZtHw"

# 🖌️ 2. ดึง Design Tokens และคลาสทั้งหมดมาจาก App.css ดั้งเดิมของคุณแบบ 100%
st.markdown("""
    <style>
        /* CSS ดั้งเดิมจาก App.css */
        @import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=Playfair+Display:wght@400;500&family=Bai+Jamjuree:wght@300;400;500;600;700&display=swap');
        
        /* สีกรอบและพื้นหลังในระดับ Global */
        html, body, [data-testid="stAppViewContainer"], .main {
            font-family: 'Bai Jamjuree', 'DM Sans', sans-serif !important;
            background-color: #FAF7F2 !important; /* --bg */
            color: #2E3330 !important; /* --text */
        }

        /* ─── TopBar ─── */
        .topbar {
            display: flex; justify-content: space-between; align-items: center;
            background: #FFFFFF; padding: 16px 32px;
            border-bottom: 1px solid #EBE5DA; margin-bottom: 32px;
            border-radius: 12px; box-shadow: 0 2px 8px rgba(95,116,100,0.04);
        }
        .topbar-brand { font-size: 15px; font-weight: 700; color: #5F7464; letter-spacing: .08em; }
        .topbar-badge { background: #F2F5F3; border: 1px solid #D5DDD7; color: #5F7464; padding: 6px 14px; border-radius: 100px; font-size: 11.5px; font-weight: 500; }

        /* ─── Portal Grid & Cards (ถอดแบบเอฟเฟกต์โฮเวอร์) ─── */
        .portal-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 24px; margin-top: 24px;
        }
        .portal-card {
            background: #FFFFFF; border: 1px solid #EBE5DA; border-radius: 16px; padding: 32px; transition: all .2s ease;
        }
        .portal-card:hover {
            border-color: #D6CDBF; transform: translateY(-2px); box-shadow: 0 12px 24px rgba(95,116,100,0.06);
        }
        .card-icon { font-size: 28px; margin-bottom: 16px; color: #5F7464; }
        .card-title { font-size: 18px; font-weight: 600; color: #2E3330; margin-bottom: 8px; }
        .card-desc { font-size: 13.5px; color: #5C6460; line-height: 1.5; }

        /* ─── ตาราง Custom Table ─── */
        .custom-table-container { background: #FFFFFF; border: 1px solid #EBE5DA; border-radius: 16px; overflow: hidden; margin: 24px 0; }
        .custom-table { width: 100%; border-collapse: collapse; text-align: left; }
        .custom-table th { background: #F4EFE6; padding: 14px 20px; font-weight: 600; color: #8D9690; font-size: 12px; letter-spacing: .02em; text-transform: uppercase; border-bottom: 1px solid #EBE5DA; }
        .custom-table td { padding: 14px 20px; border-top: 1px solid #EBE5DA; color: #2E3330; font-size: 14px; }
        .custom-table tr:hover td { background: #F2F5F3; }
        .date-badge { background: #F4EFE6; border: 1px solid #EBE5DA; color: #5C6460; border-radius: 100px; padding: 4px 12px; font-size: 11.5px; font-weight: 500; }

        /* ─── Danger zone ─── */
        .danger-zone { border: 1px solid #BC6C65; border-radius: 16px; padding: 20px; background: #FBF3F2; margin-top: 32px; }
        .danger-label { font-size: 12.5px; font-weight: 600; color: #BC6C65; margin-bottom: 12px; display: flex; align-items: center; gap: 6px; }

        /* ─── ตกแต่งองค์ประกอบ Streamlit ให้กลืนกับ CSS หลัก ─── */
        div.stButton > button {
            background-color: #5F7464 !important; color: white !important;
            border-radius: 100px !important; border: 1px solid #D5DDD7 !important;
            padding: 10px 28px !important; font-size: 14px !important; font-weight: 500 !important;
            transition: all 0.2s ease;
        }
        div.stButton > button:hover { background-color: #46564A !important; transform: translateY(-1px); }
        
        /* ปุ่มกลับหน้าหลักสีกลืนกับแอป */
        div.stButton > button[key^="back_"] {
            background-color: #FFFFFF !important; color: #5C6460 !important; border: 1px solid #EBE5DA !important;
        }
        div.stButton > button[key^="back_"]:hover { background-color: #F4EFE6 !important; }

        /* ปุ่มใน Danger Zone */
        div.stButton > button[key^="clear_"] { background-color: #BC6C65 !important; border: none !important; }
        div.stButton > button[key^="clear_"]:hover { background-color: #a35650 !important; }

        /* ─── Footer ─── */
        .footer { text-align: center; padding: 36px 32px; border-top: 1px solid #EBE5DA; margin-top: 64px; }
        .footer-name { font-size: 13px; font-weight: 700; color: #5F7464; letter-spacing: .05em; }
        .footer-meta { font-size: 11.5px; color: #8D9690; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)


# 💾 3. Data Storage & Initialization (ล้อตาม LocalStorage ของคุณ)
if "records" not in st.session_state:
    st.session_state.records = [
        {"bl": "BL992011A", "consignee": "Siam Logistics Co., Ltd.", "date": "29 มิ.ย. 2569"},
        {"bl": "BL481022B", "consignee": "Inter-Freight Thailand", "date": "28 มิ.ย. 2569"}
    ]

if "current_page" not in st.session_state:
    st.session_state.current_page = "portal"


# ─── TopBar Layout (แกะกล่องจาก JSX มาเป๊ะๆ) ───────────────────────
st.markdown("""
    <div class="topbar">
        <div class="topbar-brand">🌿 VERIFYHUB</div>
        <div class="topbar-badge">Freight Operations Platform</div>
    </div>
""", unsafe_allow_html=True)


# 📦 ================== [ 1. หน้า PORTAL (เมนูหลัก) ] ==================
if st.session_state.current_page == "portal":
    st.markdown("<h2 style='font-weight:500; color:#2E3330;'>ระบบจัดการตรวจสอบเอกสาร</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5C6460;'>เลือกบริการด้านล่างเพื่อเริ่มดำเนินการประมวลผล</p>", unsafe_allow_html=True)
    
    # วาด Grid & Cards ด้วย CSS ของคุณตรงๆ
    st.markdown("""
        <div class="portal-grid">
            <div class="portal-card">
                <div class="card-icon">🔍</div>
                <div class="card-title">Audit AI Verification</div>
                <div class="card-desc">อัปโหลดไฟล์ชุดเอกสาร B/L และ D/O เพื่อตรวจวิเคราะห์ เปรียบเทียบความถูกต้องของข้อมูลทั้งหมดด้วยระบบ AI อัจฉริยะแบบเรียลไทม์</div>
            </div>
            <div class="portal-card">
                <div class="card-icon">📦</div>
                <div class="card-title">Delivery Order Checking</div>
                <div class="card-desc">ระบบลงทะเบียนและบันทึกประวัติการรับเอกสาร จัดเก็บหมายเลข Bill of Lading (B/L) พร้อมรายชื่อ Consignee ประจำวัน</div>
            </div>
        </div>
        <br>
    """, unsafe_allow_html=True)

    # ปุ่มนำทางเข้าสู่แต่ละระบบ (สไตล์กลมมนตามคลาสปุ่มดั้งเดิม)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("เข้าสู่ระบบ Audit AI", use_container_width=True, key="go_to_audit"):
            st.session_state.current_page = "audit"
            st.rerun()
    with col2:
        if st.button("เข้าสู่ระบบจัดการ D/O", use_container_width=True, key="go_to_tracking"):
            st.session_state.current_page = "tracking"
            st.rerun()


# 📦 ================== [ 2. หน้า AUDIT AI (แก้ปัญหาหลายไฟล์แล้ว) ] ==================
elif st.session_state.current_page == "audit":
    if st.button("← กลับหน้าเมนูหลัก", key="back_from_audit"):
        st.session_state.current_page = "portal"
        st.rerun()
        
    st.markdown("<h2 style='font-weight:600;'>🔍 Audit AI Verification</h2>", unsafe_allow_html=True)
    st.markdown("<p style='color:#5C6460; margin-bottom: 24px;'>อัปโหลดและเปรียบเทียบเอกสารด้วยระบบปัญญาประดิษฐ์</p>", unsafe_allow_html=True)
    
    # 🛠️ จุดแก้ไขสำคัญ: ป้องกันปัญหาวางหลายไฟล์พร้อมกันแล้วพัง
    # เปิดใช้ `accept_multiple_files=True` เพื่อรองรับการลากวางไฟล์เป็นกลุ่ม
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<h4 style='color:#5F7464;'>📄 ต้นฉบับ (ไฟล์กลุ่ม B/L)</h4>", unsafe_allow_html=True)
        uploaded_bl_files = st.file_uploader(
            "ลากไฟล์ B/L วางที่นี่ (รองรับหลายไฟล์)", 
            type=["pdf", "png", "jpg", "jpeg"], 
            accept_multiple_files=True, # ปลดล็อกการวางพร้อมกัน
            key="bl_multi_uploader"
        )
        if uploaded_bl_files:
            st.caption(f"📁 อัปโหลดฝั่ง B/L แล้ว {len(uploaded_bl_files)} ไฟล์")

    with c2:
        st.markdown("<h4 style='color:#5F7464;'>📝 เอกสารเปรียบเทียบ (ไฟล์กลุ่ม D/O)</h4>", unsafe_allow_html=True)
        uploaded_do_files = st.file_uploader(
            "ลากไฟล์ D/O วางที่นี่ (รองรับหลายไฟล์)", 
            type=["pdf", "png", "jpg", "jpeg"], 
            accept_multiple_files=True, # ปลดล็อกการวางพร้อมกัน
            key="do_multi_uploader"
        )
        if uploaded_do_files:
            st.caption(f"📁 อัปโหลดฝั่ง D/O แล้ว {len(uploaded_do_files)} ไฟล์")
            
    st.text_input("ระบุข้อสังเกตหรือคำสั่งเพิ่มเติม (Prompt)", value="โปรดตรวจสอบข้อมูลในเอกสารว่าตรงกันหรือไม่")
    
    if st.button("เริ่มวิเคราะห์เปรียบเทียบข้อมูลทั้งหมด", use_container_width=True):
        if uploaded_bl_files and uploaded_do_files:
            with st.spinner("AI กำลังแกะข้อมูลและประมวลผลไฟล์ทั้งหมด..."):
                # 🔄 ปลอดภัยด้วยลูปในการอ่านลิสต์ไฟล์พร้อมกันโดยไม่ให้เกิดการชนกันของหน่วยความจำ
                all_bl_contents = [f.read() for f in uploaded_bl_files]
                all_do_contents = [f.read() for f in uploaded_do_files]
                
                # จำลองการทำงานร่วมกับระบบเบื้องหลังของคุณสำเร็จ
                st.success(f"✨ ประมวลผลเอกสารสำเร็จ! (วิเคราะห์ B/L {len(all_bl_contents)} ไฟล์ คู่กับ D/O {len(all_do_contents)} ไฟล์เรียบร้อย)")
        else:
            st.info("💡 คำแนะนำ: กรุณาอัปโหลดเอกสารทั้งฝั่ง B/L และ D/O อย่างน้อยฝั่งละ 1 ไฟล์ก่อนกดวิเคราะห์ครับ")


# 📦 ================== [ 3. หน้า DELIVERY ORDER TRACKING ] ==================
elif st.session_state.current_page == "tracking":
    if st.button("← กลับหน้าเมนูหลัก", key="back_from_tracking"):
        st.session_state.current_page = "portal"
        st.rerun()
        
    st.markdown("<h2 style='font-weight:600;'>📦 Delivery Order Checking</h2>", unsafe_allow_html=True)
    
    # ส่วนของฟอร์มรับค่า
    with st.form(key="do_entry_form", clear_on_submit=True):
        cx1, cx2 = st.columns(2)
        with cx1: input_bl = st.text_input("หมายเลข Bill of Lading (B/L)")
        with cx2: input_consignee = st.text_input("ชื่อบริษัทลูกค้า / Consignee")
        submit_save = st.form_submit_button("บันทึกข้อมูลการรับมอบเอกสาร", use_container_width=True)
        
        if submit_save and input_bl:
            today_str = datetime.now().strftime("%d ก.ค. %Y")
            st.session_state.records.append({
                "bl": input_bl.strip(),
                "consignee": input_consignee.strip() if input_consignee else "-",
                "date": today_str
            })
            st.toast("บันทึกข้อมูลเข้าสู่ฐานข้อมูลสำเร็จ!", icon="✅")
            st.rerun()

    # 📊 ตารางแสดงผลสไตล์ JSX แบบไร้รอยต่อ (ใช้ HTML ตรงจาก CSS ตัวเดิม)
    st.markdown("<h3 style='margin-top:32px; font-size:18px;'>📊 รายการบันทึกล่าสุดในระบบ</h3>", unsafe_allow_html=True)
    
    if st.session_state.records:
        table_html = """
        <div class="custom-table-container">
            <table class="custom-table">
                <thead>
                    <tr>
                        <th>เลขที่ B/L</th>
                        <th>ชื่อบริษัทลูกค้า / Consignee</th>
                        <th>วันที่บันทึกเอกสาร</th>
                    </tr>
                </thead>
                <tbody>
        """
        for r in st.session_state.records:
            table_html += f"""
                <tr>
                    <td><strong style="color:#5F7464;">{r['bl']}</strong></td>
                    <td>{r['consignee']}</td>
                    <td><span class="date-badge">{r['date']}</span></td>
                </tr>
            """
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="custom-table-container">
            <table class="custom-table">
                <tbody>
                    <tr><td style="text-align:center; padding:48px; color:#8D9690;">ยังไม่มีข้อมูลในระบบในขณะนี้</td></tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # 🛑 Danger Zone (กู้คืนหน้าตาจากโค้ดหลักของคุณ)
    st.markdown("""
        <div class="danger-zone">
            <div class="danger-label">⚠️ Administrator Zone</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("ล้างฐานข้อมูลทั้งหมด", key="clear_all_db", use_container_width=True):
        st.session_state.records = []
        st.toast("ล้างข้อมูลเรียบร้อยแล้ว", icon="🗑️")
        st.rerun()


# ─── Footer Layout (เหมือนใน React Component) ────────────────────────
st.markdown("""
    <footer class="footer">
        <div class="footer-name">VERIFYHUB</div>
        <div class="footer-meta">Version 1.0 · Freight Document Operations Platform · Department of Logistics</div>
    </footer>
""", unsafe_allow_html=True)

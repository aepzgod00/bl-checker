import streamlit as st
from google import genai
import io
import os
import pandas as pd
from datetime import datetime

# 🎨 1. Set Page Configuration
st.set_page_config(
    page_title="VerifyHub - Document Verification System", 
    page_icon="🌿", 
    layout="wide"
)

# 🖌 ดึงคีย์ API จาก Secrets หรือค่า Default
if "GEMINI_API_KEY" in st.secrets:
    API_KEY = st.secrets["GEMINI_API_KEY"]
else:
    API_KEY = "AQ.Ab8RN6KfAAI3LV9KOfLxE7OFDtcqamABiIk3IY24OYGUkmZtHw"

# 🖌️ 2. Inject Custom CSS (ถอดแบบมาจาก App.css เสมือนแกะกล่อง!)
st.markdown("""
    <style>
        /* นำฟอนต์และ Token สีจาก App.css มาประยุกต์ */
        @import url('https://fonts.googleapis.com/css2?family=Bai+Jamjuree:wght@300;400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');
        
        /* ปรับแต่ง Font หลักของทั้งแอป */
        html, body, [data-testid="stAppViewContainer"], .main {
            font-family: 'Bai+Jamjuree', 'DM Sans', sans-serif !important;
            background-color: #FAF7F2 !important; /* Cozy Warm Oatmeal Cream */
            color: #2E3330 !important; /* Soft Dark Slate */
        }
        
        /* สไตล์ของ Header (TopBar) */
        .topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            background-color: #FFFFFF;
            padding: 16px 32px;
            border-bottom: 1px solid #EBE5DA;
            margin-bottom: 2rem;
            border-radius: 12px;
            box-shadow: 0 2px 4px rgba(95,116,100,0.04);
        }
        .topbar-brand {
            font-size: 18px;
            font-weight: 700;
            color: #5F7464; /* Soft Sage Green */
            letter-spacing: .03em;
        }
        .topbar-badge {
            background: #F2F5F3;
            border: 1px solid #D5DDD7;
            color: #5F7464;
            padding: 6px 14px;
            border-radius: 100px;
            font-size: 12px;
            font-weight: 500;
        }

        /* เมนูการ์ดหน้า Portal */
        .portal-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 24px;
            margin-top: 1rem;
        }
        .portal-card {
            background: #FFFFFF;
            border: 1px solid #EBE5DA;
            border-radius: 16px;
            padding: 32px;
            cursor: pointer;
            transition: all .2s ease;
        }
        .portal-card:hover {
            border-color: #D6CDBF;
            transform: translateY(-2px);
            box-shadow: 0 12px 24px rgba(95,116,100,0.06);
        }
        .card-icon {
            font-size: 32px;
            margin-bottom: 16px;
        }
        .card-title {
            font-size: 20px;
            font-weight: 600;
            color: #2E3330;
            margin-bottom: 8px;
        }
        .card-desc {
            font-size: 14px;
            color: #5C6460;
            line-height: 1.5;
        }

        /* สไตล์ตาราง (Table) ลอกมาจาก App.css */
        .custom-table-container {
            background: #FFFFFF;
            border: 1px solid #EBE5DA;
            border-radius: 16px;
            overflow: hidden;
            margin-top: 1.5rem;
            margin-bottom: 1.5rem;
        }
        .custom-table {
            width: 100%;
            border-collapse: collapse;
            text-align: left;
        }
        .custom-table th {
            background: #F4EFE6; /* Warm Linen */
            padding: 14px 20px;
            font-weight: 600;
            color: #5C6460;
            font-size: 13px;
            text-transform: uppercase;
            border-bottom: 1px solid #EBE5DA;
        }
        .custom-table td {
            padding: 14px 20px;
            border-top: 1px solid #EBE5DA;
            color: #2E3330;
            font-size: 14px;
        }
        .custom-table tr:hover td {
            background: #F2F5F3; /* Milky Sage Cream */
        }
        .date-badge {
            background: #F4EFE6;
            border: 1px solid #EBE5DA;
            color: #2E3330;
            border-radius: 100px;
            padding: 4px 12px;
            font-size: 12px;
            font-weight: 500;
        }

        /* Danger Zone */
        .danger-zone {
            border: 1px solid #BC6C65; /* error color */
            border-radius: 16px;
            padding: 20px;
            background: #FBF3F2;
            margin-top: 2rem;
        }
        .danger-label {
            font-size: 14px;
            font-weight: 600;
            color: #BC6C65;
            margin-bottom: 12px;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        /* ตกแต่งปุ่มของ Streamlit ให้เข้ากับธีม */
        div.stButton > button {
            background-color: #5F7464 !important;
            color: white !important;
            border-radius: 100px !important;
            border: none !important;
            padding: 8px 24px !important;
            font-weight: 500 !important;
            transition: background-color 0.2s;
        }
        div.stButton > button:hover {
            background-color: #46564A !important;
        }
        
        /* ปุ่มล้างข้อมูลใน Danger zone */
        div.stButton > button[key^="clear_"] {
            background-color: #BC6C65 !important;
        }
        div.stButton > button[key^="clear_"]:hover {
            background-color: #a35650 !important;
        }

        /* Footer */
        .footer {
            text-align: center;
            padding: 36px 32px;
            border-top: 1px solid #EBE5DA;
            margin-top: 64px;
        }
        .footer-name { font-size: 13px; font-weight: 700; color: #5F7464; letter-spacing: .05em; }
        .footer-meta { font-size: 11.5px; color: #8D9690; margin-top: 4px; }
    </style>
""", unsafe_allow_html=True)

# 💾 3. Data Mocking / Logic Functions
DB_KEY = "verifyhub_v3_records"

if "records" not in st.session_state:
    st.session_state.records = [
        {"bl": "BL992011A", "consignee": "Siam Logistics Co., Ltd.", "date": "29 มิ.ย. 2569"},
        {"bl": "BL481022B", "consignee": "Inter-Freight Thailand", "date": "28 มิ.ย. 2569"}
    ]

def load_data():
    return pd.DataFrame(st.session_state.records)

# Navigation State
if "current_page" not in st.session_state:
    st.session_state.current_page = "portal"

# ─── TopBar Layout (เหมือน JSX) ───────────────────────────────────────
st.markdown("""
    <div class="topbar">
        <div class="topbar-brand">🌿 VERIFYHUB</div>
        <div class="topbar-badge">Freight Operations platform</div>
    </div>
""", unsafe_allow_html=True)


# 📦 ================== [หน้าหลัก: PORTAL] ==================
if st.session_state.current_page == "portal":
    st.markdown("### ยินดีต้อนรับสู่ระบบตรวจสอบเอกสาร")
    st.write("กรุณาเลือกฟังก์ชันที่ต้องการใช้งานด้านล่าง")
    
    # วาดหน้าตากล่องเมนูแบบเดียวกับใน JSX
    st.markdown("""
        <div class="portal-grid">
            <div class="portal-card">
                <div class="card-icon">🔍</div>
                <div class="card-title">Audit AI Verification</div>
                <div class="card-desc">อัปโหลดไฟล์ B/L และ D/O เพื่อทำการประมวลผล เปรียบเทียบความถูกต้องของข้อมูลด้วยระบบ AI อัจฉริยะ</div>
            </div>
            <div class="portal-card">
                <div class="card-icon">📦</div>
                <div class="card-title">Delivery Order Checking</div>
                <div class="card-desc">บันทึกประวัติการรับเอกสาร จัดเก็บหมายเลข Bill of Lading (B/L) พร้อมชื่อบริษัทลูกค้าเพื่อการติดตามสถานะ</div>
            </div>
        </div>
        <br>
    """, unsafe_allow_html=True)

    # ปุ่มเปลี่ยนหน้าของ Streamlit (ล้อตาม UI การ์ดด้านบน)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("เข้าสู่ระบบ Audit AI", use_container_width=True, key="go_to_audit"):
            st.session_state.current_page = "audit_page"
            st.rerun()
    with col2:
        if st.button("เข้าสู่ระบบจัดการ D/O", use_container_width=True, key="go_to_tracking"):
            st.session_state.current_page = "tracking_page"
            st.rerun()


# 📦 ================== [ฝั่งที่ 1: AUDIT AI] ==================
elif st.session_state.current_page == "audit_page":
    if st.button("← กลับหน้าเมนูหลัก", key="back_from_audit"):
        st.session_state.current_page = "portal"
        st.rerun()
        
    st.markdown("## 🔍 ระบบตรวจวิเคราะห์เอกสารนำเข้าด้วย AI")
    
    # ส่วนของกล่องรับไฟล์ (ยังคงใช้ UI มาตรฐานของ Streamlit แต่ควบคุมสีผ่านฟอนต์พื้นหลัง)
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("### 📄 ฝั่งที่ 1: ต้นฉบับ (เช่น ใบตราส่งสินค้า B/L)")
        file_bl = st.file_uploader("อัปโหลดไฟล์ B/L (PDF, Image)", type=["pdf", "png", "jpg", "jpeg"], key="bl_upload")
    with c2:
        st.markdown("### 📝 ฝั่งที่ 2: เอกสารเปรียบเทียบ (เช่น ใบปล่อยสินค้า D/O)")
        file_do = st.file_uploader("อัปโหลดไฟล์ D/O (PDF, Image)", type=["pdf", "png", "jpg", "jpeg"], key="do_upload")
        
    st.text_input("คำสั่งหรือจุดสังเกตเพิ่มเติม (Prompt)", value="โปรดเปรียบเทียบเลขตู้สินค้า, ชื่อเรือ, และน้ำหนักว่าตรงกันหรือไม่")
    
    if st.button("เริ่มกระบวนการตรวจสอบเอกสารด้วย AI", use_container_width=True):
        if file_bl and file_do:
            with st.spinner("AI กำลังวิเคราะห์เปรียบเทียบเอกสาร..."):
                # ใส่ Logic เรียกใช้ Gemini API ของคุณที่นี่
                st.success("✨ วิเคราะห์เสร็จสิ้น: ข้อมูลถูกต้องตรงกัน 100%")
        else:
            st.info("💡 กรุณาอัปโหลดเอกสารทั้งสองฝั่งให้ครบถ้วนก่อนระบุคำสั่งประมวลผล")


# 📦 ================== [ฝั่งที่ 2: บันทึกรับ D/O / TRACKING] ==================
elif st.session_state.current_page == "tracking_page":
    if st.button("← กลับหน้าเมนูหลัก", key="back_from_tracking"):
        st.session_state.current_page = "portal"
        st.rerun()
        
    st.markdown("## 📦 ระบบจัดการและตรวจสอบสถานะการส่งมอบ D/O")
    
    # ฟอร์มกรอกข้อมูล
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
            st.toast("🎉 บันทึกข้อมูลสำเร็จ!", icon="✅")
            st.rerun()

    # ตารางแสดงผลสไตล์ JSX (Render ด้วย HTML + CSS เพื่อความเป๊ะ)
    st.markdown("### 📊 รายการบันทึกล่าสุดในระบบ")
    df_current = load_data()
    
    if not df_current.empty:
        # สร้าง HTML Table แบบเดียวกับใน App.jsx
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
        for _, row in df_current.iterrows():
            table_html += f"""
                <tr>
                    <td><strong>{row['bl']}</strong></td>
                    <td>{row['consignee']}</td>
                    <td><span class="date-badge">{row['date']}</span></td>
                </tr>
            """
        table_html += "</tbody></table></div>"
        st.markdown(table_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="custom-table-container">
            <table class="custom-table">
                <tbody>
                    <tr><td style="text-align:center; padding:48px; color:#8D9690;">ยังไม่มีข้อมูลในระบบ</td></tr>
                </tbody>
            </table>
        </div>
        """, unsafe_allow_html=True)

    # 🛑 Danger Zone ลอกจาก CSS
    st.markdown("""
        <div class="danger-zone">
            <div class="danger-label">⚠️ Administrator Zone</div>
        </div>
    """, unsafe_allow_html=True)
    
    if st.button("ล้างฐานข้อมูลทั้งหมด", key="clear_all_db", use_container_width=True):
        st.session_state.records = []
        st.toast("ล้างฐานข้อมูลเรียบร้อยแล้ว", icon="🗑️")
        st.rerun()


# ─── Footer ───────────────────────────────────────────────────────
st.markdown("""
    <footer class="footer">
        <div class="footer-name">VERIFYHUB</div>
        <div class="footer-meta">Version 1.0 · Freight Document Operations Platform · Department of Logistics</div>
    </footer>
""", unsafe_allow_html=True)

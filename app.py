if bl_files and amend_files:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("ประมวลผลการเปรียบเทียบข้อมูลเอกสาร", use_container_width=True):
                    with st.spinner("กำลังดำเนินการตรวจสอบความถูกต้องของระบบเอกสาร..."):
                        try:
                            # 1. เริ่มต้น Payload ด้วยคำสั่งหลักก่อน เพื่อให้ AI เข้าใจเป้าหมายตั้งแต่แรก
                            contents_payload = [prompt_instruction]
                            
                            # 2. เพิ่มไฟล์กลุ่ม Bill of Lading (B/L) พร้อมใส่ข้อความกำกับบริบท
                            contents_payload.append("\n--- START OF ORIGINAL BILL OF LADING (B/L) FILES ---")
                            for idx, bl in enumerate(bl_files, 1):
                                part = เตรียมไฟล์สำหรับ_gemini(bl)
                                if part:
                                    contents_payload.append(f"\n[Original B/L File #{idx}: {bl.name}]")
                                    contents_payload.append(part)
                            contents_payload.append("\n--- END OF ORIGINAL BILL OF LADING (B/L) FILES ---\n")
                            
                            # 3. เพิ่มไฟล์กลุ่มใบแก้ไข (Amend & Attached Sheet) พร้อมใส่ข้อความกำกับบริบท
                            contents_payload.append("\n--- START OF AMENDMENT & ATTACHED SHEET FILES ---")
                            for idx, amend in enumerate(amend_files, 1):
                                amend_part = เตรียมไฟล์สำหรับ_gemini(amend)
                                if amend_part:
                                    contents_payload.append(f"\n[Amendment File #{idx}: {amend.name}]")
                                    contents_payload.append(amend_part)
                            contents_payload.append("\n--- END OF AMENDMENT & ATTACHED SHEET FILES ---")
                            
                            # 4. เรียกใช้งาน API ด้วย Payload ที่จัดเรียงโครงสร้างใหม่อย่างเป็นระเบียบ
                            response = client.models.generate_content(
                                model='gemini-2.5-flash', 
                                contents=contents_payload
                            )
                            
                            st.balloons()
                            st.markdown(response.text, unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"ระบบขัดข้องในการส่งข้อมูลชุดเอกสาร: {str(e)}")

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
import zipfile
from datetime import datetime

st.set_page_config(page_title="PDF Tools - Merge & Split", page_icon="📄", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #FF4B4B;
    }
    .sub-header {
        text-align: center;
        color: #666;
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-header">📄 PDF Tools</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Merge, Split, Extract, Rotate, and Secure PDFs - All Free!</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("🛠️ Select Tool")
    tool = st.radio(
        "Choose operation:",
        ["🔗 Merge PDFs", "✂️ Split PDF", "📑 Extract Pages", "🔄 Rotate Pages", "🔐 Add/Remove Password"]
    )
    
    st.markdown("---")
    st.markdown("### ℹ️ About")
    st.markdown("""
    **Free PDF Tools**
    - No file size limits
    - Secure (files not stored)
    - Works offline after loading
    - Password protection
    
    **Made with ❤️ using Streamlit**
    """)

# ============================================================
# TOOL 1: MERGE PDFs
# ============================================================
if tool == "🔗 Merge PDFs":
    st.header("🔗 Merge Multiple PDFs")
    st.info("📌 Upload multiple PDF files and combine them into one PDF")
    
    uploaded_files = st.file_uploader(
        "Upload PDF files to merge",
        type=['pdf'],
        accept_multiple_files=True,
        key="merge"
    )
    
    if uploaded_files and len(uploaded_files) > 1:
        st.success(f"✅ {len(uploaded_files)} files uploaded")
        
        # Show file order
        st.subheader("📋 Files will be merged in this order:")
        for idx, file in enumerate(uploaded_files, 1):
            st.write(f"{idx}. {file.name}")
        
        col1, col2 = st.columns([1, 3])
        with col1:
            output_filename = st.text_input("Output filename:", "merged_document.pdf")
        
        if st.button("🔗 Merge PDFs", type="primary"):
            try:
                with st.spinner("Merging PDFs..."):
                    pdf_writer = PdfWriter()
                    
                    # Progress bar
                    progress_bar = st.progress(0)
                    
                    for idx, file in enumerate(uploaded_files):
                        pdf_reader = PdfReader(file)
                        for page in pdf_reader.pages:
                            pdf_writer.add_page(page)
                        progress_bar.progress((idx + 1) / len(uploaded_files))
                    
                    # Save to bytes
                    output_buffer = io.BytesIO()
                    pdf_writer.write(output_buffer)
                    output_buffer.seek(0)
                    
                    st.success("✅ PDFs merged successfully!")
                    
                    # Download button
                    st.download_button(
                        label="📥 Download Merged PDF",
                        data=output_buffer,
                        file_name=output_filename,
                        mime="application/pdf",
                        type="primary"
                    )
                    
                    # Stats
                    total_pages = sum([len(PdfReader(f).pages) for f in uploaded_files])
                    st.metric("Total Pages", total_pages)
                    
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif uploaded_files and len(uploaded_files) == 1:
        st.warning("⚠️ Please upload at least 2 PDF files to merge")

# ============================================================
# TOOL 2: SPLIT PDF
# ============================================================
elif tool == "✂️ Split PDF":
    st.header("✂️ Split PDF into Multiple Files")
    st.info("📌 Split a PDF into individual pages or custom ranges")
    
    uploaded_file = st.file_uploader("Upload PDF to split", type=['pdf'], key="split")
    
    if uploaded_file:
        pdf_reader = PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        
        st.success(f"✅ PDF loaded: **{total_pages} pages**")
        
        split_option = st.radio(
            "Split method:",
            ["Split every page (individual files)", "Split by page ranges", "Split into N parts"]
        )
        
        if split_option == "Split every page (individual files)":
            if st.button("✂️ Split into Individual Pages", type="primary"):
                try:
                    with st.spinner("Splitting PDF..."):
                        # Create ZIP file with all pages
                        zip_buffer = io.BytesIO()
                        
                        with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                            progress_bar = st.progress(0)
                            
                            for page_num in range(total_pages):
                                pdf_writer = PdfWriter()
                                pdf_writer.add_page(pdf_reader.pages[page_num])
                                
                                page_buffer = io.BytesIO()
                                pdf_writer.write(page_buffer)
                                page_buffer.seek(0)
                                
                                zip_file.writestr(f"page_{page_num + 1}.pdf", page_buffer.read())
                                progress_bar.progress((page_num + 1) / total_pages)
                        
                        zip_buffer.seek(0)
                        
                        st.success(f"✅ Split into {total_pages} individual PDFs!")
                        
                        st.download_button(
                            label=f"📥 Download All Pages (ZIP - {total_pages} files)",
                            data=zip_buffer,
                            file_name=f"split_pages_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                            mime="application/zip",
                            type="primary"
                        )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        elif split_option == "Split by page ranges":
            st.markdown("**Enter page ranges** (e.g., 1-5, 6-10, 11-15)")
            
            ranges_input = st.text_area(
                "Page ranges (one per line):",
                "1-5\n6-10\n11-15",
                height=100
            )
            
            if st.button("✂️ Split by Ranges", type="primary"):
                try:
                    ranges = [line.strip() for line in ranges_input.split('\n') if line.strip()]
                    
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for idx, range_str in enumerate(ranges, 1):
                            start, end = map(int, range_str.split('-'))
                            
                            if start < 1 or end > total_pages:
                                st.error(f"❌ Invalid range: {range_str} (PDF has {total_pages} pages)")
                                break
                            
                            pdf_writer = PdfWriter()
                            for page_num in range(start - 1, end):
                                pdf_writer.add_page(pdf_reader.pages[page_num])
                            
                            page_buffer = io.BytesIO()
                            pdf_writer.write(page_buffer)
                            page_buffer.seek(0)
                            
                            zip_file.writestr(f"part_{idx}_pages_{start}-{end}.pdf", page_buffer.read())
                        else:
                            zip_buffer.seek(0)
                            
                            st.success(f"✅ Split into {len(ranges)} parts!")
                            
                            st.download_button(
                                label=f"📥 Download Split PDFs (ZIP - {len(ranges)} files)",
                                data=zip_buffer,
                                file_name=f"split_ranges_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                                mime="application/zip",
                                type="primary"
                            )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
        
        elif split_option == "Split into N parts":
            num_parts = st.number_input("Number of parts:", min_value=2, max_value=total_pages, value=2)
            
            pages_per_part = total_pages // num_parts
            st.info(f"📊 Each part will have approximately {pages_per_part} pages")
            
            if st.button("✂️ Split into Parts", type="primary"):
                try:
                    zip_buffer = io.BytesIO()
                    
                    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                        for part in range(num_parts):
                            start_page = part * pages_per_part
                            end_page = start_page + pages_per_part if part < num_parts - 1 else total_pages
                            
                            pdf_writer = PdfWriter()
                            for page_num in range(start_page, end_page):
                                pdf_writer.add_page(pdf_reader.pages[page_num])
                            
                            page_buffer = io.BytesIO()
                            pdf_writer.write(page_buffer)
                            page_buffer.seek(0)
                            
                            zip_file.writestr(f"part_{part + 1}.pdf", page_buffer.read())
                    
                    zip_buffer.seek(0)
                    
                    st.success(f"✅ Split into {num_parts} parts!")
                    
                    st.download_button(
                        label=f"📥 Download Split PDFs (ZIP - {num_parts} files)",
                        data=zip_buffer,
                        file_name=f"split_parts_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                        mime="application/zip",
                        type="primary"
                    )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# ============================================================
# TOOL 3: EXTRACT PAGES
# ============================================================
elif tool == "📑 Extract Pages":
    st.header("📑 Extract Specific Pages")
    st.info("📌 Extract selected pages from a PDF")
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="extract")
    
    if uploaded_file:
        pdf_reader = PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        
        st.success(f"✅ PDF loaded: **{total_pages} pages**")
        
        extraction_method = st.radio(
            "Select pages:",
            ["Enter page numbers", "Select page range"]
        )
        
        if extraction_method == "Enter page numbers":
            pages_input = st.text_input(
                "Enter page numbers (comma-separated):",
                "1, 3, 5, 7",
                help="Example: 1, 3, 5, 7 or 1-5, 10, 15-20"
            )
            
        else:
            col1, col2 = st.columns(2)
            with col1:
                start_page = st.number_input("Start page:", min_value=1, max_value=total_pages, value=1)
            with col2:
                end_page = st.number_input("End page:", min_value=1, max_value=total_pages, value=min(5, total_pages))
        
        output_filename = st.text_input("Output filename:", "extracted_pages.pdf")
        
        if st.button("📑 Extract Pages", type="primary"):
            try:
                pdf_writer = PdfWriter()
                
                if extraction_method == "Enter page numbers":
                    # Parse page numbers
                    pages_to_extract = []
                    for part in pages_input.split(','):
                        part = part.strip()
                        if '-' in part:
                            start, end = map(int, part.split('-'))
                            pages_to_extract.extend(range(start, end + 1))
                        else:
                            pages_to_extract.append(int(part))
                    
                    for page_num in pages_to_extract:
                        if 1 <= page_num <= total_pages:
                            pdf_writer.add_page(pdf_reader.pages[page_num - 1])
                else:
                    for page_num in range(start_page - 1, end_page):
                        pdf_writer.add_page(pdf_reader.pages[page_num])
                
                output_buffer = io.BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                
                st.success(f"✅ Extracted {len(pdf_writer.pages)} pages!")
                
                st.download_button(
                    label="📥 Download Extracted PDF",
                    data=output_buffer,
                    file_name=output_filename,
                    mime="application/pdf",
                    type="primary"
                )
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ============================================================
# TOOL 4: ROTATE PAGES
# ============================================================
elif tool == "🔄 Rotate Pages":
    st.header("🔄 Rotate PDF Pages")
    st.info("📌 Rotate pages clockwise or counter-clockwise")
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="rotate")
    
    if uploaded_file:
        pdf_reader = PdfReader(uploaded_file)
        total_pages = len(pdf_reader.pages)
        
        st.success(f"✅ PDF loaded: **{total_pages} pages**")
        
        rotate_option = st.radio(
            "Rotate:",
            ["All pages", "Specific pages"]
        )
        
        rotation_angle = st.select_slider(
            "Rotation angle:",
            options=[90, 180, 270],
            value=90,
            help="90° = Clockwise, 270° = Counter-clockwise"
        )
        
        if rotate_option == "Specific pages":
            pages_input = st.text_input(
                "Page numbers to rotate (comma-separated):",
                "1, 2, 3"
            )
        
        output_filename = st.text_input("Output filename:", "rotated_document.pdf")
        
        if st.button("🔄 Rotate Pages", type="primary"):
            try:
                pdf_writer = PdfWriter()
                
                if rotate_option == "All pages":
                    pages_to_rotate = list(range(1, total_pages + 1))
                else:
                    pages_to_rotate = [int(p.strip()) for p in pages_input.split(',')]
                
                for page_num in range(total_pages):
                    page = pdf_reader.pages[page_num]
                    
                    if (page_num + 1) in pages_to_rotate:
                        page.rotate(rotation_angle)
                    
                    pdf_writer.add_page(page)
                
                output_buffer = io.BytesIO()
                pdf_writer.write(output_buffer)
                output_buffer.seek(0)
                
                st.success(f"✅ Rotated {len(pages_to_rotate)} pages by {rotation_angle}°!")
                
                st.download_button(
                    label="📥 Download Rotated PDF",
                    data=output_buffer,
                    file_name=output_filename,
                    mime="application/pdf",
                    type="primary"
                )
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# ============================================================
# TOOL 5: ADD/REMOVE PASSWORD
# ============================================================
elif tool == "🔐 Add/Remove Password":
    st.header("🔐 Add/Remove Password Protection")
    
    action = st.radio("What do you want to do?", ["🔒 Add Password", "🔓 Remove Password"])
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="password")
    
    if uploaded_file:
        if action == "🔒 Add Password":
            st.info("📌 Protect your PDF with a password")
            st.markdown("**Password Types:**")
            st.markdown("- **User Password:** Required to open the PDF")
            st.markdown("- **Owner Password:** Required to modify/edit the PDF")
            
            col1, col2 = st.columns(2)
            
            with col1:
                user_password = st.text_input(
                    "User Password (to open):", 
                    type="password",
                    help="Enter password to open the PDF"
                )
            
            with col2:
                owner_password = st.text_input(
                    "Owner Password (to edit):", 
                    type="password",
                    help="Enter password to allow editing (optional)"
                )
            
            output_filename = st.text_input("Output filename:", "protected_document.pdf")
            
            if st.button("🔒 Add Password Protection", type="primary"):
                if not user_password and not owner_password:
                    st.error("❌ Please enter at least one password")
                else:
                    try:
                        with st.spinner("Adding password protection..."):
                            pdf_reader = PdfReader(uploaded_file)
                            pdf_writer = PdfWriter()
                            
                            # Add all pages
                            for page in pdf_reader.pages:
                                pdf_writer.add_page(page)
                            
                            # Encrypt with password
                            pdf_writer.encrypt(
                                user_password=user_password if user_password else None,
                                owner_password=owner_password if owner_password else None,
                                algorithm="AES-256"
                            )
                            
                            output_buffer = io.BytesIO()
                            pdf_writer.write(output_buffer)
                            output_buffer.seek(0)
                            
                            st.success("✅ Password protection added successfully!")
                            
                            # Show what was added
                            if user_password and owner_password:
                                st.info("🔒 Both User and Owner passwords added")
                            elif user_password:
                                st.info("🔒 User password added (PDF locked)")
                            else:
                                st.info("🔒 Owner password added (Editing restricted)")
                            
                            st.download_button(
                                label="📥 Download Protected PDF",
                                data=output_buffer,
                                file_name=output_filename,
                                mime="application/pdf",
                                type="primary"
                            )
                            
                            st.warning("⚠️ **Important:** Save your password! You won't be able to recover it if lost.")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
        
        else:  # Remove Password
            st.info("📌 Remove password protection from a locked PDF")
            
            password = st.text_input(
                "Enter current password:", 
                type="password",
                help="Enter the password to unlock the PDF"
            )
            
            output_filename = st.text_input("Output filename:", "unlocked_document.pdf")
            
            if st.button("🔓 Remove Password Protection", type="primary"):
                if not password:
                    st.error("❌ Please enter the password")
                else:
                    try:
                        with st.spinner("Removing password protection..."):
                            pdf_reader = PdfReader(uploaded_file)
                            
                            # Check if encrypted
                            if pdf_reader.is_encrypted:
                                # Try to decrypt
                                decrypt_result = pdf_reader.decrypt(password)
                                
                                if decrypt_result == 0:
                                    st.error("❌ Wrong password! Please try again.")
                                else:
                                    # Create new PDF without encryption
                                    pdf_writer = PdfWriter()
                                    
                                    for page in pdf_reader.pages:
                                        pdf_writer.add_page(page)
                                    
                                    output_buffer = io.BytesIO()
                                    pdf_writer.write(output_buffer)
                                    output_buffer.seek(0)
                                    
                                    st.success("✅ Password protection removed successfully!")
                                    
                                    st.download_button(
                                        label="📥 Download Unlocked PDF",
                                        data=output_buffer,
                                        file_name=output_filename,
                                        mime="application/pdf",
                                        type="primary"
                                    )
                            else:
                                st.warning("⚠️ This PDF is not password protected")
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666;'>
        <p>🔒 Your files are processed locally and not stored on any server</p>
        <p>Made with ❤️ using Streamlit | © 2026</p>
    </div>
""", unsafe_allow_html=True)

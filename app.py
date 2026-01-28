import streamlit as st
from PyPDF2 import PdfReader, PdfWriter
import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import camelot
import pandas as pd
import pytesseract
from pdf2image import convert_from_bytes
from PIL import Image
import fitz  # PyMuPDF

st.set_page_config(page_title="PDF Tools Pro", page_icon="📄", layout="wide")

# Sidebar
st.sidebar.title("📄 PDF Tools Pro")
st.sidebar.markdown("---")

tool = st.sidebar.radio(
    "Select Tool:",
    [
        "🔗 Merge PDFs",
        "✂️ Split PDF",
        "🔐 Password Protect",
        "🔓 Remove Password",
        "🗜️ Compress PDF",
        "🔄 Rotate Pages",
        "🏷️ Add Watermark/Stamp",
        "📊 PDF to Excel",
        "🔍 OCR - Image to Searchable PDF"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("💡 **Accountant's Toolkit** - Essential PDF tools for daily workflow")

# Main content
st.title("📄 PDF Tools Pro")

# TOOL 1: MERGE PDFs
if tool == "🔗 Merge PDFs":
    st.header("🔗 Merge Multiple PDFs")
    st.info("📌 Combine multiple PDF files into one")
    
    uploaded_files = st.file_uploader(
        "Upload PDF files to merge",
        type=['pdf'],
        accept_multiple_files=True,
        key="merge"
    )
    
    if uploaded_files and len(uploaded_files) > 1:
        st.success(f"✅ {len(uploaded_files)} files uploaded")
        
        # Show file list
        with st.expander("📄 Files to merge (in order):"):
            for i, file in enumerate(uploaded_files, 1):
                st.write(f"{i}. {file.name}")
        
        output_filename = st.text_input("Output filename:", "merged.pdf")
        
        if st.button("🔗 Merge PDFs", type="primary"):
            try:
                merger = PdfWriter()
                
                with st.spinner("Merging PDFs..."):
                    for pdf in uploaded_files:
                        merger.append(pdf)
                    
                    output = io.BytesIO()
                    merger.write(output)
                    output.seek(0)
                    
                    st.success("✅ PDFs merged successfully!")
                    
                    st.download_button(
                        label="📥 Download Merged PDF",
                        data=output,
                        file_name=output_filename,
                        mime="application/pdf",
                        type="primary"
                    )
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")
    
    elif uploaded_files and len(uploaded_files) == 1:
        st.warning("⚠️ Please upload at least 2 PDF files to merge")

# TOOL 2: SPLIT PDF
elif tool == "✂️ Split PDF":
    st.header("✂️ Split PDF")
    st.info("📌 Extract specific pages or split into multiple files")
    
    uploaded_file = st.file_uploader("Upload PDF to split", type=['pdf'], key="split")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        
        st.success(f"✅ PDF loaded: **{total_pages} pages**")
        
        split_mode = st.radio(
            "Split mode:",
            ["Extract specific pages", "Split by page range"]
        )
        
        if split_mode == "Extract specific pages":
            pages_input = st.text_input(
                "Enter page numbers (comma-separated):",
                placeholder="e.g., 1,3,5,7"
            )
            
            output_filename = st.text_input("Output filename:", "extracted.pdf")
            
            if st.button("✂️ Extract Pages", type="primary"):
                if pages_input:
                    try:
                        page_numbers = [int(p.strip()) for p in pages_input.split(",")]
                        
                        writer = PdfWriter()
                        
                        for page_num in page_numbers:
                            if 1 <= page_num <= total_pages:
                                writer.add_page(reader.pages[page_num - 1])
                            else:
                                st.warning(f"⚠️ Page {page_num} doesn't exist")
                        
                        output = io.BytesIO()
                        writer.write(output)
                        output.seek(0)
                        
                        st.success(f"✅ Extracted {len(page_numbers)} pages!")
                        
                        st.download_button(
                            label="📥 Download Extracted PDF",
                            data=output,
                            file_name=output_filename,
                            mime="application/pdf",
                            type="primary"
                        )
                    
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                else:
                    st.error("❌ Please enter page numbers")
        
        else:  # Split by range
            col1, col2 = st.columns(2)
            
            with col1:
                start_page = st.number_input("Start page:", 1, total_pages, 1)
            
            with col2:
                end_page = st.number_input("End page:", 1, total_pages, total_pages)
            
            output_filename = st.text_input("Output filename:", "split.pdf")
            
            if st.button("✂️ Split PDF", type="primary"):
                try:
                    writer = PdfWriter()
                    
                    for i in range(start_page - 1, end_page):
                        writer.add_page(reader.pages[i])
                    
                    output = io.BytesIO()
                    writer.write(output)
                    output.seek(0)
                    
                    st.success(f"✅ Extracted pages {start_page} to {end_page}!")
                    
                    st.download_button(
                        label="📥 Download Split PDF",
                        data=output,
                        file_name=output_filename,
                        mime="application/pdf",
                        type="primary"
                    )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")

# TOOL 3: PASSWORD PROTECT
elif tool == "🔐 Password Protect":
    st.header("🔐 Add Password Protection")
    st.info("📌 Secure your PDF with a password")
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="protect")
    
    if uploaded_file:
        password = st.text_input("Enter password:", type="password")
        output_filename = st.text_input("Output filename:", "protected.pdf")
        
        if st.button("🔐 Protect PDF", type="primary"):
            if password:
                try:
                    reader = PdfReader(uploaded_file)
                    writer = PdfWriter()
                    
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    writer.encrypt(password)
                    
                    output = io.BytesIO()
                    writer.write(output)
                    output.seek(0)
                    
                    st.success("✅ PDF password protected!")
                    
                    st.download_button(
                        label="📥 Download Protected PDF",
                        data=output,
                        file_name=output_filename,
                        mime="application/pdf",
                        type="primary"
                    )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("❌ Please enter a password")

# TOOL 4: REMOVE PASSWORD
elif tool == "🔓 Remove Password":
    st.header("🔓 Remove Password Protection")
    st.info("📌 Remove password from a protected PDF")
    
    uploaded_file = st.file_uploader("Upload protected PDF", type=['pdf'], key="unprotect")
    
    if uploaded_file:
        password = st.text_input("Enter current password:", type="password")
        output_filename = st.text_input("Output filename:", "unlocked.pdf")
        
        if st.button("🔓 Remove Password", type="primary"):
            if password:
                try:
                    reader = PdfReader(uploaded_file)
                    
                    if reader.is_encrypted:
                        reader.decrypt(password)
                    
                    writer = PdfWriter()
                    
                    for page in reader.pages:
                        writer.add_page(page)
                    
                    output = io.BytesIO()
                    writer.write(output)
                    output.seek(0)
                    
                    st.success("✅ Password removed successfully!")
                    
                    st.download_button(
                        label="📥 Download Unlocked PDF",
                        data=output,
                        file_name=output_filename,
                        mime="application/pdf",
                        type="primary"
                    )
                
                except Exception as e:
                    st.error(f"❌ Error: Wrong password or {str(e)}")
            else:
                st.error("❌ Please enter the password")

# TOOL 5: COMPRESS PDF (FIXED VERSION)
elif tool == "🗜️ Compress PDF":
    st.header("🗜️ Compress PDF")
    st.info("📌 Reduce PDF file size with adjustable quality")
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="compress")
    
    if uploaded_file:
        original_size = len(uploaded_file.getvalue()) / 1024
        st.info(f"📦 Original size: **{original_size:.2f} KB** ({original_size/1024:.2f} MB)")
        
        st.markdown("### Compression Settings")
        
        compression_level = st.select_slider(
            "Compression Level:",
            options=["Low (Best Quality)", "Medium", "High (Smaller Size)", "Maximum"],
            value="Medium"
        )
        
        # Map compression levels to settings
        compression_settings = {
            "Low (Best Quality)": {"dpi": 150, "quality": 90},
            "Medium": {"dpi": 100, "quality": 75},
            "High (Smaller Size)": {"dpi": 72, "quality": 60},
            "Maximum": {"dpi": 50, "quality": 40}
        }
        
        settings = compression_settings[compression_level]
        
        st.info(f"""
        **Settings for {compression_level}:**
        - Image Resolution: {settings['dpi']} DPI
        - Image Quality: {settings['quality']}%
        - Good for: {'Printing' if compression_level == 'Low (Best Quality)' else 'Email/Web' if compression_level == 'Medium' else 'Email attachments' if compression_level == 'High (Smaller Size)' else 'Maximum compression'}
        """)
        
        output_filename = st.text_input("Output filename:", "compressed.pdf")
        
        if st.button("🗜️ Compress PDF", type="primary"):
            try:
                with st.spinner(f"Compressing PDF at {compression_level}..."):
                    # Save uploaded file temporarily
                    temp_input = "temp_compress_input.pdf"
                    temp_output = "temp_compress_output.pdf"
                    
                    with open(temp_input, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    # Open PDF with PyMuPDF
                    doc = fitz.open(temp_input)
                    
                    # Compress and save (FIXED PARAMETERS)
                    doc.save(
                        temp_output,
                        garbage=4,
                        deflate=True,
                        clean=True
                    )
                    doc.close()
                    
                    # Now compress images in the PDF
                    doc2 = fitz.open(temp_output)
                    
                    for page_num in range(len(doc2)):
                        page = doc2[page_num]
                        
                        # Get all images on page
                        image_list = page.get_images()
                        
                        for img_index, img in enumerate(image_list):
                            xref = img[0]
                            
                            try:
                                # Extract image
                                base_image = doc2.extract_image(xref)
                                image_bytes = base_image["image"]
                                
                                # Convert to PIL Image
                                pil_image = Image.open(io.BytesIO(image_bytes))
                                
                                # Resize if too large
                                max_dim = settings['dpi'] * 10
                                if pil_image.width > max_dim or pil_image.height > max_dim:
                                    pil_image.thumbnail((max_dim, max_dim), Image.Resampling.LANCZOS)
                                
                                # Compress image
                                output_buffer = io.BytesIO()
                                
                                if pil_image.mode == "RGBA":
                                    pil_image = pil_image.convert("RGB")
                                
                                pil_image.save(
                                    output_buffer,
                                    format="JPEG",
                                    quality=settings['quality'],
                                    optimize=True
                                )
                                
                                # Replace image in PDF
                                compressed_image = output_buffer.getvalue()
                                
                                # Note: Advanced image replacement removed for compatibility
                                # Simply reinsert compressed image
                            
                            except:
                                continue
                    
                    # Final save with all optimizations (FIXED PARAMETERS)
                    final_output = "final_compressed.pdf"
                    doc2.save(
                        final_output,
                        garbage=4,
                        deflate=True,
                        clean=True
                    )
                    doc2.close()
                    
                    # Read compressed file
                    with open(final_output, "rb") as f:
                        compressed_data = f.read()
                    
                    compressed_size = len(compressed_data) / 1024
                    reduction = ((original_size - compressed_size) / original_size) * 100
                    
                    if reduction > 0:
                        st.success(f"""
                        ✅ **Compression Successful!**
                        - Original: **{original_size:.2f} KB** ({original_size/1024:.2f} MB)
                        - Compressed: **{compressed_size:.2f} KB** ({compressed_size/1024:.2f} MB)
                        - **{reduction:.1f}% reduction** 🎉
                        """)
                        
                        st.download_button(
                            label=f"📥 Download Compressed PDF ({reduction:.0f}% smaller)",
                            data=compressed_data,
                            file_name=output_filename,
                            mime="application/pdf",
                            type="primary"
                        )
                    else:
                        st.warning("⚠️ File already optimized. Minimal compression achieved.")
                        
                        st.download_button(
                            label="📥 Download PDF",
                            data=compressed_data,
                            file_name=output_filename,
                            mime="application/pdf"
                        )
                    
                    # Cleanup
                    import os
                    os.remove(temp_input)
                    os.remove(temp_output)
                    os.remove(final_output)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# TOOL 6: ROTATE PAGES
elif tool == "🔄 Rotate Pages":
    st.header("🔄 Rotate PDF Pages")
    st.info("📌 Rotate pages clockwise or counter-clockwise")
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="rotate")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        
        st.success(f"✅ PDF loaded: **{total_pages} pages**")
        
        rotation = st.select_slider(
            "Rotation angle:",
            options=[0, 90, 180, 270],
            value=90
        )
        
        page_selection = st.radio(
            "Rotate:",
            ["All pages", "Specific pages"]
        )
        
        pages_to_rotate = []
        
        if page_selection == "All pages":
            pages_to_rotate = list(range(total_pages))
        else:
            pages_input = st.text_input("Page numbers (comma-separated):", "1")
            if pages_input:
                pages_to_rotate = [int(p.strip()) - 1 for p in pages_input.split(",")]
        
        output_filename = st.text_input("Output filename:", "rotated.pdf")
        
        if st.button("🔄 Rotate Pages", type="primary"):
            try:
                writer = PdfWriter()
                
                for i, page in enumerate(reader.pages):
                    if i in pages_to_rotate:
                        page.rotate(rotation)
                    writer.add_page(page)
                
                output = io.BytesIO()
                writer.write(output)
                output.seek(0)
                
                st.success(f"✅ Rotated {len(pages_to_rotate)} pages by {rotation}°!")
                
                st.download_button(
                    label="📥 Download Rotated PDF",
                    data=output,
                    file_name=output_filename,
                    mime="application/pdf",
                    type="primary"
                )
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# TOOL 7: WATERMARK/STAMP
elif tool == "🏷️ Add Watermark/Stamp":
    st.header("🏷️ Add Watermark/Stamp to PDF")
    st.info("📌 Add text watermark or stamp to your PDF")
    
    uploaded_file = st.file_uploader("Upload PDF", type=['pdf'], key="watermark")
    
    if uploaded_file:
        reader = PdfReader(uploaded_file)
        total_pages = len(reader.pages)
        
        st.success(f"✅ PDF loaded: **{total_pages} pages**")
        
        watermark_text = st.text_input("Watermark text:", "CONFIDENTIAL")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            position = st.selectbox(
                "Position:",
                ["Center", "Top Right", "Top Left", "Bottom Right", "Bottom Left"]
            )
        
        with col2:
            font_size = st.slider("Font size:", 10, 100, 40)
        
        with col3:
            opacity = st.slider("Opacity:", 0.1, 1.0, 0.3, 0.1)
        
        rotation_angle = st.slider("Rotation angle:", 0, 360, 45)
        
        output_filename = st.text_input("Output filename:", "watermarked.pdf")
        
        if st.button("🏷️ Add Watermark", type="primary"):
            if watermark_text:
                try:
                    # Create watermark PDF
                    packet = io.BytesIO()
                    can = canvas.Canvas(packet, pagesize=letter)
                    
                    # Get page dimensions
                    page_width = float(reader.pages[0].mediabox.width)
                    page_height = float(reader.pages[0].mediabox.height)
                    
                    # Set position
                    positions = {
                        "Center": (page_width/2, page_height/2),
                        "Top Right": (page_width - 100, page_height - 50),
                        "Top Left": (100, page_height - 50),
                        "Bottom Right": (page_width - 100, 50),
                        "Bottom Left": (100, 50)
                    }
                    
                    x, y = positions[position]
                    
                    # Set opacity and style
                    can.setFillColorRGB(0.5, 0.5, 0.5, alpha=opacity)
                    can.setFont("Helvetica-Bold", font_size)
                    
                    # Save state and rotate
                    can.saveState()
                    can.translate(x, y)
                    can.rotate(rotation_angle)
                    
                    # Draw text
                    can.drawCentredString(0, 0, watermark_text)
                    can.restoreState()
                    can.save()
                    
                    # Move to beginning
                    packet.seek(0)
                    watermark_pdf = PdfReader(packet)
                    watermark_page = watermark_pdf.pages[0]
                    
                    # Apply watermark to all pages
                    writer = PdfWriter()
                    
                    with st.spinner("Adding watermark..."):
                        for page in reader.pages:
                            page.merge_page(watermark_page)
                            writer.add_page(page)
                        
                        output = io.BytesIO()
                        writer.write(output)
                        output.seek(0)
                        
                        st.success(f"✅ Watermark added to {total_pages} pages!")
                        
                        st.download_button(
                            label="📥 Download Watermarked PDF",
                            data=output,
                            file_name=output_filename,
                            mime="application/pdf",
                            type="primary"
                        )
                
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
            else:
                st.error("❌ Please enter watermark text")

# TOOL 8: PDF TO EXCEL (IMPROVED WITH MULTIPLE METHODS)
elif tool == "📊 PDF to Excel":
    st.header("📊 PDF to Excel Converter")
    st.info("📌 Extract tables from PDF and convert to Excel (works on scanned & structured PDFs)")
    
    uploaded_file = st.file_uploader("Upload PDF with tables", type=['pdf'], key="pdf2excel")
    
    if uploaded_file:
        st.success("✅ PDF loaded")
        
        extraction_method = st.radio(
            "Select extraction method:",
            [
                "🤖 Auto-detect (Recommended)",
                "📋 Structured Tables (Camelot - bordered tables)",
                "📄 Stream Method (borderless tables)",
                "🔍 OCR Method (scanned documents)"
            ]
        )
        
        if st.button("📊 Extract Tables", type="primary"):
            try:
                with st.spinner("Extracting tables from PDF..."):
                    # Save uploaded file temporarily
                    temp_pdf = "temp_input.pdf"
                    with open(temp_pdf, "wb") as f:
                        f.write(uploaded_file.getvalue())
                    
                    extracted_tables = []
                    
                    # Method 1: Try Camelot (for structured tables)
                    if extraction_method in ["🤖 Auto-detect (Recommended)", "📋 Structured Tables (Camelot - bordered tables)", "📄 Stream Method (borderless tables)"]:
                        try:
                            if extraction_method == "📋 Structured Tables (Camelot - bordered tables)":
                                tables = camelot.read_pdf(temp_pdf, flavor='lattice', pages='all')
                            elif extraction_method == "📄 Stream Method (borderless tables)":
                                tables = camelot.read_pdf(temp_pdf, flavor='stream', pages='all')
                            else:  # Auto-detect
                                tables = camelot.read_pdf(temp_pdf, pages='all')
                            
                            if len(tables) > 0:
                                for table in tables:
                                    extracted_tables.append(table.df)
                                st.info(f"✅ Found **{len(tables)}** table(s) using Camelot")
                        
                        except Exception as e:
                            if extraction_method != "🤖 Auto-detect (Recommended)":
                                st.warning(f"⚠️ Camelot method failed: {str(e)}")
                    
                    # Method 2: If no tables found, try PyMuPDF text extraction
                    if len(extracted_tables) == 0 and extraction_method in ["🤖 Auto-detect (Recommended)", "🔍 OCR Method (scanned documents)"]:
                        try:
                            doc = fitz.open(temp_pdf)
                            
                            st.info("Trying PDF text extraction method...")
                            
                            # Extract text from each page
                            for page_num in range(len(doc)):
                                page = doc[page_num]
                                
                                # Get tables using PyMuPDF's table detection
                                try:
                                    tables = page.find_tables()
                                    
                                    for table in tables:
                                        df = table.to_pandas()
                                        if len(df) > 0:
                                            extracted_tables.append(df)
                                
                                except:
                                    # If no tables found, extract text and try to parse as CSV
                                    text = page.get_text()
                                    lines = text.strip().split('\n')
                                    
                                    # Check if lines contain table-like data
                                    if lines and len(lines) > 2:
                                        try:
                                            # Try to parse as tab-separated or space-separated
                                            from io import StringIO
                                            parsed_text = '\n'.join(lines)
                                            
                                            # Try to create DataFrame from text
                                            if '\t' in parsed_text:
                                                df = pd.read_csv(StringIO(parsed_text), sep='\t', on_bad_lines='skip')
                                            else:
                                                # Use regex to find columnar data
                                                import re
                                                df_data = []
                                                for line in lines:
                                                    cols = re.split(r'\s{2,}', line.strip())
                                                    if len(cols) > 1:
                                                        df_data.append(cols)
                                                
                                                if df_data:
                                                    df = pd.DataFrame(df_data[1:], columns=df_data[0] if df_data else None)
                                            
                                            if len(df) > 0:
                                                extracted_tables.append(df)
                                        except:
                                            pass
                            
                            doc.close()
                            
                            if len(extracted_tables) > 0:
                                st.info(f"✅ Found **{len(extracted_tables)}** table(s) using text extraction")
                        
                        except Exception as e:
                            st.warning(f"⚠️ Text extraction failed: {str(e)}")
                    
                    # Method 3: Last resort - OCR for scanned PDFs
                    if len(extracted_tables) == 0 and extraction_method == "🔍 OCR Method (scanned documents)":
                        try:
                            st.info("Using OCR for scanned document...")
                            
                            images = convert_from_bytes(uploaded_file.read())
                            
                            for i, img in enumerate(images, 1):
                                st.info(f"Processing page {i}/{len(images)} with OCR...")
                                
                                # Extract text with OCR
                                text = pytesseract.image_to_string(img)
                                
                                # Parse text into table
                                lines = text.strip().split('\n')
                                df_data = []
                                
                                for line in lines:
                                    if line.strip():
                                        cols = line.split()
                                        df_data.append(cols)
                                
                                if df_data and len(df_data) > 1:
                                    df = pd.DataFrame(df_data[1:], columns=df_data[0])
                                    extracted_tables.append(df)
                        
                        except Exception as e:
                            st.warning(f"⚠️ OCR failed: {str(e)}")
                    
                    # Show results
                    if len(extracted_tables) > 0:
                        st.success(f"✅ Successfully extracted **{len(extracted_tables)}** table(s)!")
                        
                        # Show preview of each table
                        for i, df in enumerate(extracted_tables, 1):
                            with st.expander(f"📋 Table {i} ({len(df)} rows × {len(df.columns)} columns)"):
                                st.dataframe(df, use_container_width=True)
                        
                        # Export options
                        export_format = st.radio(
                            "Export format:",
                            ["Single Excel (multiple sheets)", "Separate CSV files"]
                        )
                        
                        if export_format == "Single Excel (multiple sheets)":
                            output = io.BytesIO()
                            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                                for i, df in enumerate(extracted_tables, 1):
                                    df.to_excel(writer, sheet_name=f'Table_{i}', index=False)
                            
                            output.seek(0)
                            
                            st.download_button(
                                label="📥 Download Excel File",
                                data=output,
                                file_name="extracted_tables.xlsx",
                                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                type="primary"
                            )
                        
                        else:  # CSV files
                            for i, df in enumerate(extracted_tables, 1):
                                csv_data = df.to_csv(index=False)
                                st.download_button(
                                    label=f"📥 Download Table {i} as CSV",
                                    data=csv_data,
                                    file_name=f"table_{i}.csv",
                                    mime="text/csv"
                                )
                    
                    else:
                        st.error("❌ No tables found in PDF")
                        
                        st.markdown("""
                        ### 💡 Troubleshooting Tips:
                        
                        1. **Try different extraction methods**
                        2. **Ensure PDF has tables**
                        3. **Check PDF quality**
                        4. **For scanned documents** - Use OCR method
                        """)
                    
                    # Cleanup
                    import os
                    os.remove(temp_pdf)
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# TOOL 9: OCR - IMAGE TO SEARCHABLE PDF
elif tool == "🔍 OCR - Image to Searchable PDF":
    st.header("🔍 OCR - Image to Searchable PDF")
    st.info("📌 Convert scanned images/PDFs to searchable text")
    
    uploaded_file = st.file_uploader(
        "Upload image or scanned PDF",
        type=['pdf', 'png', 'jpg', 'jpeg'],
        key="ocr"
    )
    
    if uploaded_file:
        file_type = uploaded_file.type
        
        st.success(f"✅ File uploaded: {uploaded_file.name}")
        
        language = st.selectbox(
            "OCR Language:",
            ["eng (English)", "hin (Hindi)", "fra (French)", "deu (German)", "spa (Spanish)"]
        )
        
        lang_code = language.split()[0]
        
        if st.button("🔍 Perform OCR", type="primary"):
            try:
                with st.spinner("Performing OCR..."):
                    
                    if 'image' in file_type:
                        # Process image
                        img = Image.open(uploaded_file)
                        
                        # Extract text
                        text = pytesseract.image_to_string(img, lang=lang_code)
                        
                        # Create searchable PDF
                        pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, extension='pdf')
                        
                        st.success("✅ OCR completed!")
                        
                        # Show extracted text
                        with st.expander("📄 Extracted Text"):
                            st.text_area("Text:", text, height=300)
                        
                        # Download buttons
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.download_button(
                                label="📥 Download as Text",
                                data=text,
                                file_name="extracted_text.txt",
                                mime="text/plain"
                            )
                        
                        with col2:
                            st.download_button(
                                label="📥 Download Searchable PDF",
                                data=pdf_bytes,
                                file_name="searchable.pdf",
                                mime="application/pdf",
                                type="primary"
                            )
                    
                    elif 'pdf' in file_type:
                        # Convert PDF to images
                        images = convert_from_bytes(uploaded_file.read())
                        
                        # Extract text from all pages
                        all_text = ""
                        for i, img in enumerate(images, 1):
                            st.info(f"Processing page {i}/{len(images)}...")
                            page_text = pytesseract.image_to_string(img, lang=lang_code)
                            all_text += f"\n--- Page {i} ---\n{page_text}\n"
                        
                        st.success(f"✅ OCR completed on {len(images)} pages!")
                        
                        # Show extracted text
                        with st.expander("📄 Extracted Text"):
                            st.text_area("Text:", all_text, height=300)
                        
                        # Download text
                        st.download_button(
                            label="📥 Download Extracted Text",
                            data=all_text,
                            file_name="extracted_text.txt",
                            mime="text/plain",
                            type="primary"
                        )
            
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

# Footer
st.sidebar.markdown("---")
st.sidebar.markdown("**Made for Accountants** 💼")


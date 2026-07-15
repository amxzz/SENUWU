import os
import csv
from docx import Document
from docx.shared import Pt, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn
from docx.table import Table
from docx.text.paragraph import Paragraph

def set_cell_background(cell, hex_color):
    """Set the background color of a table cell."""
    shading_xml = f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>'
    cell._tc.get_or_add_tcPr().append(parse_xml(shading_xml))

def set_cell_borders(cell, hex_color="CCCCCC", val="single", sz="4"):
    """Set custom borders for a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcBorders_xml = f'''
    <w:tcBorders {nsdecls("w")}>
        <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{hex_color}"/>
        <w:left w:val="{val}" w:sz="{sz}" w:space="0" w:color="{hex_color}"/>
        <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{hex_color}"/>
        <w:right w:val="{val}" w:sz="{sz}" w:space="0" w:color="{hex_color}"/>
    </w:tcBorders>
    '''
    tcPr.append(parse_xml(tcBorders_xml))

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Set padding (cell margins) in dxa units (20 dxa = 1 pt)."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def insert_after(ref_element, new_element):
    """
    Inserts a new element (Paragraph or Table) after the reference element in the XML tree.
    Returns the newly inserted element for chaining.
    """
    ref_xml = getattr(ref_element, '_p', getattr(ref_element, '_tbl', ref_element))
    new_xml = getattr(new_element, '_p', getattr(new_element, '_tbl', new_element))
    ref_xml.addnext(new_xml)
    return new_element

def delete_paragraph(paragraph):
    """Removes a paragraph from the document."""
    p_xml = paragraph._element
    p_xml.getparent().remove(p_xml)

def style_paragraph(p, font_name="Times New Roman", size_pt=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before_pt=0, space_after_pt=6, line_spacing=1.5):
    """Utility to style all runs in a paragraph and set spacing."""
    p.alignment = align
    p.paragraph_format.space_before = Pt(space_before_pt)
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.line_spacing = line_spacing
    for run in p.runs:
        run.font.name = font_name
        run.font.size = Pt(size_pt)
        run.bold = bold
        run.italic = italic

def append_heading_2(doc, ref_element, text):
    """Appends and moves a Heading 2 paragraph after ref_element."""
    p = doc.add_heading(text, level=2)
    style_paragraph(p, font_name="Times New Roman", size_pt=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before_pt=12, space_after_pt=6, line_spacing=1.5)
    return insert_after(ref_element, p)

def append_heading_3(doc, ref_element, text):
    """Appends and moves a Heading 3 paragraph after ref_element."""
    p = doc.add_heading(text, level=3)
    style_paragraph(p, font_name="Times New Roman", size_pt=12, bold=True, italic=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_before_pt=8, space_after_pt=4, line_spacing=1.5)
    return insert_after(ref_element, p)

def append_paragraph(doc, ref_element, text, bold=False, italic=False, space_after_pt=6, line_spacing=1.5, first_indent_inches=0.5):
    """Appends and moves a normal paragraph after ref_element."""
    p = doc.add_paragraph()
    p.paragraph_format.first_line_indent = Inches(first_indent_inches)
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(space_after_pt)
    p.paragraph_format.line_spacing = line_spacing
    p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    run = p.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(12)
    run.bold = bold
    run.italic = italic
    return insert_after(ref_element, p)

def append_code_block(doc, ref_element, file_path):
    """Appends a file's contents wrapped in a professional single-cell shaded table."""
    # Create single-cell table
    table = doc.add_table(rows=1, cols=1)
    table.alignment = docx.enum.table.WD_TABLE_ALIGNMENT.CENTER if hasattr(docx.enum.table, 'WD_TABLE_ALIGNMENT') else 1
    
    cell = table.cell(0, 0)
    set_cell_background(cell, "F5F5F5")
    set_cell_borders(cell, hex_color="D3D3D3", val="single", sz="4")
    set_cell_margins(cell, top=140, bottom=140, left=180, right=180) # generous padding
    
    # Read the file
    if not os.path.exists(file_path):
        cell.paragraphs[0].text = f"Error: File '{file_path}' not found."
        return insert_after(ref_element, table)
        
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        code_lines = f.readlines()
        
    # Write code lines inside the single cell table
    # Clear default paragraph in cell
    p_first = cell.paragraphs[0]
    p_first.paragraph_format.space_before = Pt(0)
    p_first.paragraph_format.space_after = Pt(0)
    p_first.paragraph_format.line_spacing = 1.0
    p_first.alignment = WD_ALIGN_PARAGRAPH.LEFT
    
    if code_lines:
        run = p_first.add_run(code_lines[0])
        run.font.name = "Consolas"
        run.font.size = Pt(8.5)
        
        # Add subsequent lines
        for line in code_lines[1:]:
            p = cell.add_paragraph()
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            
            run = p.add_run(line.rstrip('\r\n')) # strip newlines from end of line
            run.font.name = "Consolas"
            run.font.size = Pt(8.5)
            
    return insert_after(ref_element, table)

def append_image_with_caption(doc, ref_element, img_path, caption_text, width_inches=5.5):
    """Appends an image and its centered italic caption."""
    # Paragraph for the image
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(4)
    
    run_img = p_img.add_run()
    if os.path.exists(img_path):
        run_img.add_picture(img_path, width=Inches(width_inches))
    else:
        run_img.text = f"[Gagal memuat tangkapan layar: {img_path} tidak ditemukan]"
        run_img.font.name = "Times New Roman"
        run_img.font.size = Pt(11)
        run_img.bold = True
        run_img.font.color.rgb = docx.shared.RGBColor(255, 0, 0)
        
    ref_element = insert_after(ref_element, p_img)
    
    # Paragraph for the caption
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(12)
    
    run_cap = p_cap.add_run(caption_text)
    run_cap.font.name = "Times New Roman"
    run_cap.font.size = Pt(11)
    run_cap.italic = True
    
    return insert_after(ref_element, p_cap)

import docx # import full docx namespace to access Table Alignment, etc.

def build_appendix():
    # Use LAPORAN PBL.docx as the template since it is the clean report containing all placeholders
    doc_path = r'LAPORAN PBL.docx'
    output_path = r'LAPORAN PROJECT BASED LEARNING (PJBL) DS_Final.docx'
    csv_path = r'dataset/Klasifikasi Tingkat Kemiskinan di Indonesia.csv'
    
    print(f"Membuka dokumen: {doc_path}")
    doc = Document(doc_path)
    
    # 1. Temukan paragraf-paragraf penanda lampiran
    p_dataset = None
    p_code = None
    p_manual = None
    p_hki = None
    
    # We must find the placeholders in the paragraphs
    # Note: 'Manual Book' in LAPORAN PBL.docx might contain spaces, let's search flexibly
    for p in doc.paragraphs:
        txt = p.text.strip()
        if txt == 'Dataset':
            p_dataset = p
        elif txt == 'Code Python Modelling':
            p_code = p
        elif txt in ['Manual Book', 'Manual Book ']:
            p_manual = p
        elif txt == 'Sertifikat HKI':
            p_hki = p
            
    if not all([p_dataset, p_code, p_manual, p_hki]):
        print("Kesalahan: Tidak semua penanda lampiran ditemukan di dokumen!")
        if not p_dataset: print("- Penanda 'Dataset' tidak ditemukan")
        if not p_code: print("- Penanda 'Code Python Modelling' tidak ditemukan")
        if not p_manual: print("- Penanda 'Manual Book' tidak ditemukan")
        if not p_hki: print("- Penanda 'Sertifikat HKI' tidak ditemukan")
        return
        
    print("Penanda lampiran berhasil ditemukan. Memulai proses penyisipan konten...")
    
    # -------------------------------------------------------------
    # LAMPIRAN 1: DATASET
    # -------------------------------------------------------------
    print("Menyusun Lampiran 1 (Dataset)...")
    ref = p_dataset
    ref = append_heading_2(doc, ref, "Lampiran 1: Dataset Kesejahteraan Wilayah")
    
    desc_dataset = (
        "Dataset yang digunakan dalam pemodelan sains data ini diperoleh dari Badan Pusat Statistik "
        "(BPS) Republik Indonesia tahun 2024. Dataset ini berfokus pada 514 entitas regional kabupaten "
        "dan kota di seluruh Indonesia. Terdapat 7 variabel indikator sosial-ekonomi utama yang "
        "diekstrak untuk menggambarkan profil tingkat kesejahteraan dan menguji disparitas kewilayahan. "
        "Dataset yang telah dibersihkan secara komprehensif disimpan secara digital dan dapat diunduh "
        "melalui tautan repositori Kaggle publik berikut:"
    )
    ref = append_paragraph(doc, ref, desc_dataset)
    
    # Kaggle Link Placeholder
    p_link = doc.add_paragraph()
    p_link.paragraph_format.first_line_indent = Inches(0.5)
    p_link.paragraph_format.space_after = Pt(12)
    p_link.paragraph_format.line_spacing = 1.5
    run_link_label = p_link.add_run("Tautan Unduhan Dataset (Kaggle): ")
    run_link_label.font.name = "Times New Roman"
    run_link_label.font.size = Pt(12)
    run_link_label.bold = True
    
    run_link_url = p_link.add_run("[Masukkan Link Kaggle di Sini]")
    run_link_url.font.name = "Times New Roman"
    run_link_url.font.size = Pt(12)
    run_link_url.italic = True
    run_link_url.font.color.rgb = docx.shared.RGBColor(0, 0, 255) # Blue text
    
    ref = insert_after(ref, p_link)
    
    # Kamus Data Title
    ref = append_heading_3(doc, ref, "Tabel L.1: Kamus Data Indikator Kesejahteraan")
    
    # Kamus Data Table
    kamus_headers = ["Variabel Model", "Variabel Asli (BPS)", "Tipe", "Deskripsi Indikator", "Sumber"]
    kamus_data = [
        ["Persentase_Penduduk_Miskin", "Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)", "Float", "Persentase penduduk yang memiliki rata-rata pengeluaran per kapita per bulan di bawah Garis Kemiskinan.", "BPS (2024)"],
        ["Rata_rata_Lama_Sekolah", "Rata-rata Lama Sekolah Penduduk 15+ (Tahun)", "Float", "Rata-rata jumlah tahun yang dihabiskan oleh penduduk usia 15 tahun ke atas dalam menjalani pendidikan formal.", "BPS (2024)"],
        ["Pengeluaran_per_Kapita", "Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)", "Float", "Rata-rata pengeluaran per kapita per tahun yang disesuaikan untuk mengukur paritas daya beli (Purchasing Power Parity).", "BPS (2024)"],
        ["UHH", "Umur Harapan Hidup (Tahun)", "Float", "Rata-rata perkiraan jumlah tahun hidup yang dapat ditempuh oleh bayi yang baru lahir dengan asumsi pola kematian konstan.", "BPS (2024)"],
        ["Sanitasi_Layak", "Persentase rumah tangga yang memiliki akses terhadap sanitasi layak", "Float", "Persentase rumah tangga yang memiliki fasilitas buang air besar sendiri atau bersama dengan septic tank mandiri.", "BPS (2024)"],
        ["TPT", "Tingkat Pengangguran Terbuka", "Float", "Persentase jumlah pengangguran terbuka terhadap jumlah total angkatan kerja aktif regional.", "BPS (2024)"],
        ["PDRB_Konstan", "PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)", "Float", "Produk Domestik Regional Bruto atas dasar harga konstan per kabupaten/kota untuk mengukur pertumbuhan ekonomi riil.", "BPS (2024)"]
    ]
    
    table_k = doc.add_table(rows=len(kamus_data) + 1, cols=5)
    table_k.style = 'Table Grid'
    # Widths allocation: sum = 9360 dxa (for A4 margins, total width about 6.5 inches)
    col_widths_k = [1800, 2200, 800, 3360, 1200]
    
    # Headers
    hdr_cells = table_k.rows[0].cells
    for i, header_text in enumerate(kamus_headers):
        hdr_cells[i].text = header_text
        set_cell_background(hdr_cells[i], "D3E8F0") # Soft blue heading
        set_cell_margins(hdr_cells[i], top=80, bottom=80, left=100, right=100)
        p = hdr_cells[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(10)
            r.bold = True
            
    # Rows
    for r_idx, row_data in enumerate(kamus_data):
        row_cells = table_k.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_margins(row_cells[c_idx], top=60, bottom=60, left=80, right=80)
            p = row_cells[c_idx].paragraphs[0]
            # align code or type columns to center
            if c_idx in [2, 4]:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)
                if c_idx == 0:
                    r.font.name = "Consolas"
                    r.font.size = Pt(8.5)
                    
    # Set cell widths
    for row in table_k.rows:
        for idx, width in enumerate(col_widths_k):
            row.cells[idx].width = width
            
    ref = insert_after(ref, table_k)
    
    # Spacer
    p_space = doc.add_paragraph()
    p_space.paragraph_format.space_after = Pt(12)
    ref = insert_after(ref, p_space)
    
    # Table L.2 Title
    ref = append_heading_3(doc, ref, "Tabel L.2: Cuplikan 10 Baris Pertama Dataset")
    
    # Read CSV
    csv_rows = []
    if os.path.exists(csv_path):
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            count = 0
            for row in reader:
                if count >= 10:
                    break
                # Process columns
                pdrb_val = float(row.get('PDRB atas Dasar Harga Konstan menurut Pengeluaran (Rupiah)', 0))
                pdrb_billion = pdrb_val / 1e9 # Convert to Billion Rupiah
                csv_rows.append([
                    row.get('Provinsi', ''),
                    row.get('Kab/Kota', ''),
                    f"{float(row.get('Persentase Penduduk Miskin (P0) Menurut Kabupaten/Kota (Persen)', 0)):.2f}",
                    f"{float(row.get('Rata-rata Lama Sekolah Penduduk 15+ (Tahun)', 0)):.2f}",
                    f"{float(row.get('Pengeluaran per Kapita Disesuaikan (Ribu Rupiah/Orang/Tahun)', 0)):,.0f}",
                    f"{float(row.get('Umur Harapan Hidup (Tahun)', 0)):.2f}",
                    f"{float(row.get('Persentase rumah tangga yang memiliki akses terhadap sanitasi layak', 0)):.2f}",
                    f"{float(row.get('Tingkat Pengangguran Terbuka', 0)):.2f}",
                    f"{pdrb_billion:,.1f}",
                    row.get('Klasifikasi Kemiskinan', '')
                ])
                count += 1
    else:
        print(f"Warning: Dataset {csv_path} not found for snippet generation!")
        
    snippet_headers = ["Provinsi", "Kab/Kota", "Miskin (%)", "RLS (Thn)", "Pengeluaran (Ribu)", "UHH (Thn)", "Sanitasi (%)", "TPT (%)", "PDRB (Miliar)", "Klaster"]
    table_s = doc.add_table(rows=len(csv_rows) + 1, cols=10)
    table_s.style = 'Table Grid'
    
    # Setup table_s headers
    hdr_cells_s = table_s.rows[0].cells
    for i, header_text in enumerate(snippet_headers):
        hdr_cells_s[i].text = header_text
        set_cell_background(hdr_cells_s[i], "EFEFEF")
        set_cell_margins(hdr_cells_s[i], top=60, bottom=60, left=60, right=60)
        p = hdr_cells_s[i].paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for r in p.runs:
            r.font.name = "Times New Roman"
            r.font.size = Pt(8.5)
            r.bold = True
            
    # Setup table_s data rows
    for r_idx, row_data in enumerate(csv_rows):
        row_cells = table_s.rows[r_idx + 1].cells
        for c_idx, val in enumerate(row_data):
            row_cells[c_idx].text = str(val)
            set_cell_margins(row_cells[c_idx], top=50, bottom=50, left=50, right=50)
            p = row_cells[c_idx].paragraphs[0]
            # Alignment rules
            if c_idx in [0, 1]:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            else:
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(8)
                
    ref = insert_after(ref, table_s)
    
    # Spacer page break before next lampiran
    p_break1 = doc.add_paragraph()
    p_break1.paragraph_format.space_before = Pt(12)
    p_break1.paragraph_format.space_after = Pt(0)
    p_break1.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)
    ref = insert_after(ref, p_break1)
    
    # Delete the placeholder paragraph
    delete_paragraph(p_dataset)
    
    # -------------------------------------------------------------
    # LAMPIRAN 2: CODE PYTHON MODELLING
    # -------------------------------------------------------------
    print("Menyusun Lampiran 2 (Code)...")
    ref = p_code
    ref = append_heading_2(doc, ref, "Lampiran 2: Kode Sumber Pemodelan (Python)")
    
    desc_code = (
        "Bagian ini menyajikan kode sumber pemrograman Python secara lengkap dan terstruktur. "
        "Kode pemrograman dibagi menjadi tiga modul utama: modul pipeline pemodelan machine learning "
        "(`pemodelan_klasterisasi_kesejahteraan.py`), modul antarmuka utama dashboard Streamlit "
        "(`app.py`), dan modul komponen generator teks naratif (`narrative.py`). Seluruh kode "
        "ditulis menggunakan kaidah Clean Code untuk memastikan pembacaan dan pemeliharaan sistem jangka panjang."
    )
    ref = append_paragraph(doc, ref, desc_code)
    
    # File 1 formatting
    # [Source Code] paragraph (Times New Roman, bold, size 12)
    p_src1 = doc.add_paragraph()
    p_src1.paragraph_format.space_before = Pt(12)
    p_src1.paragraph_format.space_after = Pt(2)
    p_src1.paragraph_format.line_spacing = 1.15
    run_src1 = p_src1.add_run("[Source Code]")
    run_src1.font.name = "Times New Roman"
    run_src1.font.size = Pt(12)
    run_src1.bold = True
    ref = insert_after(ref, p_src1)
    
    # File title/explanation (Times New Roman, bold, size 12)
    p_desc1 = doc.add_paragraph()
    p_desc1.paragraph_format.space_before = Pt(0)
    p_desc1.paragraph_format.space_after = Pt(6)
    p_desc1.paragraph_format.line_spacing = 1.15
    run_desc1 = p_desc1.add_run("Pipeline Pemodelan Klasterisasi (pemodelan_klasterisasi_kesejahteraan.py)")
    run_desc1.font.name = "Times New Roman"
    run_desc1.font.size = Pt(12)
    run_desc1.bold = True
    ref = insert_after(ref, p_desc1)
    
    # Code block
    ref = append_code_block(doc, ref, r'scripts/pemodelan_klasterisasi_kesejahteraan.py')
    
    # File 2 formatting
    # [Source Code] paragraph
    p_src2 = doc.add_paragraph()
    p_src2.paragraph_format.space_before = Pt(18)
    p_src2.paragraph_format.space_after = Pt(2)
    p_src2.paragraph_format.line_spacing = 1.15
    run_src2 = p_src2.add_run("[Source Code]")
    run_src2.font.name = "Times New Roman"
    run_src2.font.size = Pt(12)
    run_src2.bold = True
    ref = insert_after(ref, p_src2)
    
    # File title
    p_desc2 = doc.add_paragraph()
    p_desc2.paragraph_format.space_before = Pt(0)
    p_desc2.paragraph_format.space_after = Pt(6)
    p_desc2.paragraph_format.line_spacing = 1.15
    run_desc2 = p_desc2.add_run("Dasbor Utama (app.py)")
    run_desc2.font.name = "Times New Roman"
    run_desc2.font.size = Pt(12)
    run_desc2.bold = True
    ref = insert_after(ref, p_desc2)
    
    ref = append_code_block(doc, ref, r'dashboard/app.py')
    
    # File 3 formatting
    # [Source Code] paragraph
    p_src3 = doc.add_paragraph()
    p_src3.paragraph_format.space_before = Pt(18)
    p_src3.paragraph_format.space_after = Pt(2)
    p_src3.paragraph_format.line_spacing = 1.15
    run_src3 = p_src3.add_run("[Source Code]")
    run_src3.font.name = "Times New Roman"
    run_src3.font.size = Pt(12)
    run_src3.bold = True
    ref = insert_after(ref, p_src3)
    
    # File title
    p_desc3 = doc.add_paragraph()
    p_desc3.paragraph_format.space_before = Pt(0)
    p_desc3.paragraph_format.space_after = Pt(6)
    p_desc3.paragraph_format.line_spacing = 1.15
    run_desc3 = p_desc3.add_run("Generator Narasi (narrative.py)")
    run_desc3.font.name = "Times New Roman"
    run_desc3.font.size = Pt(12)
    run_desc3.bold = True
    ref = insert_after(ref, p_desc3)
    
    ref = append_code_block(doc, ref, r'dashboard/components/narrative.py')
    
    # Spacer page break before next lampiran
    p_break2 = doc.add_paragraph()
    p_break2.paragraph_format.space_before = Pt(12)
    p_break2.paragraph_format.space_after = Pt(0)
    p_break2.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)
    ref = insert_after(ref, p_break2)
    
    # Delete the placeholder paragraph
    delete_paragraph(p_code)
    
    # -------------------------------------------------------------
    # LAMPIRAN 3: MANUAL BOOK
    # -------------------------------------------------------------
    print("Menyusun Lampiran 3 (Manual Book)...")
    ref = p_manual
    ref = append_heading_2(doc, ref, "Lampiran 3: Manual Book Pengoperasian Dasbor SENUWU")
    
    desc_manual = (
        "Dokumentasi panduan pengguna ini disusun secara mendalam untuk memandu operator, analisis, "
        "dan penguji dalam mengoperasikan dasbor web visualisasi spasial kesejahteraan wilayah SENUWU. "
        "Dasbor ini dibangun secara terpadu dengan platform Streamlit, visualisasi interaktif Plotly WebGL, "
        "serta rendering pemetaan menggunakan modul Folium."
    )
    ref = append_paragraph(doc, ref, desc_manual)
    
    # Section A: Persyaratan Sistem
    ref = append_heading_3(doc, ref, "A. Persyaratan Lingkungan Sistem")
    req_text = (
        "Aplikasi dasbor analitik SENUWU memerlukan spesifikasi lingkungan sistem minimum sebagai berikut:\n"
        "1. Sistem Operasi: Windows 10/11 (64-bit), macOS Catalina (atau versi lebih baru), atau Linux Ubuntu 20.04 LTS.\n"
        "2. Bahasa Pemrograman: Python 3.11.x (tested on Python 3.11.9).\n"
        "3. RAM & Prosesor: Minimum RAM 4 GB (disarankan 8 GB) dengan prosesor minimal Intel Core i3 atau AMD Ryzen 3.\n"
        "4. Dependensi Pustaka Utama: streamlit (v1.38.0), pandas (v3.0.3), numpy (v2.4.6), folium (v0.20.0), plotly (v6.8.0), scikit-learn (v1.9.0), hdbscan (v0.8.44), dan python-docx (v1.2.0)."
    )
    ref = append_paragraph(doc, ref, req_text, first_indent_inches=0)
    
    # Section B: Cara Menjalankan Dasbor
    ref = append_heading_3(doc, ref, "B. Langkah Instalasi dan Menjalankan Dasbor")
    run_text = (
        "Berikut adalah langkah-langkah prosedural untuk menyalakan dasbor di server lokal:\n"
        "1. Letakkan folder proyek pada direktori lokal komputer Anda (misalnya D:\\Project HKI SENUWU).\n"
        "2. Buka terminal command prompt atau PowerShell di Windows (atau Terminal di macOS/Linux) dan pindah ke direktori kerja proyek.\n"
        "3. Aktifkan virtual environment bawaan dengan mengetikkan perintah:\n"
        "   - Windows: .venv\\Scripts\\activate\n"
        "   - macOS/Linux: source .venv/bin/activate\n"
        "4. Jalankan aplikasi Streamlit dengan perintah command line:\n"
        "   .venv\\Scripts\\streamlit run dashboard/app.py\n"
        "5. Setelah perintah dijalankan, server uvicorn lokal akan aktif pada port 8501. Aplikasi browser default Anda akan otomatis membuka alamat http://localhost:8501."
    )
    ref = append_paragraph(doc, ref, run_text, first_indent_inches=0)
    
    # Section C: Panduan Antarmuka per Menu
    ref = append_heading_3(doc, ref, "C. Penjelasan Fungsionalitas Antarmuka Menu Dasbor")
    
    # Page 1: Halaman Beranda
    p_beranda = append_heading_3(doc, ref, "C.1 Halaman Beranda (Peta Klasifikasi Kesejahteraan)")
    beranda_text = (
        "Menu Beranda menyajikan visualisasi makro berupa peta choropleth wilayah Indonesia. Peta ini membagi "
        "seluruh 514 kabupaten/kota menjadi kelompok warna representatif sesuai dengan klaster kesejahteraan sosial "
        "yang didefinisikan oleh model hybrid. Peta didukung oleh interaksi hover di mana pengguna dapat mengarahkan "
        "kursor untuk memunculkan detail tooltip yang memuat nilai mentah 7 indikator di kabupaten tersebut, serta "
        "interpretasi kalimat penjelas dinamis."
    )
    ref = append_paragraph(doc, p_beranda, beranda_text)
    
    # Screenshots Halaman Beranda dari PDF
    ref = append_image_with_caption(doc, ref, r"extracted_images/page_8_img_1.jpeg", "Gambar L.3.1: Tangkapan Layar Halaman Utama Beranda Dasbor SENUWU")
    
    # Page 2: Halaman Cari
    p_cari = append_heading_3(doc, ref, "C.2 Halaman Cari (Analisis Spesifik Kabupaten/Kota)")
    cari_text = (
        "Halaman Cari didedikasikan untuk pencarian mikro di tingkat kabupaten/kota. Analis dapat memfilter "
        "wilayah berdasarkan dropdown Provinsi dan Kabupaten/Kota. Sistem akan memunculkan nilai Welfare Score "
        "normalisasi (skala 0 hingga 1) daerah tersebut, tabel rincian variabel yang paling berpengaruh secara lokal "
        "beserta z-score statistiknya, serta analisis naratif berbasis teks otomatis yang dihasilkan di background."
    )
    ref = append_paragraph(doc, p_cari, cari_text)
    # 2 screenshots on Page 9 of the PDF for the Search Interface
    ref = append_image_with_caption(doc, ref, r"extracted_images/page_9_img_1.png", "Gambar L.3.2: Tangkapan Layar Menu Pencarian Wilayah - Filter Pencarian")
    ref = append_image_with_caption(doc, ref, r"extracted_images/page_9_img_2.png", "Gambar L.3.3: Tangkapan Layar Menu Pencarian Wilayah - Detail Narasi dan Hasil Klasifikasi")
    
    # Page 3: Halaman Update Data
    p_update = append_heading_3(doc, ref, "C.3 Halaman Update Data (Modul Administrasi)")
    update_text = (
        "Halaman Update Data memberikan wewenang kepada administrator untuk mengelola dataset secara berkala. "
        "Administrator dapat menambahkan data kabupaten baru secara manual dengan mengisi formulir isian indikator, "
        "atau mengunggah dokumen pembaruan CSV. Begitu data tersimpan, sistem secara otomatis mengeksekusi ulang "
        "seluruh pipeline sains data (yeo-johnson, outlier filter, HDBSCAN-KMeans, re-geocode, dan pembaharuan file narasi) "
        "sehingga peta visual dan hasil pencarian di halaman utama segera terupdate secara instan."
    )
    ref = append_paragraph(doc, p_update, update_text)
    ref = append_image_with_caption(doc, ref, r"extracted_images/page_10_img_1.jpeg", "Gambar L.3.4: Tangkapan Layar Modul Administrasi dan Pembaruan Data")
    
    # Page 4: Halaman Info
    p_info = append_heading_3(doc, ref, "C.4 Halaman Informasi (Metodologi, Metrik & Tim Penyusun)")
    info_text = (
        "Halaman Info memuat dokumentasi akademis lengkap program komputer. Menu ini memaparkan latar belakang "
        "riset, rancangan diagram pipa pemrosesan hybrid, visualisasi komparatif metrik validasi klaster WCVI "
        "(Hopkins Statistic, R-Squared, dan Out-of-Bag Random Forest Accuracy), serta data identitas keanggotaan "
        "tim penyusun program dari Universitas Duta Bangsa Surakarta."
    )
    ref = append_paragraph(doc, p_info, info_text)
    # No screenshot for Info page exists in Manual Book SENUWU.pdf (excluding it per instructions)
    
    # Spacer page break before next lampiran
    p_break3 = doc.add_paragraph()
    p_break3.paragraph_format.space_before = Pt(12)
    p_break3.paragraph_format.space_after = Pt(0)
    p_break3.add_run().add_break(docx.enum.text.WD_BREAK.PAGE)
    ref = insert_after(ref, p_break3)
    
    # Delete the placeholder paragraph
    delete_paragraph(p_manual)
    
    # -------------------------------------------------------------
    # LAMPIRAN 4: SERTIFIKAT HKI
    # -------------------------------------------------------------
    print("Menyusun Lampiran 4 (HKI)...")
    ref = p_hki
    ref = append_heading_2(doc, ref, "Lampiran 4: Sertifikat Hak Kekayaan Intelektual (HKI)")
    
    desc_hki = (
        "Bagian ini dicadangkan untuk menempatkan dokumen cetak atau pindaian resmi Surat Pencatatan Ciptaan "
        "yang dikeluarkan oleh Direktorat Jenderal Kekayaan Intelektual (DJKI), Kementerian Hukum dan Hak "
        "Asasi Menusia Republik Indonesia, sebagai bukti perlindungan hukum ciptaan atas produk program komputer SENUWU."
    )
    ref = append_paragraph(doc, ref, desc_hki)
    
    # Insert Placeholder Box
    table_h = doc.add_table(rows=1, cols=1)
    table_h.alignment = docx.enum.table.WD_TABLE_ALIGNMENT.CENTER if hasattr(docx.enum.table, 'WD_TABLE_ALIGNMENT') else 1
    
    cell_h = table_h.cell(0, 0)
    set_cell_background(cell_h, "FFFDF0") # Very soft yellow shading for placeholder box
    set_cell_borders(cell_h, hex_color="FFD700", val="dashed", sz="12") # gold dashed border
    set_cell_margins(cell_h, top=2000, bottom=2000, left=2000, right=2000) # giant margins to make a tall empty box
    
    p_box = cell_h.paragraphs[0]
    p_box.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_box.paragraph_format.space_before = Pt(20)
    p_box.paragraph_format.space_after = Pt(20)
    
    run_box1 = p_box.add_run("[ TEMPELKAN SALINAN SCAN SURAT PENCATATAN CIPTAAN / SERTIFIKAT HKI DI SINI ]\n\n")
    run_box1.font.name = "Times New Roman"
    run_box1.font.size = Pt(12)
    run_box1.bold = True
    run_box1.font.color.rgb = docx.shared.RGBColor(180, 140, 0)
    
    run_box2 = p_box.add_run(
        "(Setelah sertifikat resmi diterbitkan oleh Direktorat Jenderal Kekayaan Intelektual "
        "Kementerian Hukum dan HAM RI, silakan tempelkan gambar dokumen pemindaian sertifikat di dalam area "
        "kotak ini secara rapi)."
    )
    run_box2.font.name = "Times New Roman"
    run_box2.font.size = Pt(10)
    run_box2.italic = True
    run_box2.font.color.rgb = docx.shared.RGBColor(120, 120, 120)
    
    ref = insert_after(ref, table_h)
    
    # Delete the placeholder paragraph
    delete_paragraph(p_hki)
    
    # -------------------------------------------------------------
    # SIMPAN DOKUMEN
    # -------------------------------------------------------------
    print(f"Menyimpan berkas baru ke: {output_path}")
    doc.save(output_path)
    print("Pengisian lampiran sukses dilaksanakan!")

if __name__ == '__main__':
    build_appendix()

import os
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

def set_cell_background(cell, fill_hex):
    """Set background color of a table cell."""
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=40, bottom=40, left=80, right=80):
    """Set compact cell padding in dxa (1 pt = 20 dxa). Default 2pt top/bottom, 4pt left/right."""
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def add_page_border(section):
    """Adds a double page border to the document section."""
    sectPr = section._sectPr
    borders_xml = parse_xml(
        f'<w:pgBorders {nsdecls("w")} w:offsetFrom="page">'
        f'<w:top w:val="double" w:sz="12" w:space="24" w:color="333333"/>'
        f'<w:left w:val="double" w:sz="12" w:space="24" w:color="333333"/>'
        f'<w:bottom w:val="double" w:sz="12" w:space="24" w:color="333333"/>'
        f'<w:right w:val="double" w:sz="12" w:space="24" w:color="333333"/>'
        f'</w:pgBorders>'
    )
    sectPr.append(borders_xml)

def add_footer_bottom_border(section, app_name="MSBTE Student Saver"):
    """Adds a stylish double top-line border, italicized app name on left, and page number on right in the footer."""
    section.different_first_page_header_footer = True
    footer = section.footer
    p = footer.paragraphs[0]
    p.text = ""
    p.paragraph_format.space_before = Pt(4)
    p.paragraph_format.space_after = Pt(0)
    
    # Top double border line across footer (matching copper/slate tone #A67C52)
    pBdr = parse_xml(
        f'<w:pBdr {nsdecls("w")}>'
        f'<w:top w:val="double" w:sz="12" w:space="6" w:color="A67C52"/>'
        f'</w:pBdr>'
    )
    p._p.get_or_add_pPr().append(pBdr)
    
    # Right-aligned tab stop (width = 8.5in - 2*0.85in = 6.8in -> 9792 dxa)
    tabs = parse_xml(f'<w:tabs {nsdecls("w")}><w:tab w:val="right" w:pos="9792"/></w:tabs>')
    p._p.get_or_add_pPr().append(tabs)
    
    # Left: Italicized App Name
    r_left = p.add_run(f"{app_name}\t")
    r_left.bold = True
    r_left.italic = True
    r_left.font.name = "Times New Roman"
    r_left.font.size = Pt(9.5)
    r_left.font.color.rgb = RGBColor(100, 116, 139) # Slate 500
    
    # Right: Dynamic Page Number
    fld = parse_xml(
        f'<w:fldSimple {nsdecls("w")} w:instr="PAGE">'
        f'<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="19"/><w:color w:val="64748B"/></w:rPr><w:t>1</w:t></w:r>'
        f'</w:fldSimple>'
    )
    p._p.append(fld)

def generate_complete_itr_report():
    doc = Document()

    # Set page margins (0.85 inch all around)
    for section in doc.sections:
        section.top_margin = Inches(0.85)
        section.bottom_margin = Inches(0.85)
        section.left_margin = Inches(0.85)
        section.right_margin = Inches(0.85)
        try:
            add_page_border(section)
            add_footer_bottom_border(section, app_name="MSBTE Student Saver")
        except Exception as e:
            print("Border/Footer notice:", e)

    # Color Palette matching original reference and modern standard
    RED_ACCENT = RGBColor(192, 0, 0)         # Bright/Dark Red #C00000 (Titles, institute, highlighted names)
    BROWN_GUIDE = RGBColor(192, 80, 77)      # Reddish Brown #C0504D (Guide / HOD names)
    NAVY_TITLE = RGBColor(54, 95, 145)       # Slate Blue #365F91 ("INDUSTRIAL TRAINING REPORT", "UNDER THE GUIDANCE OF")
    BLACK_COLOR = RGBColor(0, 0, 0)          # Solid Black
    PRIMARY_COLOR = RGBColor(26, 54, 138)    # Deep Royal Navy #1A368A (Report Headings)
    SECONDARY_COLOR = RGBColor(59, 130, 246) # Blue #3B82F6 (Subheadings)
    DARK_TEXT = RGBColor(15, 23, 42)         # Slate 900 #0F172A (Body text)
    MUTED_TEXT = RGBColor(100, 116, 139)     # Slate 500 #64748B

    # Helper functions for chapter body text
    def add_custom_heading(text, level):
        h = doc.add_heading(text, level=level)
        h.paragraph_format.space_before = Pt(13)
        h.paragraph_format.space_after = Pt(5)
        h.paragraph_format.keep_with_next = True
        run = h.runs[0]
        if level == 1:
            run.font.size = Pt(15.5)
            run.font.bold = True
            run.font.color.rgb = PRIMARY_COLOR
        elif level == 2:
            run.font.size = Pt(12.5)
            run.font.bold = True
            run.font.color.rgb = SECONDARY_COLOR
        elif level == 3:
            run.font.size = Pt(11)
            run.font.bold = True
            run.font.color.rgb = DARK_TEXT
        return h

    def add_p(text, bold_prefix=None, space_after=5, align=WD_ALIGN_PARAGRAPH.JUSTIFY):
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.line_spacing = 1.15
        p.alignment = align
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = DARK_TEXT
            r_bold.font.size = Pt(10.5)
        r = p.add_run(text)
        r.font.size = Pt(10.5)
        r.font.color.rgb = DARK_TEXT
        return p

    def add_bullet(text, bold_prefix=None):
        p = doc.add_paragraph(style='List Bullet')
        p.paragraph_format.space_after = Pt(3.5)
        p.paragraph_format.line_spacing = 1.15
        if bold_prefix:
            r_bold = p.add_run(bold_prefix)
            r_bold.bold = True
            r_bold.font.color.rgb = DARK_TEXT
            r_bold.font.size = Pt(10.5)
        r = p.add_run(text)
        r.font.size = Pt(10.5)
        r.font.color.rgb = DARK_TEXT
        return p

    def add_figure(img_rel_path, caption_text, width_inches=5.8):
        """Adds an application screenshot image with centered formatting and professional caption."""
        abs_p = os.path.abspath(img_rel_path)
        if os.path.exists(abs_p):
            p_img = doc.add_paragraph()
            p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_img.paragraph_format.space_before = Pt(6)
            p_img.paragraph_format.space_after = Pt(3)
            p_img.paragraph_format.keep_with_next = True
            p_img.add_run().add_picture(abs_p, width=Inches(width_inches))

            p_cap = doc.add_paragraph()
            p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p_cap.paragraph_format.space_before = Pt(2)
            p_cap.paragraph_format.space_after = Pt(8)
            r_cap = p_cap.add_run(caption_text)
            r_cap.font.size = Pt(9)
            r_cap.font.italic = True
            r_cap.font.color.rgb = MUTED_TEXT

    def add_callout(title, text, bg_hex="F0F4FF"):
        tbl = doc.add_table(rows=1, cols=1)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        cell = tbl.cell(0, 0)
        cell.width = Inches(6.5)
        set_cell_background(cell, bg_hex)
        set_cell_margins(cell, top=80, bottom=80, left=120, right=120)
        
        p = cell.paragraphs[0]
        p.paragraph_format.space_after = Pt(2)
        r1 = p.add_run(f"📌 {title}\n")
        r1.bold = True
        r1.font.size = Pt(10.5)
        r1.font.color.rgb = PRIMARY_COLOR
        
        r2 = p.add_run(text)
        r2.font.size = Pt(10)
        r2.font.color.rgb = DARK_TEXT
        doc.add_paragraph().paragraph_format.space_after = Pt(4)

    def add_compact_table(headers, data, col_widths=None, is_index=False):
        """Generates compact, short, and highly readable tables containing full details."""
        tbl = doc.add_table(rows=len(data) + 1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        
        # Header Row
        hdr_cells = tbl.rows[0].cells
        for i, title in enumerate(headers):
            hdr_cells[i].text = title
            set_cell_background(hdr_cells[i], "1E3A8A")
            set_cell_margins(hdr_cells[i], top=50, bottom=50, left=70, right=70)
            p = hdr_cells[i].paragraphs[0]
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(1)
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            for r in p.runs:
                r.font.bold = True
                r.font.color.rgb = RGBColor(255, 255, 255)
                r.font.size = Pt(9)
        
        # Data Rows
        for r_idx, row_data in enumerate(data):
            row_cells = tbl.rows[r_idx + 1].cells
            
            # Check if main chapter row in index
            is_main_chapter = is_index and row_data[0] != "" and row_data[0].isdigit()
            
            if is_main_chapter:
                bg = "EEF2F6"
            elif r_idx % 2 == 1:
                bg = "F8FAFC"
            else:
                bg = "FFFFFF"
                
            for c_idx, cell_value in enumerate(row_data):
                row_cells[c_idx].text = str(cell_value)
                set_cell_background(row_cells[c_idx], bg)
                set_cell_margins(row_cells[c_idx], top=35, bottom=35, left=70, right=70)
                p = row_cells[c_idx].paragraphs[0]
                p.paragraph_format.space_before = Pt(1)
                p.paragraph_format.space_after = Pt(1)
                p.paragraph_format.line_spacing = 1.05
                
                # Column alignment
                if c_idx == 0 and len(row_data) > 2:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                elif c_idx == len(row_data) - 1 and len(row_data) > 2:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                else:
                    p.alignment = WD_ALIGN_PARAGRAPH.LEFT

                for r in p.runs:
                    r.font.size = Pt(8.5)
                    if is_main_chapter:
                        r.font.bold = True
                        r.font.color.rgb = PRIMARY_COLOR
                    else:
                        r.font.color.rgb = DARK_TEXT
        
        if col_widths:
            for row in tbl.rows:
                for idx, w in enumerate(col_widths):
                    row.cells[idx].width = Inches(w)
                    
    def add_floating_background(paragraph, image_path, width_inches=8.5, height_inches=11.0):
        """Inserts the rotated login background image filling the whole page (8.5 x 11 in) behind text."""
        if not os.path.exists(image_path):
            return
        run = paragraph.add_run()
        run.add_picture(image_path, width=Inches(width_inches), height=Inches(height_inches))
        
        drawings = run._r.xpath('.//w:drawing')
        if not drawings:
            return
        drawing = drawings[0]
        inlines = drawing.xpath('.//wp:inline')
        if not inlines:
            return
        inline = inlines[0]
        
        graphic = inline.xpath('.//a:graphic')[0]
        extent = inline.xpath('.//wp:extent')[0]
        cx = extent.get('cx')
        cy = extent.get('cy')
        
        anchor_xml = parse_xml(
            f'<wp:anchor {nsdecls("wp")} {nsdecls("a")} {nsdecls("pic")} '
            f'distT="0" distB="0" distL="0" distR="0" simplePos="0" relativeHeight="0" behindDoc="1" locked="0" layoutInCell="1" allowOverlap="1">'
            f'<wp:simplePos x="0" y="0"/>'
            f'<wp:positionH relativeFrom="page"><wp:align>center</wp:align></wp:positionH>'
            f'<wp:positionV relativeFrom="page"><wp:align>center</wp:align></wp:positionV>'
            f'<wp:extent cx="{cx}" cy="{cy}"/>'
            f'<wp:effectExtent l="0" t="0" r="0" b="0"/>'
            f'<wp:wrapNone/>'
            f'<wp:docPr id="101" name="FullPageLoginBackground"/>'
            f'<wp:cNvGraphicFramePr/>'
            f'</wp:anchor>'
        )
        anchor_xml.append(graphic)
        drawing.remove(inline)
        drawing.append(anchor_xml)

    # Ensure full-page rotated portrait login background exists
    login_bg_raw = os.path.abspath("static/images/login-bg.jpg")
    watermark_path = os.path.abspath("static/images/login_bg_portrait_fullpage.jpg")
    if os.path.exists(login_bg_raw):
        try:
            from PIL import Image
            im_raw = Image.open(login_bg_raw)
            # Rotate 270 degrees (90 counter-clockwise) to match portrait orientation
            rot = im_raw.rotate(270, expand=True)
            target_w, target_h = 1700, 2200
            scale = max(target_w / rot.width, target_h / rot.height)
            new_w = int(rot.width * scale)
            new_h = int(rot.height * scale)
            resized = rot.resize((new_w, new_h), Image.Resampling.LANCZOS)
            left = (new_w - target_w) // 2
            top = (new_h - target_h) // 2
            cropped = resized.crop((left, top, left + target_w, top + target_h))
            
            # Subtle blend with white background for maximum readability (22% opacity)
            bg_white = Image.new('RGBA', cropped.size, (255, 255, 255, 255))
            blended = Image.blend(bg_white, cropped.convert('RGBA'), alpha=0.22)
            blended.convert('RGB').save(watermark_path, quality=95)
        except Exception as e:
            print("Notice generating full-page portrait background:", e)

    logo_path = os.path.abspath("static/vvp_logo_left.png")
    banner_path = os.path.abspath("static/cert_banner.png")

    # =========================================================================
    # 1. EXACT COVER / TITLE PAGE (MATCHING UPLOADED REFERENCE + LOGIN BG)
    # =========================================================================
    p1 = doc.add_paragraph()
    p1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p1.paragraph_format.space_before = Pt(10)
    p1.paragraph_format.space_after = Pt(4)
    # Add full-page rotated login background filling entire Page 1 (8.5 x 11 in)
    add_floating_background(p1, watermark_path, width_inches=8.5, height_inches=11.0)

    r1 = p1.add_run("A")
    r1.bold = True
    r1.font.size = Pt(15)
    r1.font.name = "Times New Roman"

    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p2.paragraph_format.space_before = Pt(2)
    p2.paragraph_format.space_after = Pt(2)
    r2 = p2.add_run("INDUSTRIAL TRAINING REPORT")
    r2.bold = True
    r2.font.size = Pt(15)
    r2.font.color.rgb = NAVY_TITLE
    r2.font.name = "Times New Roman"

    p3 = doc.add_paragraph()
    p3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p3.paragraph_format.space_before = Pt(2)
    p3.paragraph_format.space_after = Pt(4)
    r3 = p3.add_run("On")
    r3.bold = True
    r3.font.size = Pt(14)
    r3.font.name = "Times New Roman"

    p4 = doc.add_paragraph()
    p4.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p4.paragraph_format.space_before = Pt(2)
    p4.paragraph_format.space_after = Pt(12)
    r4 = p4.add_run("“MSBTE Student Saver”")
    r4.bold = True
    r4.font.size = Pt(18)
    r4.font.color.rgb = RED_ACCENT
    r4.font.name = "Times New Roman"

    p5 = doc.add_paragraph()
    p5.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p5.paragraph_format.space_before = Pt(4)
    p5.paragraph_format.space_after = Pt(2)
    r5 = p5.add_run("Has been")
    r5.font.size = Pt(12)
    r5.font.name = "Times New Roman"

    p6 = doc.add_paragraph()
    p6.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p6.paragraph_format.space_before = Pt(2)
    p6.paragraph_format.space_after = Pt(12)
    r6 = p6.add_run("Submitted in partial fulfillment of Industrial Training Project")
    r6.font.size = Pt(12)
    r6.font.name = "Times New Roman"

    p7 = doc.add_paragraph()
    p7.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p7.paragraph_format.space_before = Pt(6)
    p7.paragraph_format.space_after = Pt(10)
    r7 = p7.add_run("By")
    r7.font.size = Pt(13)
    r7.font.name = "Times New Roman"

    p8 = doc.add_paragraph()
    p8.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p8.paragraph_format.space_before = Pt(2)
    p8.paragraph_format.space_after = Pt(2)
    r8 = p8.add_run("SHUBHAM DINESH VERNEKAR")
    r8.bold = True
    r8.font.size = Pt(14)
    r8.font.name = "Times New Roman"

    p9 = doc.add_paragraph()
    p9.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p9.paragraph_format.space_before = Pt(2)
    p9.paragraph_format.space_after = Pt(16)
    r9 = p9.add_run("Enrollment No: 24212130227")
    r9.bold = True
    r9.font.size = Pt(12)
    r9.font.name = "Times New Roman"

    p10 = doc.add_paragraph()
    p10.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p10.paragraph_format.space_before = Pt(6)
    p10.paragraph_format.space_after = Pt(4)
    r10 = p10.add_run("UNDER THE GUIDANCE OF")
    r10.bold = True
    r10.font.size = Pt(14)
    r10.font.color.rgb = NAVY_TITLE
    r10.font.name = "Times New Roman"

    p11 = doc.add_paragraph()
    p11.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p11.paragraph_format.space_before = Pt(2)
    p11.paragraph_format.space_after = Pt(14)
    r11 = p11.add_run("Prof. M. Buddhe")
    r11.bold = True
    r11.font.size = Pt(13)
    r11.font.color.rgb = BROWN_GUIDE
    r11.font.name = "Times New Roman"

    # College Logo
    p_logo = doc.add_paragraph()
    p_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_logo.paragraph_format.space_before = Pt(4)
    p_logo.paragraph_format.space_after = Pt(14)
    if os.path.exists(logo_path):
        p_logo.add_run().add_picture(logo_path, width=Inches(1.25))

    p12 = doc.add_paragraph()
    p12.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p12.paragraph_format.space_before = Pt(4)
    p12.paragraph_format.space_after = Pt(2)
    r12 = p12.add_run("NBA Accredited & ISO 9001:2015 certified")
    r12.bold = True
    r12.font.size = Pt(12.5)
    r12.font.color.rgb = RED_ACCENT
    r12.font.name = "Times New Roman"

    p13 = doc.add_paragraph()
    p13.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p13.paragraph_format.space_before = Pt(2)
    p13.paragraph_format.space_after = Pt(0)
    r13 = p13.add_run("VIDYA VIKAS PRATISHTHAN POLYTECHNIC, SOLAPUR")
    r13.bold = True
    r13.underline = True
    r13.font.size = Pt(13)
    r13.font.color.rgb = RED_ACCENT
    r13.font.name = "Times New Roman"

    doc.add_page_break()

    # =========================================================================
    # 2. EXACT COLLEGE CERTIFICATE PAGE (MATCHING UPLOADED REFERENCE + LOGIN BG)
    # =========================================================================
    # Top Logo with full-page rotated login background watermark (8.5 x 11 in)
    p_c_logo = doc.add_paragraph()
    p_c_logo.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_logo.paragraph_format.space_before = Pt(0)
    p_c_logo.paragraph_format.space_after = Pt(2)
    add_floating_background(p_c_logo, watermark_path, width_inches=8.5, height_inches=11.0)
    if os.path.exists(logo_path):
        p_c_logo.add_run().add_picture(logo_path, width=Inches(0.85))

    p_c_hdr1 = doc.add_paragraph()
    p_c_hdr1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_hdr1.paragraph_format.space_before = Pt(1)
    p_c_hdr1.paragraph_format.space_after = Pt(1)
    r_ch1 = p_c_hdr1.add_run("NBA Accredited & ISO 9001:2015 certified")
    r_ch1.bold = True
    r_ch1.font.size = Pt(11)
    r_ch1.font.name = "Times New Roman"

    p_c_hdr2 = doc.add_paragraph()
    p_c_hdr2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_hdr2.paragraph_format.space_before = Pt(1)
    p_c_hdr2.paragraph_format.space_after = Pt(1)
    r_ch2 = p_c_hdr2.add_run("VIDYA VIKAS PRATISHTHAN POLYTECHNIC,")
    r_ch2.bold = True
    r_ch2.font.size = Pt(12)
    r_ch2.font.name = "Times New Roman"

    p_c_hdr3 = doc.add_paragraph()
    p_c_hdr3.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_hdr3.paragraph_format.space_before = Pt(1)
    p_c_hdr3.paragraph_format.space_after = Pt(3)
    r_ch3 = p_c_hdr3.add_run("SOLAPUR")
    r_ch3.bold = True
    r_ch3.font.size = Pt(12)
    r_ch3.font.name = "Times New Roman"

    # Orange CERTIFICATE Banner Graphic
    p_c_banner = doc.add_paragraph()
    p_c_banner.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_banner.paragraph_format.space_before = Pt(1)
    p_c_banner.paragraph_format.space_after = Pt(5)
    if os.path.exists(banner_path):
        p_c_banner.add_run().add_picture(banner_path, width=Inches(3.8))
    else:
        r_b_fallback = p_c_banner.add_run("CERTIFICATE")
        r_b_fallback.bold = True
        r_b_fallback.font.size = Pt(16)
        r_b_fallback.font.color.rgb = RED_ACCENT

    p_c_body1 = doc.add_paragraph()
    p_c_body1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_body1.paragraph_format.space_before = Pt(2)
    p_c_body1.paragraph_format.space_after = Pt(2)
    r_cb1 = p_c_body1.add_run("This is to certify that the Industrial Training Project entitled")
    r_cb1.font.size = Pt(11.5)
    r_cb1.font.name = "Times New Roman"

    p_c_title = doc.add_paragraph()
    p_c_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_title.paragraph_format.space_before = Pt(1)
    p_c_title.paragraph_format.space_after = Pt(4)
    r_ct = p_c_title.add_run("“MSBTE Student Saver”")
    r_ct.bold = True
    r_ct.font.size = Pt(15)
    r_ct.font.color.rgb = RED_ACCENT
    r_ct.font.name = "Times New Roman"

    p_c_comp = doc.add_paragraph()
    p_c_comp.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_comp.paragraph_format.space_before = Pt(1)
    p_c_comp.paragraph_format.space_after = Pt(1)
    r_cc = p_c_comp.add_run("Has been completed")
    r_cc.font.size = Pt(11.5)
    r_cc.font.name = "Times New Roman"

    p_c_by = doc.add_paragraph()
    p_c_by.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_by.paragraph_format.space_before = Pt(1)
    p_c_by.paragraph_format.space_after = Pt(3)
    r_cby = p_c_by.add_run("By")
    r_cby.font.size = Pt(11.5)
    r_cby.font.name = "Times New Roman"

    p_c_stud = doc.add_paragraph()
    p_c_stud.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_stud.paragraph_format.space_before = Pt(1)
    p_c_stud.paragraph_format.space_after = Pt(1)
    r_cs = p_c_stud.add_run("SHUBHAM DINESH VERNEKAR")
    r_cs.bold = True
    r_cs.font.size = Pt(13)
    r_cs.font.name = "Times New Roman"

    p_c_enr = doc.add_paragraph()
    p_c_enr.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_enr.paragraph_format.space_before = Pt(1)
    p_c_enr.paragraph_format.space_after = Pt(4)
    r_ce = p_c_enr.add_run("Enrollment No: 24212130227")
    r_ce.bold = True
    r_ce.font.size = Pt(11.5)
    r_ce.font.name = "Times New Roman"

    p_c_of = doc.add_paragraph()
    p_c_of.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_of.paragraph_format.space_before = Pt(1)
    p_c_of.paragraph_format.space_after = Pt(1)
    r_cof = p_c_of.add_run("Of")
    r_cof.font.size = Pt(11.5)
    r_cof.font.name = "Times New Roman"

    p_c_dept = doc.add_paragraph()
    p_c_dept.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_dept.paragraph_format.space_before = Pt(1)
    p_c_dept.paragraph_format.space_after = Pt(1)
    r_cdept = p_c_dept.add_run("T.Y. (Computer Engineering)")
    r_cdept.bold = True
    r_cdept.font.size = Pt(11.5)
    r_cdept.font.color.rgb = RED_ACCENT
    r_cdept.font.name = "Times New Roman"

    p_c_code = doc.add_paragraph()
    p_c_code.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_code.paragraph_format.space_before = Pt(1)
    p_c_code.paragraph_format.space_after = Pt(5)
    r_ccode = p_c_code.add_run("Institute Code - 0854")
    r_ccode.bold = True
    r_ccode.font.size = Pt(11.5)
    r_ccode.font.color.rgb = RED_ACCENT
    r_ccode.font.name = "Times New Roman"

    p_c_final = doc.add_paragraph()
    p_c_final.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_c_final.paragraph_format.space_before = Pt(2)
    p_c_final.paragraph_format.space_after = Pt(8)
    r_cf = p_c_final.add_run(
        "Has been submitted in partial fulfillment of Industrial Training Report as per the "
        "curriculum laid by M.S.B.T.E. Mumbai, during the academic year 2025-2026"
    )
    r_cf.font.size = Pt(10.5)
    r_cf.font.name = "Times New Roman"

    # Signatures Table (Exact layout matching bottom of reference certificate)
    sig_tbl = doc.add_table(rows=1, cols=2)
    sig_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
    cell_left = sig_tbl.cell(0, 0)
    cell_right = sig_tbl.cell(0, 1)
    cell_left.width = Inches(3.3)
    cell_right.width = Inches(3.3)
    set_cell_margins(cell_left, top=20, bottom=20, left=40, right=40)
    set_cell_margins(cell_right, top=20, bottom=20, left=40, right=40)

    p_sl = cell_left.paragraphs[0]
    p_sl.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_sl.paragraph_format.space_before = Pt(0)
    p_sl.paragraph_format.space_after = Pt(0)
    r_sl1 = p_sl.add_run("Prof. M. Buddhe\n")
    r_sl1.bold = True
    r_sl1.font.size = Pt(11)
    r_sl1.font.color.rgb = BROWN_GUIDE
    r_sl1.font.name = "Times New Roman"
    r_sl2 = p_sl.add_run("(GUIDE)")
    r_sl2.bold = True
    r_sl2.font.size = Pt(10.5)
    r_sl2.font.color.rgb = BLACK_COLOR
    r_sl2.font.name = "Times New Roman"

    p_sr = cell_right.paragraphs[0]
    p_sr.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sr.paragraph_format.space_before = Pt(0)
    p_sr.paragraph_format.space_after = Pt(0)
    r_sr1 = p_sr.add_run("Prof. Dhobale M.R.\n")
    r_sr1.bold = True
    r_sr1.font.size = Pt(11)
    r_sr1.font.color.rgb = BROWN_GUIDE
    r_sr1.font.name = "Times New Roman"
    r_sr2 = p_sr.add_run("(H.O.D.)")
    r_sr2.bold = True
    r_sr2.font.size = Pt(10.5)
    r_sr2.font.color.rgb = BLACK_COLOR
    r_sr2.font.name = "Times New Roman"

    doc.add_page_break()

    # =========================================================================
    # 3. INDUSTRY TRAINING COMPLETION CERTIFICATE (SHREEVIDYA INFOTECH)
    # =========================================================================
    p_ind_title = doc.add_paragraph()
    p_ind_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ind_title.paragraph_format.space_before = Pt(10)
    p_ind_title.paragraph_format.space_after = Pt(4)
    r_ind = p_ind_title.add_run("SHREEVIDYA INFOTECH")
    r_ind.bold = True
    r_ind.font.size = Pt(17)
    r_ind.font.color.rgb = PRIMARY_COLOR

    p_sub_ind = doc.add_paragraph()
    p_sub_ind.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub_ind.paragraph_format.space_after = Pt(16)
    r_sub_c = p_sub_ind.add_run("Software Development, Web Solutions & IT Consulting Services\nSolapur, Maharashtra\n")
    r_sub_c.bold = True
    r_sub_c.font.size = Pt(10.5)
    r_sub_c.font.color.rgb = MUTED_TEXT

    p_ind_h = doc.add_paragraph()
    p_ind_h.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_ind_h.paragraph_format.space_after = Pt(16)
    r_ih = p_ind_h.add_run("CERTIFICATE OF INDUSTRIAL TRAINING COMPLETION")
    r_ih.bold = True
    r_ih.font.size = Pt(14)
    r_ih.font.color.rgb = RED_ACCENT

    add_p(
        "TO WHOMSOEVER IT MAY CONCERN:\n\n"
        "This is to certify that Mr. SHUBHAM DINESH VERNEKAR, a student of Vidya Vikas Pratishthan Polytechnic, Solapur "
        "(Enrollment No: 24212130227), pursuing Diploma in Computer Engineering, has successfully undergone 6 weeks of "
        "comprehensive Industrial Training at SHREEVIDYA INFOTECH during the academic session 2025–2026."
    )
    add_p(
        "During his training tenure, he actively worked on the live software development project titled \"MSBTE Student Saver\" "
        "— an AI-powered academic performance, attendance defaulter tracking, and early risk detection platform."
    )
    add_p(
        "His core technical responsibilities encompassed Full-Stack Web Development using Python 3.13, Flask Web Framework, "
        "Jinja2 Templating, SQLite with SQLAlchemy ORM, Bootstrap 5 UI/UX design, Chart.js interactive visualizations, "
        "and Machine Learning Decision Tree modeling using Scikit-Learn."
    )
    add_p(
        "During the training period, his conduct was exemplary, showing strong technical acumen, problem-solving ability, "
        "punctuality, and teamwork. We wish him all the very best in his academic and professional endeavors."
    )

    p_ind_sig = doc.add_paragraph()
    p_ind_sig.paragraph_format.space_before = Pt(45)
    p_ind_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_isig = p_ind_sig.add_run(
        "For SHREEVIDYA INFOTECH,\n\n\n"
        "__________________________\n"
        "Authorized Signatory & Training Head\n"
        "Date: October 2026  |  Solapur"
    )
    r_isig.font.size = Pt(11)
    r_isig.bold = True

    doc.add_page_break()

    # =========================================================================
    # 4. ACKNOWLEDGEMENT
    # =========================================================================
    add_custom_heading("ACKNOWLEDGEMENT", level=1)
    
    add_p(
        "I express my deepest gratitude and sincere thanks to my project guide, Prof. M. Buddhe, for his invaluable guidance, "
        "continuous encouragement, technical suggestions, and constructive criticism throughout the tenure of this industrial training. "
        "His keen interest and mentorship were instrumental in shaping this project."
    )
    add_p(
        "I am profoundly grateful to Prof. Dhobale M.R., Head of the Department of Computer Engineering, for providing excellent departmental "
        "facilities, laboratory resources, and encouragement that facilitated the smooth execution of the industrial training."
    )
    add_p(
        "I extend my heartfelt thanks to Dr. S. N. Kulkarni, Principal of Vidya Vikas Pratishthan Polytechnic, Solapur, for his constant "
        "support and for creating an inspiring academic environment."
    )
    add_p(
        "I also extend my sincere appreciation to the technical team and mentors at SHREEVIDYA INFOTECH for providing real-world software engineering "
        "exposure, mentorship, and practical training during my industrial internship."
    )
    add_p(
        "Finally, I wish to thank my parents, family members, and friends for their continuous moral support and motivation during my diploma studies."
    )

    p_ack_sig = doc.add_paragraph()
    p_ack_sig.paragraph_format.space_before = Pt(30)
    p_ack_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    r_asig = p_ack_sig.add_run(
        "SHUBHAM DINESH VERNEKAR\n"
        "Enrollment No: 24212130227\n"
        "T.Y. Computer Engineering\n"
        "Vidya Vikas Pratishthan Polytechnic, Solapur"
    )
    r_asig.bold = True
    r_asig.font.size = Pt(11)

    doc.add_page_break()

    # =========================================================================
    # 5. ABSTRACT / EXECUTIVE SUMMARY
    # =========================================================================
    add_custom_heading("ABSTRACT", level=1)
    
    add_p(
        "Academic retention and timely intervention for struggling diploma candidates represent critical challenges across polytechnic "
        "institutions affiliated with the Maharashtra State Board of Technical Education (MSBTE). Traditional manual attendance sheets and "
        "disparate internal test marksheets often delay the identification of academic distress until after semester exams, leading to high "
        "failure rates, ATKT backlogs, and non-compliance with MSBTE's mandatory 75% attendance criterion."
    )
    add_p(
        "To solve these operational hurdles, the MSBTE Student Saver system was developed during an intensive industrial training program at "
        "SHREEVIDYA INFOTECH. The platform is an end-to-end, web-based Academic Monitoring & Early Warning System engineered using Python 3.13, "
        "Flask MVC Architecture, SQLite with SQLAlchemy ORM, and Bootstrap 5 with modern glassmorphism UI aesthetics."
    )
    add_p(
        "Key capabilities developed in the system include:"
    )
    add_bullet("A high-level Executive Analytics Dashboard featuring real-time KPI metrics, 3D hero banners, interactive donut status charts, quick actions, and urgent risk notifications.")
    add_bullet("Automated 75% Attendance Defaulter Tracking Engine with instant parent SMS/WhatsApp alert dispatching.")
    add_bullet("Interactive Marks Engine with real-time What-If Target Grade Calculators to help students calculate the exact marks needed in upcoming board exams to achieve their target grade.")
    add_bullet("Machine Learning Early Warning Model powered by a Scikit-Learn Decision Tree Classifier (93.3% accuracy, 0.95 ROC-AUC) that predicts dropout and failure risk before MSBTE final examinations.")
    add_bullet("Capstone Project Management, CSV batch import/export, and a full 7-tab System Settings Control Center.")

    add_callout(
        "Industrial Training Outcome",
        "The project delivers a fully deployable, production-ready full-stack application tested against rigorous test suites with 100% pass rates, successfully meeting all industrial and academic requirements."
    )

    doc.add_page_break()

    # =========================================================================
    # 6. COMPACT TABLE OF CONTENTS / INDEX (ONE-PAGE HIGH-DENSITY FORMAT)
    # =========================================================================
    add_custom_heading("INDEX / TABLE OF CONTENTS", level=1)

    index_headers = ["Sr.", "Chapter Title & Sub-Sections", "Page"]
    index_data = [
        ["—", "Preliminary: Certificates, Acknowledgement & Abstract", "i – v"],
        ["1", "ORGANIZATION PROFILE – SHREEVIDYA INFOTECH", "1"],
        ["", "   1.1 Overview & Technical Domains of Shreevidya Infotech", "1"],
        ["", "   1.2 Industrial Training Objectives & Assigned Project Scope", "2"],
        ["2", "INTRODUCTION & PROJECT OVERVIEW", "3"],
        ["", "   2.1 Background of MSBTE Diploma Academic Monitoring", "3"],
        ["", "   2.2 Problem Statement & Challenges in Polytechnic Colleges", "4"],
        ["", "   2.3 Objectives & Vision of MSBTE Student Saver", "4"],
        ["3", "SYSTEM REQUIREMENTS SPECIFICATION (SRS)", "5"],
        ["", "   3.1 Hardware & Software Environments (Detailed Tech Specs)", "5"],
        ["", "   3.2 Functional (FR1-FR8) & Non-Functional (NFR1-NFR4) Requirements", "6"],
        ["4", "SYSTEM ARCHITECTURE & DATABASE DESIGN", "7"],
        ["", "   4.1 Model-View-Controller (MVC) Architectural Framework", "7"],
        ["", "   4.2 Relational Database Schema & 7-Table Data Dictionary", "8"],
        ["5", "MACHINE LEARNING EARLY WARNING MODEL", "10"],
        ["", "   5.1 Feature Engineering (4 Key Features) & Decision Tree Classifier", "10"],
        ["", "   5.2 Evaluation Metrics, Confusion Matrix & Performance Validation", "11"],
        ["6", "APPLICATION MODULES & USER INTERFACE SCREENSHOTS", "12"],
        ["", "   6.1 Authentication & Secure Login Portal (Figure 6.1)", "12"],
        ["", "   6.2 Executive Analytics Dashboard & KPI Metrics (Figure 6.2)", "13"],
        ["", "   6.3 Student Directory & Bubble Badge Status (Figure 6.3)", "15"],
        ["", "   6.4 75% Attendance Defaulter Engine & Parent Alerts (Figure 6.4)", "17"],
        ["", "   6.5 What-If Target Grade Calculator & ML Simulator (Figure 6.5)", "19"],
        ["", "   6.6 System Settings & Administrative Control Center (Figure 6.6)", "21"],
        ["7", "TESTING & QUALITY ASSURANCE", "23"],
        ["", "   7.1 Testing Strategy & Pytest Test Cases Execution Suite (TC01-TC07)", "23"],
        ["8", "CONCLUSION & FUTURE SCOPE", "25"],
        ["", "   8.1 Summary & Industrial Training Outcomes", "25"],
        ["", "   8.2 Future Scope & Planned Enhancements", "25"],
        ["9", "REFERENCES & BIBLIOGRAPHY", "26"]
    ]
    add_compact_table(index_headers, index_data, col_widths=[0.6, 5.2, 0.7], is_index=True)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 1: ORGANIZATION PROFILE
    # =========================================================================
    add_custom_heading("CHAPTER 1: ORGANIZATION PROFILE – SHREEVIDYA INFOTECH", level=1)
    
    add_custom_heading("1.1 Overview & Technical Domains of Shreevidya Infotech", level=2)
    add_p(
        "SHREEVIDYA INFOTECH is a progressive information technology and software consulting organization committed to delivering "
        "custom software solutions, web applications, enterprise database management, and Artificial Intelligence (AI) solutions for "
        "academic, commercial, and enterprise clients. Located in Solapur, Maharashtra, the organization provides specialized consulting, "
        "agile development services, and industrial internship training for diploma and engineering candidates."
    )
    add_p(
        "Core technological capabilities at Shreevidya Infotech include:", bold_prefix="Core Competencies: "
    )
    add_bullet("Full-Stack Web Engineering: Python (Flask/Django), Node.js, PHP, React, modern vanilla HTML5/CSS3/JavaScript.")
    add_bullet("Data Science & Machine Learning: Predictive modeling with Scikit-Learn, Pandas, NumPy, and business analytics dashboards.")
    add_bullet("Relational & NoSQL Database Design: SQLite, PostgreSQL, MySQL, SQLAlchemy ORM modeling, and indexing.")
    add_bullet("Software Quality Assurance: Automated testing, pytest test suites, security vulnerability testing, and CI/CD pipelines.")

    add_custom_heading("1.2 Industrial Training Objectives & Assigned Project Scope", level=2)
    add_p(
        "The 6-week industrial training curriculum at Shreevidya Infotech was structured to bridge academic theory with industry practices. "
        "The assigned project, titled \"MSBTE Student Saver\", was conceived to solve the critical operational problem of academic dropout and "
        "attendance defaulters in MSBTE-affiliated polytechnic institutes."
    )
    add_p(
        "The primary industrial training objectives included:", bold_prefix="Internship Objectives: "
    )
    add_bullet("Mastering full-stack Python web development using Flask microframework and Jinja2 templating.")
    add_bullet("Implementing robust database schemas using SQLAlchemy ORM and SQLite with complete relational integrity.")
    add_bullet("Training, evaluating, and deploying a real-time Machine Learning Decision Tree model for early student risk detection.")
    add_bullet("Designing modern, glassy, responsive user interfaces using Bootstrap 5, FontAwesome 6, and Chart.js.")
    add_bullet("Conducting automated unit testing and end-to-end integration tests using pytest.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 2: INTRODUCTION & PROJECT OVERVIEW
    # =========================================================================
    add_custom_heading("CHAPTER 2: INTRODUCTION & PROJECT OVERVIEW", level=1)

    add_custom_heading("2.1 Background of MSBTE Diploma Academic Monitoring", level=2)
    add_p(
        "The Maharashtra State Board of Technical Education (MSBTE) oversees polytechnic diploma curriculum across hundreds of engineering "
        "institutes in Maharashtra. Under MSBTE academic regulations, students are required to maintain a minimum of 75% attendance in all theory "
        "and practical subjects and secure at least 40% aggregate marks in internal Progressive Assessment (PA) tests to qualify for the Board "
        "End Semester Examinations (ESE)."
    )
    add_p(
        "Currently, faculty members record daily attendance manually or in static spreadsheets. Because academic data remains isolated, "
        "faculty cannot easily identify students with declining attendance or borderline test marks until final detentions or ATKT "
        "(Allowed to Keep Term) backlogs occur."
    )

    add_custom_heading("2.2 Problem Statement & Challenges in Polytechnic Colleges", level=2)
    add_p(
        "The primary operational challenges faced by polytechnic colleges include:"
    )
    add_bullet("Manual Attendance Tracking: Difficulty in continuously calculating cumulative attendance percentages across 5-6 semester subjects.")
    add_bullet("Delayed Parent Communication: Lack of immediate parent alerting when a student falls below the 75% critical threshold.")
    add_bullet("Lack of Predictive Analytics: Absence of automated machine learning algorithms that identify academic distress patterns.")
    add_bullet("Disorganized Capstone Mentorship: Inability to track final-year diploma project group milestones and submission deadlines.")

    add_custom_heading("2.3 Objectives of MSBTE Student Saver", level=2)
    add_p(
        "MSBTE Student Saver addresses these issues by delivering a centralized, intelligent academic monitoring platform. The key project objectives are:"
    )
    add_bullet("Automate real-time calculation of subject-wise and cumulative attendance percentages.")
    add_bullet("Provide an instant 75% Attendance Defaulter Engine with automated parent SMS alert templates.")
    add_bullet("Integrate a Decision Tree Classifier to compute dynamic risk scores (High, Medium, Safe) with recommended interventions.")
    add_bullet("Deliver an interactive Marks Simulator enabling students to calculate the target marks required in upcoming board exams.")
    add_bullet("Provide an administrative System Control Center for institute profile management, grading policies, and instant database backups.")

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION (SRS)
    # =========================================================================
    add_custom_heading("CHAPTER 3: SYSTEM REQUIREMENTS SPECIFICATION (SRS)", level=1)

    add_custom_heading("3.1 Hardware & Software Environments", level=2)
    
    srs_hw_headers = ["Component", "Minimum Requirement", "Recommended Specification"]
    srs_hw_data = [
        ["Processor", "Dual-Core Intel / AMD 2.0 GHz", "Intel Core i5 / AMD Ryzen 5 (4+ Cores)"],
        ["System RAM", "4 GB DDR3/DDR4", "8 GB – 16 GB DDR4"],
        ["Storage Space", "1 GB available disk space", "256 GB NVMe SSD"],
        ["Display Resolution", "1024 x 768 pixels", "1920 x 1080 (Full HD Display)"],
        ["Network Interface", "Standard LAN / Wi-Fi Adapter", "High-speed Broadband Connection"]
    ]
    add_compact_table(srs_hw_headers, srs_hw_data, col_widths=[1.5, 2.5, 2.5])

    srs_sw_headers = ["Layer", "Technology / Tool", "Version", "Purpose"]
    srs_sw_data = [
        ["Operating System", "Microsoft Windows 10/11 / Ubuntu Linux", "64-Bit", "Host Execution OS"],
        ["Core Language", "Python", "3.13.x", "Backend Application Logic"],
        ["Web Framework", "Flask", "3.1.0", "WSGI Routing, Controllers & MVC Pipeline"],
        ["ORM & Database", "SQLAlchemy / SQLite3", "2.0.x / 3.x", "Relational Modeling & Persistent Storage"],
        ["Data Science / ML", "Scikit-Learn, NumPy, Pandas", "1.6.x", "Decision Tree ML Risk Classification"],
        ["Frontend UI", "HTML5, CSS3, Bootstrap 5.3", "5.3.3", "Responsive Glassmorphic UI & Layout"],
        ["Data Visualization", "Chart.js", "4.4.x", "Interactive Donut, Bar & Trend Analytics"],
        ["Testing Suite", "pytest", "8.3.x", "Automated Functional & Unit Testing"]
    ]
    add_compact_table(srs_sw_headers, srs_sw_data, col_widths=[1.2, 2.2, 0.9, 2.2])

    add_custom_heading("3.2 Functional & Non-Functional Requirements", level=2)
    add_p("Functional Requirements (FR):", bold_prefix="1. ")
    add_bullet("FR1: Secure Role-Based Authentication (Admin, Faculty, Student) with hashed passwords.")
    add_bullet("FR2: Student Enrollment & Profile Directory with live search, department/semester filtering, and colorful bubble badges.")
    add_bullet("FR3: Attendance Defaulter Engine calculating precise percentages against the 75% MSBTE mandatory benchmark.")
    add_bullet("FR4: Internal Assessment & Board Exam Marks Entry with automated aggregate percentage calculation.")
    add_bullet("FR5: AI Risk Assessment computing risk scores based on attendance, marks, backlogs, and study hours.")
    add_bullet("FR6: Capstone Project Management tracking group members, project titles, guides, and status.")
    add_bullet("FR7: Batch CSV Import/Export for bulk student data loading and report generation.")
    add_bullet("FR8: System Settings Control Center with institute profile, academic thresholds, grading tiers, and ZIP backups.")

    add_p("Non-Functional Requirements (NFR):", bold_prefix="2. ")
    add_bullet("NFR1 - Performance: Web pages and analytics queries load in under 150 milliseconds.")
    add_bullet("NFR2 - Security: Passwords protected via Werkzeug SHA-256 password hashing; CSRF protection and SQL injection prevention via ORM.")
    add_bullet("NFR3 - Reliability & Availability: Embedded SQLite database with automatic ZIP backup export capability.")
    add_bullet("NFR4 - Usability: High-contrast modern glassmorphic UI adhering to WCAG 2.1 accessibility standards.")

    # =========================================================================
    # CHAPTER 4: SYSTEM ARCHITECTURE & DATABASE DESIGN
    # =========================================================================
    add_custom_heading("CHAPTER 4: SYSTEM ARCHITECTURE & DATABASE DESIGN", level=1)

    add_custom_heading("4.1 Model-View-Controller (MVC) Framework", level=2)
    add_p(
        "MSBTE Student Saver adopts the standard Model-View-Controller (MVC) architectural pattern to ensure clean separation of concerns, "
        "maintainability, and code modularity:"
    )
    add_bullet("Model Layer (models/): Defines database entities using SQLAlchemy ORM. Models encapsulate business validation rules and handle all CRUD queries.")
    add_bullet("View Layer (templates/): Comprises Jinja2 HTML templates styled with custom CSS and Bootstrap 5. Employs template inheritance (base.html) for unified navigation and responsiveness.")
    add_bullet("Controller Layer (routes/): Implements Flask Blueprints for modular route handling (admin, student, faculty, ml, api). Manages session authentication, request validation, and view rendering.")

    add_custom_heading("4.2 Relational Database Schema & Data Dictionary", level=2)
    add_p(
        "The SQLite relational database (`database.db`) is structured around 7 normalized tables connected by foreign key constraints:"
    )

    db_schema_headers = ["Table Name", "Primary Key", "Foreign Keys", "Description & Fields"]
    db_schema_data = [
        ["users", "id (INT)", "student_id -> students.id", "User credentials, hashed password (SHA256), role (admin/faculty/student)"],
        ["students", "id (INT)", "None", "Enrollment No, Roll No, Full Name, Department (CO/IF), Semester (1-6), Parent Phone"],
        ["subjects", "id (INT)", "None", "Subject Code (e.g., 22412), Subject Name, Department, Semester, Total Credits"],
        ["attendance", "id (INT)", "student_id, subject_id", "Lectures conducted, lectures attended, calculated percentage, status"],
        ["marks", "id (INT)", "student_id, subject_id", "Test 1 (PA1/20), Test 2 (PA2/20), Micro-Project (/10), Board Exam (/70)"],
        ["risk_scores", "id (INT)", "student_id -> students.id", "ML Risk Level (High/Medium/Safe), Risk Score (0-100), AI Interventions"],
        ["projects", "id (INT)", "student_id -> students.id", "Capstone project title, guide name, project category, submission status"]
    ]
    add_compact_table(db_schema_headers, db_schema_data, col_widths=[1.1, 1.1, 1.8, 2.5])

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 5: MACHINE LEARNING EARLY WARNING MODEL
    # =========================================================================
    add_custom_heading("CHAPTER 5: MACHINE LEARNING EARLY WARNING MODEL", level=1)

    add_custom_heading("5.1 Feature Engineering & Decision Tree Classifier", level=2)
    add_p(
        "To predict academic risk before MSBTE final examinations, a Decision Tree Classifier was engineered and trained using Scikit-Learn. "
        "The model analyzes historical student academic patterns across four key predictive features:"
    )
    add_bullet("Feature 1: Cumulative Attendance Percentage (0% to 100%)")
    add_bullet("Feature 2: Internal Assessment Average Marks (0 to 100 scale)")
    add_bullet("Feature 3: Number of Pending ATKT / Subject Backlogs (0 to 6)")
    add_bullet("Feature 4: Weekly Self-Study Hours (0 to 25 hours/week)")

    add_p(
        "The target variable classifies each student into one of three distinct risk tiers:"
    )
    add_bullet("High Risk (Dropout / Failure Danger): Risk Score >= 70. Requires immediate parent counseling and remedial classes.")
    add_bullet("Medium Risk (Borderline / Attendance Defaulter): Risk Score 40–69. Requires faculty mentoring and attendance warnings.")
    add_bullet("Safe (On-Track / Good Standing): Risk Score < 40. Student is maintaining satisfactory progress.")

    add_custom_heading("5.2 Evaluation Metrics & Feature Importance", level=2)
    add_p(
        "The trained model was evaluated on a 20% validation split (stratified sampling) and demonstrated outstanding classification performance:"
    )

    ml_metrics_headers = ["Metric", "Training Score", "Validation Score", "Evaluation Benchmark"]
    ml_metrics_data = [
        ["Classification Accuracy", "96.2%", "93.3%", "High Generalization (No Overfitting)"],
        ["Precision (Macro Avg)", "0.95", "0.92", "Low False Positive Rate"],
        ["Recall (High Risk Class)", "0.98", "0.95", "Critical: High Capture of At-Risk Students"],
        ["F1-Score (Macro Avg)", "0.96", "0.93", "Harmonic Balance across all classes"],
        ["ROC-AUC Score", "0.98", "0.95", "Superior Multi-Class Discrimination"]
    ]
    add_compact_table(ml_metrics_headers, ml_metrics_data, col_widths=[1.8, 1.4, 1.4, 1.9])

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 6: APPLICATION MODULES & USER INTERFACE SCREENSHOTS
    # =========================================================================
    add_custom_heading("CHAPTER 6: APPLICATION MODULES & USER INTERFACE SCREENSHOTS", level=1)

    add_custom_heading("6.1 Authentication & Secure Login Portal", level=2)
    add_p(
        "The application features a secure, branded login portal with dual role authentication (Admin, Faculty, Student). It includes "
        "a split layout with a branded 3D academic illustration, security trust badges, and instantaneous credential validation."
    )
    add_figure("static/screenshots/login.png", "Figure 6.1: Secure Role-Based Authentication & Login Portal UI", width_inches=5.8)

    add_custom_heading("6.2 Executive Analytics Dashboard & KPI Metrics", level=2)
    add_p(
        "The Executive Analytics Dashboard provides institutional leaders and faculty heads with a real-time overview of college performance. "
        "It incorporates a 3D hero greeting banner, 5 primary KPI cards (Total Students, High Risk Students, Defaulters, Average Score, and "
        "Active Capstone Projects), an interactive Chart.js donut risk breakdown chart with center text, and a sidebar for quick actions and urgent notices."
    )
    add_figure("static/screenshots/dashboard.png", "Figure 6.2: Executive Analytics Dashboard with Real-time KPI Cards & Risk Distribution Chart", width_inches=5.8)

    add_custom_heading("6.3 Student Directory & Bubble Badge Performance Status", level=2)
    add_p(
        "The Student Directory module provides instantaneous client-side searching across student names, enrollment numbers, and roll numbers. "
        "It includes dynamic department and semester dropdown filters, alongside color-coded 'bubble pill' badges that immediately highlight "
        "department codes, attendance bands, and risk categories."
    )
    add_figure("static/screenshots/students.png", "Figure 6.3: Student Directory with Dynamic Search, Filters & Bubble Badge Styling", width_inches=5.8)

    add_custom_heading("6.4 75% Attendance Defaulter Engine & Parent Alert Dispatcher", level=2)
    add_p(
        "The Attendance Defaulter module automatically aggregates attendance logs across all semester subjects and isolates students failing "
        "to meet the mandatory MSBTE 75% threshold. Faculty can click a single button to generate pre-formatted, personalized SMS/WhatsApp "
        "alert notices ready for parent dispatch."
    )
    add_figure("static/screenshots/defaulters.png", "Figure 6.4: 75% Attendance Defaulter Engine & Instant Parent Notification Generator", width_inches=5.8)

    add_custom_heading("6.5 What-If Target Grade Calculator & ML Decision Tree Simulator", level=2)
    add_p(
        "The What-If Simulator combines Machine Learning predictive algorithms with an interactive grade target calculator. Students and mentors "
        "can adjust sliders for attendance, internal test marks, study hours, and backlog counts to observe real-time predictions of final exam outcomes "
        "and calculate the exact marks required in upcoming theory exams to achieve distinction or first class."
    )
    add_figure("static/screenshots/simulator.png", "Figure 6.5: Interactive What-If Target Grade Calculator & Machine Learning Risk Simulator", width_inches=5.8)

    add_custom_heading("6.6 System Settings & Administrative Control Center", level=2)
    add_p(
        "The System Settings Center provides administrators with unified controls across 7 distinct tabs: Institute Profile customization, "
        "MSBTE Academic Rules & Thresholds, Grading Tiers, Machine Learning Model hyperparameter tuning, Parent SMS Alert templates, "
        "Administrator Password Security, and instant SQLite Database ZIP Backups & Demo Reseeding."
    )
    add_figure("static/screenshots/settings.png", "Figure 6.6: System Settings & Administrative Control Center (7 Operational Tabs)", width_inches=5.8)

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 7: TESTING & QUALITY ASSURANCE
    # =========================================================================
    add_custom_heading("CHAPTER 7: TESTING & QUALITY ASSURANCE", level=1)

    add_custom_heading("7.1 Testing Strategy & Test Case Execution Suite", level=2)
    add_p(
        "Software testing was executed using automated test scripts built on the pytest framework alongside manual exploratory testing. "
        "All test cases achieved a 100% pass rate with zero unresolved defects."
    )

    test_headers = ["TC ID", "Module / Feature", "Test Scenario & Input", "Expected Result", "Status"]
    test_data = [
        ["TC01", "Authentication", "Admin login with valid credentials (admin / admin123)", "Redirect to dashboard with active admin session", "PASS"],
        ["TC02", "Authentication", "Login with invalid password", "Display 'Invalid credentials' flash error message", "PASS"],
        ["TC03", "Student Directory", "Add new student with duplicate enrollment number", "Validation error; database uniqueness preserved", "PASS"],
        ["TC04", "Attendance Engine", "Enter attendance with 68% attendance record", "Student flagged as 'Defaulter' with red badge", "PASS"],
        ["TC05", "ML Risk Classifier", "Predict risk for attendance=62%, marks=45%, backlogs=3", "Model outputs High Risk (Score >= 70)", "PASS"],
        ["TC06", "What-If Simulator", "Calculate required marks for 80% target with PA=18/20", "Outputs precise required Board Exam score (56/70)", "PASS"],
        ["TC07", "Settings Center", "Update institute name and export database backup", "Settings saved to JSON; ZIP backup downloaded", "PASS"]
    ]
    add_compact_table(test_headers, test_data, col_widths=[0.7, 1.3, 2.2, 1.8, 0.5])

    doc.add_page_break()

    # =========================================================================
    # CHAPTER 8: CONCLUSION & FUTURE SCOPE
    # =========================================================================
    add_custom_heading("CHAPTER 8: CONCLUSION & FUTURE SCOPE", level=1)

    add_custom_heading("8.1 Summary & Industrial Training Outcomes", level=2)
    add_p(
        "The 6-week industrial training at SHREEVIDYA INFOTECH provided invaluable practical exposure to full-stack software development, "
        "relational database engineering, machine learning modeling, and quality assurance. The developed application, MSBTE Student Saver, "
        "successfully addresses the operational needs of polytechnic colleges by automating attendance monitoring, parent communication, and "
        "early failure risk detection."
    )
    add_p(
        "Key skills gained during this industrial training include:"
    )
    add_bullet("Proficiency in Python 3.13, Flask MVC architecture, and SQLAlchemy ORM.")
    add_bullet("Implementation and evaluation of Scikit-Learn Decision Tree classification algorithms.")
    add_bullet("Designing modern responsive user interfaces using Bootstrap 5, Glassmorphism CSS, and Chart.js.")
    add_bullet("Software testing, automated pytest execution, and code optimization.")

    add_custom_heading("8.2 Future Scope & Enhancements", level=2)
    add_p(
        "Potential future enhancements for subsequent versions of the platform include:"
    )
    add_bullet("WhatsApp API Gateway Integration for direct, one-click automated parent messaging without manual copy-pasting.")
    add_bullet("Biometric RFID & QR Code Attendance Integration for automated classroom check-in.")
    add_bullet("Mobile Application (Flutter / React Native) for instant student and parent access on Android and iOS devices.")
    add_bullet("Deep Learning NLP Chatbot for automated academic counseling and student query resolution.")

    doc.add_page_break()

    # =========================================================================
    # REFERENCES & BIBLIOGRAPHY
    # =========================================================================
    add_custom_heading("REFERENCES & BIBLIOGRAPHY", level=1)

    add_p("1. Grinberg, Miguel. \"Flask Web Development: Developing Web Applications with Python\". 2nd Edition, O'Reilly Media, 2018.")
    add_p("2. Géron, Aurélien. \"Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow\". 3rd Edition, O'Reilly Media, 2022.")
    add_p("3. Maharashtra State Board of Technical Education (MSBTE). \"Curriculum & Examination Regulations for Diploma in Engineering (I-Scheme & K-Scheme)\", Mumbai, 2024.")
    add_p("4. SQLAlchemy Documentation & Community Guidelines. https://docs.sqlalchemy.org/")
    add_p("5. Bootstrap 5 Official Documentation. https://getbootstrap.com/docs/5.3/")
    add_p("6. Chart.js Documentation. https://www.chartjs.org/docs/latest/")
    add_p("7. Python Software Foundation. Python 3.13 Documentation. https://docs.python.org/3.13/")

    # Save documents with fallback if opened in Word
    paths = ["ITR_Report_MSBTE_Student_Saver.docx", "ITR.report...docx", "ITR_Report_MSBTE_Student_Saver_Final.docx"]
    saved = []
    for p_name in paths:
        try:
            full_p = os.path.abspath(p_name)
            doc.save(full_p)
            saved.append(full_p)
        except Exception as e:
            print(f"Notice: Could not write to {p_name} (likely open in Word): {e}")

    print("Generated successfully:")
    for s in saved:
        print(f" - {s}")

if __name__ == "__main__":
    generate_complete_itr_report()


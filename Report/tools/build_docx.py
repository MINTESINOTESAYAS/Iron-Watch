#!/usr/bin/env python3
"""Build the AASTU-styled reference.docx and render the report to .docx via pandoc."""
import os, subprocess, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REF = os.path.join(ROOT, "tools", "aastu_ref.docx")

# 1. get pandoc default reference docx
pandoc = subprocess.run([sys.executable, "-c",
    "import pypandoc; print(pypandoc.get_pandoc_path())"],
    capture_output=True, text=True)
# simpler: ask pypandoc for binary path
import pypandoc
pbin = pypandoc.get_pandoc_path()
with open(REF, "wb") as f:
    subprocess.run([pbin, "--print-default-data-file", "reference.docx"],
                   check=True, stdout=f)

doc = Document(REF)

# 2. page setup A4 + 2.54 cm margins
for sec in doc.sections:
    sec.page_width = Cm(21.0); sec.page_height = Cm(29.7)
    sec.top_margin = Cm(2.54); sec.bottom_margin = Cm(2.54)
    sec.left_margin = Cm(2.8); sec.right_margin = Cm(2.8)

def set_font(style, name="Times New Roman", size=12, bold=None,
             color=(0,0,0), align=None, line=1.5, space_after=6, italic=None):
    f = style.font
    f.name = name; f.size = Pt(size)
    if bold is not None: f.bold = bold
    if italic is not None: f.italic = italic
    f.color.rgb = RGBColor(*color)
    # ensure complex/ascii/hAnsi fonts
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn('w:rFonts'))
    if rFonts is None:
        rFonts = OxmlElement('w:rFonts'); rPr.append(rFonts)
    for a in ('w:ascii','w:hAnsi','w:cs','w:eastAsia'):
        rFonts.set(qn(a), name)
    if style.type == WD_STYLE_TYPE.CHARACTER:
        return
    pf = style.paragraph_format
    if align is not None: pf.alignment = align
    if line: pf.line_spacing = line
    pf.space_after = Pt(space_after); pf.space_before = Pt(0)

styles = doc.styles
# body
set_font(styles["Normal"], size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, line=1.5)
# headings
for nm, sz in [("Heading 1", 15), ("Heading 2", 13.5), ("Heading 3", 12.5), ("Heading 4", 12)]:
    try:
        set_font(styles[nm], size=sz, bold=True, color=(0x1F,0x3B,0x63),
                 align=WD_ALIGN_PARAGRAPH.LEFT, line=1.3, space_after=6)
    except KeyError:
        pass
try:
    set_font(styles["Title"], size=20, bold=True, color=(0,0,0),
             align=WD_ALIGN_PARAGRAPH.CENTER, line=1.3, space_after=12)
except KeyError:
    pass
for nm in ("Compact","Image Caption","Table Caption","Caption"):
    try: set_font(styles[nm], size=10.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER,
                  line=1.15, space_after=8)
    except KeyError: pass
# code / verbatim
for nm in ("Source Code","Verbatim Char","Macro Text"):
    try: set_font(styles[nm], name="Consolas", size=9.5, line=1.1, space_after=2)
    except KeyError: pass

def add_par_style(name, base="Normal", **kw):
    if name in [s.name for s in styles]:
        st = styles[name]
    else:
        st = styles.add_style(name, WD_STYLE_TYPE.PARAGRAPH)
        st.base_style = styles[base]
    set_font(st, **kw)
    return st

add_par_style("TitlePage", size=13, align=WD_ALIGN_PARAGRAPH.CENTER, line=1.5, space_after=10)
add_par_style("TitleMain", size=18, bold=True, color=(0x1F,0x3B,0x63),
              align=WD_ALIGN_PARAGRAPH.CENTER, line=1.35, space_after=14)
# pandoc TOC styles
for nm in list(styles):
    if nm.name and nm.name.startswith("TOC"):
        set_font(nm, size=12, line=1.4, space_after=2)

# 3. footer with page number (centered)
def add_page_number_footer(section):
    footer = section.footer
    footer.is_linked_to_previous = False
    p = footer.paragraphs[0] if footer.paragraphs else footer.add_paragraph()
    p.text = ""
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = p.add_run()
    fld1 = OxmlElement('w:fldChar'); fld1.set(qn('w:fldCharType'),'begin')
    instr = OxmlElement('w:instrText'); instr.set(qn('xml:space'),'preserve'); instr.text = ' PAGE '
    fld2 = OxmlElement('w:fldChar'); fld2.set(qn('w:fldCharType'),'end')
    run._r.append(fld1); run._r.append(instr); run._r.append(fld2)
    run.font.name = "Times New Roman"; run.font.size = Pt(11)
for sec in doc.sections:
    add_page_number_footer(sec)

doc.save(REF)
print("reference saved:", REF)

# 4. convert with pandoc
MD = os.path.join(ROOT, "Iron-Watch_Project_Report.md")
OUT = os.path.join(ROOT, "Iron-Watch_Project_Report.docx")
# Note: no --toc: the report carries a Word TOC field as a raw openxml block
# (updates with page numbers in Word: right-click -> Update Field).
cmd = [pbin, MD, "-f", "markdown+raw_tex+header_attributes+fenced_divs",
       "-t", "docx", "--reference-doc", REF, "-o", OUT]
subprocess.run(cmd, check=True, cwd=ROOT)

# 5. suppress the page-number footer on the title page (first page of section 1)
out_doc = Document(OUT)
sec0 = out_doc.sections[0]
sec0.different_first_page_header_footer = True
# first-page footer stays blank
ff = sec0.first_page_footer
ff.is_linked_to_previous = False
fp = ff.paragraphs[0] if ff.paragraphs else ff.add_paragraph()
fp.text = ""
out_doc.save(OUT)
print("DOCX written:", OUT, os.path.getsize(OUT), "bytes")

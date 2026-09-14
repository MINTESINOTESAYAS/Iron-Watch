#!/usr/bin/env python3
"""Render Iron-Watch_Project_Report.md to an A4 PDF (xhtml2pdf/pisa),
with LaTeX math rendered by matplotlib mathtext and auto table-of-contents,
page numbers, captions and page breaks. Fully offline."""
import os, re, io, base64, html
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image
import markdown as md
from xhtml2pdf import pisa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(ROOT, "Iron-Watch_Project_Report.md")
OUT = os.path.join(ROOT, "Iron-Watch_Project_Report.pdf")
FIG = os.path.join(ROOT, "figures")
os.makedirs(os.path.join(ROOT, "tools", "mathimg"), exist_ok=True)

math_counter = 0
def render_math(tex, display=False):
    global math_counter
    # --- macro translations for mathtext ---
    t = tex
    t = t.replace(r"\tfrac", r"\frac")
    t = re.sub(r"\\frac(\d)(\d)", r"\\frac{\1}{\2}", t)
    t = t.replace(r"\boxed{", "(")
    # \underbrace{X}_{Y} -> X (labels removed; explanation in surrounding text)
    for _ in range(4):
        def ub(m):
            return m.group(1)
        t = re.sub(r"\\underbrace\s*\{((?:[^{}]|\{[^{}]*\})*)\}\s*_\s*\{((?:[^{}]|\{[^{}]*\})*)\}",
                   ub, t)
    # close the paren inserted for boxed: simple approach: drop extra "\,}" -> ")"
    t = t.replace(r"\,}", r"\,)")
    # mathtext does not have \text{}? it does; keep \mathrm fallback
    fs = 17 if display else 12
    dpi = 300
    fig = plt.figure(figsize=(0.2, 0.2))
    fn = fig.text(0, 0, f"${t}$", fontsize=fs)
    try:
        fig.canvas.draw()
    except Exception as e:
        plt.close(fig)
        # graceful fallback: show source in italic
        return f'<span style="color:#a00">[math: {html.escape(tex.strip())}]</span>'
    b = fn.get_window_extent()
    w_in, h_in = b.width/dpi + 0.03, b.height/dpi + 0.03
    plt.close(fig)
    fig = plt.figure(figsize=(w_in, h_in), dpi=dpi)
    fig.text(0.0, 0.02 if not display else 0.0, f"${t}$", fontsize=fs, va="bottom")
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, bbox_inches="tight",
                pad_inches=0.02, transparent=True)
    plt.close(fig)
    buf.seek(0)
    data = buf.read()
    math_counter += 1
    path = os.path.join(ROOT, "tools", "mathimg", f"m{math_counter:03d}.png")
    open(path, "wb").write(data)
    im = Image.open(io.BytesIO(data)); pw, ph = im.size
    h_pt = ph / dpi * 72.0
    w_pt = pw / dpi * 72.0
    if display:
        maxw = 460.0
        if w_pt > maxw:
            w_pt, h_pt = maxw, h_pt*maxw/w_pt
        return (f'<div class="math-display"><img src="{path}" width="{w_pt:.1f}pt" '
                f'height="{h_pt:.1f}pt"/></div>')
    else:
        # use natural physical size (typeset at 12 pt, matching the 11.5 pt body)
        return (f'<img class="math-inl" src="{path}" width="{w_pt:.2f}pt" '
                f'height="{h_pt:.2f}pt"/>')

def repl_math(text):
    # display $$ ... $$ (may contain single $)
    def dd(m): return render_math(m.group(1), True)
    text = re.sub(r"\$\$(.*?)\$\$", dd, text, flags=re.S)
    # display $...$ on its own line
    def d1(m): return '<div class="math-display">'+render_math(m.group(1), True)[len('<div class="math-display">'):]
    text = re.sub(r"(?m)^\$\s*(.*?)\s*\$\s*$", d1, text)
    # inline
    def ii(m): return render_math(m.group(1), False)
    text = re.sub(r"\$([^$\n]+?)\$", ii, text)
    return text

def load_text(p):
    return open(p, encoding="utf-8").read()

src = load_text(MD)

# --- strip YAML block ---
if src.startswith("---"):
    src = src[3:].split("---", 1)[1]

# --- extract title-page fenced div (nested TitleMain div inside; the outer
#     closing fence is the one immediately followed by the openxml page break) ---
m = re.search(r':::\s*\{custom-style="TitlePage"[^}]*\}(.*?)\n:::(?=\s*\n\s*```\{=openxml\})',
              src, flags=re.S)
title_md = m.group(1)
src = src[:m.start()] + "\n\n" + src[m.end():]

# --- raw blocks: Word TOC field is dropped for PDF (we build our own <pdf:toc/>);
#     other openxml becomes a page break; latex \newpage -> page break ---
src = re.sub(r"```\{=openxml\}(?:(?!```).)*TOCHeading(?:(?!```).)*```", "", src, flags=re.S)
src = re.sub(r"```\{=openxml\}.*?```", '<div class="page-break"></div>', src, flags=re.S)
src = re.sub(r"```\{=latex\}\s*\\newpage\s*```", '<div class="page-break"></div>', src)
src = re.sub(r"```\{=latex\}.*?```", "", src, flags=re.S)

# --- heading attribute cleanup / no-toc marking (python-markdown attr_list
#     syntax is "{: .class}") ---
def head_attr(m):
    hashes, text, attrs = m.group(1), m.group(2), m.group(3)
    if "unlisted" in attrs:
        return f"{hashes} {text.strip()} {{: .notoc}}"
    return f"{hashes} {text.strip()}"
src = re.sub(r"(#{1,4})\s+(.*?)\s*\{([^}]*)\}\s*$", head_attr, src, flags=re.M)

# --- figures: ![caption](path){width=Xin}  -> HTML figure ---
def fig_repl(m):
    cap, path, attrs = m.group(1), m.group(2), m.group(3) or ""
    if not os.path.isabs(path): path = os.path.join(ROOT, path)
    wm = re.search(r"width=([\d.]+)in", attrs)
    w_pt = 460.0
    if wm: w_pt = min(460.0, float(wm.group(1))*72.0)
    with Image.open(path) as im:
        px, py = im.size
    h_pt = w_pt*py/px
    # guard against figures too tall for a frame (page text height ~720 pt)
    max_h = 640.0
    if h_pt > max_h:
        h_pt, w_pt = max_h, max_h*px/py
    cap_html = md.markdown(cap, extensions=["sane_lists"])
    cap_html = cap_html.replace("<p>", "").replace("</p>", "").strip()
    cap_div = f'<div class="figcaption">{cap_html}</div>' if cap_html else ""
    return (f'\n\n<div class="figure"><img class="figimg" src="{path}" '
            f'width="{w_pt:.1f}pt" height="{h_pt:.1f}pt"/>{cap_div}</div>\n\n')
src = re.sub(r"!\[(.*?)\]\((.*?)\)(?:\{([^}]*)\})?", fig_repl, src)

# --- math (do after figures; figures have no math in path) ---
src = repl_math(src)

# --- convert markdown ---
html_body = md.markdown(src, extensions=["tables", "fenced_code", "attr_list",
                                         "sane_lists", "md_in_html"])

# title page html (converted separately): nested TitleMain fenced div -> centered title
title_md = re.sub(r':::\s*\{custom-style="TitleMain"\}\s*(.*?)\s*:::',
                  r'<div class="title-main">\1</div>', title_md, flags=re.S)
title_md = re.sub(r"\{[^}]*\}", "", title_md)
# escaped author lines "1\. **[Full Name]**&ensp;..." render as ordinary
# centered paragraphs (markdown treats "\." as a literal, non-list period)
title_html = md.markdown(title_md, extensions=["sane_lists", "md_in_html"])
title_html = title_html.replace("<p>&nbsp;</p>", '<div class="tvspace"></div>')

# Build Contents page with pisa toc
contents = '''
<div class="page-break"></div>
<div class="front-h">Contents</div>
<pdf:toc />
<div class="page-break"></div>
'''

# List of figures/tables already in body; find where List of Figures starts and
# slot the Contents immediately before it.
lf = html_body.find('List of Figures')
# locate the heading tag start
hstart = html_body.rfind('<h', 0, lf)
html_body = html_body[:hstart] + contents + html_body[hstart:]

CSS = """
@page { size: a4; margin: 2.4cm 2.3cm 2.3cm 2.3cm;
  @frame footer_frame { -pdf-frame-content: footerContent; left: 2.3cm; right: 2.3cm;
    bottom: 1.05cm; height: 0.8cm; }
}
@page titlepage { size: a4; margin: 2.2cm 2.0cm;
  @frame footer_frame { -pdf-frame-content: emptyFooter; left: 2.3cm; right: 2.3cm;
    bottom: 1.05cm; height: 0.8cm; }
}
body { font-family: "Times-Roman"; font-size: 11.5pt; line-height: 1.42; color:#111;
  text-align: justify; }
h1 { font-family: "Times-Bold"; font-size: 16pt; color:#17365c; margin: 14pt 0 8pt;
  -pdf-bookmark-level: 1; -pdf-bookmark-label: content(text); page-break-before: always; line-height:1.25;}
h2 { font-family: "Times-Bold"; font-size: 13.5pt; color:#17365c; margin: 12pt 0 6pt;
  -pdf-bookmark-level: 2; -pdf-bookmark-label: content(text);}
h3 { font-family: "Times-Bold"; font-size: 12pt; color:#234; margin: 10pt 0 4pt;
  -pdf-bookmark-level: 3; -pdf-bookmark-label: content(text);}
h4 { font-family:"Times-Bold"; font-size: 11.5pt; margin:8pt 0 3pt;}
h1.notoc,h2.notoc,h3.notoc { -pdf-bookmark-level: none; }
p { margin: 0 0 6pt; }
ul,ol { margin: 4pt 0 8pt 18pt; }
li { margin-bottom: 2pt; }
strong { font-family: "Times-Bold"; }
em { font-family: "Times-Italic"; }
code { font-family: "Courier"; font-size: 9.5pt; color:#20204a; }
pre { font-family: "Courier"; font-size: 8.6pt; background:#f2f4f7; border:0.5pt solid #c6cfda;
  padding:6pt; line-height:1.25; white-space:pre-wrap; wrap-option: wrap; margin: 6pt 0 10pt;}
table { border-collapse: collapse; width: 100%; margin: 8pt 0 4pt; font-size: 9.6pt; }
th { background:#e7edf5; border:0.6pt solid #8a97a8; padding:3.5pt 4.5pt; text-align:left;
  font-family:"Times-Bold";}
td { border:0.6pt solid #9aa6b4; padding:3pt 4.5pt; vertical-align: top;
  word-wrap: break-word; -pdf-word-wrap: CJK;}
td code, th code { font-size: 8.8pt; word-wrap: break-word; -pdf-word-wrap: CJK;}
.figure { text-align:center; margin: 8pt 0 12pt; }
.figimg { border: 0.4pt solid #b9c2cd; }
.figcaption { font-size: 10pt; font-style: italic; margin-top: 3pt; text-align:center;
  color:#222; }
.math-display { text-align:center; margin: 7pt 0; }
.math-inl { vertical-align: middle; margin: 0 1pt; }
.page-break { page-break-before: always; }
.front-h { font-family:"Times-Bold"; font-size:16pt; color:#17365c; text-align:center; margin-bottom:14pt;}
#footerContent { text-align:center; font-size:9.5pt; color:#444; }
#emptyFooter { display: none; }
/* title page */
.titlepage { page: titlepage; text-align:center; }
.tauthor { text-align:center; margin-bottom: 6pt; }
.titlepage p { margin-bottom: 10pt; font-size:13pt; }
.title-main { font-family:"Times-Bold"; font-size:19pt; color:#17365c; line-height:1.3;
  margin: 18pt 0 10pt; text-align:center;}
.tvspace { height: 14pt; }
/* TOC */
.pdf-toc { font-size:11.5pt; }
.pdf-toc-level-1 { font-family:"Times-Bold"; margin-top:7pt; }
.pdf-toc-level-2 { margin-left: 14pt; }
.pdf-toc-level-3 { margin-left: 28pt; font-size:10.5pt; }
"""

# collapse runs of explicit page breaks to one; drop a break directly before
# an auto-breaking <h1>; strip leading break at body start
html_body = re.sub(r'(?:<div class="page-break"></div>\s*){2,}',
                   '<div class="page-break"></div>\n', html_body)
html_body = re.sub(r'<div class="page-break"></div>\s*(?=<h1)', '', html_body)
html_body = html_body.lstrip()
html_body = re.sub(r'^\s*<div class="page-break"></div>\s*', '', html_body)

doc = f"""<html><head><meta charset="utf-8"><style>{CSS}</style></head><body>
<div id="emptyFooter"></div>
<div class="titlepage">{title_html}</div>
{html_body}
<div id="footerContent"><pdf:pagenow/> of <pdf:pagecount/></div>
</body></html>"""

with open(os.path.join(ROOT, "tools", "report_render.html"), "w") as f:
    f.write(doc)

with open(OUT, "wb") as f:
    result = pisa.CreatePDF(doc, dest=f, path_callback=lambda u, rel: u,
                            encoding="utf-8")
print("PDF errors:", result.err, "| pages:", getattr(result, "page", "?"))

# Post-process: named-page empty footer is ignored by pisa, so blank the
# "page x of y" footer rectangle on the title page (page 1).
try:
    import fitz  # PyMuPDF
    pdf = fitz.open(OUT)
    pg = pdf[0]
    H, W = pg.rect.height, pg.rect.width
    BAND = H - 75  # footer sits ~56 pt above the page edge
    for rect in pg.search_for("of"):
        if rect.y0 > BAND and W*0.25 < rect.x0 < W*0.75:  # footer band, centered
            pg.add_redact_annot(rect, fill=(1, 1, 1))
    # also catch the page numbers beside "of"
    for w in pg.get_text("words"):
        x0, y0, x1, y1, word = w[:5]
        if (y0 > BAND and W*0.25 < x0 < W*0.75 and word.strip().isdigit()):
            pg.add_redact_annot(fitz.Rect(x0-2, y0-1, x1+2, y1+1), fill=(1, 1, 1))
    pg.apply_redactions()
    pdf.save(OUT + ".tmp", garbage=3)
    pdf.close()
    os.replace(OUT + ".tmp", OUT)
except Exception as e:
    print("footer post-process skipped:", e)
print("OUT:", OUT, os.path.getsize(OUT), "bytes")

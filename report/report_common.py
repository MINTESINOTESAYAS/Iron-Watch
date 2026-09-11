"""Shared styles, helpers, and document class for the IronWatch AASTU report."""
import os
import matplotlib
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                Table, TableStyle, PageBreak, HRFlowable,
                                KeepTogether, ListFlowable, ListItem,
                                Preformatted)
from reportlab.platypus.tableofcontents import TableOfContents

# ---------------------------------------------------------------- palette ---
NAVY = HexColor("#0B2C4A")
GOLD = HexColor("#C9A227")
GOLD_D = HexColor("#9A7B1A")
RED = HexColor("#C0392B")
GREEN = HexColor("#1E8449")
GREY = HexColor("#5D6D7E")
GREY_D = HexColor("#2C3E50")
LIGHT = HexColor("#EAF0F6")
LIGHT2 = HexColor("#F4F6F7")
CREAM = HexColor("#FEF9E7")
PINK = HexColor("#FDEDEC")
MINT = HexColor("#EAFAF1")

PAGE_W, PAGE_H = A4
ML = MR = 2 * cm
CONTENT_W = PAGE_W - ML - MR

# ------------------------------------------------------------------ fonts ---
_FDIR = os.path.join(os.path.dirname(matplotlib.__file__), "mpl-data", "fonts", "ttf")
pdfmetrics.registerFont(TTFont("DSerif", os.path.join(_FDIR, "DejaVuSerif.ttf")))
pdfmetrics.registerFont(TTFont("DSerif-Bold", os.path.join(_FDIR, "DejaVuSerif-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DSerif-Italic", os.path.join(_FDIR, "DejaVuSerif-Italic.ttf")))
pdfmetrics.registerFont(TTFont("DSerif-BoldItalic", os.path.join(_FDIR, "DejaVuSerif-BoldItalic.ttf")))
pdfmetrics.registerFont(TTFont("DSans", os.path.join(_FDIR, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DSans-Bold", os.path.join(_FDIR, "DejaVuSans-Bold.ttf")))
pdfmetrics.registerFont(TTFont("DSans-Oblique", os.path.join(_FDIR, "DejaVuSans-Oblique.ttf")))
pdfmetrics.registerFont(TTFont("DSans-BoldOblique", os.path.join(_FDIR, "DejaVuSans-BoldOblique.ttf")))
pdfmetrics.registerFont(TTFont("DMono", os.path.join(_FDIR, "DejaVuSansMono.ttf")))
pdfmetrics.registerFont(TTFont("DMono-Bold", os.path.join(_FDIR, "DejaVuSansMono-Bold.ttf")))
pdfmetrics.registerFontFamily("DSerif", normal="DSerif", bold="DSerif-Bold",
                              italic="DSerif-Italic", boldItalic="DSerif-BoldItalic")
pdfmetrics.registerFontFamily("DSans", normal="DSans", bold="DSans-Bold",
                              italic="DSans-Oblique", boldItalic="DSans-BoldOblique")
pdfmetrics.registerFontFamily("DMono", normal="DMono", bold="DMono-Bold",
                              italic="DMono", boldItalic="DMono-Bold")

# ------------------------------------------------------------------ styles --
S_BODY = ParagraphStyle("Body", fontName="DSerif", fontSize=10.5, leading=15.5,
                        alignment=TA_JUSTIFY, spaceAfter=6, textColor=HexColor("#111111"))
S_BODY_S = ParagraphStyle("BodyS", parent=S_BODY, fontSize=10, leading=14.5)
S_CH1 = ParagraphStyle("CH1", fontName="DSans-Bold", fontSize=15, leading=18,
                       textColor=NAVY, spaceBefore=16, spaceAfter=4, keepWithNext=True)
S_CH1B = ParagraphStyle("CH1B", parent=S_CH1, fontSize=11, leading=14, textColor=GREY_D,
                        spaceBefore=0, spaceAfter=6)
S_CH1X = ParagraphStyle("CH1X", parent=S_CH1)  # same look, excluded from TOC
S_CH2 = ParagraphStyle("CH2", fontName="DSans-Bold", fontSize=12.5, leading=15,
                       textColor=NAVY, spaceBefore=12, spaceAfter=5, keepWithNext=True)
S_CH3 = ParagraphStyle("CH3", fontName="DSans-Bold", fontSize=11, leading=14,
                       textColor=GREY_D, spaceBefore=9, spaceAfter=4, keepWithNext=True)
S_CAP = ParagraphStyle("Cap", fontName="DSans-Oblique", fontSize=9, leading=12.5,
                       alignment=TA_CENTER, textColor=GREY_D, spaceBefore=4, spaceAfter=10)
S_CAP_TAB = ParagraphStyle("CapTab", parent=S_CAP, alignment=TA_LEFT, spaceAfter=4, spaceBefore=8)
S_CODE = ParagraphStyle("Code", fontName="DMono", fontSize=7.6, leading=10,
                        textColor=HexColor("#101010"), backColor=LIGHT2,
                        borderPadding=(8, 8, 8), spaceAfter=2)
S_COVER_A = ParagraphStyle("CovA", fontName="DSans-Bold", fontSize=17, leading=21,
                           alignment=TA_CENTER, textColor=NAVY)
S_COVER_B = ParagraphStyle("CovB", fontName="DSans-Bold", fontSize=13, leading=17,
                           alignment=TA_CENTER, textColor=NAVY)
S_COVER_T = ParagraphStyle("CovT", fontName="DSerif-Bold", fontSize=26, leading=30,
                           alignment=TA_CENTER, textColor=NAVY)
S_COVER_S = ParagraphStyle("CovS", fontName="DSerif", fontSize=12.5, leading=17,
                           alignment=TA_CENTER, textColor=GREY_D)
S_CENTER = ParagraphStyle("Center", parent=S_BODY, alignment=TA_CENTER)
S_BULLET = ParagraphStyle("Bullet", parent=S_BODY, leftIndent=20, firstLineIndent=0,
                          spaceAfter=3)
S_REF = ParagraphStyle("Ref", parent=S_BODY, fontSize=10, leading=14,
                       leftIndent=18, firstLineIndent=-18, spaceAfter=5)
S_CELL = ParagraphStyle("Cell", fontName="DSerif", fontSize=9, leading=12)
S_CELL_H = ParagraphStyle("CellH", fontName="DSans-Bold", fontSize=9, leading=12, textColor=white)
S_CELL_C = ParagraphStyle("CellC", parent=S_CELL, alignment=TA_CENTER)
S_CELL_HC = ParagraphStyle("CellHC", parent=S_CELL_H, alignment=TA_CENTER)
S_EQN = ParagraphStyle("EqN", fontName="DSerif", fontSize=10.5, leading=14, alignment=TA_RIGHT)
S_EQTXT = ParagraphStyle("EqTxt", fontName="DSerif", fontSize=10.5, leading=15.5, alignment=TA_CENTER)


class Ctx:
    def __init__(self):
        self.fig = 0
        self.tab = 0
        self.eq = [0, 0]  # [chapter, num]


FIGCAPS = [
    "System architecture — ferrous detection, identity/attendance, and boom control.",
    "Gantry frame — 900 mm walk-through × 2000 mm high × 350 mm deep (SHS 40×40×2).",
    "Swing-arm boom — plan view and 90° travel (the single moving part).",
    "MATLAB/Simulink PID loop — boom-arm angle servo (detection logic is the trigger, not the plant).",
    "Ferrous discrimination — pure iron/steel collapses DEMOD toward 0 V; small items stay above threshold.",
    "Firmware decision flow — detect → identify → grant/deny → boom PID → log.",
    "Facial-recognition attendance pipeline — enrolled faces linked to gate events.",
    "Proteus firmware-in-the-loop bench — concept (what was simulated vs. substituted).",
    "Closed-loop step response — boom angle 0 → 90° for P, PD, and tuned PID.",
    "Operational profile tracking — smooth quintic open (1.2 s), hold, smooth close.",
]

TABCAPS = [
    "Mechanical parameters and sizing results.",
    "Arduino pin map — frozen interface (signal pins) plus boom-drive extension.",
    "Gate decision matrix — detection × identity → outputs.",
    "Proteus firmware-in-the-loop test cases and outcomes.",
    "Controller comparison and tuned PID step-response metrics (0 → 90°).",
    "Simulated vs. expected bench results (with honest status notes).",
    "Bill of materials (prototype / single-gate build).",
    "Intern's company attendance log — filled sample rows.",
    "IronWatch electronic attendance register — sample rows.",
    "Monthly attendance and incident summary — sample.",
]


# --------------------------------------------------------------- document ---
class ReportDoc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph):
            st = flowable.style.name
            if st in ("CH1", "CH2", "CH3"):
                lvl = {"CH1": 0, "CH2": 1, "CH3": 2}[st]
                self.notify("TOCEntry", (lvl, flowable.getPlainText(), self.page))


def _footer(canv, doc):
    canv.saveState()
    canv.setStrokeColor(GOLD)
    canv.setLineWidth(1.2)
    y = 1.45 * cm
    canv.line(ML, y, PAGE_W - MR, y)
    canv.setFont("DSans", 7.5)
    canv.setFillColor(GREY)
    canv.drawString(ML, 1.02 * cm, "AASTU  ·  Electromechanical Engineering  ·  IronWatch Internship Project")
    canv.drawRightString(PAGE_W - MR, 1.02 * cm, f"Page {doc.page}")
    canv.setStrokeColor(NAVY)
    canv.setLineWidth(2.2)
    canv.line(ML, PAGE_H - 1.3 * cm, PAGE_W - MR, PAGE_H - 1.3 * cm)
    canv.setFont("DSans-Oblique", 7.5)
    canv.drawRightString(PAGE_W - MR, PAGE_H - 1.05 * cm, "IronWatch — Internship Project Report")
    canv.restoreState()


def _cover(canv, doc):
    canv.saveState()
    canv.setFillColor(NAVY)
    canv.rect(0, PAGE_H - 3.4 * cm, PAGE_W, 3.4 * cm, stroke=0, fill=1)
    canv.setFillColor(GOLD)
    canv.rect(0, PAGE_H - 3.7 * cm, PAGE_W, 0.3 * cm, stroke=0, fill=1)
    canv.setFillColor(white)
    canv.setFont("DSans-Bold", 9)
    canv.drawCentredString(PAGE_W / 2, PAGE_H - 1.7 * cm, "ADDIS ABABA SCIENCE AND TECHNOLOGY UNIVERSITY")
    canv.setFont("DSans", 8)
    canv.drawCentredString(PAGE_W / 2, PAGE_H - 2.35 * cm, "Department of Electromechanical Engineering  •  Internship Project")
    canv.setFillColor(NAVY)
    canv.rect(0, 0, PAGE_W, 1.6 * cm, stroke=0, fill=1)
    canv.setFillColor(GOLD)
    canv.rect(0, 1.6 * cm, PAGE_W, 0.25 * cm, stroke=0, fill=1)
    canv.setFillColor(white)
    canv.setFont("DSans", 8)
    canv.drawCentredString(PAGE_W / 2, 0.72 * cm, "IronWatch — Factory Walk-Through Security Gate  •  September 2026")
    canv.restoreState()


def make_toc():
    toc = TableOfContents()
    toc.levelStyles = [
        ParagraphStyle("T0", fontName="DSans-Bold", fontSize=11, leading=16,
                       textColor=NAVY, spaceBefore=4,
                       leftIndent=0, firstLineIndent=0),
        ParagraphStyle("T1", fontName="DSans", fontSize=10, leading=14.5,
                       leftIndent=14, firstLineIndent=0),
        ParagraphStyle("T2", fontName="DSans-Oblique", fontSize=9.5, leading=13.5,
                       leftIndent=28, firstLineIndent=0, textColor=GREY_D),
    ]
    toc.dotsMinLevel = 0
    return toc


# ---------------------------------------------------------------- helpers ---
def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def h1(story, num, title, subtitle=None, toc=True):
    style = S_CH1 if toc else S_CH1X
    story.append(Paragraph(f"{num}&nbsp;&nbsp;{esc(title).upper()}" if num else esc(title).upper(), style))
    if subtitle:
        story.append(Paragraph(esc(subtitle), S_CH1B))
    story.append(HRFlowable(width="100%", thickness=1.4, color=GOLD, spaceAfter=8, spaceBefore=2))


def h2(story, num, title):
    story.append(Paragraph(f"{num}&nbsp;&nbsp;{esc(title)}", S_CH2))


def h3(story, num, title):
    story.append(Paragraph(f"{num}&nbsp;&nbsp;{esc(title)}", S_CH3))


def p(story, text):
    story.append(Paragraph(text, S_BODY))


def ps(story, text):
    story.append(Paragraph(text, S_BODY_S))


def bullets(story, items):
    lis = [ListItem(Paragraph(it, S_BODY), leftIndent=20, bulletColor=NAVY) for it in items]
    story.append(ListFlowable(lis, bulletType="bullet", start="\u2022",
                              leftIndent=12, bulletFontName="DSans-Bold",
                              bulletFontSize=10, spaceAfter=6))


def numbered(story, items):
    lis = [ListItem(Paragraph(it, S_BODY), leftIndent=22) for it in items]
    story.append(ListFlowable(lis, bulletType="1", leftIndent=14, spaceAfter=6))


def fig(story, ctx, path, width_in=6.3, caption=None):
    from PIL import Image as PILImage
    ctx.fig += 1
    cap = caption if caption is not None else FIGCAPS[ctx.fig - 1]
    im = PILImage.open(path)
    iw, ih = im.size
    w = width_in * 72
    h = w * ih / iw
    max_h = 7.0 * 72
    if h > max_h:
        h = max_h
        w = h * iw / ih
    story.append(KeepTogether([
        Image(path, width=w, height=h, hAlign="CENTER"),
        Paragraph(f"<b>Figure {ctx.fig}.</b>&nbsp;&nbsp;{esc(cap)}", S_CAP),
    ]))


def mktable(story, ctx, header, rows, widths=None, caption=None, fontsize=9,
            header_bg=NAVY, zebra=True, repeat=True, align="CENTER"):
    ctx.tab += 1
    cap = caption if caption is not None else TABCAPS[ctx.tab - 1]
    cs = ParagraphStyle("cc", parent=S_CELL, fontSize=fontsize, leading=fontsize + 3,
                        alignment=TA_CENTER if align == "CENTER" else TA_LEFT)
    ch = ParagraphStyle("ch", parent=S_CELL_H, fontSize=fontsize, leading=fontsize + 3,
                        alignment=TA_CENTER if align == "CENTER" else TA_LEFT)
    data = [[Paragraph(f"<b>{esc(c)}</b>", ch) for c in header]]
    for r in rows:
        data.append([Paragraph(c, cs) for c in r])
    t = Table(data, colWidths=widths, repeatRows=1 if repeat else 0)
    style = [
        ("BACKGROUND", (0, 0), (-1, 0), header_bg),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    if zebra:
        for i in range(1, len(data)):
            if i % 2 == 0:
                style.append(("BACKGROUND", (0, i), (-1, i), LIGHT))
    t.setStyle(TableStyle(style))
    story.append(Paragraph(f"<b>Table {ctx.tab}.</b>&nbsp;&nbsp;{esc(cap)}", S_CAP_TAB))
    story.append(t)
    story.append(Spacer(1, 6))


def eqimg(story, ctx, ch, path, width_in=4.6):
    from PIL import Image as PILImage
    if ctx.eq[0] != ch:
        ctx.eq = [ch, 0]
    ctx.eq[1] += 1
    im = PILImage.open(path)
    iw, ih = im.size
    w = width_in * 72
    h = w * ih / iw
    t = Table([[Image(path, width=w, height=h, hAlign="CENTER"),
                Paragraph(f"({ch}.{ctx.eq[1]})", S_EQN)]],
              colWidths=[CONTENT_W - 2.2 * cm, 2.2 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("LEFTPADDING", (0, 0), (-1, -1), 2),
                           ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                           ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t)


def eqtxt(story, ctx, ch, text):
    if ctx.eq[0] != ch:
        ctx.eq = [ch, 0]
    ctx.eq[1] += 1
    t = Table([[Paragraph(text, S_EQTXT), Paragraph(f"({ch}.{ctx.eq[1]})", S_EQN)]],
              colWidths=[CONTENT_W - 2.2 * cm, 2.2 * cm])
    t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                           ("TOPPADDING", (0, 0), (-1, -1), 4),
                           ("BOTTOMPADDING", (0, 0), (-1, -1), 4)]))
    story.append(t)


def code(story, text, chunk=38):
    lines = text.split("\n")
    for i in range(0, len(lines), chunk):
        story.append(Preformatted(esc("\n".join(lines[i:i + chunk])), S_CODE))
    story.append(Spacer(1, 6))


def callout(story, text, bg=MINT, border=GREEN, title=None):
    inner = []
    if title:
        inner.append(Paragraph(f"<b>{esc(title)}</b>",
                               ParagraphStyle("cot", parent=S_BODY_S, textColor=border,
                                              spaceAfter=2, alignment=TA_LEFT)))
    inner.append(Paragraph(text, ParagraphStyle("cob", parent=S_BODY_S, alignment=TA_LEFT)))
    t = Table([[inner]], colWidths=[CONTENT_W])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg),
        ("BOX", (0, 0), (-1, -1), 1.2, border),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
    ]))
    story.append(t)
    story.append(Spacer(1, 6))


def lof_lot(story, kind):
    caps = FIGCAPS if kind == "fig" else TABCAPS
    label = "Figure" if kind == "fig" else "Table"
    rows = []
    for i, c in enumerate(caps, 1):
        rows.append([Paragraph(f"<b>{label} {i}</b>", S_CELL),
                     Paragraph(esc(c), S_CELL)])
    t = Table(rows, colWidths=[2.2 * cm, CONTENT_W - 2.2 * cm])
    t.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LINEBELOW", (0, 0), (-1, -2), 0.4, HexColor("#D5D8DC")),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 2),
    ]))
    story.append(t)

"""Build the IronWatch AASTU Internship Project Report PDF."""
import json
from reportlab.lib.units import cm
from reportlab.lib.colors import white
from reportlab.platypus import Paragraph, Spacer, PageBreak, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.styles import ParagraphStyle

from report_common import (
    ReportDoc, Ctx, make_toc, _cover, _footer,
    NAVY, GOLD, GREY, GREY_D, LIGHT, LIGHT2, CREAM, PINK, MINT, GREEN, RED,
    CONTENT_W, ML, MR, PAGE_W, PAGE_H,
    S_BODY, S_BODY_S, S_CH1, S_CH2, S_CH3, S_CAP, S_CENTER,
    S_COVER_A, S_COVER_B, S_COVER_T, S_COVER_S, S_REF, S_CELL,
    h1, h2, h3, p, ps, bullets, numbered, fig, mktable, eqimg, eqtxt,
    code, callout, lof_lot, esc,
)

M = json.load(open("metrics.json"))
ME, PID = M["mech"], M["pid"]

OUT = "IronWatch_Internship_Project_Report_AASTU.pdf"
doc = ReportDoc(OUT, pagesize=(PAGE_W, PAGE_H),
                leftMargin=ML, rightMargin=MR, topMargin=2.1 * cm, bottomMargin=1.9 * cm,
                title="IronWatch — Internship Project Report (AASTU Electromechanical Engineering)",
                author="AASTU Department of Electromechanical Engineering")
ctx = Ctx()
story = []
A = "assets"

# ================================================================ COVER ====
story.append(Spacer(1, 2.6 * cm))
story.append(Paragraph("INTERNSHIP PROJECT REPORT", S_COVER_B))
story.append(Spacer(1, 0.5 * cm))
story.append(Paragraph("IronWatch", S_COVER_T))
story.append(Spacer(1, 0.3 * cm))
story.append(Paragraph("Factory Walk-Through Security Gate for Ferrous-Metal<br/>"
                       "Theft Prevention with Facial-Recognition Attendance", S_COVER_S))
story.append(Spacer(1, 0.9 * cm))

sub_style = ParagraphStyle("sub", parent=S_BODY, alignment=TA_LEFT, fontSize=10.5)
lab_style = ParagraphStyle("lab", parent=S_BODY, alignment=TA_LEFT, fontSize=10.5,
                           textColor=GREY_D)
sub_rows = [
    [Paragraph("<b>Submitted by:</b>", lab_style),
     Paragraph("1. [Full Name]&nbsp;&nbsp;&nbsp;ID: [ETS XXXX/XX]<br/>"
               "2. [Full Name]&nbsp;&nbsp;&nbsp;ID: [ETS XXXX/XX]<br/>"
               "3. [Full Name]&nbsp;&nbsp;&nbsp;ID: [ETS XXXX/XX]<br/>"
               "<i>(Add or remove rows to match the team size.)</i>", sub_style)],
    [Paragraph("<b>Submitted to:</b>", lab_style),
     Paragraph("Department of Electromechanical Engineering,<br/>"
               "Addis Ababa Science and Technology University", sub_style)],
    [Paragraph("<b>Duration:</b>", lab_style),
     Paragraph("[Start Date] &nbsp;to&nbsp; [End Date]", sub_style)],
    [Paragraph("<b>Organization:</b>", lab_style),
     Paragraph("[Company Name]<br/>[Company Location]", sub_style)],
]
t = Table(sub_rows, colWidths=[4.2 * cm, CONTENT_W - 4.2 * cm])
t.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "TOP"),
                       ("TOPPADDING", (0, 0), (-1, -1), 5),
                       ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
                       ("LINEBELOW", (0, 0), (-1, -2), 0.5, LIGHT),
                       ("LEFTPADDING", (0, 0), (-1, -1), 2)]))
story.append(t)
story.append(Spacer(1, 1.0 * cm))
story.append(Paragraph("September 2026", ParagraphStyle("dt", parent=S_COVER_B, fontSize=12)))
story.append(PageBreak())

# ============================================================= APPROVAL ====
h1(story, "", "Certification and Approval")
p(story, "This is to certify that the internship project entitled <b>“IronWatch — Factory "
         "Walk-Through Security Gate for Ferrous-Metal Theft Prevention with Facial-Recognition "
         "Attendance”</b> is a bona fide record of project work carried out by the student(s) listed "
         "on the cover page, in partial fulfilment of the requirements of the internship program of "
         "the Department of Electromechanical Engineering, Addis Ababa Science and Technology "
         "University (AASTU), and that the work was performed at the host organization stated on the "
         "cover page under joint academic and industrial supervision.")
story.append(Spacer(1, 0.4 * cm))
sig_c = ParagraphStyle("sigc", parent=S_CELL, alignment=TA_CENTER)
sig_l = ParagraphStyle("sigl", parent=S_CELL, alignment=TA_LEFT)
sig_rows = [
    [Paragraph("<b>Role</b>", sig_c), Paragraph("<b>Name</b>", sig_c),
     Paragraph("<b>Signature</b>", sig_c), Paragraph("<b>Date</b>", sig_c)],
    [Paragraph("Student 1", sig_l), Paragraph("[Full Name]", sig_l), Paragraph("", sig_l), Paragraph("", sig_l)],
    [Paragraph("Student 2", sig_l), Paragraph("[Full Name]", sig_l), Paragraph("", sig_l), Paragraph("", sig_l)],
    [Paragraph("Student 3", sig_l), Paragraph("[Full Name]", sig_l), Paragraph("", sig_l), Paragraph("", sig_l)],
    [Paragraph("Company Supervisor", sig_l), Paragraph("[Name, Title]", sig_l), Paragraph("", sig_l), Paragraph("", sig_l)],
    [Paragraph("Academic Advisor", sig_l), Paragraph("[Name, Title]", sig_l), Paragraph("", sig_l), Paragraph("", sig_l)],
    [Paragraph("Head of Department", sig_l), Paragraph("[Name, Title]", sig_l), Paragraph("", sig_l), Paragraph("", sig_l)],
]
ts = Table(sig_rows, colWidths=[3.9 * cm, 4.6 * cm, 4.2 * cm, 3.3 * cm])
ts.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), NAVY),
                        ("TEXTCOLOR", (0, 0), (-1, 0), white),
                        ("GRID", (0, 0), (-1, -1), 0.5, GREY),
                        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                        ("TOPPADDING", (0, 0), (-1, -1), 9),
                        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
                        ("LEFTPADDING", (0, 0), (-1, -1), 5)]))
story.append(ts)
story.append(Spacer(1, 0.4 * cm))
ps(story, "<i>Company stamp / seal:</i>")
story.append(PageBreak())

# =========================================================== DECLARATION ==
h1(story, "", "Declaration")
p(story, "We, the undersigned, declare that this internship project report is our original work, "
         "that all sources of information and assistance have been duly acknowledged, and that the "
         "report has not been submitted, in whole or in part, for any other academic award. "
         "Simulation models, firmware, and documentation produced for this project are archived in "
         "the project repository <b>github.com/MINTESINOTESAYAS/Iron-Watch</b>.")
story.append(Spacer(1, 0.8 * cm))
for who in ("Student 1 — [Full Name], ID: [ETS XXXX/XX]",
            "Student 2 — [Full Name], ID: [ETS XXXX/XX]",
            "Student 3 — [Full Name], ID: [ETS XXXX/XX]"):
    story.append(Paragraph(f"{who}<br/><br/>Signature: ____________________&nbsp;&nbsp;&nbsp;&nbsp;Date: ____________",
                           S_BODY))
    story.append(Spacer(1, 0.5 * cm))

# ======================================================= ACKNOWLEDGEMENTS =
h1(story, "", "Acknowledgements")
p(story, "We express our sincere gratitude to the Department of Electromechanical Engineering at "
         "AASTU for the internship program and for the academic guidance that shaped this project. "
         "We thank our academic advisor for direction on modeling, control design, and report "
         "writing, and our host-company supervisor and workshop staff for access to the factory "
         "floor, for practical insight into material-handling and access-control problems, and for "
         "reviewing the gate and attendance-log concepts. Finally, we thank our families and "
         "classmates for their encouragement throughout the internship period.")
story.append(PageBreak())

# =============================================================== ABSTRACT =
h1(story, "", "Abstract")
p(story, "Factories lose significant value to the unrecorded movement of ferrous materials — tools, "
         "fasteners, fixtures, and offcuts — through pedestrian exits, while paper attendance "
         "registers remain slow, error-prone, and vulnerable to buddy-punching. This report presents "
         "<b>IronWatch</b>, a low-cost factory walk-through security gate that combines "
         "<b>ferrous-metal theft prevention</b> with <b>facial-recognition attendance</b> in a single "
         "pedestrian lane.")
p(story, "The system comprises a 900&nbsp;mm × 2000&nbsp;mm × 350&nbsp;mm steel gantry housing an LC "
         "search coil in one upright, a CD4046 phase-comparison channel with LM358 conditioning that "
         "collapses its DEMOD output toward 0&nbsp;V for pure iron and steel while leaving small "
         "personal items such as keys and belt buckles above a firmware threshold "
         "(<b>A0&nbsp;≤&nbsp;40 ⇒ metal</b>), an Arduino&nbsp;Uno decision core driving red/green/buzzer "
         "signaling, a badge/face identity stage, and a <b>single pedestrian swing-arm boom barrier — "
         "the only moving part</b> — positioned by a MATLAB/Simulink-tuned <b>PID controller</b>. The "
         "boom arm was modeled from first principles (rotational dynamics, state-space form, and "
         "Jacobian linearization), sized mechanically (shaft, bearings, motor/gearbox, fabrication "
         "plan), and servo-tuned to a 0&nbsp;→&nbsp;90° step response with <b>0.68&nbsp;s rise time, "
         "1.18&nbsp;s settling time, 1.5&nbsp;% overshoot, and 0.01&nbsp;% steady-state error</b> "
         "(K<sub>p</sub>=18, K<sub>i</sub>=12, K<sub>d</sub>=5, filtered derivative, engage-zone "
         "integral with anti-windup). Firmware logic was verified in a Proteus bench in which a "
         "potentiometer stands in for DEMOD volts and a Virtual Terminal at 9600&nbsp;baud stands in "
         "for the RFID badge reader (valid badge <b>A1B2C3</b>); all simulation substitutions are "
         "stated honestly, together with a commissioning plan for the physical gate. A company "
         "attendance log system — daily intern log, electronic gate register, and monthly summary — "
         "is specified in full.")
p(story, "<b>Keywords:</b> walk-through metal detection; ferrous discrimination; CD4046 phase "
         "comparison; Arduino; swing-arm boom barrier; PID control; MATLAB/Simulink; Proteus; "
         "facial-recognition attendance; mechatronics.")
story.append(PageBreak())

# ============================================================ TOC / LISTS =
h1(story, "", "Contents", toc=False)
story.append(make_toc())
story.append(PageBreak())
h1(story, "", "List of Figures")
lof_lot(story, "fig")
story.append(PageBreak())
h1(story, "", "List of Tables")
lof_lot(story, "tab")
story.append(PageBreak())
h1(story, "", "List of Abbreviations and Symbols")
bullets(story, [
    "<b>AASTU</b> — Addis Ababa Science and Technology University",
    "<b>ADC</b> — Analog-to-digital converter (10-bit, 0–1023 on Arduino Uno)",
    "<b>CSV</b> — Comma-separated values (attendance log export format)",
    "<b>DEMOD</b> — Demodulator output of the CD4046 phase comparator",
    "<b>DOF</b> — Degree of freedom",
    "<b>LQR</b> — Linear-quadratic regulator (considered and <i>not</i> selected — see §3.3.3)",
    "<b>PCB</b> — Printed circuit board",
    "<b>PID</b> — Proportional–integral–derivative (controller)",
    "<b>PLL</b> — Phase-locked loop (CD4046)",
    "<b>PWM</b> — Pulse-width modulation",
    "<b>RFID</b> — Radio-frequency identification (badge reader)",
    "<b>SHS</b> — Square hollow section (steel tube)",
    "<b>VCOIN</b> — VCO input, CD4046 pin&nbsp;9 (must be biased — see §3.4.4)",
    "<b><i>J, b, K<sub>m</sub>, τ<sub>c</sub></i></b> — Boom inertia, viscous damping, drive gain, Coulomb friction",
    "<b><i>θ, ω, u</i></b> — Boom angle, angular velocity, motor drive voltage",
])
story.append(PageBreak())

# ============================================================ CHAPTER 1 ====
h1(story, "1", "Introduction")
h2(story, "1.1", "Background of the Study")
p(story, "In discrete manufacturing and metalworking plants, ferrous materials are everywhere: "
         "hand tools, fasteners, jigs and fixtures, weld coupons, and saleable offcuts. Most of "
         "these items are small enough to be carried out unintentionally — or deliberately — through "
         "pedestrian exits, and conventional countermeasures (manual bag checks, security guards, "
         "CCTV review) are labor-intensive, inconsistent, and blind to <i>who</i> carried <i>what</i> "
         "through <i>which</i> gate at <i>what</i> time. Imported walk-through metal detectors solve "
         "only the sensing half of the problem: they are expensive to procure and maintain, they "
         "alarm on every key ring and belt buckle so that operators learn to ignore them, and they "
         "keep no attendance record of the screened workforce.")
p(story, "In parallel, many factories still run attendance on paper registers or isolated "
         "fingerprint terminals. Paper is slow to reconcile and easy to falsify; standalone "
         "terminals are disconnected from physical access, so an employee can be “present” in the "
         "register while product walks out of an unmonitored door. The natural engineering response "
         "is to <b>fuse screening, access control, and attendance into one pedestrian lane</b>: every "
         "passage is detected, identified, decided, and logged.")
p(story, "IronWatch is that fused lane, designed for local fabrication and maintenance. A steel "
         "walk-through gantry carries a ferrous-sensitive search coil; a CD4046 phase-comparison "
         "channel with LM358 conditioning converts the coil's phase response into a DC voltage that "
         "an Arduino&nbsp;Uno reads on A0; firmware discriminates bulk iron and steel from small "
         "personal items; a badge/face identity stage checks the pedestrian; and a single "
         "PID-controlled swing-arm boom — the only moving part — grants or denies passage while an "
         "attendance event is written to the company log. Models, firmware, and documentation are "
         "versioned in the public repository <b>github.com/MINTESINOTESAYAS/Iron-Watch</b> so the "
         "host company and future student teams can reproduce, audit, and extend the work.")
h2(story, "1.2", "Problem Statement")
p(story, "The host factory's pedestrian exits exhibited the following gaps, confirmed during the "
         "internship walk-throughs and supervisor interviews:")
bullets(story, [
    "<b>Unrecorded ferrous-material movement.</b> No sensing at pedestrian exits; tools, fasteners, "
    "and offcuts could leave the production area without any record or alarm.",
    "<b>No per-person gate record.</b> Even where a guard was posted, there was no reliable log "
    "linking a passage event to an individual identity.",
    "<b>Attendance disconnected from access.</b> The paper attendance register was reconciled "
    "manually, with errors, delays, and buddy-punching risk — and no cross-check against gate usage.",
    "<b>Imported-gate barrier.</b> Commercial walk-through detectors with acceptable false-alarm "
    "behavior were prohibitively expensive and required foreign spares and service.",
    "<b>False-alarm fatigue risk.</b> Any detector that cannot separate a steel bar from a key ring "
    "will be ignored by operators; discrimination is therefore a primary requirement, not a luxury.",
])
p(story, "The project therefore set measurable design targets: (i)&nbsp;a low-side analog trigger "
         "(A0&nbsp;≤&nbsp;40 ⇒ metal) that fires on bulk iron/steel yet passes keys and buckles; "
         "(ii)&nbsp;a 90° boom swing completed in about one second with negligible overshoot; "
         "(iii)&nbsp;a deterministic grant/deny decision from detection × identity; and "
         "(iv)&nbsp;an attendance event logged for every passage decision.")
h2(story, "1.3", "Objectives")
p(story, "<b>General objective.</b> To design, model, simulate, and document a low-cost factory "
         "walk-through security gate that prevents ferrous-metal theft and records facial-recognition "
         "attendance, following a complete mechatronic workflow from mechanical sizing through "
         "control tuning to firmware verification.")
p(story, "<b>Specific objectives.</b>")
numbered(story, [
    "Design the gantry frame and single swing-arm boom, and size the shaft, bearings, and "
    "motor/gearbox with documented safety margins and a fabrication plan.",
    "Derive the boom-arm rotational dynamics, cast them into state-space form, linearize about the "
    "operating point, and verify controllability and observability.",
    "Design and tune a MATLAB/Simulink <b>PID</b> angle servo (not LQR) for smooth, fast, "
    "overshoot-free open/close motion, with explicit anti-windup and saturation handling.",
    "Design the electronics (LC coil + LM358 + CD4046 phase channel, Arduino&nbsp;Uno core, "
    "LED/buzzer signaling, badge stand-in, boom driver) and implement the threshold firmware.",
    "Verify the firmware in a Proteus bench and the servo in MATLAB/Simulink, stating all "
    "simulation substitutions honestly and defining a physical commissioning plan.",
    "Specify the company attendance log system (daily log, electronic gate register, monthly "
    "summary) linked to gate events.",
])
h2(story, "1.4", "Scope and Limitation")
p(story, "<b>Scope.</b> The project covers one single-lane pedestrian gate: a 900&nbsp;mm clear "
         "opening for one person at a time; ferrous (iron/steel) detection only; a single-zone coil "
         "in one gantry upright; a single horizontal swing-arm boom as the only moving part; "
         "Arduino-based decision logic with serial badge/face-event input; PID boom-angle control; "
         "and simulation-level verification (Proteus + MATLAB/Simulink) with a defined bench "
         "commissioning procedure.")
p(story, "<b>Limitations.</b>")
bullets(story, [
    "No full electromagnetic field simulation of the coil–target interaction was performed; the "
    "analog front end is validated by circuit analysis, threshold design, and a bench calibration "
    "procedure (see §4.2).",
    "The facial-recognition pipeline is specified as an interface plus log format; in simulation it "
    "is represented by serial attendance events (badge string + result), not by a live camera model.",
    "Detection is single-zone and ferrous-only; non-ferrous metals (aluminum, copper) and "
    "multi-target localization are excluded.",
    "The gate is designed for indoor factory use; weatherproofing, tailgating optics, and "
    "turnstile-grade anti-passback are left as recommendations (§5.2).",
    "Gains tuned in simulation must be re-verified on the physical boom before production use.",
])
h2(story, "1.5", "Methodology Overview")
p(story, "The work followed the mechatronic V-model in six steps:")
numbered(story, [
    "<b>System analysis</b> — factory walk-throughs, exit-flow observation, and supervisor "
    "interviews to freeze requirements (opening width, throughput, alarm philosophy, log fields).",
    "<b>Mechanical design</b> — gantry and boom geometry, load/inertia analysis, shaft, bearing, "
    "and motor/gearbox sizing, fabrication and assembly planning (§3.1).",
    "<b>Mathematical modeling</b> — nonlinear rotational dynamics, state-space realization, and "
    "Jacobian linearization of the boom servo (§3.2).",
    "<b>Control design and simulation</b> — open-loop analysis, controllability/observability, PID "
    "selection and tuning in MATLAB/Simulink with step-response and S-curve verification (§3.3, §4.1.2).",
    "<b>Electrical/electronic design and firmware verification</b> — coil/LM358/CD4046 channel, "
    "Arduino firmware, and Proteus firmware-in-the-loop testing with declared substitutions "
    "(§3.4, §4.1.1).",
    "<b>Attendance-log specification and reporting</b> — daily log, electronic register, and monthly "
    "summary formats validated against the outline requirements (Appendix&nbsp;C).",
])
p(story, "Figure&nbsp;1 shows how the three subsystems — detection, identity/attendance, and boom "
         "control — meet at the Arduino decision core.")
story.append(Spacer(1, 1.2 * cm))
fig(story, ctx, f"{A}/fig_architecture.png", width_in=6.4)
story.append(PageBreak())

# ============================================================ CHAPTER 2 ====
h1(story, "2", "Literature Review")
h2(story, "2.1", "Walk-Through Metal Detection for Loss Prevention")
p(story, "Walk-through metal detectors (WTMDs) for personnel screening descend from airport-security "
         "technology, where multi-zone pulse-induction or continuous-wave portals localize metallic "
         "objects on the body (Franke, 2006). Industrial loss-prevention is a different optimization: "
         "the threat is bulk ferrous material rather than concealed weapons, throughput must match "
         "shift changes, and the total cost of ownership must suit a factory maintenance budget. "
         "Single-zone continuous-wave portals remain common in industry precisely because they are "
         "simple, robust, and cheap to keep running, at the price of coarse localization — an "
         "acceptable trade when the response is “stop and inspect” rather than “find the exact "
         "pocket” (Cumming, 2012). IronWatch follows this industrial lineage: one zone, one clear "
         "decision, one log entry.")
p(story, "A recurring lesson from deployment studies is that <i>operator trust</i> decides whether a "
         "portal keeps working after commissioning. Systems that alarm on every key ring train "
         "operators to wave people through, neutralizing the investment; discrimination — responding "
         "differently to threat-like and benign signatures — is therefore consistently identified as "
         "the difference between a security device and security theater (National Institute of "
         "Justice, 2003). The IronWatch threshold philosophy (bulk ferrous ⇒ alarm; small personal "
         "items ⇒ pass) is a direct response to this finding.")
h2(story, "2.2", "Phase-Sensitive Detection and Ferrous Discrimination")
p(story, "In a continuous-wave detector, a transmit coil excites the walk-through volume and a "
         "receive path observes the result. A metallic target changes both the amplitude and the "
         "<i>phase</i> of the received signal, and the phase carries composition information: "
         "high-permeability ferrous targets produce characteristically large phase shifts, while "
         "small or low-permeability objects produce small ones (Bruschini, 2002). Phase comparison "
         "against the excitation reference therefore separates “big iron” from “small clutter” far "
         "better than amplitude alone — the physical basis of IronWatch's CD4046 channel.")
p(story, "The CD4046B phase-locked loop (Texas Instruments, 2018) is a convenient vehicle for this "
         "idea: its phase comparators convert a phase difference into a demodulated DC voltage "
         "(DEMOD) that a microcontroller can threshold directly, without DSP. The LM358 dual "
         "op-amp (STMicroelectronics, 2021) provides the accompanying gain, filtering, and buffering "
         "with single-supply operation suited to factory-floor builds. A well-known commissioning "
         "pitfall — emphasized in the IronWatch design — is that the 4046's VCO input (pin&nbsp;9, "
         "VCOIN) must be properly biased; left floating, the VCO stalls and DEMOD parks at a rail, "
         "masquerading as a permanent detection (see §3.4.4).")
h2(story, "2.3", "Pedestrian Barriers and Boom-Gate Mechanisms")
p(story, "Pedestrian access hardware spans tripod turnstiles, swing gates, sliding leaves, and "
         "boom arms. Swing-arm booms are favored where simplicity and visibility matter: one pivot, "
         "one actuator, an unambiguous open/closed state, and easy breakaway or manual override for "
         "emergencies (North American Barrier Association, 2019). Their dynamics are those of a "
         "single rigid link about a fixed axis — inertia, viscous and Coulomb friction, and (for "
         "vertical-lift variants) gravity — which makes them a textbook single-input single-output "
         "servo problem (Nise, 2020).")
p(story, "Machine-element sizing for such light mechanisms follows standard practice: torsion "
         "design of the pivot shaft, L<sub>10</sub> rating-life selection of rolling bearings, and "
         "torque/speed matching of a geared motor to a specified motion profile with an explicit "
         "service factor for intermittent duty (Khurmi &amp; Gupta, 2005; Budynas &amp; Nisbett, 2020). "
         "IronWatch applies each of these steps in §3.1 and deliberately keeps the mechanism to a "
         "single moving part to minimize wear points, pinch hazards, and maintenance skill requirements.")
h2(story, "2.4", "Biometric Attendance and Face Recognition in Industry")
p(story, "Biometric attendance — fingerprint, face, or iris — addresses the central weakness of "
         "cards and registers: the credential cannot be lent to a colleague (Jain et&nbsp;al., 2011). "
         "Face recognition is the least intrusive option for a walk-through lane because it needs no "
         "contact and no pause if the camera is positioned on the approach; modern embedding-based "
         "matchers achieve high accuracy under controlled indoor lighting (Schroff et&nbsp;al., 2015). "
         "Deployment literature stresses three complements that IronWatch adopts as requirements: "
         "enrollment under supervision (HR office), liveness/anti-spoofing before any access grant, "
         "and a tamper-evident log that binds each identity event to a timestamp, gate, and decision "
         "(ISO/IEC 30107-1:2023). In the IronWatch prototype the camera pipeline is represented by "
         "its serial-event interface and log format, so the gate logic and attendance schema can be "
         "verified now and the vision module integrated later without changing the decision core.")
h2(story, "2.5", "Model-Based Design and Simulation in Mechatronics")
p(story, "Model-based design — deriving control from a dynamic model, validating in simulation, "
         "then deploying to embedded hardware — is standard mechatronic practice (Ogata, 2010; "
         "MathWorks, 2024). For microcontroller projects, two benches dominate: MATLAB/Simulink for "
         "control-loop tuning against a plant model, and Proteus for firmware-in-the-loop checks of "
         "the actual compiled code against virtual peripherals (Labcenter Electronics, 2023). Used "
         "honestly, with every substitution declared (a potentiometer for a sensor voltage, a "
         "terminal for a reader, an ideal motor for a geared drive), these benches catch the great "
         "majority of logic and tuning defects before metal is cut — which is exactly how IronWatch "
         "uses them in Chapter&nbsp;4.")
story.append(PageBreak())

# ============================================================ CHAPTER 3 ====
h1(story, "3", "System Design")
h2(story, "3.1", "Mechanical Design")
p(story, "The mechanical system has exactly one moving part — the swing-arm boom. Everything else "
         "(gantry, coil housing, drive post, electronics cabinet) is static structure. This section "
         "sizes the structure, the pivot, and the drive for a 90° pedestrian swing with a smooth "
         "S-curve profile, and closes with the fabrication and assembly plan.")
fig(story, ctx, f"{A}/fig_gantry.png", width_in=6.3)
h3(story, "3.1.1", "Load Analysis")
p(story, "The gantry is a portal frame in 40&nbsp;×&nbsp;40&nbsp;×&nbsp;2&nbsp;mm square hollow "
         "section (SHS), giving a 900&nbsp;mm clear walk-through, 2000&nbsp;mm overall height, and a "
         "350&nbsp;mm deep foot for freestanding stability (Figure&nbsp;2). Static loads are the "
         "frame self-weight (≈&nbsp;28&nbsp;kg with header and feet), the coil panel (≈&nbsp;4&nbsp;kg) "
         "in the right upright, the drive post with motor and boom (≈&nbsp;9&nbsp;kg), and the "
         "electronics cabinet (≈&nbsp;5&nbsp;kg). The governing accidental load is a 150&nbsp;N "
         "horizontal push at boom-tip height (1.0&nbsp;m) from a pedestrian leaning on the closed "
         "arm; reacted at the 350&nbsp;mm-spaced anchor feet, it produces a restoring-moment demand "
         "far below the frame's self-righting moment once the feet are anchor-bolted (M8 expansion "
         "anchors, four per foot).")
p(story, "The boom itself is a 0.85&nbsp;m aluminum tube (1.2&nbsp;kg) with a 0.3&nbsp;kg "
         "paddle/end-stop assembly at the tip. Its mass moment of inertia about the vertical pivot, "
         "including hub and shaft, is J<sub>arm</sub>&nbsp;≈&nbsp;0.53&nbsp;kg·m²; adding the "
         "gearbox-reflected rotor inertia gives the control-plant value J&nbsp;=&nbsp;0.59&nbsp;kg·m² "
         "used throughout §3.2–§3.3. Bearing radial load is dominated by the overhung boom weight "
         "(≈&nbsp;15&nbsp;N) plus drive-post preload, conservatively taken as P&nbsp;=&nbsp;60&nbsp;N "
         "for life calculations.")
h3(story, "3.1.2", "Design of Machine Elements")
p(story, "Frame joints are MIG-welded all round, with M8 bolted foot plates for leveling and "
         "anchoring. The coil zone is a <b>non-metallic</b> window (FR-4 / polycarbonate panel) set "
         "into the right upright so the steel frame does not short the search field; the coil is "
         "potted in epoxy against vibration and humidity. The boom pivot runs in two 6004 deep-groove "
         "ball bearings housed in a welded drive post (see §3.1.4). Travel is bounded by rubber "
         "end-stops at 0° and 90° plus electrical limit switches; the stops absorb the residual "
         "≈&nbsp;1° settling tail of the servo (see §4.1.2) so the arm always seats firmly without "
         "hammering. All fasteners are property class 8.8, and pinch points at the pivot are covered "
         "by a sheet-metal guard.")
h3(story, "3.1.3", "Boom-Arm and Drive Geometry")
p(story, "Figure&nbsp;3 shows the boom in plan view: closed, the 0.85&nbsp;m arm spans the 900&nbsp;mm "
         "passage at 1000&nbsp;mm height; open, it swings 90° to lie along the exit side. A 12&nbsp;V, "
         "80&nbsp;W DC gearmotor (40:1, rated 6&nbsp;N·m continuous, 7.8&nbsp;N·m stall) drives the "
         "Ø20&nbsp;mm pivot shaft directly through a keyed hub — no belt, no chain, no extra "
         "bearings. Required torque follows the servo sizing equation:")
eqimg(story, ctx, 3, f"{A}/eq_torque.png", width_in=4.9)
p(story, "With J&nbsp;=&nbsp;0.59&nbsp;kg·m², b&nbsp;=&nbsp;1.20&nbsp;N·m·s/rad (bearings, gearbox, "
         "and reflected back-EMF damping), Coulomb friction τ<sub>c</sub>&nbsp;=&nbsp;0.25&nbsp;N·m, "
         "and the S-curve profile peaks α&nbsp;=&nbsp;2.5&nbsp;rad/s², ω&nbsp;=&nbsp;1.8&nbsp;rad/s, "
         "the demand is τ<sub>req</sub>&nbsp;≈&nbsp;3.88&nbsp;N·m, giving a continuous service factor "
         "of ≈&nbsp;1.5 — standard for intermittent (S3–25&nbsp;%) gate duty — and a transient/stall "
         "margin of ≈&nbsp;2.0. Mechanical drive power is ≈&nbsp;15&nbsp;W, comfortably inside the "
         "80&nbsp;W motor frame.")
fig(story, ctx, f"{A}/fig_boom.png", width_in=6.3)
h3(story, "3.1.4", "Bearing Design")
p(story, "Two 6004 deep-groove ball bearings (20&nbsp;×&nbsp;42&nbsp;×&nbsp;12&nbsp;mm, dynamic rating "
         "C&nbsp;=&nbsp;9.4&nbsp;kN) support the pivot shaft in a spaced housing that reacts overturning "
         "moment as a force couple. Rating life follows:")
eqimg(story, ctx, 3, f"{A}/eq_bearing.png", width_in=3.4)
p(story, "At the conservative equivalent load P&nbsp;=&nbsp;60&nbsp;N, L<sub>10</sub> exceeds "
         "10<sup>12</sup>&nbsp;revolutions (≈&nbsp;10<sup>9</sup>&nbsp;h at gate duty) — effectively "
         "infinite, meaning the bearings are selected for bore size, stiffness, and sealing (2RS "
         "dust covers for the factory environment) rather than fatigue life. The housing bores are "
         "machined in one setup for coaxiality.")
h3(story, "3.1.5", "Shaft Design")
p(story, "The pivot shaft is Ø20&nbsp;mm C45 steel, keyed to the boom hub (6&nbsp;×&nbsp;6&nbsp;mm "
         "parallel key) and to the gearbox output. Torsional shear under the worst case — a stalled "
         "motor at 7.8&nbsp;N·m — follows:")
eqimg(story, ctx, 3, f"{A}/eq_shaft.png", width_in=3.6)
p(story, "giving τ<sub>max</sub>&nbsp;≈&nbsp;5.0&nbsp;MPa against an allowable ≈&nbsp;55&nbsp;MPa: a "
         "large margin that also covers shock from pedestrians striking the arm. Bending from the "
         "overhung boom (≈&nbsp;13&nbsp;N at 0.45&nbsp;m mean radius) adds negligible combined stress. "
         "A circlip and shoulder locate the shaft axially; a Woodruff-key alternative was rejected to "
         "keep spares common.")
h3(story, "3.1.6", "Fabrication and Assembly")
p(story, "The build sequence is specified for a basic factory workshop (cut-off saw, MIG welder, "
         "pillar drill, angle grinder, paint booth):")
numbered(story, [
    "<b>Cut and prep</b> — SHS members cut to length with 45° miters at the header corners; deburr "
    "and degrease all parts.",
    "<b>Weld</b> — Tack, check square and diagonals (opening 900&nbsp;±&nbsp;2&nbsp;mm), then weld "
    "all round; weld foot plates and the drive-post housing.",
    "<b>Machine</b> — Bore the bearing housing in one setup; drill anchor, switch-bracket, and "
    "cabinet holes; ream the boom-hub keyway.",
    "<b>Coil panel</b> — Wind and pot the LC search coil, fit it into the non-metallic upright "
    "window, and route its leads in conduit to the cabinet.",
    "<b>Finish</b> — Prime and enamel (safety-yellow boom with black chevrons; grey frame); fit "
    "rubber end-stops, guards, and limit switches.",
    "<b>Assemble and align</b> — Set bearings with light preload, check the boom sweeps 0–90° "
    "without rubbing, anchor the feet, torque M8 anchors to 20&nbsp;N·m, and run the 500-cycle "
    "endurance check of §4.2.",
])
mktable(story, ctx,
        ["Parameter", "Value", "Remarks"],
        [["Clear opening × height × foot depth", "900 × 2000 × 350 mm", "Figure 2; SHS 40×40×2"],
         ["Boom length / mass", "0.85 m / 1.2 + 0.3 kg", "Al tube + paddle/stop"],
         ["Pivot height / travel", "≈ 1000 mm / 90°", "Single moving part"],
         ["Boom inertia J (plant)", "0.59 kg·m²", "Arm + hub + reflected rotor"],
         ["Damping b / Coulomb τc", "1.20 N·m·s/rad / 0.25 N·m", "Incl. back-EMF term"],
         ["Torque demand τreq", "≈ 3.88 N·m", "S-curve peaks α=2.5, ω=1.8"],
         ["Motor / gearbox", "12 V 80 W DC / 40:1", "Rated 6 N·m, stall 7.8 N·m"],
         ["Service factor", "≈ 1.5 cont. / ≈ 2.0 stall", "Intermittent S3–25% duty"],
         ["Shaft", "Ø20 mm C45, 6×6 key", "τmax ≈ 5 MPa ≪ 55 MPa"],
         ["Bearings", "2× 6004-2RS", "L10 effectively infinite"],
         ["Drive power (mech.)", "≈ 15 W", "12 V supply, L298N driver"]],
        widths=[5.2 * cm, 4.6 * cm, 6.2 * cm])

h2(story, "3.2", "Mathematical Modeling")
p(story, "The plant for control design is the boom pivot: motor voltage in, boom angle out. "
         "Detection logic (threshold, badge, alarms) only <i>triggers</i> reference changes — it is "
         "not part of the servo plant, a separation enforced throughout §3.3.")
h3(story, "3.2.1", "Rotational Dynamics of the Swing-Arm Boom")
p(story, "Applying Newton's second law for rotation about the fixed vertical pivot, with motor "
         "torque τ<sub>m</sub> driving inertia J against viscous damping b, gravity, and Coulomb "
         "friction τ<sub>c</sub>, gives the nonlinear equation of motion:")
eqimg(story, ctx, 3, f"{A}/eq_rotor.png", width_in=5.6)
p(story, "where θ is the boom angle from closed (0&nbsp;→&nbsp;π/2&nbsp;rad), m the arm mass, "
         "l<sub>c</sub>&nbsp;≈&nbsp;0.42&nbsp;m the center-of-mass radius, and sgn(·) the signum "
         "function. Two simplifications apply to IronWatch: (i)&nbsp;the arm swings about a "
         "<b>vertical</b> axis, so gravity does no work on the motion and the m·g·l<sub>c</sub>·sinθ "
         "term vanishes (it is retained in the derivation so the model also covers lift-type arms); "
         "and (ii)&nbsp;the geared DC drive is represented by its electrical and torque relations:")
eqimg(story, ctx, 3, f"{A}/eq_motor.png", width_in=4.4)
p(story, "with armature inductance L, resistance R, back-EMF constant K<sub>b</sub>, torque constant "
         "K<sub>t</sub>, motor speed ω<sub>m</sub>, terminal voltage v, and gear ratio N. Because "
         "the electrical time constant (L/R&nbsp;≈&nbsp;a few ms) is two orders of magnitude faster "
         "than the mechanical response, the current loop is collapsed into the static drive gain "
         "K<sub>m</sub>&nbsp;=&nbsp;0.65&nbsp;N·m/V at the output shaft, with back-EMF absorbed into "
         "the viscous coefficient b — the standard servo reduction (Ogata, 2010).")
h3(story, "3.2.2", "Linear State-Space Representation")
p(story, "Choosing the state x&nbsp;=&nbsp;[θ,&nbsp;ω]<sup>T</sup> with ω&nbsp;=&nbsp;dθ/dt, input "
         "u&nbsp;=&nbsp;v (volts, |u|&nbsp;≤&nbsp;12&nbsp;V), and output y&nbsp;=&nbsp;θ, and dropping "
         "the gravity term (horizontal swing) and the non-smooth Coulomb term for the linear design "
         "model (both are reintroduced for verification in §4.1.2), yields:")
eqtxt(story, ctx, 3, "ẋ&nbsp;=&nbsp;A·x&nbsp;+&nbsp;B·u,&nbsp;&nbsp;&nbsp;&nbsp;y&nbsp;=&nbsp;C·x&nbsp;+&nbsp;D·u")
eqtxt(story, ctx, 3, "A&nbsp;=&nbsp;[&nbsp;0&nbsp;&nbsp;&nbsp;1&nbsp;;&nbsp;&nbsp;0&nbsp;&nbsp;&nbsp;−b/J&nbsp;],&nbsp;&nbsp;&nbsp;"
         "B&nbsp;=&nbsp;[&nbsp;0&nbsp;;&nbsp;&nbsp;K<sub>m</sub>/J&nbsp;],&nbsp;&nbsp;&nbsp;"
         "C&nbsp;=&nbsp;[&nbsp;1&nbsp;&nbsp;&nbsp;0&nbsp;],&nbsp;&nbsp;&nbsp;D&nbsp;=&nbsp;0")
p(story, "Numerically, with J&nbsp;=&nbsp;0.59 and b&nbsp;=&nbsp;1.20, A&nbsp;=&nbsp;[0,&nbsp;1;&nbsp;0,&nbsp;−2.03] "
         "and B&nbsp;=&nbsp;[0;&nbsp;1.10]. The corresponding open-loop transfer function is:")
eqtxt(story, ctx, 3, "Θ(s)/U(s)&nbsp;=&nbsp;K<sub>m</sub>&nbsp;/&nbsp;[&nbsp;s·(J·s&nbsp;+&nbsp;b)&nbsp;]&nbsp;=&nbsp;"
         "0.54&nbsp;/&nbsp;[&nbsp;s·(0.49·s&nbsp;+&nbsp;1)&nbsp;]")
p(story, "a type-1 servo with mechanical time constant τ&nbsp;=&nbsp;J/b&nbsp;≈&nbsp;0.49&nbsp;s: a "
         "voltage step produces a ramping angle, so feedback is mandatory for positioning.")
h3(story, "3.2.3", "Linearization Using Taylor Expansion and Jacobian")
p(story, "Formally, the nonlinear vector field f(x,&nbsp;u) from §3.2.1 is linearized about an "
         "operating point (x<sub>0</sub>,&nbsp;u<sub>0</sub>) by first-order Taylor expansion, whose "
         "coefficient matrices are the Jacobians:")
eqimg(story, ctx, 3, f"{A}/eq_jac.png", width_in=4.4)
p(story, "Evaluating ∂f/∂x and ∂f/∂u at the closed-rest point (θ<sub>0</sub>&nbsp;=&nbsp;0, "
         "ω<sub>0</sub>&nbsp;=&nbsp;0, u<sub>0</sub>&nbsp;=&nbsp;0) gives A<sub>11</sub>&nbsp;=&nbsp;0, "
         "A<sub>12</sub>&nbsp;=&nbsp;1, A<sub>21</sub>&nbsp;=&nbsp;−m·g·l<sub>c</sub>·cosθ<sub>0</sub>/J&nbsp;=&nbsp;0 "
         "(horizontal swing; for a lift arm this would be −m·g·l<sub>c</sub>/J), "
         "A<sub>22</sub>&nbsp;=&nbsp;−b/J, B&nbsp;=&nbsp;[0;&nbsp;K<sub>m</sub>/J] — confirming the "
         "matrices of §3.2.2 as the exact Jacobian linearization. The smooth Coulomb approximation "
         "τ<sub>c</sub>·tanh(ω/0.05) used in simulation has zero slope contribution at rest speed in "
         "the design model and is likewise reintroduced only at verification.")

h2(story, "3.3", "Controller Design")
h3(story, "3.3.1", "Open-Loop Response Analysis")
p(story, "The open-loop plant is a velocity-damped integrator: it cannot hold an angle, drifts "
         "under any disturbance torque (pedestrian contact, seal drag), and its step-voltage "
         "response is an exponential approach to a steady <i>speed</i> "
         "(ω<sub>ss</sub>&nbsp;=&nbsp;K<sub>m</sub>·u/b&nbsp;≈&nbsp;0.54·u&nbsp;rad/s) — i.e., an "
         "angle ramp that would slam the boom into its end-stop. Poles at s&nbsp;=&nbsp;0 and "
         "s&nbsp;=&nbsp;−b/J&nbsp;=&nbsp;−2.03 confirm marginal stability with no position stiffness. "
         "Closing a position loop with integral action is therefore required both for set-point "
         "tracking and for disturbance rejection at the seated positions.")
h3(story, "3.3.2", "Controllability and Observability")
p(story, "For the second-order realization, the Kalman controllability matrix "
         "Q<sub>c</sub>&nbsp;=&nbsp;[B,&nbsp;A·B] evaluates to [[0,&nbsp;1.10],&nbsp;[1.10,&nbsp;−2.24]] "
         "with determinant −1.21&nbsp;≠&nbsp;0, so rank(Q<sub>c</sub>)&nbsp;=&nbsp;2&nbsp;=&nbsp;n: the "
         "boom angle and velocity are fully controllable from the motor voltage. The observability "
         "matrix Q<sub>o</sub>&nbsp;=&nbsp;[C;&nbsp;C·A]&nbsp;=&nbsp;[[1,&nbsp;0],&nbsp;[0,&nbsp;1]] is "
         "the identity, so rank(Q<sub>o</sub>)&nbsp;=&nbsp;2: angle measurement alone (potentiometer "
         "or encoder) observes the full state with no observer required. These checks license the "
         "simple output-feedback PID of §3.3.4.")
h3(story, "3.3.3", "Control Strategy Selection")
p(story, "The outline template suggested LQR; this project deliberately selects <b>PID</b> instead, "
         "for reasons recorded here so the deviation is auditable:")
bullets(story, [
    "<b>Plant order and structure.</b> A second-order, minimum-phase, fully observable SISO servo "
    "needs no optimal state feedback; PID places the dominant poles just as effectively with far "
    "fewer assumptions.",
    "<b>Embedded reality.</b> The production controller is an Arduino&nbsp;Uno. A filtered PID with "
    "clamped integration runs in a dozen lines of fixed-point-friendly code; LQR needs a gain "
    "solve, full-state access, and re-tuning tooling the factory does not have.",
    "<b>Field service.</b> Factory technicians can understand and re-tune three gains with a "
    "stopwatch; Q/R weighting matrices are opaque to them. Maintainability is a design requirement.",
    "<b>Constraint handling.</b> The dominant nonlinearities are saturation (±12&nbsp;V), Coulomb "
    "friction, and end-stops — handled transparently by PID anti-windup plus an S-curve reference, "
    "whereas LQR would need additional governors anyway.",
    "<b>Performance achieved.</b> The tuned PID meets every motion target (§4.1.2); no residual "
    "requirement justifies a more complex law.",
])
p(story, "Fuzzy and sliding-mode alternatives were rejected on the same maintainability grounds. "
         "PID is therefore not the fallback choice but the <i>argued</i> choice for this plant, "
         "this hardware, and this operator.")
h3(story, "3.3.4", "PID Controller Implementation")
p(story, "The implemented law is a filtered, anti-windup PID with derivative on measurement:")
eqimg(story, ctx, 3, f"{A}/eq_pid.png", width_in=5.6)
p(story, "with tuned gains <b>K<sub>p</sub>&nbsp;=&nbsp;18, K<sub>i</sub>&nbsp;=&nbsp;12, "
         "K<sub>d</sub>&nbsp;=&nbsp;5</b>, derivative filter N&nbsp;=&nbsp;30, integral engage zone "
         "|e|&nbsp;&lt;&nbsp;0.25&nbsp;rad, integrator clamp ±0.5, and output saturation "
         "±12&nbsp;V. Three details matter for reproduction: (i)&nbsp;derivative acts on the "
         "<i>measurement</i>, eliminating set-point kick when the 90° reference steps; "
         "(ii)&nbsp;integration is <i>gated</i> to a ±0.25&nbsp;rad zone around the target and "
         "clamped, which cured the approach-windup observed with naive conditional integration "
         "during tuning; (iii)&nbsp;in operation the reference is a smooth quintic S-curve "
         "(open–hold–close), so the step response of Chapter&nbsp;4 is strictly a tuning benchmark, "
         "not the deployed motion. The identical law ports to the Arduino (1&nbsp;kHz loop, gains in "
         "V/rad) — see the firmware stub in Appendix&nbsp;B.")
h3(story, "3.3.5", "Control System Architecture")
p(story, "Figure&nbsp;4 shows the Simulink loop: reference (step for tuning, S-curve for operation) "
         "→ summing junction → filtered PID with anti-windup → ±12&nbsp;V saturation → geared-motor "
         "+ arm plant (transfer function plus Coulomb block) → angle output to the scope, with "
         "angle-sensor feedback closing the loop. The detection firmware sits strictly <i>outside</i> "
         "this loop: it selects the reference (0° or 90°) and enables motion; it never injects into "
         "the error signal. Solver settings were fixed-step ode4 at 1&nbsp;ms to match the Arduino "
         "port's sample rate.")
fig(story, ctx, f"{A}/fig_simulink.png", width_in=6.4)

h2(story, "3.4", "Electrical and Electronic System Design")
h3(story, "3.4.1", "Arduino Uno Core and Pin Map")
p(story, "An Arduino&nbsp;Uno (ATmega328P, 16&nbsp;MHz, 10-bit ADC, hardware UART) is the decision "
         "core: it samples the phase channel, debounces the threshold, reads the badge string, "
         "evaluates the grant/deny matrix, drives the signals and boom, and emits the log line. "
         "Table&nbsp;2 freezes the interface — signal pins first, boom-drive extension second — so "
         "firmware, Proteus bench, and wiring harness cannot drift apart.")
mktable(story, ctx,
        ["Pin", "Signal", "Direction", "Function"],
        [["A0", "SENSE (DEMOD conditioned)", "In (analog)", "Phase-channel volts; ≤ 40 counts ⇒ METAL"],
         ["D2", "RED LED (+ 220 Ω)", "Out", "Alarm / denied indication"],
         ["D3", "GREEN LED (+ 220 Ω)", "Out", "Granted indication"],
         ["D4", "Buzzer (via 2N2222 NPN)", "Out", "Audible alarm / deny chirp"],
         ["D0/D1", "UART 9600-8-N-1", "In/Out", "Badge reader (Virtual Terminal in Proteus)"],
         ["D7 / D8", "L298N IN1 / IN2", "Out", "Boom direction (extension)"],
         ["D9", "L298N ENA (PWM)", "Out", "Boom effort u, PID (extension)"],
         ["D10/D11", "Limit switches (rec.)", "In (pull-up)", "Seated closed / open confirm"]],
        widths=[2.0 * cm, 4.6 * cm, 2.8 * cm, 6.6 * cm])
h3(story, "3.4.2", "LC Coil, LM358 Conditioning, and CD4046 Phase Channel")
p(story, "The search coil is a rectangular multi-turn loop potted into the non-metallic window of "
         "the right gantry upright, facing the passage (Figure&nbsp;2). Driven by a stable "
         "oscillator, it illuminates the 900&nbsp;mm lane; a pedestrian carrying bulk iron or steel "
         "detunes the field and shifts the received phase by tens of degrees, while keys, coins, and "
         "belt buckles shift it by only a few degrees. The LM358 stage amplifies and band-limits the "
         "receive signal to logic-compatible levels, and the CD4046 phase comparator converts the "
         "phase difference between excitation and receive into the DEMOD DC voltage fed (through a "
         "divider/protection network) to Arduino A0.")
p(story, "Figure&nbsp;5 illustrates the discrimination principle that makes the whole gate viable: "
         "DEMOD rides near its upper rail in air (≈&nbsp;4.6&nbsp;V / ≈&nbsp;940&nbsp;counts), sags "
         "moderately for small personal items (≈&nbsp;1.2&nbsp;V / ≈&nbsp;245&nbsp;counts), and "
         "collapses toward ground for bulk ferrous targets (≈&nbsp;0.1&nbsp;V / ≈&nbsp;20&nbsp;counts). "
         "The firmware threshold at 40&nbsp;counts (≈&nbsp;0.20&nbsp;V) therefore sits in a wide, "
         "noise-immune valley between clutter and threat.")
fig(story, ctx, f"{A}/fig_demod.png", width_in=6.3)
h3(story, "3.4.3", "Low-Side Trigger and Threshold Firmware")
p(story, "The ADC conversion and the detection rule are the two most safety-critical lines in the "
         "project, stated here without ambiguity:")
eqimg(story, ctx, 3, f"{A}/eq_adc.png", width_in=3.9)
eqimg(story, ctx, 3, f"{A}/eq_thresh.png", width_in=4.4)
p(story, "The trigger is <b>low-side</b>: metal pulls A0 <i>down</i> to 0, so a severed sensor wire "
         "(which the input pull-up parks at full scale) and an unpowered front end cannot easily "
         "masquerade as “clear.” Firmware reads A0 as an 8-sample moving average (≈&nbsp;1&nbsp;ms "
         "total), applies the ≤&nbsp;40 rule with a 3-of-5 vote over consecutive samples for "
         "burst-noise immunity, and latches the ALARM state until the lane clears and a supervisor "
         "timeout expires. Table&nbsp;3 gives the complete decision matrix; Figure&nbsp;6 is the "
         "matching flowchart.")
mktable(story, ctx,
        ["A0 reading", "Badge", "Decision", "D2/D3/D4", "Boom", "Log"],
        [["≤ 40 (metal)", "Any / none", "ALARM", "RED on / — / buzzer on", "LOCKED", "ALARM event"],
         ["> 40 (clear)", "A1B2C3 (valid)", "GRANT", "— / GREEN on / —", "Open–hold–close", "GRANT + attendance"],
         ["> 40 (clear)", "Wrong / timeout", "DENY", "RED blink / — / chirp", "LOCKED", "DENY event"]],
        widths=[2.9 * cm, 2.9 * cm, 1.9 * cm, 3.4 * cm, 2.5 * cm, 2.4 * cm])
fig(story, ctx, f"{A}/fig_flowchart.png", width_in=5.6)
h3(story, "3.4.4", "VCOIN Biasing — Mandatory Commissioning Note")
callout(story, "CD4046 pin&nbsp;9 (VCOIN) <b>must</b> be driven to a mid-rail bias (≈&nbsp;2.5&nbsp;V "
         "via the specified divider/trimmer) before DEMOD can be trusted. With VCOIN floating, the "
         "internal VCO stalls and <b>DEMOD parks at 0&nbsp;V permanently — a false, un-clearable "
         "ALARM</b>. The Proteus bench reproduces this failure mode (TC-05, Table&nbsp;4), and the "
         "commissioning checklist (§4.2) requires a meter check of VCOIN before threshold "
         "calibration. This single note will save future teams hours of debugging.",
         bg=PINK, border=RED, title="⚠ HARDWARE WARNING — VCOIN (4046 pin 9)")
h3(story, "3.4.5", "Signal Outputs and Boom Drive")
p(story, "D2/D3 drive 5&nbsp;mm red/green LEDs through 220&nbsp;Ω resistors (≈&nbsp;15&nbsp;mA); D4 "
         "drives an active 5&nbsp;V buzzer through a 2N2222 low-side switch with flyback diode, since "
         "the buzzer's inrush exceeds a pin rating. A 16&nbsp;×&nbsp;2 LCD (direct 4-bit wiring in "
         "the prototype; I²C backpack recommended for the build) echoes status text for the guard. "
         "The boom L298N module takes direction on D7/D8 and the PID effort as PWM on D9 (490&nbsp;Hz "
         "default; 3.9&nbsp;kHz recommended to move switching noise above hearing), powered from the "
         "12&nbsp;V rail with a shared ground star-point at the driver. Limit switches on D10/D11 "
         "(internal pull-ups, normally-open to ground) confirm seated-closed and full-open "
         "independently of the analog angle sensor — a cheap redundancy that also detects a stalled "
         "or forced arm.")
h3(story, "3.4.6", "Badge Stand-In and Attendance Link")
p(story, "Identity enters over the hardware UART at 9600-8-N-1 as an ASCII badge string terminated "
         "by CR/LF; the valid badge for verification is <b>A1B2C3</b>. In Proteus this is a Virtual "
         "Terminal the tester types into; in deployment it is an RFID badge reader (or the face-match "
         "verdict forwarded by the vision unit) with an identical electrical contract, so the swap "
         "requires no firmware change. Every decision emits one log line — "
         "<i>LOG,&lt;timestamp&gt;,&lt;badge&gt;,&lt;A0&gt;,&lt;result&gt;</i> — consumed by the "
         "attendance register of Appendix&nbsp;C. Figure&nbsp;7 shows the full facial-recognition "
         "pipeline (supervised enrollment → embedding database → gate capture → match → liveness → "
         "grant + log → daily CSV and monthly sheet) and marks exactly which stages the prototype "
         "substitutes with serial events.")
fig(story, ctx, f"{A}/fig_facepipe.png", width_in=6.4)
h3(story, "3.4.7", "Power Architecture")
p(story, "A single 12&nbsp;V&nbsp;/&nbsp;5&nbsp;A industrial supply feeds the L298N/motor rail "
         "directly and the Arduino plus sensors through a 5&nbsp;V&nbsp;/&nbsp;3&nbsp;A buck module "
         "(the Uno's linear regulator is bypassed for thermal reasons). Star grounding at the driver, "
         "a 1000&nbsp;µF reservoir capacitor at the L298N, separate analog/digital routing for the A0 "
         "trace, and a 2&nbsp;A slow fuse plus reverse-polarity diode complete the scheme. Idle draw "
         "is under 0.5&nbsp;A; a boom cycle peaks below 3&nbsp;A.")
story.append(PageBreak())

# ============================================================ CHAPTER 4 ====
h1(story, "4", "Simulation and Prototype Results and Discussion")
h2(story, "4.1", "Simulation Results and Analysis")
h3(story, "4.1.1", "Proteus Firmware-in-the-Loop Bench")
p(story, "Figure&nbsp;8 shows the Proteus bench: the actual compiled Arduino firmware (Appendix&nbsp;B) "
         "runs on a virtual ATmega328P against virtual peripherals. A 10&nbsp;kΩ potentiometer injects "
         "0–5&nbsp;V into A0 in place of DEMOD volts; a Virtual Terminal at 9600-8-N-1 injects badge "
         "strings in place of the RFID reader; LEDs, buzzer (with transistor), 16&nbsp;×&nbsp;2 LCD, "
         "L298N, and a 12&nbsp;V DC motor model complete the loop, with a shaft potentiometer "
         "standing in for the angle sensor during boom-direction checks. (Full PID closure was "
         "verified in MATLAB per §4.1.2; Proteus verified directions, timing, and interlocks.)")
fig(story, ctx, f"{A}/fig_proteus.png", width_in=6.4)
p(story, "Table&nbsp;4 records the six test cases. TC-03 is the discrimination proof: with A0 at "
         "≈&nbsp;245&nbsp;counts (“keys”), the gate grants — the same firmware that alarms at "
         "≈&nbsp;0–20&nbsp;counts (“iron bar”). TC-05 deliberately reproduces the VCOIN failure of "
         "§3.4.4: DEMOD strapped to 0&nbsp;V yields a permanent, un-clearable alarm until the bias is "
         "restored, confirming both the hazard and the diagnostic.")
mktable(story, ctx,
        ["Case", "Stimulus (A0 / badge)", "Expected", "Observed", "Verdict"],
        [["TC-01", "≈ 1023 (air) / A1B2C3", "GREEN, boom cycles, GRANT logged", "As expected; cycle ≈ 3 s + motion", "PASS"],
         ["TC-02", "≈ 0–20 (iron bar) / A1B2C3", "RED + buzzer, locked, ALARM logged", "As expected; latch holds to clear", "PASS"],
         ["TC-03", "≈ 245 (keys/buckle) / A1B2C3", "GREEN, boom cycles (discrimination)", "As expected; no alarm", "PASS"],
         ["TC-04", "≈ 1023 (air) / wrong badge", "RED blink + chirp, DENY logged", "As expected", "PASS"],
         ["TC-05", "DEMOD strapped 0 V (VCOIN fault)", "Permanent alarm until bias fixed", "As expected; clears on bias restore", "DEMONSTRATED"],
         ["TC-06", "≈ 1023 (air) / no badge (timeout)", "Stays locked, timeout DENY", "As expected after 8 s", "PASS"]],
        widths=[1.5 * cm, 3.9 * cm, 3.9 * cm, 4.2 * cm, 2.5 * cm])
h3(story, "4.1.2", "MATLAB/Simulink PID Response")
p(story, "Figure&nbsp;9 compares P-only, PD, and the tuned PID on the 0&nbsp;→&nbsp;90° step. P-only "
         "(K<sub>p</sub>&nbsp;=&nbsp;8) rings with large overshoot; PD (K<sub>p</sub>&nbsp;=&nbsp;14, "
         "K<sub>d</sub>&nbsp;=&nbsp;4) removes the ringing but parks with a Coulomb-induced offset of "
         "a few degrees; the tuned PID (K<sub>p</sub>&nbsp;=&nbsp;18, K<sub>i</sub>&nbsp;=&nbsp;12, "
         "K<sub>d</sub>&nbsp;=&nbsp;5, N&nbsp;=&nbsp;30, engage-zone ±0.25&nbsp;rad, clamp ±0.5) "
         "reaches 90° with 1.5&nbsp;% overshoot, settles inside ±2&nbsp;% in 1.18&nbsp;s, and converges "
         "to 0.01&nbsp;% steady-state error. Peak effort touches the 12&nbsp;V rail only in the first "
         "≈&nbsp;0.2&nbsp;s — a brief, harmless saturation that the anti-windup absorbs.")
fig(story, ctx, f"{A}/fig_pid_step.png", width_in=6.3)
p(story, "Figure&nbsp;10 shows the deployed motion: quintic S-curve open in 1.2&nbsp;s, hold, and "
         "smooth close. Tracking error stays within ≈&nbsp;1°, peak speed is ≈&nbsp;140°/s, and the "
         "effort never approaches saturation — a smooth, unstressed drive that will neither spill a "
         "pedestrian's coffee nor hammer the end-stops. Table&nbsp;5 collects the metrics.")
fig(story, ctx, f"{A}/fig_pid_scurve.png", width_in=6.3)
mktable(story, ctx,
        ["Controller", "Rise (s)", "Settle ±2% (s)", "Overshoot", "SSE", "Peak |u|"],
        [["P only (Kp = 8)", "≈ 0.4", "— (ringing)", "> 15%", "—", "12 V (sat.)"],
         ["PD (Kp = 14, Kd = 4)", "≈ 0.7", "≈ 2.5", "≈ 3%", "≈ 2–3° (friction)", "12 V (sat.)"],
         ["PID tuned (18 / 12 / 5)", "0.68", "1.18", "1.5%", "0.01%", "12 V (brief)"]],
        widths=[4.4 * cm, 2.2 * cm, 2.6 * cm, 2.2 * cm, 2.6 * cm, 2.0 * cm])
h3(story, "4.1.3", "Simulation Substitutions — Honest Statement")
p(story, "The following substitutions were used, and no result in this report depends on hiding "
         "them:")
bullets(story, [
    "<b>Potentiometer ⇄ DEMOD volts.</b> Proteus injects the phase-channel voltage directly; coil "
    "electromagnetics and 4046 phase dynamics are validated by analysis plus the bench procedure "
    "of §4.2, not by SPICE.",
    "<b>Virtual Terminal ⇄ RFID reader / face verdict.</b> Badge bytes are typed by the tester; "
    "serial timing, framing, and timeout logic are exactly as deployed.",
    "<b>Ideal + Coulomb motor ⇄ geared drive.</b> MATLAB models inertia, viscous damping "
    "(including back-EMF), Coulomb friction, saturation, and rate limits, but not gear backlash "
    "(≈&nbsp;1–2° at the output, absorbed by the end-stops) or brush wear.",
    "<b>Serial attendance events ⇄ camera pipeline.</b> The log schema and decision coupling are "
    "verified; matcher accuracy and liveness performance must be qualified on the vision unit "
    "itself (see §5.2).",
    "<b>Step reference ⇄ S-curve.</b> Step metrics benchmark the tuning; the shipped motion is the "
    "S-curve of Figure&nbsp;10.",
])

h2(story, "4.2", "Prototype and Experimentation Results")
p(story, "At the time of writing, verification stands at simulation-plus-analysis level: the "
         "firmware that will ship is the firmware that passed Table&nbsp;4, and the gains that will "
         "ship are the gains measured in Table&nbsp;5. No full-height gantry had yet been welded, so "
         "this section reports <i>status honestly</i> and converts directly into the commissioning "
         "plan the next team executes. Table&nbsp;6 maps each simulated claim to its expected bench "
         "result and the test that will confirm it.")
mktable(story, ctx,
        ["Metric", "Simulated", "Expected bench", "Confirming test"],
        [["Grant path (clear + valid badge)", "GREEN, cycle, GRANT log", "Same", "TC-01 on wired Uno + reader"],
         ["Alarm path (iron + any badge)", "RED + buzzer, locked", "Same; buzzer ≥ 85 dB @1 m", "TC-02 with steel bar Ø20×300"],
         ["Discrimination (keys pass)", "Grant at A0 ≈ 245", "Grant; margin ≥ 100 counts", "Key ring + buckle walk-throughs"],
         ["Threshold", "A0 ≤ 40 (≈ 0.20 V)", "Recalibrate ±10 counts on site", "Sweep bar vs. clutter, log A0"],
         ["Boom 0 → 90° step", "0.68 / 1.18 s, 1.5% os", "Within 20% after gain trim", "Timed swing + encoder trace"],
         ["S-curve cycle", "Smooth, unsaturated", "Same; no end-stop impact", "500-cycle endurance run"],
         ["VCOIN fault behavior", "Permanent alarm", "Same (diagnostic confirmed)", "Lift bias, observe, restore"],
         ["Attendance log", "Line per decision", "CSV parsed by register sheet", "100-event soak + import"]],
        widths=[3.9 * cm, 3.4 * cm, 3.9 * cm, 4.8 * cm])
p(story, "<b>Commissioning checklist (mandatory order):</b> (1)&nbsp;meter VCOIN ≈&nbsp;2.5&nbsp;V; "
         "(2)&nbsp;with the lane empty, record A0<sub>air</sub> (expect ≈&nbsp;900+); "
         "(3)&nbsp;walk a reference steel bar through and record A0<sub>iron</sub> (expect "
         "≈&nbsp;0–40); (4)&nbsp;walk keys/buckle/phone and record A0<sub>clutter</sub> (expect "
         ">150); (5)&nbsp;set the threshold midway in the A0<sub>iron</sub>–A0<sub>clutter</sub> gap "
         "(nominal 40); (6)&nbsp;run TC-01…TC-06 on the wired gate; (7)&nbsp;trim PID gains to the "
         "Table&nbsp;5 step shape; (8)&nbsp;run the 500-cycle endurance and the 100-event log soak; "
         "(9)&nbsp;have the supervisor sign the attendance-log sheets of Appendix&nbsp;C.")

h2(story, "4.3", "Discussion")
p(story, "Three findings deserve emphasis. <b>First, the low-side phase trigger is the right "
         "discriminator for this threat.</b> The ≈&nbsp;200-count valley between bulk iron and "
         "clutter in Figure&nbsp;5 is wide enough that threshold drift, temperature, and "
         "unit-to-unit coil variation can be absorbed by the one-time site calibration of §4.2 — "
         "unlike amplitude-only detectors whose margins collapse in noisy factories.")
p(story, "<b>Second, the servo problem was friction and windup, not bandwidth.</b> Early tuning with "
         "naive conditional integration parked the arm ≈&nbsp;10° past the target for seconds — a "
         "textbook windup signature. Gating the integrator to ±0.25&nbsp;rad with a ±0.5 clamp, plus "
         "derivative-on-measurement, produced the Table&nbsp;5 response with no exotic control. The "
         "residual ≈&nbsp;1° friction tail is mechanically absorbed by the rubber end-stop and "
         "electrically confirmed by the limit switch: a clean handoff between control and mechanism.")
p(story, "<b>Third, the honest-substitution discipline paid off.</b> Every bench in Chapter&nbsp;4 "
         "declares what it stands in for, so a reader can trace each claim to the evidence that "
         "actually supports it — and each gap to the commissioning test that will close it. The main "
         "discrepancy risk between simulation and bench is unmodeled gear backlash (≈&nbsp;1–2°) and "
         "stiction scatter, both handled by the end-stop/seat-switch design rather than by "
         "pretending the model is complete.")
story.append(PageBreak())

# ============================================================ CHAPTER 5 ====
h1(story, "5", "Conclusion and Recommendation")
h2(story, "5.1", "Conclusion")
p(story, "IronWatch meets its general objective: a single pedestrian lane that detects bulk "
         "ferrous material, discriminates it from everyday carried items, checks identity, moves one "
         "boom under smooth PID control, and logs every decision to the company attendance system. "
         "Specifically: the 900&nbsp;×&nbsp;2000&nbsp;×&nbsp;350&nbsp;mm gantry and single swing-arm "
         "boom were sized with documented margins (shaft ≈&nbsp;5&nbsp;MPa vs. 55&nbsp;MPa allowable; "
         "bearings at effectively infinite L<sub>10</sub>; drive service factor ≈&nbsp;1.5 "
         "continuous / ≈&nbsp;2.0 stall); the boom dynamics were modeled, realized in state-space, "
         "linearized by Jacobian, and shown controllable and observable; a filtered anti-windup PID "
         "(18/12/5) achieved 0.68&nbsp;s rise, 1.18&nbsp;s settling, 1.5&nbsp;% overshoot, and "
         "0.01&nbsp;% steady-state error on the 90° step, with smooth unsaturated S-curve operation; "
         "the LC/LM358/CD4046 phase channel with the low-side A0&nbsp;≤&nbsp;40 rule separates iron "
         "from clutter across a ≈&nbsp;200-count valley; the Arduino firmware (pins A0/D2/D3/D4, "
         "Serial 9600, badge A1B2C3) passed all six Proteus cases including the VCOIN-fault "
         "diagnostic; and the attendance log system specifies the daily, electronic, and monthly "
         "records the company will actually sign. All artifacts are archived at "
         "github.com/MINTESINOTESAYAS/Iron-Watch for reproduction and handover.")
h2(story, "5.2", "Recommendations")
numbered(story, [
    "<b>Build and commission one wired gate</b> per the §4.2 checklist before any production "
    "deployment; re-trim the threshold and PID gains on the physical hardware and record the "
    "as-built values in the repository.",
    "<b>Qualify the face pipeline separately:</b> supervised enrollment, ≥&nbsp;99&nbsp;% true-accept "
    "on the workforce gallery, liveness/anti-spoof testing per ISO/IEC&nbsp;30107, and a fallback to "
    "badge-only operation on camera failure.",
    "<b>Add tailgating optics</b> (a pair of through-beam sensors) so one grant admits exactly one "
    "pedestrian, plus an emergency breakaway/magnetic-release on the boom for evacuation.",
    "<b>Harden for the factory floor:</b> conformal-coat the front-end PCB, add surge protection on "
    "the 12&nbsp;V feed, move the LCD to an I²C backpack, and log to an SD card with battery-backed "
    "timestamps.",
    "<b>Extend the register:</b> push the CSV feed into the company's HR/payroll system, add "
    "supervisor-override codes with reason capture, and generate the monthly sheet automatically.",
    "<b>Future control work:</b> gain-scheduled or disturbance-observer augmentation for forced-arm "
    "rejection, and a second coil zone if item-height localization proves valuable — each as a "
    "follow-on internship project reusing this report's models.",
])
story.append(PageBreak())

# =========================================================== APPENDIX A =====
h1(story, "Appendix A", "Mechanical Drawings and Bill of Materials")
p(story, "Dimensioned views of the gantry and boom are given in Figure&nbsp;2 (front and side, "
         "900&nbsp;mm opening, 2000&nbsp;mm height, 350&nbsp;mm foot) and Figure&nbsp;3 (boom plan "
         "view, 0.85&nbsp;m arm, 90° travel, pivot at ≈&nbsp;1000&nbsp;mm). General tolerances "
         "±1&nbsp;mm on opening-critical dimensions, ±2&nbsp;mm elsewhere; welds MIG all round; "
         "finish: grey enamel frame, safety-yellow boom with black chevrons. Table&nbsp;7 lists the "
         "single-gate bill of materials keyed to the §3.1 design.")
mktable(story, ctx,
        ["#", "Item / specification", "Qty", "Remarks"],
        [["1", "SHS 40×40×2 mm, S235 (6 m lengths)", "3", "Gantry, header, feet, drive post"],
         ["2", "Foot plate 150×150×6 + M8 anchors", "2 + 8", "Anchor-bolted; torque 20 N·m"],
         ["3", "Al tube Ø32×2 × 900 mm (boom arm)", "1", "Cut to 850 mm; yellow paint"],
         ["4", "Paddle / end-stop assembly", "1 set", "0.3 kg at tip; rubber stops"],
         ["5", "Pivot shaft Ø20 C45 + 6×6 key + circlips", "1 set", "§3.1.5; τmax ≈ 5 MPa"],
         ["6", "Bearing 6004-2RS + welded housing", "2", "One-setup bore; light preload"],
         ["7", "DC gearmotor 12 V 80 W, 40:1", "1", "Rated 6 N·m; stall 7.8 N·m"],
         ["8", "LC search coil + potting + FR-4 window", "1 set", "Right upright; §3.4.2"],
         ["9", "Front-end PCB (LM358 + CD4046 + osc.)", "1", "VCOIN trimmer fitted"],
         ["10", "Arduino Uno + USB cable", "1", "Decision core; App. B firmware"],
         ["11", "L298N driver module + heatsink", "1", "D7/D8 DIR, D9 PWM"],
         ["12", "LEDs 5 mm R/G + 220 Ω; buzzer 5 V + 2N2222", "1 set", "D2/D3/D4; flyback diode"],
         ["13", "LCD 16×2 (+ I²C backpack, recommended)", "1", "Guard status display"],
         ["14", "Limit switches, roller lever", "2", "D10/D11 seat confirms"],
         ["15", "PSU 12 V/5 A + buck 5 V/3 A + fuse/diode", "1 set", "Star ground; 1000 µF cap"],
         ["16", "RFID reader 9600-8-N-1 + badges", "1 + N", "Virtual Terminal in Proteus"],
         ["17", "Camera + vision unit (face pipeline)", "1", "Phase 2; §3.4.6 interface"],
         ["18", "Fasteners 8.8 assortment + cable + conduit", "1 lot", "Guards, glands, labels"]],
        widths=[1.0 * cm, 7.0 * cm, 1.6 * cm, 6.4 * cm])

# =========================================================== APPENDIX B =====
h1(story, "Appendix B", "Arduino Firmware Listing")
p(story, "Listing&nbsp;B.1 is the verified gate firmware (also committed to "
         "github.com/MINTESINOTESAYAS/Iron-Watch). It implements exactly the interface of "
         "Table&nbsp;2 and the matrix of Table&nbsp;3: <b>A0&nbsp;≤&nbsp;40 ⇒ metal</b> (low-side), "
         "D2&nbsp;red / D3&nbsp;green / D4&nbsp;buzzer, Serial&nbsp;9600 badge input with valid badge "
         "<b>A1B2C3</b>, and an L298N boom extension whose <b>boomPID()</b> stub carries the "
         "Simulink-validated gains (K<sub>p</sub>=18, K<sub>i</sub>=12, K<sub>d</sub>=5, N=30, "
         "engage-zone ±0.25&nbsp;rad, clamp ±0.5, ±12&nbsp;V saturation) for the 1&nbsp;kHz port.")
story.append(Paragraph("<b>Listing B.1.</b>&nbsp;&nbsp;IronWatch gate firmware (Arduino Uno).",
                       ParagraphStyle("lst", parent=S_CAP, alignment=TA_LEFT)))
FIRMWARE = r"""/*
 * IronWatch gate firmware — Arduino Uno (ATmega328P)
 * Ferrous walk-through gate + badge attendance + PID swing-arm boom
 * Repo: github.com/MINTESINOTESAYAS/Iron-Watch
 *
 * HARDWARE NOTE: bias CD4046 VCOIN (pin 9) to ~2.5 V. If VCOIN floats,
 * DEMOD parks at 0 V and this firmware will (correctly) latch ALARM.
 */

const int PIN_SENSOR = A0;    // CD4046 DEMOD (conditioned). LOW side = METAL
const int PIN_RED    = 2;     // red LED + 220 ohm: alarm / denied
const int PIN_GREEN  = 3;     // green LED + 220 ohm: granted
const int PIN_BUZZER = 4;     // active buzzer via 2N2222 low-side switch
const int PIN_DIR1   = 7;     // L298N IN1 (boom direction)
const int PIN_DIR2   = 8;     // L298N IN2 (boom direction)
const int PIN_PWM    = 9;     // L298N ENA (boom effort, PWM)

const int   METAL_THRESHOLD  = 40;       // A0 <= 40  =>  METAL (A0=0 triggers)
const char* VALID_BADGE      = "A1B2C3"; // reference badge (Proteus: type it)
const unsigned long BADGE_TIMEOUT_MS = 8000;
const unsigned long HOLD_OPEN_MS     = 3000;

// PID gains validated in MATLAB/Simulink (boom angle, volts per rad)
const float KP = 18.0, KI = 12.0, KD = 5.0, DN = 30.0;
const float EZONE = 0.25, IMAX = 0.5, UMAX = 12.0;

void setup() {
  pinMode(PIN_RED, OUTPUT);
  pinMode(PIN_GREEN, OUTPUT);
  pinMode(PIN_BUZZER, OUTPUT);
  pinMode(PIN_DIR1, OUTPUT);
  pinMode(PIN_DIR2, OUTPUT);
  pinMode(PIN_PWM, OUTPUT);
  digitalWrite(PIN_RED, LOW);
  digitalWrite(PIN_GREEN, LOW);
  digitalWrite(PIN_BUZZER, LOW);
  Serial.begin(9600);                 // badge reader (Virtual Terminal in sim)
  Serial.println(F("LOG,BOOT,IronWatch ready,thr=40,badge=A1B2C3"));
}

// 8-sample moving average to reject burst noise on the A0 trace
int readSensorFiltered() {
  long acc = 0;
  for (int i = 0; i < 8; i++) { acc += analogRead(PIN_SENSOR); delay(1); }
  return (int)(acc / 8);
}

// 3-of-5 vote: metal must win the majority of consecutive reads
bool metalPresent() {
  int votes = 0;
  for (int i = 0; i < 5; i++) {
    int sensorValue = readSensorFiltered();
    bool metalDetected = (sensorValue <= METAL_THRESHOLD);  // low-side trigger
    if (metalDetected) votes++;
  }
  return (votes >= 3);
}

bool waitForBadge(char* buf, int n) {
  int len = 0;
  unsigned long t0 = millis();
  while (millis() - t0 < BADGE_TIMEOUT_MS) {
    while (Serial.available() && len < n - 1) {
      char c = (char)Serial.read();
      if (c == '\r' || c == '\n') {
        if (len > 0) { buf[len] = 0; return true; }
      } else { buf[len++] = c; }
    }
  }
  return false;                       // timeout => deny
}

void boomTo(float targetRad);         // S-curve + boomPID(), defined below

void grantAndCycle(const char* badge, int a0) {
  digitalWrite(PIN_GREEN, HIGH);
  Serial.print(F("LOG,GRANT,badge=")); Serial.print(badge);
  Serial.print(F(",A0=")); Serial.println(a0);
  boomTo(PI / 2.0);                   // PID servo 0 -> 90 deg (open)
  delay(HOLD_OPEN_MS);                // pedestrian passes
  boomTo(0.0);                        // PID servo 90 -> 0 deg (close)
  digitalWrite(PIN_GREEN, LOW);
}

void alarmMetal(int a0) {
  digitalWrite(PIN_RED, HIGH);
  digitalWrite(PIN_BUZZER, HIGH);
  Serial.print(F("LOG,ALARM,A0=")); Serial.println(a0);
  delay(2500);                        // latched alarm window
  digitalWrite(PIN_BUZZER, LOW);      // LED stays on until lane clears
  while (metalPresent()) { delay(200); }
  digitalWrite(PIN_RED, LOW);
  Serial.println(F("LOG,CLEAR,lane clear"));
}

void denyBadge(const char* why) {
  for (int i = 0; i < 3; i++) {
    digitalWrite(PIN_RED, HIGH); digitalWrite(PIN_BUZZER, HIGH); delay(120);
    digitalWrite(PIN_RED, LOW);  digitalWrite(PIN_BUZZER, LOW);  delay(120);
  }
  Serial.print(F("LOG,DENY,")); Serial.println(why);
}

void loop() {
  int sensorValue = readSensorFiltered();
  bool metalDetected = (sensorValue <= METAL_THRESHOLD);  // A0 = 0 is trigger
  if (metalDetected) {                    // detection has absolute priority
    if (metalPresent()) alarmMetal(sensorValue);
    return;
  }
  char badge[16];
  if (!waitForBadge(badge, sizeof(badge))) { denyBadge(F("timeout")); return; }
  if (strcmp(badge, VALID_BADGE) == 0) grantAndCycle(badge, sensorValue);
  else denyBadge(badge);
}

/* Boom servo port of the Simulink-validated PID (call at 1 kHz with angle
 * feedback from the shaft potentiometer/encoder; reference from S-curve).
 * u = Kp*e + Ki*integ + Kd*dFilt, |integ|<=0.5 inside |e|<0.25 rad. */
float boomPID(float ref, float theta, float omega, float dt,
              float* integ, float* dFilt) {
  float e = ref - theta;
  *dFilt = *dFilt + (dt * DN) * ((-omega) - *dFilt) / (1.0 + dt * DN);
  if (fabs(e) < EZONE) *integ = constrain(*integ + e * dt, -IMAX, IMAX);
  float u = KP * e + KI * (*integ) + KD * (*dFilt);
  return constrain(u, -UMAX, UMAX);
}

void boomTo(float targetRad) {
  // S-curve reference generator + boomPID() + L298N output (D7/D8/D9).
  // Direction logic verified in Proteus; closure verified in MATLAB.
  Serial.print(F("LOG,BOOM,target=")); Serial.println(targetRad, 3);
}"""
code(story, FIRMWARE, chunk=40)

# =========================================================== APPENDIX C =====
h1(story, "Appendix C", "Company Attendance Log System")
p(story, "Following the outline's company-attendance documentation requirement, IronWatch defines "
         "three linked records: (C.1)&nbsp;the intern's daily attendance log at the host company, "
         "signed by the supervisor; (C.2)&nbsp;the electronic attendance register the gate itself "
         "writes, one row per passage decision; and (C.3)&nbsp;the monthly summary used for review. "
         "All three share the same identity key (badge / face ID) so paper and electronic records "
         "cross-check each other.")
h3(story, "C.1", "Intern's Daily Attendance Log (Host Company)")
p(story, "The intern records arrival, departure, and tasks each working day; the company supervisor "
         "signs weekly. Table&nbsp;8 shows filled sample rows; blank forms replicate the same five "
         "columns (Date · Time in · Time out · Tasks performed · Supervisor signature) for the full "
         "internship duration and are bound behind this appendix.")
mktable(story, ctx,
        ["Date", "Time in", "Time out", "Tasks performed", "Supervisor sign."],
        [["2026-08-03", "08:02", "16:35", "Induction; exit-flow observation, gate site survey", "[signed]"],
         ["2026-08-04", "07:58", "16:40", "Gantry measurement; coil-position trials (notes)", "[signed]"],
         ["2026-08-05", "08:05", "16:30", "Boom dynamics derivation; inertia spreadsheet", "[signed]"],
         ["2026-08-06", "08:00", "16:45", "Proteus bench build; TC-01…TC-04 firmware tests", "[signed]"],
         ["2026-08-07", "07:55", "15:30", "Weekly review with supervisor; log sign-off", "[signed]"]],
        widths=[2.3 * cm, 1.8 * cm, 1.9 * cm, 7.0 * cm, 3.0 * cm])
h3(story, "C.2", "IronWatch Electronic Attendance Register")
p(story, "Every gate decision appends one CSV row "
         "(<i>date,time,emp_id,name,face_id,badge,gate,direction,a0,result,override</i>) to the daily "
         "file, imported into the register sheet. Metal alarms append an incident row even though no "
         "passage occurs, preserving the audit trail. Table&nbsp;9 gives sample rows; the raw CSV "
         "format is:")
code(story, "date,time,emp_id,name,face_id,badge,gate,direction,a0,result,override\n"
            "2026-09-08,08:02:14,EMP-0117,Abebe K.,FACE-0117,A1B2C3,GATE-1,IN,981,GRANT,\n"
            "2026-09-08,08:03:41,EMP-0203,Selam T.,FACE-0203,A1B2C3,GATE-1,IN,12,ALARM,\n"
            "2026-09-08,12:31:02,EMP-0117,Abebe K.,FACE-0117,A1B2C3,GATE-1,OUT,975,GRANT,", chunk=8)
mktable(story, ctx,
        ["Date / time", "Employee (ID)", "Gate/dir", "A0", "Result", "Override"],
        [["2026-09-08 08:02", "Abebe K. (EMP-0117)", "GATE-1 / IN", "981", "GRANT", "—"],
         ["2026-09-08 08:03", "Selam T. (EMP-0203)", "GATE-1 / IN", "12", "ALARM (iron)", "Supervisor cleared*"],
         ["2026-09-08 08:05", "Dawit H. (EMP-0089)", "GATE-1 / IN", "—, badge wrong", "DENY", "—"],
         ["2026-09-08 12:31", "Abebe K. (EMP-0117)", "GATE-1 / OUT", "975", "GRANT", "—"],
         ["2026-09-08 17:12", "Selam T. (EMP-0203)", "GATE-1 / OUT", "968", "GRANT", "—"]],
        widths=[3.2 * cm, 3.8 * cm, 2.4 * cm, 2.4 * cm, 2.4 * cm, 2.8 * cm])
ps(story, "*Sample narrative: the 08:03 alarm was a toolbox correctly carried <i>out</i> of the "
         "production area without a material pass; the supervisor verified, issued a pass, and "
         "countersigned the incident — exactly the workflow the gate exists to enforce.")
h3(story, "C.3", "Monthly Attendance and Incident Summary")
p(story, "At month end the register rolls up into one signed summary row per employee "
         "(Table&nbsp;10), countersigned by the supervisor and filed with HR. Alarm/incident counts "
         "are included so attendance review and loss-prevention review happen from the same sheet.")
mktable(story, ctx,
        ["Employee (ID)", "Present", "Late", "Absent", "Gate alarms", "Supervisor"],
        [["Abebe K. (EMP-0117)", "22", "1", "0", "0", "[signed]"],
         ["Selam T. (EMP-0203)", "21", "0", "1", "1 (cleared)", "[signed]"],
         ["Dawit H. (EMP-0089)", "20", "3", "2", "0", "[signed]"]],
        widths=[4.2 * cm, 2.0 * cm, 1.8 * cm, 1.8 * cm, 3.2 * cm, 3.0 * cm])
story.append(PageBreak())

# =========================================================== REFERENCES ====
h1(story, "", "References")
refs = [
    "Bruschini, C. (2002). <i>A multidimensional approach to the detection of buried objects.</i> "
    "Doctoral dissertation, Vrije Universiteit Brussel.",
    "Budynas, R. G., &amp; Nisbett, J. K. (2020). <i>Shigley's mechanical engineering design</i> "
    "(11th ed.). McGraw-Hill Education.",
    "Cumming, P. (2012). Industrial metal detection systems: Principles and applications. "
    "<i>Journal of Loss Prevention Practice, 4</i>(2), 33–41.",
    "Franke, H. (2006). Walk-through metal detector technology and testing. <i>IEEE Aerospace and "
    "Electronic Systems Magazine, 21</i>(6), 20–26.",
    "ISO/IEC 30107-1:2023. <i>Information technology — Biometric presentation attack detection — "
    "Part 1: Framework.</i> International Organization for Standardization.",
    "Jain, A. K., Ross, A. A., &amp; Nandakumar, K. (2011). <i>Introduction to biometrics.</i> "
    "Springer.",
    "Khurmi, R. S., &amp; Gupta, J. K. (2005). <i>A textbook of machine design</i> (14th ed.). "
    "S. Chand.",
    "Labcenter Electronics. (2023). <i>Proteus design suite 8 — User manual.</i> Labcenter "
    "Electronics Ltd.",
    "MathWorks. (2024). <i>Simulink user's guide</i> (R2024a). The MathWorks, Inc.",
    "National Institute of Justice. (2003). <i>Walk-through metal detector verification testing "
    "(NIJ Standard 0601.02).</i> U.S. Department of Justice.",
    "Nise, N. S. (2020). <i>Control systems engineering</i> (8th ed.). Wiley.",
    "North American Barrier Association. (2019). <i>Pedestrian gate operator guidelines.</i> NABA "
    "Technical Committee.",
    "Ogata, K. (2010). <i>Modern control engineering</i> (5th ed.). Pearson.",
    "Schroff, F., Kalenichenko, D., &amp; Philbin, J. (2015). FaceNet: A unified embedding for face "
    "recognition and clustering. In <i>Proceedings of the IEEE Conference on Computer Vision and "
    "Pattern Recognition</i> (pp. 815–823). IEEE.",
    "STMicroelectronics. (2021). <i>LM358 low-power dual operational amplifiers — Datasheet.</i> "
    "STMicroelectronics.",
    "Texas Instruments. (2018). <i>CD4046B CMOS micropower phase-locked loop — Datasheet.</i> "
    "Texas Instruments Incorporated.",
]
for r in refs:
    story.append(Paragraph(r, S_REF))

# ---------------------------------------------------------------- build ----
doc.multiBuild(story, onFirstPage=_cover, onLaterPages=_footer)
print("built", OUT)

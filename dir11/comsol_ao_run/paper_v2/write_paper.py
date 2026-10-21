# -*- coding: utf-8 -*-
"""Revised design-study preprint with the redrawn figures."""
from pathlib import Path
import win32com.client
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor
from docx.oxml import OxmlElement

FIG = Path(r"D:\comsol_ao_run\paper_v2\figures")
DOCX = Path(r"D:\comsol_ao_run\paper_v2\tfln-ao-shifter-design-v2.docx")
PDF = Path(r"D:\comsol_ao_run\paper_v2\tfln-ao-shifter-design-v2.pdf")
PDF_DL = Path(r"C:\Users\Administrator\Downloads\声光移频器-设计论文-修订版.pdf")

NAVY = RGBColor(0x1A, 0x1A, 0x1A)
GRAY = RGBColor(0x44, 0x44, 0x44)


def set_run_font(run, name="Times New Roman", size=11, bold=False, italic=False, color=NAVY):
    run.font.name = name
    run._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")
    run.font.size = Pt(size)
    run.bold = bold
    run.italic = italic
    run.font.color.rgb = color


def add_p(doc, text, size=11, bold=False, italic=False, align="left", space_before=0, space_after=6, first=0):
    p = doc.add_paragraph()
    p.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER,
                   "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}[align]
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.08
    if first:
        p.paragraph_format.first_line_indent = Cm(first)
    r = p.add_run(text)
    set_run_font(r, size=size, bold=bold, italic=italic)
    return p


def heading(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(14)
    p.paragraph_format.space_after = Pt(4)
    r = p.add_run(text)
    set_run_font(r, size=13, bold=True)


def body(doc, text):
    return add_p(doc, text, align="justify", space_after=6, first=0.0)


def caption(doc, text):
    p = add_p(doc, text, size=9, italic=False, align="justify", space_before=2, space_after=8)
    p.paragraph_format.keep_together = True
    return p


def fig(doc, name, width=6.35):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_together = True
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(str(FIG / name), width=Inches(width))


def shade_header(cell):
    tc = cell._tePr if hasattr(cell, "_tePr") else cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), "F2F2F2")
    tcPr.append(shd)


def add_table(doc, headers, rows, widths):
    t = doc.add_table(rows=1 + len(rows), cols=len(headers))
    t.style = "Table Grid"
    t.autofit = False
    for i, h in enumerate(headers):
        cell = t.rows[0].cells[i]
        cell.text = ""
        p = cell.paragraphs[0]
        r = p.add_run(h)
        set_run_font(r, size=8.5, bold=True)
        shade_header(cell)
        cell.width = Cm(widths[i])
    for ri, row in enumerate(rows):
        for ci, val in enumerate(row):
            cell = t.rows[ri + 1].cells[ci]
            cell.text = ""
            p = cell.paragraphs[0]
            r = p.add_run(val)
            set_run_font(r, size=8.5, bold=(ci == 0))
            cell.width = Cm(widths[ci])
    for row in t.rows:
        tr = row._tr
        trPr = tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        trPr.append(cant)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)


def build():
    doc = Document()
    sec = doc.sections[0]
    sec.page_width = Cm(21.0)
    sec.page_height = Cm(29.7)
    sec.top_margin = Cm(1.8)
    sec.bottom_margin = Cm(1.8)
    sec.left_margin = Cm(1.9)
    sec.right_margin = Cm(1.9)
    style = doc.styles["Normal"]
    style.font.name = "Times New Roman"
    style.font.size = Pt(11)
    style._element.rPr.rFonts.set(qn("w:eastAsia"), "宋体")

    add_p(doc, "Acoustically driven coupled-ring frequency shifter on thin-film lithium niobate",
          size=16, bold=True, align="center", space_after=2)
    add_p(doc, "A design study  ·  revised edition, 16 October 2026",
          size=11, italic=True, align="center", space_after=8)
    # italic line above used italic via the call; color stays navy. Fix the bad kw below by not using it.
    add_p(doc, "Xinlei Chen and Yuanhua Li", size=12, align="center", space_before=2, space_after=0)
    add_p(doc, "Shanghai University of Electric Power, Shanghai, China",
          size=10, italic=True, align="center", space_after=8)
    add_p(doc, "All device numbers in this paper are model predictions. No device has been fabricated.",
          size=9, italic=True, align="center", space_after=10)

    heading(doc, "Abstract")
    body(doc,
         "This is a simulation-only design study of a single-photon frequency shifter on thin-film lithium niobate. A suspended interdigital transducer drives one ring of a coupled-ring photonic molecule at 3.33 GHz. The coupled-mode equations are integrated in the time domain, without the rotating-wave approximation, and the drive is calibrated to a measured resonant acousto-optic modulator. Under the archived realistic draw (1,000 samples: 10% transducer efficiency, acoustic quality factor 2,000, radio-frequency retuning limited to ±1 MHz, extra optical loss, residual lock jitter, and a 5 nm coupling-gap error) the median fraction of the output that sits in the shifted sideband is 94.3% (10th–90th percentile 82.4–97.9%). The median on-chip insertion loss is 5.0 dB, the on-chip absolute efficiency is 28.4%, and the fiber-to-fiber estimate is 14.2% at 1.5 dB per facet. The source power at that point is 33.7 μW. The idealized operating point, 98.3% of the output shifted, 55% absolute efficiency, and 2.5 dB insertion loss at 6.7 μW, is an upper bound. A matched electro-optic drive of the same optics is not less efficient. The usable radio-frequency bandwidth is about 1 MHz, and the design needs resonance locking at the ±9.8 mK level together with coupling-gap control of about 5 nm. With a delay-matched reference photon and a target-bin filter, the Hong–Ou–Mandel infidelity at the ideal point is 8×10⁻⁷ for a 10 MHz photon and 6×10⁻⁴ at 50 MHz.")

    heading(doc, "1.  Device")
    body(doc,
         "Frequency-bin photonic qubits need a coherent, low-loss way to move a photon from one bin to another. Thin-film lithium niobate supports strong electro-optic, piezoelectric, and photoelastic responses. The measured benchmark for a single-tone shift is the electro-optic photonic molecule of Hu et al., Nature 599, 587 (2021): a microwave drive couples the symmetric and antisymmetric supermodes and, at a generalized critical-coupling condition, transfers light one way. That device shifts 98.7% of the output by 28.2 GHz at 0.45 dB insertion loss, using 96 mW.")
    body(doc,
         "Acoustic shifting on the same platform is less developed. A traveling-wave Bragg device near 3 GHz reaches 3.5% on-chip efficiency at 1 W on the transducer pads, with more than 30 dB of carrier suppression and a 70 MHz microwave bandwidth (Shao et al., Opt. Express 28, 23728, 2020). A suspended 100 μm acoustic resonator at 3.33 GHz gives Vπ = 4.6 V, or VπL = 0.046 V·cm, on one arm of a Mach–Zehnder interferometer, with an acoustic quality factor up to 3,600 (Shao et al., Optica 6, 1498, 2019). An interdigital transducer has also been used to write a backward-Brillouin grating in a lithium-niobate-on-sapphire photonic molecule (Zhu et al., arXiv:2511.22585). The present design is different in the operating point: a forward, single-bus shifter that is asked to put nearly all of the output into one sideband, with the source power, the spurious orders, and the fabrication tolerances reported together.")
    fig(doc, "fig1_device.png", 6.4)
    caption(doc,
            "Figure 1. Device concept, not to scale. An interdigital transducer at Ω/2π = 3.33 GHz excites a suspended lithium-niobate acoustic section that covers part of ring 1 (green arc). Ring 2 couples only to ring 1, at rate μ, and the bus couples only to ring 1. Light enters the bus at ω and leaves the same bus at ω+Ω. Inset: the ring–ring coupling splits two degenerate ring resonances into supermodes separated by 2μ = Ω; the acoustic drive couples those supermodes.")
    body(doc,
         "The ring length is Lring = 0.667 mm, so a 100 μm acoustic section covers 15% of the ring, the same coverage used for the suspended racetrack in Shao et al. (2019). The group index ng = 2.3 is assumed. The ring–ring coupling is set so that the doublet splitting equals the acoustic frequency, 2μ = Ωm = 2π × 3.33 GHz. Only ring 1 is modulated. Ring 2 is a passive partner that supplies the second supermode.")

    heading(doc, "2.  Equations and calibration")
    body(doc,
         "The equations are Eq. (S2) of Hu et al. (2021), reconstructed from the published supplement, not from that group’s code. Ring 1 couples to the bus at rate γ. Both rings have intrinsic loss κi. With a laser detuning Δ from the ring-1 resonance and a peak frequency excursion δω,")
    add_p(doc,
          "da1/dt = [−i(Δ + δω cos Ωm t) − (γ+κi)/2] a1 − iμ a2 − √γ αin",
          size=10.5, align="center", space_before=2, space_after=1)
    add_p(doc,
          "da2/dt = [−i(Δ + s δω cos Ωm t) − κi/2] a2 − iμ a1",
          size=10.5, align="center", space_before=0, space_after=1)
    add_p(doc,
          "aout = αin + √γ a1",
          size=10.5, align="center", space_before=0, space_after=6)
    body(doc,
         "For the acoustic drive, s = 0. For the electro-optic reference, s = −1, which is the push–pull drive of Hu et al. The laser sits on the symmetric supermode, Δ = μ. In the supermode basis the single-ring term contains a coupling of strength δω/2 and a common-mode phase modulation. The common-mode piece is what produces the carrier and the unwanted orders; push–pull electro-optic driving cancels it.")
    body(doc,
         "The integration is a fixed-step fourth-order Runge–Kutta method, 80 steps per modulation period (3.75 ps at 3.33 GHz), for 40 ns, with no rotating-wave approximation. The output is projected onto ωL + qΩm for |q| ≤ 3, using the last 20 ns. The shift ratio is ηshift = Pshift/Pout, the absolute efficiency is ηabs = Pshift/Pin, and the insertion loss is IL = −10 log10(Pout/Pin). The shifted line is the up-shifted order q = +1. Sideband levels quoted below are relative to that line.")
    body(doc,
         "A peak voltage V from a 50 Ω source, PRF = V²/(2R), writes a phase Δφ = π V La /(VπL) over the covered length La = 100 μm. The ring resonance then moves by δω = Δφ c /(ng Lring). With VπL = 0.046 V·cm this is 21.3 GHz/V. Shao et al. (2019) extract Vπ from S21 referenced to a 50 Ω source, so the calibration already includes the measured electrical-to-acoustic coupling of that transducer, about 50% (a −3 dB dip in S11). We call this the Shao transducer. An ideally matched transducer needs half the power. A transducer of efficiency ηIDT needs 0.5/ηIDT times the Shao-transducer power. The acoustic resonance is taken at Qm = 2,000 and γe/γ = 0.15, the values used to model the measured devices; the measured acoustic quality factor reaches 3,600. An unsourced value Qm = 1,570 is kept only as a conservative power estimate.")
    body(doc,
         "Optically, γ/2π = 0.6 GHz. The intrinsic loss is taken from Table S2 of Shao et al. (2019): κ/2π = 95 MHz and 2κe/κ = 0.3, so κi/2π = 80.75 MHz and Qi ≈ 2.4×10⁶ at 193.4 THz. The electro-optic reference uses the same optics, push–pull modulation, and an electro-optic coefficient of about 0.5 GHz/V referred to the voltage on the electrode capacitor. The electrode is the lumped circuit of Hu et al., C = 0.11 pF, L = 0.12 nH, R = 1.5 Ω, with a capacitive reactance of 434 Ω at 3.33 GHz. Four feeds are compared: the source voltage directly on the capacitor, an open-circuited capacitor at twice the source voltage, a lumped LC match with inductor quality factor 30 or 100, and an ideal inductor. The QL = 30 match has a radio-frequency bandwidth of about 122 MHz.")
    body(doc,
         "The same ideal point was integrated independently as a global ordinary-differential-equation system in COMSOL Multiphysics 6.3, with a strict maximum step of 3.75 ps. That cross-check is an integrator test, not a three-dimensional electromagnetic or acoustic solve. It returns ηshift = 98.31%, absolute efficiency 55.4%, insertion loss 2.49 dB, and, relative to q = +1, a lower sideband of −21.18 dB, a carrier of −22.82 dB, and a q = +2 order of −23.64 dB. The archived Runge–Kutta peak, on a finer drive grid, is 98.35%, −21.20 dB, −23.16 dB, and −23.56 dB. The two integrators agree at the rounding used in Table 1.")

    heading(doc, "3.  Operating point and source power")
    body(doc,
         "Sections 3 and 4 use identical rings, no fabrication error, and no extra loss. The prediction we treat as the design point is the Monte Carlo result in Section 5. At γ/2π = 0.6 GHz the acoustic drive peaks at ηshift = 98.3% when δω/2π = 0.55 GHz: a source peak voltage of 26 mV and 6.7 μW with the Shao transducer. The absolute efficiency is 55% and the insertion loss is 2.5 dB. Both are set by the intrinsic loss, not by the drive. Relative to the shifted line, the largest spur is q = −1 at −21.2 dB, the carrier is at −23.2 dB, and q = +2 is at −23.6 dB. The push–pull electro-optic drive of the same optics reaches 99.6%, with the carrier at −26.0 dB and q = −1 at −30.6 dB, and the same 2.5 dB insertion loss.")
    fig(doc, "fig2_power_spectrum.png", 6.4)
    caption(doc,
            "Figure 2. Ideal operating point, γ/2π = 0.6 GHz and κi/2π = 80.75 MHz. (a) Shift ratio versus source radio-frequency power. Blue: acoustic drive with the Shao transducer (about 50% coupling), an ideal transducer, and a 10% transducer. Red: electro-optic drive with the source voltage on the capacitor, and with an open capacitor. Gold: LC-matched electro-optic drive at inductor quality factors 30, 100, and an ideal inductor. The star is the measured electro-optic shifter of Hu et al. (98.7% at 96 mW, 28.2 GHz). The 3.5% on-chip result of Shao et al. (2020) at 1 W is an absolute efficiency, not a shift ratio, and is not drawn on this axis. (b) Output in each order relative to the shifted line q = +1, at the acoustic and electro-optic optima. The q = +1 bar has zero height by this normalization.")

    add_p(doc, "Table 1. Ideal operating points. These are upper bounds. The realistic draw is in Table 3.",
          size=9, italic=True, space_before=6, space_after=2)
    add_table(doc,
              ["", "AO, simulation", "EO, same optics", "Hu 2021, measured"],
              [
                  ["Shift (GHz)", "3.33", "3.33", "28.2"],
                  ["γ/2π (GHz)", "0.60", "0.60", "5.31"],
                  ["κi/2π (MHz)", "80.75", "80.75", "170"],
                  ["ηshift", "98.3%", "99.6%", "98.7%"],
                  ["ηabs", "55%", "56%", "—"],
                  ["Insertion loss", "2.5 dB", "2.5 dB", "0.45 dB"],
                  ["Carrier vs q=+1", "−23.2 dB", "−26.0 dB", "—"],
                  ["Largest spur", "−21.2 dB (q=−1)", "−30.6 dB (q=−1)", "—"],
                  ["Source power, as built", "6.7 μW", "3.1 mW", "96 mW"],
                  ["Source power, matched", "3.4 μW", "1.2–13 μW", "—"],
                  ["RF bandwidth", "~1 MHz", "~122 MHz (QL=30)", ">3 GHz"],
              ],
              [4.2, 3.6, 3.8, 4.2])
    add_p(doc, "The as-built acoustic feed is the Shao transducer. The matched acoustic feed is an ideal transducer. The electro-optic matched range runs from an ideal inductor (1.2 μW) to QL = 30 (13 μW).",
          size=8.5, space_after=6)

    add_p(doc, "Table 2. Source power at the optimum shift ratio.",
          size=9, italic=True, space_before=4, space_after=2)
    add_table(doc,
              ["Drive and feed", "Source power"],
              [
                  ["AO, Shao transducer (~50%)", "6.7 μW"],
                  ["AO, ideal transducer", "3.4 μW"],
                  ["AO, 10% transducer, Qm = 2,000", "33.7 μW"],
                  ["AO, 10% transducer, Qm = 3,600", "18.7 μW"],
                  ["AO, 10% transducer, assumed Qm = 1,570", "43 μW"],
                  ["EO, Vc = V0", "3.1 mW"],
                  ["EO, open capacitor, Vc = 2V0", "0.77 mW"],
                  ["EO, LC match, QL = 30", "13 μW"],
                  ["EO, LC match, QL = 100", "4.8 μW"],
                  ["EO, ideal inductor", "1.2 μW"],
              ],
              [11.0, 4.8])
    body(doc,
         "Without matching, the electro-optic drive needs 3.1 mW, about 460 times the 6.7 μW of the Shao-transducer acoustic drive, and the measured Hu device used 96 mW. That comparison sets a resonant acoustic drive against a non-resonant electrode. It does not survive a matched comparison. With an LC match the electro-optic power falls to 13 μW, 4.8 μW, or 1.2 μW. Against an ideally matched transducer at 3.4 μW, the two drives differ by a factor between 0.36 and 3.9, and the electro-optic drive is the more economical one when the inductor loss is low. This paper does not claim a power advantage. What the acoustic resonator does provide is voltage gain without an external matching network, at the cost of a hundred-fold narrower radio-frequency bandwidth and a shift frequency fixed by the acoustic mode.")

    heading(doc, "4.  Tolerances")
    fig(doc, "fig3_tolerance.png", 6.4)
    caption(doc,
            "Figure 3. Tolerances of the acoustic design at the re-optimized drive. (a) Shift ratio and absolute efficiency versus intrinsic quality factor. The dotted line is the Qi implied by Shao et al. (2019). (b) Shift ratio versus detuning of the drive from the doublet splitting. For the acoustic drive the amplitude follows a Lorentzian of Qm = 2,000 (full width 1.67 MHz). The electro-optic curve is flat inside the 122 MHz bandwidth of the QL = 30 match. (c) Acoustic source power versus transducer efficiency, compared with the three matched electro-optic feeds. Vertical dotted lines mark 10% and 50%.")
    body(doc,
         "At the Shao intrinsic quality factor the shift ratio stays near 98% while the absolute efficiency is 55%. Dropping to Qi ≈ 1.3×10⁶ keeps the shift ratio near 98% but cuts the absolute efficiency to about 33% and raises the insertion loss to 4.7 dB. At Qi ≈ 6.5×10⁵ the shift ratio itself falls to about 82% and the insertion loss is 7.7 dB. The acoustic curve in Fig. 3(b) is the narrow object: 96.7% at 0.4 MHz of radio-frequency detuning, 80% at 1 MHz, 44% at 2 MHz, and 10% at 5 MHz. The matched electro-optic drive stays near 99.6% across the same window. Figure 3(c) shows why the transducer efficiency matters more than a further improvement of an already-matched electrode. The acoustic power scales as 1/ηIDT. Below about 25% transducer efficiency the acoustic drive uses more source power than a QL = 30 electro-optic match. Efficiencies near 10% have been reported in related lithium-niobate microrings, which is why 33.7 μW, not 6.7 μW, is the power quoted for the realistic design.")
    fig(doc, "fig4_thermal.png", 6.4)
    caption(doc,
            "Figure 4. Frequency tolerances at the acoustic operating point. (a) Shift ratio versus a common detuning Δ of both rings, a ring-2 minus ring-1 mismatch δr, and a splitting error 2μ−Ω. Dashed and dotted horizontals mark 95% and 90%. The top axis converts the frequency offset to temperature with the thermo-optic coefficient only, |df/dT| ≈ 2.8 GHz/K. Including thermal expansion (≈5.6 GHz/K) halves every temperature window. (b) Insertion loss for the same three cuts. (c) Shift ratio versus Δ and δr together. The dashed line is Δ = δr/2, the ridge along which a common heater can still track the laser.")
    body(doc,
         "The window with ηshift ≥ 95% is asymmetric. For the common detuning it runs from −72 MHz to +55 MHz. Converted with the thermo-optic coefficient alone, the narrower side is ±20 mK; with thermal expansion included it is ±9.8 mK. The ring-mismatch window is wider, −104 MHz to +145 MHz, or ±19 mK once expansion is included, and a heater on one ring can null it. The splitting window, −96 MHz to +53 MHz, is not a temperature specification: the acoustic frequency barely moves, so 2μ has to be fabricated, or trimmed, onto Ω. Passive temperature control does not hold the common resonance. The device needs an active lock, or a laser locked to the resonance, at the ±9.8 mK level.")

    heading(doc, "5.  Realistic Monte Carlo")
    body(doc,
         "The draw has 1,000 samples (seed 1 of the archived script). Relative to the ideal point it doubles the intrinsic loss, draws the coupling gap from a normal distribution of standard deviation 5 nm, holds a residual lock jitter of 5 mK, and allows the radio-frequency source to retune by at most ±1 MHz. The acoustic quality factor is fixed at 2,000, and the transducer efficiency is 10%. These additions are assumptions. Each was also scanned one at a time.")
    fig(doc, "fig5_montecarlo.png", 6.4)
    caption(doc,
            "Figure 5. Realistic-condition Monte Carlo, N = 1,000. (a) Shift ratio. The dashed line is the ideal 98.3%; the solid line is the sample median, 94.3%. (b) On-chip insertion loss; median 5.0 dB against an ideal 2.5 dB. (c) Absolute shifted fraction: ideal chip, Monte Carlo on-chip, Monte Carlo fiber-to-fiber at 1.5 dB per facet, and the measured 3.5% of Shao et al. (2020). Error bars are the 10th and 90th percentiles. (d–f) One-parameter scans. The line is the median shift ratio and the band is the 10th–90th percentile. The horizontal dotted line is 90%.")

    add_p(doc, "Table 3. Realistic draw. Medians, with the 10th–90th percentile in parentheses where the archive records it.",
          size=9, italic=True, space_before=4, space_after=2)
    add_table(doc,
              ["Quantity", "Ideal", "Monte Carlo"],
              [
                  ["ηshift", "98.3%", "94.3% (82.4–97.9%)"],
                  ["Fraction of samples ≥ 90%", "—", "73%"],
                  ["Fraction of samples ≥ 95%", "—", "45%"],
                  ["On-chip insertion loss", "2.5 dB", "5.0 dB"],
                  ["On-chip absolute efficiency", "55%", "28.4% (21.5–38.8%)"],
                  ["Fiber-to-fiber, 1.5 dB/facet", "—", "14.2%"],
                  ["Source power, 10% IDT", "33.7 μW", "33.7 μW"],
                  ["Splitting-error std. dev.", "0", "114 MHz"],
                  ["Samples left outside ±1 MHz", "—", "99.2%"],
              ],
              [7.4, 3.4, 5.0])
    body(doc,
         "The coupling gap dominates. A 5 nm error already produces about 114 MHz root-mean-square error in the splitting, far outside the 1 MHz acoustic linewidth, and radio-frequency retuning leaves 99% of the samples uncorrected. At a 10 nm gap error the median shift ratio falls to 0.89, with a 10th percentile of 0.64. A heater on the coupler between the rings would make the splitting tunable; that heater is not in the model. The lock is the next term: the median is 0.91 at 10 mK of residual jitter and 0.80 at 20 mK. Extra optical loss is less damaging to the shift ratio than to the insertion loss, and it may be double-counted, because the quality factor taken from Shao et al. (2019) already belongs to a suspended racetrack with a transducer.")

    heading(doc, "6.  Two-photon interference and thermal phonons")
    body(doc,
         "For a quantum interface the relevant quantity is the overlap of the shifted photon with a reference photon in the target bin. The Hong–Ou–Mandel visibility is computed from the complex shift spectrum on a delay scan from −20 ns to +20 ns, with the reference delay chosen to maximize the overlap. Filtering to the target bin removes the carrier and the spurious orders. Without that filter the visibility cannot exceed the shift ratio.")
    fig(doc, "fig6_hom.png", 4.5)
    caption(doc,
            "Figure 6. Hong–Ou–Mandel infidelity versus the root-mean-square bandwidth of the photon, at the ideal operating point. Circles: the shifted photon is filtered to the target bin and the reference delay is matched. Squares: no filter. The dotted line is 1−ηshift. The unfiltered points sit on that floor at narrow bandwidth and rise once the photon spectrum no longer fits inside one bin.")
    body(doc,
         "At 10 MHz the filtered infidelity is 7.8×10⁻⁷. At 5, 25, 50, 100, and 200 MHz it is 6.2×10⁻⁸, 3.0×10⁻⁵, 6.1×10⁻⁴, 1.1×10⁻², and 9.2×10⁻². The unfiltered infidelity at 10 MHz is 1.65×10⁻², which is 1−ηshift. These numbers are the ideal-point spectrum. They do not include the Monte Carlo spread of the shift ratio, and they are not a measured interference fringe.")
    body(doc,
         "Thermal occupation of the acoustic mode is a separate, smaller term. With g0/2π = 1.1 kHz, κ/2π = 681 MHz, and γm/2π = 1.67 MHz, the coherent phonon number at the operating drive is Ncoh = 1.75×10¹¹. At 300 K the thermal occupation is nth = 1,877, so nth/Ncoh = 1.1×10⁻⁸. The corresponding incoherent coupling, nth C0 with C0 = 4.3×10⁻⁹, is 8×10⁻⁶, below the 1.7% of light that is already outside the shifted line. At 4 K and at 10 mK the ratio is smaller still. Room-temperature thermal phonons are not the limit of this shifter. The limit is the optical spurious orders, the insertion loss, and the fabrication of the splitting.")

    heading(doc, "7.  What this edition does not change")
    body(doc,
         "The curves are redrawn from the archived tables (efficiency versus power, quality-factor scan, radio-frequency detuning, transducer-efficiency scan, tolerance grid, Monte Carlo sample file, and the delay-matched Hong–Ou–Mandel table). No operating point was re-optimized for this edition. Two plotting choices of the previous figures are corrected. The sideband panel is now referenced to the shifted line, so a suppression of 21 dB is a bar at −21 dB rather than a bar whose baseline had been shifted by hand. The 3.5% result of the 2020 traveling-wave shifter is an absolute efficiency and is plotted only against other absolute efficiencies, in Fig. 5(c).")
    body(doc,
         "The following limits are unchanged, and they are the ones that decide whether the design is worth laying out. The radio-frequency bandwidth is about 1 MHz and the shift is fixed at 3.33 GHz, against 12.5–28.2 GHz and a multi-gigahertz bandwidth for the measured electro-optic molecule. The ideal insertion loss, 2.5 dB, is already worse than the 0.45 dB of that measured device, and the realistic median is 5.0 dB. The fiber-to-fiber number assumes 1.5 dB per facet; the suspended chip of Shao et al. (2019) was closer to 5 dB per facet. The conversion from the measured Mach–Zehnder VπL to a ring that is only 15% covered assumes the same mode overlap and a uniform acoustic phase along the covered arc, and it assumes ng = 2.3. Heating of the transducer, and the resonance drift that heating produces, is not in the model; the 2019 experiment saw a red shift as the microwave power increased. There is no layout, and the photoelastic overlap that would replace the 21.3 GHz/V calibration has not been computed from a mode solve.")
    body(doc,
         "A later Monte Carlo that turns a splitting heater on, and quotes a median near 96%, is not used here. The sample table for that draw is not in the archive this edition is plotted from. The numbers above are the seed-1 draw with the heater off.")

    heading(doc, "8.  Conclusion")
    body(doc,
         "In this model, a suspended acoustic resonator driving one ring of a thin-film-lithium-niobate photonic molecule shifts light by 3.33 GHz. Under the stated realistic assumptions the median shift ratio is 94.3% (82.4–97.9%), the median on-chip absolute efficiency is 28%, and the fiber-to-fiber estimate is 14%, at 34 μW from a 10%-efficient transducer. The ideal point, 98.3% at about 7 μW with 55% absolute efficiency, is an upper bound and is reproduced by an independent integration of the same equations. The design is not more power-efficient than an impedance-matched electro-optic drive of the same optics. It is narrower in radio frequency, fixed in shift frequency, and it requires a ±9.8 mK lock and a coupling gap controlled to about 5 nm. With a delay-matched reference and a target-bin filter, the ideal-point Hong–Ou–Mandel infidelity is 8×10⁻⁷ at 10 MHz and 6×10⁻⁴ at 50 MHz, and thermal phonons at room temperature are negligible beside the optical spurious orders.")
    body(doc,
         "The measurements that would make the prediction falsifiable are the acousto-optic coupling of a high-Q ring that the acoustic field covers only in part, the transducer efficiency and the optical loss and heating added by the transducer, and the gap and lock that a real chip can hold. Until those are measured, every number in this paper remains a calculation.")

    heading(doc, "References")
    refs = [
        "Y. Hu et al., Nature 599, 587 (2021).",
        "L. Shao et al., Optica 6, 1498 (2019).",
        "L. Shao et al., Opt. Express 28, 23728 (2020).",
        "M. Zhang et al., Nat. Photonics 13, 36 (2019).",
        "C. Wang et al., Nature 562, 101 (2018).",
        "M. Zhang, C. Wang, R. Cheng, A. Shams-Ansari, and M. Lončar, Optica 4, 1536 (2017).",
        "J. M. Lukens and P. Lougovski, Optica 4, 8 (2017).",
        "H.-H. Lu et al., Phys. Rev. Lett. 120, 030502 (2018).",
        "M. Kues et al., Nature 546, 622 (2017).",
        "D. Zhu et al., Light Sci. Appl. 11, 327 (2022).",
        "Z. Qiu et al., Opt. Lett. 50, 1132 (2025).",
        "Z.-X. Zhu et al., arXiv:2511.22585 (2025).",
        "X.-B. Xu et al., arXiv:2509.01940 (2025).",
        "S. Kapfinger et al., Nat. Commun. 6, 8540 (2015).",
        "S. A. Tadesse and M. Li, Nat. Commun. 5, 5402 (2014).",
    ]
    for i, t in enumerate(refs, 1):
        add_p(doc, f"[{i}]  {t}", size=9, space_after=1)

    add_p(doc,
          "Data. The curves in Figures 2–6 are computed from the archived tables in the design-study directory of the authors’ data repository (xinleichen666/tfln-data, dir11/paperB/data): eff_vs_power.csv, results_B.json, Q_tolerance.csv, RF_detuning.csv, IDT_sensitivity.csv, tol_scan.csv, mc_samples.csv, realistic_summary.json, and HOM.csv. Scripts: core.py, make_all.py, hom_post.py, tol_scan.py, realistic.py.",
          size=9, space_before=8, space_after=2)

    doc.save(DOCX)
    print("docx", DOCX, DOCX.stat().st_size)


def to_pdf():
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    word.DisplayAlerts = 0
    d = word.Documents.Open(str(DOCX))
    d.SaveAs(str(PDF), FileFormat=17)
    d.SaveAs(str(PDF_DL), FileFormat=17)
    d.Close(False)
    try:
        word.Quit()
    except Exception as e:
        print("quit", e)
    print("pdf", PDF, PDF.stat().st_size)


if __name__ == "__main__":
    build()
    to_pdf()

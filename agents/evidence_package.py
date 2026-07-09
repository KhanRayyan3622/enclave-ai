"""
Regulator-Ready Evidence Package Generator.

Bundles a completed Enclave pipeline run into a single professional PDF:
verdict, policy citations, sovereignty score, audit chain hash, EU AI Act
Annex IV mapping, and Gemma second-opinion check — the artifact a real
compliance officer would attach to a case file.
"""
from datetime import datetime, timezone
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_evidence_pdf(pipeline_result: dict, output_path: str = "results/evidence_package.pdf"):
    Path(output_path).parent.mkdir(exist_ok=True)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleCustom", parent=styles["Title"], textColor=colors.HexColor("#0A5C36"), fontSize=20
    )
    heading_style = ParagraphStyle(
        "HeadingCustom", parent=styles["Heading2"], textColor=colors.HexColor("#0A5C36")
    )
    body_style = styles["BodyText"]
    mono_style = ParagraphStyle("Mono", parent=styles["Code"], fontSize=8, leading=10)

    doc = SimpleDocTemplate(output_path, pagesize=letter,
                             topMargin=0.6*inch, bottomMargin=0.6*inch)
    story = []

    # --- Header ---
    story.append(Paragraph("Enclave — Regulator-Ready Evidence Package", title_style))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        f"Generated: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')} | "
        f"Data Residency: 0 bytes left this node", body_style
    ))
    story.append(Spacer(1, 20))

    # --- Task & Verdict ---
    story.append(Paragraph("1. Task Reviewed", heading_style))
    story.append(Paragraph(pipeline_result.get("task", "N/A"), body_style))
    story.append(Spacer(1, 10))

    verdict = pipeline_result.get("verdict", "UNKNOWN")
    verdict_color = {"PASS": colors.green, "FLAGGED": colors.orange, "FAIL": colors.red}.get(verdict, colors.black)
    story.append(Paragraph("2. Final Verdict", heading_style))
    story.append(Paragraph(f'<font color="{verdict_color}"><b>{verdict}</b></font>', styles["Heading3"]))
    story.append(Spacer(1, 10))

    # --- Auditor Reasoning ---
    auditor_text = pipeline_result.get("results", {}).get("auditor", {}).get("result", "N/A")
    story.append(Paragraph("3. Auditor Reasoning (Policy-Cited)", heading_style))
    import re as _re
    def _safe_bold(line: str) -> str:
        # Escape any raw angle brackets first so they don't break the XML parser
        line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        # Convert markdown **bold** pairs to <b>...</b>, properly alternating tags
        parts = line.split("**")
        result = ""
        for i, part in enumerate(parts):
            if i % 2 == 1:
                result += f"<b>{part}</b>"
            else:
                result += part
        return result

    for line in auditor_text.split("\n"):
        if line.strip():
            story.append(Paragraph(_safe_bold(line), body_style))
    story.append(Spacer(1, 14))

    # --- Escalation ---
    escalation = pipeline_result.get("escalation")
    if escalation:
        story.append(Paragraph("4. Human Escalation Required", heading_style))
        data = [
            ["Routed To", ", ".join(escalation.get("routed_to", []))],
            ["Priority", escalation.get("priority", "N/A")],
            ["SLA", escalation.get("sla_note", "N/A")],
        ]
        t = Table(data, colWidths=[1.5*inch, 4.5*inch])
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (0,-1), colors.HexColor("#E8F5E9")),
            ("FONTSIZE", (0,0), (-1,-1), 9),
        ]))
        story.append(t)
        story.append(Spacer(1, 14))

    # --- Sovereignty Score ---
    sov = pipeline_result.get("sovereignty_score", {})
    story.append(Paragraph("5. Sovereignty Score", heading_style))
    story.append(Paragraph(f"<b>{sov.get('sovereignty_score', 'N/A')} / 100</b>", styles["Heading3"]))
    breakdown = sov.get("breakdown", {})
    if breakdown:
        rows = [["Component", "Score", "Detail"]]
        for k, v in breakdown.items():
            rows.append([k.replace("_", " ").title(), f"{v['score']}/{v['max']}", str(v["detail"])])
        t = Table(rows, colWidths=[2*inch, 1*inch, 3*inch])
        t.setStyle(TableStyle([
            ("GRID", (0,0), (-1,-1), 0.5, colors.grey),
            ("BACKGROUND", (0,0), (-1,0), colors.HexColor("#0A5C36")),
            ("TEXTCOLOR", (0,0), (-1,0), colors.white),
            ("FONTSIZE", (0,0), (-1,-1), 8),
        ]))
        story.append(t)
    story.append(Spacer(1, 14))

    # --- Framework Coverage ---
    fw = pipeline_result.get("framework_coverage", {})
    story.append(Paragraph("6. Regulatory Framework Coverage", heading_style))
    story.append(Paragraph(f"Frameworks touched: {', '.join(fw.get('frameworks_touched', [])) or 'None'}", body_style))
    for section in fw.get("eu_ai_act_annex_iv_sections_covered", []):
        story.append(Paragraph(f"EU AI Act Annex IV: {section}", body_style))
    story.append(Spacer(1, 14))

    # --- Gemma Second Opinion ---
    gemma = pipeline_result.get("gemma_second_opinion", {})
    story.append(Paragraph("7. Independent Second-Opinion Check (Gemma)", heading_style))
    if gemma.get("checked"):
        story.append(Paragraph(f"Model: {gemma.get('model')}", body_style))
        story.append(Paragraph(gemma.get("response", "")[:500], body_style))
    else:
        story.append(Paragraph(f"Not performed: {gemma.get('reason', 'N/A')}", body_style))
    story.append(Spacer(1, 14))

    # --- Integrity & Audit ---
    story.append(Paragraph("8. Cryptographic Integrity", heading_style))
    story.append(Paragraph(f"Audit chain verified: {pipeline_result.get('audit_chain_verified')}", body_style))
    story.append(Paragraph(f"Audit chain entries: {pipeline_result.get('audit_chain_entries')}", body_style))
    story.append(Paragraph(f"Integrity manifest hash: {pipeline_result.get('integrity_manifest_hash', 'N/A')}", mono_style))

    # --- Annex IV full doc as appendix ---
    story.append(PageBreak())
    story.append(Paragraph("Appendix: EU AI Act Annex IV Technical Documentation", heading_style))
    annex_doc = pipeline_result.get("eu_ai_act_annex_iv_doc", "")
    for line in annex_doc.split("\n"):
        if line.strip():
            safe_line = line.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            story.append(Paragraph(safe_line, mono_style))

    doc.build(story)
    return output_path

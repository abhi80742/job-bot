from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import cm
from reportlab.lib import colors
import os

def generate_pdf(resume_text: str, cover_letter: str,
                 company: str, role: str) -> str:
    os.makedirs("outputs", exist_ok=True)
    safe = f"{company}_{role}".replace(" ", "_").replace("/", "-")
    filename = f"outputs/{safe}.pdf"

    doc = SimpleDocTemplate(
        filename, pagesize=A4,
        leftMargin=2*cm, rightMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )
    styles = getSampleStyleSheet()
    h1 = ParagraphStyle(
        "h1", parent=styles["Heading1"],
        fontSize=14, textColor=colors.HexColor("#1a1a2e"),
        spaceAfter=6
    )
    body = ParagraphStyle(
        "body", parent=styles["Normal"],
        fontSize=11, leading=16, spaceAfter=4
    )
    story = []

    story.append(Paragraph("Cover Letter", h1))
    story.append(Spacer(1, 0.3*cm))
    for line in cover_letter.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), body))
            story.append(Spacer(1, 0.1*cm))

    story.append(Spacer(1, 0.8*cm))
    story.append(Paragraph("Resume", h1))
    story.append(Spacer(1, 0.3*cm))
    for line in resume_text.split("\n"):
        if line.strip():
            story.append(Paragraph(line.strip(), body))
            story.append(Spacer(1, 0.1*cm))

    doc.build(story)
    print(f"  PDF saved: {filename}")
    return filename
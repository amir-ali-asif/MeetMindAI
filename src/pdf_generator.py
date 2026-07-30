import os
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_meeting_report_pdf(meeting_data: dict, output_path: str) -> dict:
    """
    Takes the pipeline output (summary, key_decisions, action_items) 
    and generates a clean, professional PDF report.
    """
    try:
        doc = SimpleDocTemplate(output_path, pagesize=A4,
                                 topMargin=0.75 * inch, bottomMargin=0.75 * inch)
        styles = getSampleStyleSheet()

        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["Heading1"],
            fontSize=20, spaceAfter=6, textColor=colors.HexColor("#1a1a2e")
        )
        heading_style = ParagraphStyle(
            "HeadingStyle", parent=styles["Heading2"],
            fontSize=14, spaceBefore=16, spaceAfter=8, textColor=colors.HexColor("#16213e")
        )
        body_style = ParagraphStyle(
            "BodyStyle", parent=styles["Normal"],
            fontSize=11, leading=16
        )

        elements = []

        # Title
        elements.append(Paragraph("Meeting Report", title_style))
        elements.append(Paragraph(
            f"Generated on {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
            styles["Normal"]
        ))
        elements.append(Spacer(1, 20))

        # Summary
        elements.append(Paragraph("Summary", heading_style))
        elements.append(Paragraph(meeting_data["summary"], body_style))
        elements.append(Spacer(1, 10))

        # Key Decisions
        elements.append(Paragraph("Key Decisions", heading_style))
        for decision in meeting_data["key_decisions"]:
            elements.append(Paragraph(f"• {decision}", body_style))
        elements.append(Spacer(1, 10))

        # Action Items as a table
        elements.append(Paragraph("Action Items", heading_style))

        table_data = [["Task", "Owner", "Deadline", "Confidence"]]
        for item in meeting_data["action_items"]:
            table_data.append([
                item["task"],
                item["owner"] or "Unassigned",
                item["deadline"] or "Not specified",
                item["confidence"].capitalize()
            ])

        table = Table(table_data, colWidths=[2.6 * inch, 1.2 * inch, 1.3 * inch, 1.1 * inch])
        table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a1a2e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f5f5f5")]),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements.append(table)

        doc.build(elements)

        return {"success": True, "path": output_path, "error": None}

    except Exception as e:
        return {"success": False, "path": None, "error": str(e)}


if __name__ == "__main__":
    sample_data = {
        "summary": "The team discussed the upcoming deployment schedule and testing requirements.",
        "key_decisions": [
            "Deployment will proceed tomorrow at 5 PM",
            "Testing will run in parallel with deployment"
        ],
        "action_items": [
            {"task": "Complete deployment", "owner": "Ahmed", "deadline": "Tomorrow 5 PM", "confidence": "high"},
            {"task": "Run parallel testing", "owner": "Speaker 2", "deadline": None, "confidence": "low"}
        ]
    }

    os.makedirs("reports", exist_ok=True)
    result = generate_meeting_report_pdf(sample_data, "reports/test_report.pdf")

    if result["success"]:
        print(f"PDF generated at: {result['path']}")
    else:
        print(f"Failed: {result['error']}")
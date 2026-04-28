import io
from reportlab.lib.pagesizes import LETTER
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from datetime import datetime

def generate_customer_report(customer_data: dict, prediction_res: dict, advice_data: dict):
    """
    Generates a professional 'Senior Tier' PDF diagnostic report for a single customer.
    Designed for executive distribution and boardroom review.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=LETTER, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)
    
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor("#5B4FE9"),
        spaceAfter=12,
        fontName='Helvetica-Bold'
    )
    
    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.grey,
        letterSpacing=1,
        textTransform='uppercase',
        spaceAfter=4
    )
    
    body_style = styles['Normal']
    
    elements = []
    
    # Header
    elements.append(Paragraph("CUSTOMERIQ STRATEGIC DIAGNOSTIC", label_style))
    elements.append(Paragraph(f"Executive Report: {customer_data['customer_id']}", title_style))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", body_style))
    elements.append(Spacer(1, 24))
    
    # --- Executive Summary ---
    elements.append(Paragraph("EXECUTIVE SUMMARY", label_style))
    status_text = f"The customer is currently classified as <b>{prediction_res.get('risk_level', 'UNKNOWN')} RISK</b> " \
                  f"with a churn probability of <b>{prediction_res.get('churn_probability', 0)*100:.1f}%</b>. "
    elements.append(Paragraph(status_text, body_style))
    elements.append(Spacer(1, 12))
    
    # --- Attributes Table ---
    elements.append(Paragraph("CUSTOMER ATTRIBUTES", label_style))
    data = [
        ["Attribute", "Value"],
        ["Age", str(customer_data.get("age", "N/A"))],
        ["Gender", str(customer_data.get("gender", "N/A"))],
        ["Tenure", f"{customer_data.get('tenure', 0)} Years"],
        ["Balance", f"${customer_data.get('balance', 0):,.2f}"],
        ["Products", str(customer_data.get("num_products", 0))],
        ["Is Active", "YES" if customer_data.get("is_active_member") else "NO"]
    ]
    
    t = Table(data, colWidths=[150, 250])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#F0F0F0")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey)
    ]))
    elements.append(t)
    elements.append(Spacer(1, 24))
    
    # --- Strategic Directives ---
    elements.append(Paragraph("STRATEGIC DIRECTIVES", label_style))
    for directive in advice_data.get("strategic_directives", []):
        elements.append(Paragraph(f"• {directive}", body_style))
        elements.append(Spacer(1, 4))
    
    elements.append(Spacer(1, 12))

    # --- Statistical Risk Drivers ---
    elements.append(Paragraph("ADVERSE RISK DRIVERS (SHAP ANALYSIS)", label_style))
    for driver in advice_data.get("risk_drivers", []):
        impact_pct = driver['impact'] * 100
        elements.append(Paragraph(f"<b>{driver['feature'].upper()}</b> — Impact Score: {impact_pct:.2f}%", body_style))
    
    elements.append(Spacer(1, 48))
    elements.append(Paragraph("CONFIDENTIAL | INTERNAL USE ONLY", styles['Italic']))
    
    doc.build(elements)
    buffer.seek(0)
    return buffer

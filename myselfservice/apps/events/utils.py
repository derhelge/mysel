import os
from io import BytesIO
from django.conf import settings
from django.utils.formats import date_format
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet 
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.units import cm
from reportlab.graphics import renderPDF
from svglib.svglib import svg2rlg

def generate_event_pdf(event):
    buffer = BytesIO()
    pt = 2.83465

    # Dokument mit Header-Callback erstellen
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=4*cm,
        bottomMargin=2*cm
    )

    def header(canvas, doc):
        width, height = A4
        logo_path = os.path.join(settings.BASE_DIR, 'static', 'logo-thga.svg')
        drawing = svg2rlg(logo_path)
        
        # Zielgrößen in mm
        target_width_mm = 53.5
        target_height_mm = 22.3
        
        # Berechne Skalierungsfaktor
        scale_x = (target_width_mm * pt) / drawing.width
        scale_y = (target_height_mm * pt) / drawing.height
        scale = min(scale_x, scale_y)  # Proportionen beibehalten
        drawing.scale(scale, scale)
        
        # Position
        left_margin_mm = 142
        top_margin_mm = 12.2
        
        renderPDF.draw(drawing, canvas, 
                      left_margin_mm * pt, 
                      height - (top_margin_mm * pt) - (target_height_mm * pt))

    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    normal_style = styles['Normal']

    story = []

    # Titel
    story.append(Paragraph(f"Zugangsdaten für die Veranstaltung: {event.name}", title_style))
    story.append(Spacer(1, 12))
    
    # Event Details
    start = date_format(event.start_date, format="SHORT_DATE_FORMAT", use_l10n=True)
    end = date_format(event.end_date, format="SHORT_DATE_FORMAT", use_l10n=True)
    story.append(Paragraph(f"Gültig vom {start} bis {end}", normal_style))
    story.append(Spacer(1, 24))

    # Übersichtstabelle 
    guests = sorted(event.guests.all(), key=lambda x: x.username)
    data = []

    table_header = ['Benutzer', 'Name', 'Unterschrift']
    data.append(table_header)
    for guest in guests:
        data.append([guest.username])
    table = Table(data, colWidths=[6*cm,6*cm,6*cm])

    table.setStyle(TableStyle([
        ('FONT', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('PADDING', (0, 0), (-1, -1), 4),
    ]))
    story.append(table)
    story.append(PageBreak())

    # Pro User ein One-Pager
    for guest in guests:
        # Deutsch
        story.append(Paragraph("WLAN-Zugang", title_style))
        story.append(Spacer(1, 12))

        # Zugangsdaten-Tabelle
        cred_data = [
            ['Benutzername:', guest.username],
            ['Passwort:', guest.password]
        ]
        cred_table = Table(cred_data, colWidths=[4*cm, 8*cm])
        cred_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica'),
            ('FONT', (1, 0), (1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        story.append(cred_table)
        story.append(Spacer(1, 24))

        # Anleitung
        story.append(Paragraph("Anleitung:", subtitle_style))
        story.append(Paragraph("1. Verbinden Sie sich mit dem WLAN 'THGA'", normal_style))
        story.append(Paragraph("2. Melden Sie sich am WLAN-Portal mit obigen Zugangsdaten an", normal_style))
        story.append(Paragraph(f"3. Dieser Account ist gültig vom {start} bis zum {end}", normal_style))
        story.append(Spacer(1, 24))
        
        # Warnhinweise
        story.append(Paragraph("Wichtige Hinweise:", subtitle_style))
        warnings = [
            "Der Zugang darf nicht weitergegeben werden",
            "Die Verbindungen werden protokolliert",
            "Die WLAN-Verbindung ist unverschlüsselt"
        ]
        for warning in warnings:
            story.append(Paragraph(f"• {warning}", normal_style))

        story.append(Spacer(1, 24))
        
        # Trennlinie
        story.append(Table([['']], colWidths=[16*cm], style=[
            ('LINEABOVE', (0,0), (-1,0), 1, colors.black),
        ]))
        story.append(Spacer(1, 24))

        # English
        story.append(Paragraph("WiFi Access", title_style))
        story.append(Spacer(1, 12))
        # Credentials table in English
        cred_data = [
            ['Username:', guest.username],
            ['Password:', guest.password]
        ]
        cred_table = Table(cred_data, colWidths=[4*cm, 8*cm])
        cred_table.setStyle(TableStyle([
            ('FONT', (0, 0), (0, -1), 'Helvetica'),
            ('FONT', (1, 0), (1, -1), 'Courier'),
            ('FONTSIZE', (0, 0), (-1, -1), 11),
            ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'), 
            ('PADDING', (0, 0), (-1, -1), 6),
            ('BACKGROUND', (0, 0), (-1, -1), colors.lightgrey),
        ]))
        story.append(cred_table)
        story.append(Spacer(1, 24))
        story.append(Paragraph("Instructions:", subtitle_style))
        story.append(Paragraph("1. Connect to the 'THGA' WiFi network", normal_style))
        story.append(Paragraph("2. Log in to the WiFi portal using the credentials above", normal_style))
        story.append(Paragraph(f"3. This account is valid from {start} until {end}", normal_style))
        story.append(Spacer(1, 24))

        story.append(Paragraph("Important Notes:", subtitle_style))
        warnings_en = [
            "This access is for personal use only",
            "Network connections are logged",
            "The WiFi connection is unencrypted"
        ]
        for warning in warnings_en:
            story.append(Paragraph(f"• {warning}", normal_style))

        story.append(PageBreak())

    doc.build(story, onFirstPage=header, onLaterPages=header)
    pdf = buffer.getvalue()
    buffer.close()
    
    return pdf
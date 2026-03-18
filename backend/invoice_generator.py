from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import io
import os

def generate_invoice_pdf(order_data: dict) -> bytes:
    """
    Generate PDF invoice for an order
    
    Args:
        order_data: Dictionary containing order details
        
    Returns:
        bytes: PDF file content
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    
    # Container for PDF elements
    elements = []
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#0F172A'),
        spaceAfter=30,
        alignment=TA_CENTER
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#6D28D9'),
        spaceAfter=12
    )
    
    # Company header
    company_name = Paragraph("<b>ShopHub Premium Store</b>", title_style)
    elements.append(company_name)
    elements.append(Spacer(1, 0.2*inch))
    
    # Invoice title
    invoice_title = Paragraph("<b>INVOICE</b>", heading_style)
    elements.append(invoice_title)
    elements.append(Spacer(1, 0.3*inch))
    
    # Order details
    order_info = [
        ["Order ID:", order_data.get('id', 'N/A')],
        ["Order Date:", order_data.get('created_at', datetime.now().strftime('%Y-%m-%d %H:%M'))],
        ["Payment Status:", order_data.get('payment_status', 'Pending').upper()],
        ["Order Status:", order_data.get('order_status', 'Pending').upper()]
    ]
    
    order_table = Table(order_info, colWidths=[2*inch, 4*inch])
    order_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(order_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Customer details
    customer_heading = Paragraph("<b>Customer Details</b>", heading_style)
    elements.append(customer_heading)
    
    customer_info = [
        ["Name:", order_data.get('customer_name', 'N/A')],
        ["Email:", order_data.get('customer_email', 'N/A')],
        ["Phone:", order_data.get('phone', 'N/A')],
        ["Shipping Address:", order_data.get('shipping_address', 'N/A')]
    ]
    
    customer_table = Table(customer_info, colWidths=[2*inch, 4*inch])
    customer_table.setStyle(TableStyle([
        ('FONT', (0, 0), (0, -1), 'Helvetica-Bold', 10),
        ('FONT', (1, 0), (1, -1), 'Helvetica', 10),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#0F172A')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(customer_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Items table
    items_heading = Paragraph("<b>Order Items</b>", heading_style)
    elements.append(items_heading)
    
    items_data = [['Product', 'Quantity', 'Price', 'Total']]
    total_amount = 0
    
    for item in order_data.get('items', []):
        product_name = item.get('product_name', 'N/A')
        quantity = item.get('quantity', 0)
        price = item.get('price', 0)
        item_total = quantity * price
        total_amount += item_total
        
        items_data.append([
            product_name,
            str(quantity),
            f"₹{price:.2f}",
            f"₹{item_total:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#6D28D9')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONT', (0, 0), (-1, 0), 'Helvetica-Bold', 11),
        ('FONT', (0, 1), (-1, -1), 'Helvetica', 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E2E8F0')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F8FAFC')])
    ]))
    elements.append(items_table)
    elements.append(Spacer(1, 0.2*inch))
    
    # Total
    total_data = [
        ['', '', 'Total Amount:', f"₹{total_amount:.2f}"]
    ]
    total_table = Table(total_data, colWidths=[3*inch, 1*inch, 1.5*inch, 1.5*inch])
    total_table.setStyle(TableStyle([
        ('FONT', (2, 0), (3, 0), 'Helvetica-Bold', 12),
        ('TEXTCOLOR', (2, 0), (3, 0), colors.HexColor('#10B981')),
        ('ALIGN', (2, 0), (3, 0), 'CENTER'),
        ('BACKGROUND', (2, 0), (3, 0), colors.HexColor('#F0FDF4')),
        ('BOX', (2, 0), (3, 0), 2, colors.HexColor('#10B981')),
    ]))
    elements.append(total_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Expected delivery
    if order_data.get('expected_delivery'):
        delivery_text = Paragraph(
            f"<b>Expected Delivery:</b> {order_data['expected_delivery']}",
            styles['Normal']
        )
        elements.append(delivery_text)
        elements.append(Spacer(1, 0.2*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#64748B'),
        alignment=TA_CENTER
    )
    footer = Paragraph(
        "Thank you for shopping with us!<br/>For queries, contact support@shophub.com",
        footer_style
    )
    elements.append(Spacer(1, 0.3*inch))
    elements.append(footer)
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF bytes
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes

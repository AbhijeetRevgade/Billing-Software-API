from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.authentication import TokenAuthentication
from core.authentication import QueryParameterTokenAuthentication
from django.db import transaction
from django.http import HttpResponse
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer, InvoiceItemSerializer
from products.models import Product

# Import for PDF generation
import io

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    authentication_classes = [TokenAuthentication, QueryParameterTokenAuthentication]
    
    filterset_fields = ['payment_status', 'payment_method', 'customer']
    search_fields = ['invoice_number', 'customer__name', 'customer__phone']

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=False, methods=['POST'], permission_classes=[permissions.IsAuthenticated])
    def preview(self, request):
        """
        Preview invoice calculations and check stock without saving to database.
        Accepts the same JSON as create.
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Pull data but DONT save
        data = serializer.validated_data
        items_data = data.get('items', [])
        
        # The serializer has already calculated basic validation.
        # Let's return the preview of what would be created.
        preview_data = serializer.to_representation(Invoice(**data))
        # Note: Invoice number won't be generated since we didn't save.
        preview_data['invoice_number'] = "PREVIEW-ONLY"
        
        return Response(preview_data)

    @action(detail=True, methods=['GET'])
    def download_pdf(self, request, pk=None):
        """
        Generate and download a professional PDF of the invoice using ReportLab.
        Pure Python implementation (no system dependencies like cairo).
        """
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import cm
        from django.utils import timezone

        invoice = self.get_object()
        
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Design colors
        PRIMARY_RED = colors.HexColor('#ed1c24')
        TEXT_DARK = colors.HexColor('#333333')
        LIGHT_BG = colors.HexColor('#fcfcfc')
        SOFT_GREY = colors.HexColor('#eeeeee')

        # Create the PDF object
        doc = SimpleDocTemplate(
            buffer, 
            pagesize=A4, 
            rightMargin=1*cm, 
            leftMargin=1*cm, 
            topMargin=1*cm, 
            bottomMargin=1.5*cm
        )
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'InvoiceTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=PRIMARY_RED,
            alignment=1, # Center
            spaceAfter=2,
            textTransform='uppercase'
        )
        subtitle_style = ParagraphStyle(
            'Subtitle',
            parent=styles['Normal'],
            fontSize=9,
            textColor=colors.grey,
            alignment=1, # Center
            spaceAfter=20
        )
        section_title_style = ParagraphStyle(
            'SectionTitle',
            parent=styles['Normal'],
            fontSize=11,
            textColor=PRIMARY_RED,
            fontName='Helvetica-Bold',
            spaceAfter=5,
            borderBottomWidth=1,
            borderBottomColor=SOFT_GREY
        )
        normal_style = ParagraphStyle(
            'NormalStyle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14
        )

        # 1. Header
        elements.append(Paragraph("Vighnaharta Fataka", title_style))
        elements.append(Paragraph("Premium Firecrackers & Festival Supplies | GSTIN: APPLIED_FOR", subtitle_style))

        # 2. Info Section (Invoice & Customer details in a two-column table)
        info_data = [
            [
                Paragraph("Invoice Details", section_title_style), 
                Paragraph("Bill To", section_title_style)
            ],
            [
                Paragraph(f"<b>Number:</b> {invoice.invoice_number}<br/>"
                          f"<b>Date:</b> {invoice.created_at.strftime('%d %b %Y')}<br/>"
                          f"<b>Time:</b> {invoice.created_at.strftime('%H:%M')}<br/>"
                          f"<b>Status:</b> {invoice.get_payment_status_display()}", normal_style),
                Paragraph(f"<b>Name:</b> {invoice.customer.name if invoice.customer else 'Guest'}<br/>"
                          f"<b>Phone:</b> {invoice.customer.phone if invoice.customer else 'N/A'}<br/>"
                          f"<b>Address:</b> {invoice.customer.address or '-'}", normal_style)
            ]
        ]
        info_table = Table(info_data, colWidths=[9*cm, 9*cm])
        info_table.setStyle(TableStyle([
            ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ('BOTTOMPADDING', (0,0), (-1,-1), 0),
            ('TOPPADDING', (0,0), (-1,-1), 0),
            ('LEFTPADDING', (0,0), (-1,-1), 0),
        ]))
        elements.append(info_table)
        elements.append(Spacer(1, 15))

        # 3. Items Table
        item_header = ["#", "Item Description", "Unit", "Qty", "Price", "Total"]
        table_data = [item_header]
        
        for idx, item in enumerate(invoice.items.all(), 1):
            table_data.append([
                str(idx),
                Paragraph(f"<b>{item.product_name_snapshot}</b><br/><font size='8' color='grey'>SKU: {item.sku_snapshot}</font>", normal_style),
                item.get_unit_display(),
                str(item.quantity),
                f"{item.unit_price:.2f}",
                f"{item.total_price:.2f}"
            ])

        # Create Table
        col_widths = [1*cm, 8.5*cm, 2.5*cm, 1.5*cm, 2.5*cm, 3*cm]
        items_table = Table(table_data, colWidths=col_widths, repeatRows=1)
        
        # Style Table
        items_table.setStyle(TableStyle([
            # Header
            ('BACKGROUND', (0, 0), (-1, 0), PRIMARY_RED),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
            ('TOPPADDING', (0, 0), (-1, 0), 8),
            
            # Rows
            ('ALIGN', (0, 1), (0, -1), 'CENTER'), # # column
            ('ALIGN', (2, 1), (-1, -1), 'RIGHT'), # numbers
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 0.5, SOFT_GREY),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, LIGHT_BG]),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 10))

        # 4. Totals (Table for alignment)
        totals_data = [
            ["", "Sub-Total:", f"₹{invoice.sub_total:.2f}"],
            ["", "Tax:", f"₹{invoice.tax_amount:.2f}"],
            ["", "Discount:", f"-₹{invoice.discount_amount:.2f}"],
            ["", "GRAND TOTAL:", f"₹{invoice.grand_total:.2f}"],
            ["", "Paid Amount:", f"₹{invoice.paid_amount:.2f}"],
            ["", "Balance Due:", f"₹{invoice.due_amount:.2f}"]
        ]
        totals_table = Table(totals_data, colWidths=[12.5*cm, 3.5*cm, 3*cm])
        totals_table.setStyle(TableStyle([
            ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
            ('FONTNAME', (1, -3), (2, -3), 'Helvetica-Bold'), # Grand Total
            ('FONTSIZE', (1, -3), (2, -3), 12),
            ('TEXTCOLOR', (1, -3), (2, -3), PRIMARY_RED),
            ('FONTNAME', (1, -1), (2, -1), 'Helvetica-Bold'), # Due Amount
            # Lines
            ('LINEBELOW', (1, -4), (-1, -4), 1, PRIMARY_RED), # Above Grand Total
            ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ]))
        elements.append(totals_table)

        # 5. Footer / Terms
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Terms & Conditions", section_title_style))
        terms_style = ParagraphStyle('Terms', parent=styles['Normal'], fontSize=8, textColor=colors.grey)
        elements.append(Paragraph("1. Goods once sold will not be taken back.<br/>"
                                  "2. Thank you for your business!", terms_style))

        # Build PDF
        doc.build(elements)

        # Get response
        pdf = buffer.getvalue()
        buffer.close()
        
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{invoice.invoice_number}.pdf"'
        response.write(pdf)
        
        return response

class InvoiceItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Mostly for historical lookup or reporting."""
    queryset = InvoiceItem.objects.all().order_by('-invoice__created_at')
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['invoice', 'product']

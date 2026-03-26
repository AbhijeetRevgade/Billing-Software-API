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
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

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
        Generate and download a professional PDF of the invoice.
        """
        invoice = self.get_object()
        
        # Create a file-like buffer to receive PDF data.
        buffer = io.BytesIO()

        # Create the PDF object, using the buffer as its "file."
        doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=30, leftMargin=30, topMargin=30, bottomMargin=18)
        elements = []

        # Get styles
        styles = getSampleStyleSheet()
        title_style = styles['Heading1']
        title_style.alignment = 1 # Center
        
        # Add Title
        elements.append(Paragraph("VIGHNAHARTA FATAKA - BILL", title_style))
        elements.append(Spacer(1, 12))

        # Add Metadata (Invoice #, Date, Customer)
        meta_data = [
            [f"Invoice No: {invoice.invoice_number}", f"Date: {invoice.created_at.strftime('%d-%m-%Y')}"],
            [f"Customer: {invoice.customer.name if invoice.customer else 'Guest'}", f"Phone: {invoice.customer.phone if invoice.customer else 'N/A'}"],
            [f"Payment Status: {invoice.payment_status}", f"Method: {invoice.payment_method}"]
        ]
        meta_table = Table(meta_data, colWidths=[250, 250])
        meta_table.setStyle(TableStyle([
            ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
            ('FONTSIZE', (0,0), (-1,-1), 10),
            ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ]))
        elements.append(meta_table)
        elements.append(Spacer(1, 20))

        # Add Items Table
        item_header = ["#", "Product", "SKU", "Qty", "Rate", "Total"]
        item_data = [item_header]
        
        for idx, item in enumerate(invoice.items.all(), 1):
            item_data.append([
                str(idx),
                item.product_name_snapshot,
                item.sku_snapshot,
                f"{item.quantity} {item.get_unit_display()}",
                f"{item.unit_price:.2f}",
                f"{item.total_price:.2f}"
            ])

        # Add Totals Row
        item_data.append(["", "", "", "", "Sub-Total:", f"{invoice.sub_total:.2f}"])
        item_data.append(["", "", "", "", "Tax:", f"{invoice.tax_amount:.2f}"])
        item_data.append(["", "", "", "", "Discount:", f"-{invoice.discount_amount:.2f}"])
        item_data.append(["", "", "", "", "GRAND TOTAL:", f"{invoice.grand_total:.2f}"])
        item_data.append(["", "", "", "", "Paid Amount:", f"{invoice.paid_amount:.2f}"])
        item_data.append(["", "", "", "", "DUE AMOUNT:", f"{invoice.due_amount:.2f}"])

        # Style the items table
        items_table = Table(item_data, colWidths=[30, 180, 80, 40, 80, 90])
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -7), 1, colors.black),
            ('LINEBELOW', (4, -6), (-1, -1), 1, colors.black),
            ('FONTNAME', (4, -3), (5, -3), 'Helvetica-Bold'), # Grand Total bold
            ('TEXTCOLOR', (4, -3), (5, -3), colors.darkred),
            ('ALIGN', (4, -6), (5, -1), 'RIGHT'),
        ]))
        
        elements.append(items_table)
        elements.append(Spacer(1, 30))
        elements.append(Paragraph("Thank you for your visit!", styles['Normal']))

        # Build the PDF
        doc.build(elements)

        # Get the value of the BytesIO buffer and write it to the response.
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

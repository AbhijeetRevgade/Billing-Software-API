from rest_framework import viewsets, permissions, status
from rest_framework.response import Response
from .models import Invoice, InvoiceItem
from .serializers import InvoiceSerializer, InvoiceItemSerializer
from django.db import transaction

class InvoiceViewSet(viewsets.ModelViewSet):
    queryset = Invoice.objects.all().order_by('-created_at')
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Allow filtering and searching
    filterset_fields = ['payment_status', 'payment_method', 'customer']
    search_fields = ['invoice_number', 'customer__name', 'customer__phone']

    def perform_create(self, serializer):
        # Attach the currently authenticated user to the invoice
        serializer.save(created_by=self.request.user)

    @transaction.atomic
    def update(self, request, *args, **kwargs):
        """Custom update logic if needed (e.g., partial refund or extra payment)."""
        return super().update(request, *args, **kwargs)

    @transaction.atomic
    def partial_update(self, request, *args, **kwargs):
        """Updating invoice payment status or notes."""
        return super().partial_update(request, *args, **kwargs)

class InvoiceItemViewSet(viewsets.ReadOnlyModelViewSet):
    """Mostly for historical lookup or reporting."""
    queryset = InvoiceItem.objects.all().order_by('-invoice__created_at')
    serializer_class = InvoiceItemSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['invoice', 'product']

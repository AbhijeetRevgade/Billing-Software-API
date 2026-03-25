from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import InvoiceViewSet, InvoiceItemViewSet

router = DefaultRouter()
router.register('invoices', InvoiceViewSet, basename='invoice')
router.register('items', InvoiceItemViewSet, basename='invoice_item')

urlpatterns = [
    path('', include(router.urls)),
]

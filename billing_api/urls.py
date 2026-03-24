from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # App URLs
    path('api/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/core/', include('core.urls')),
]

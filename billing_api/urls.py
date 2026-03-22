from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # App URLs
    path('api/accounts/', include('accounts.urls')),
    path('api/products/', include('products.urls')),
    path('api/billing/', include('billing.urls')),
    path('api/customers/', include('customers.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/core/', include('core.urls')),
]

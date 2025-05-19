from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect

urlpatterns = [
    path('admin/', admin.site.urls),
    path('dashboard/', include('shop.urls')),  # Admin ERP dashboard
    path('', include('shop.customer_urls')),   # Customer-facing website
    
    # Redirect /login/ to the customer login page to work with LOGIN_URL setting
    path('login/', lambda request: redirect('customer:login')),
    path('retail/', include('online_retail_dash.urls')),  # Now routes like /retail/online/
    path('payroll/', include('online_payroll.urls')),
    path('payroll/', include('core_payroll.urls')), 
    path('crm/', include('CRM.urls')), 
    path('hrm/', include('HRM.urls')),
    path('hrm_dash/', include('hrm_dash.urls')),
    path('ps/', include('PS.urls')),  # Add this line for the PS app
    path('api/', include('PS_API.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

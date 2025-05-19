"""
URL configuration for erp_project project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('retail/', include('online_retail_dash.urls')),
    path('payroll/', include('online_payroll.urls')),
    path('payroll/', include('core_payroll.urls')),
    path('crm/', include('CRM.urls')), 
    path('hrm/', include('HRM.urls')), 
    path('hrm_dash/', include('hrm_dash.urls')), 
    path('ps/', include('PS.urls')),
    path('api/', include('PS_API.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

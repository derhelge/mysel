# config/urls.py
from django.contrib import admin
from django.urls import path, include
from apps.core.views import CustomLogoutView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/logout/', CustomLogoutView.as_view(), name='account_logout'),
    path('accounts/', include('allauth.urls')),
    path('', include('apps.core.urls')),
    path('guests/', include('apps.guests.urls')),
    path('eduroam/', include('apps.eduroam.urls')),
    path('events/', include('apps.events.urls')),
    path('emaildevice/', include('apps.emaildevice.urls')),
    path('iotdevices/', include('apps.iotdevices.urls')),
    path('fwconfig/', include('apps.fwconfig.urls')),
]
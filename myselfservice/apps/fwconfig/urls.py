from django.urls import path
from . import views

app_name = 'fwconfig'

urlpatterns = [
    path('', views.FwConfigListView.as_view(), name='list'),
    path('<int:pk>/toggle/', views.FwConfigToggleView.as_view(), name='toggle'),
    path('api/<int:pk>/status/', views.FwConfigStatusAPIView.as_view(), name='api_status'),
]
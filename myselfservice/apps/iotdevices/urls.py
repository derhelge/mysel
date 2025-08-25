from django.urls import path
from . import views

app_name = 'iotdevices'

urlpatterns = [
    path('', views.IotDeviceList.as_view(), name='list'),
    path('create/', views.IotDeviceCreate.as_view(), name='create'),
    path('<int:pk>/', views.IotDeviceDetail.as_view(), name='detail'),
    path('<int:pk>/update/', views.IotDeviceUpdate.as_view(), name='update'),
    path('<int:pk>/delete/', views.IotDeviceDelete.as_view(), name='delete'),
]
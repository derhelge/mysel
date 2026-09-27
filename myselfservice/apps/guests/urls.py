from django.urls import path
from . import views

app_name = 'guests'

urlpatterns = [
    path('', views.GuestAccountListView.as_view(), name='list'),
    path('create/', views.GuestAccountCreateView.as_view(), name='create'),
    path('applicate/', views.GuestAccountApplicateView.as_view(), name='applicate'),
    path('<int:pk>/', views.GuestAccountDetailView.as_view(), name='detail'),
    path('<int:pk>/approve/', views.GuestAccountApproveView.as_view(), name='approve'),
    path('<int:pk>/update/', views.GuestAccountUpdateView.as_view(), name='update'),
    path('<int:pk>/delete/', views.GuestAccountDeleteView.as_view(), name='delete'),
]
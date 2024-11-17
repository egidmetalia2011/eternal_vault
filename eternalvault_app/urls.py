from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('upload/', views.upload_file_view, name='upload_file'),
    path('download/<int:secure_data_id>', views.download_file_view, name='download_file'),
]
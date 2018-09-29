from django.urls import path, re_path
from . import views


app_name = 'vnc'
urlpatterns = [
    path('vnc/', views.run_vnc, name='console'),
]
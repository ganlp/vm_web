from django.urls import path, re_path
from . import views


app_name = 'user'
urlpatterns = [
    #path('login/', views.LoginView.as_view(), name='login'),
    path('login/', views.Site().login, name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
]
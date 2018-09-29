from django.urls import path, re_path
from . import views


app_name = 'vm'
urlpatterns = [
    path('', views.Index.as_view(), name='index'),
    path('userlog/', views.UserLogDisplay.as_view(), name='userlog'),
    path('create/', views.Create.as_view(), name='create'),
    path('index/vm_detail-<int:pk>', views.KvmDetial.as_view(), name='detail'),
    path('autostart/', views.AutoStartList.as_view(), name='autostart'),
]
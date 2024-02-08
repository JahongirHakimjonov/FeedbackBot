from django.urls import path
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('admin/logout/', auth_views.LogoutView.as_view(), name='logout'),
]

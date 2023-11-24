from django.urls import path, include
from . import views

urlpatterns = [
    path('user_register/', views.user_register, name="user-register"),
    path('', views.user_login, name="user-login"),
    path('logout/', views.logout_view, name='logout'),

]

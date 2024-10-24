'''URLs for Registration'''

# drive/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('accounts/login/', views.login_view, name='login'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('accounts/signup/', views.signup_view, name='signup'),
    path('', views.home_view, name='home'),  # Example for home redirection
]
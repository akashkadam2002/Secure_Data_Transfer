from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('encoding/', views.encode_image, name='encode-img'),
    path('decoding/', views.decode_image, name='decode-img'),
    path('success/', views.success, name='success'),
    path('logout/', views.logout_view, name='logout'),
    path('login_register/', views.login_register, name='login-register'),
    path('signin/', views.loginUser, name='sign-in'),
    path('signup/', views.registerUser, name='sign-up'),
    path('landing/', views.userLanding, name='landing'),
      # URL for OTP verification
]



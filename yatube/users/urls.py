from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users import views

app_name = 'users'

urlpatterns = [
    path('signup/', views.SignUp.as_view(), name='signup'),
    path(
        'logged_out/',
        LogoutView.as_view(template_name='users/logged_out.html'),
        name='logged_out'
    ),
    path(
        'login/',
        LoginView.as_view(template_name='users/login.html'),
        name='login'
    )
]

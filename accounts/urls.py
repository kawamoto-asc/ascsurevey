from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path
from accounts import views

urlpatterns = [
    path('login/', LoginView.as_view(
        redirect_authenticated_user=True,
        template_name='accounts/login.html'
    ), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('password_change', views.PasswordChange.as_view(), name='password_change'),
    path('password_change_done', views.PasswordChangeDone.as_view(), name='password_change_done'),
]

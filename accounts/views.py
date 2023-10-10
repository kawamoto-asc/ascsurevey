from django.shortcuts import render
from django.contrib.auth.views import PasswordChangeView, PasswordChangeDoneView
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import MyPasswordChangeForm
# from django.urls import reverse_lazy


# Create your views here.
class PasswordChange(LoginRequiredMixin, PasswordChangeView):
    """パスワード変更ビュー"""
    form_class = MyPasswordChangeForm
    # success_url = reverse_lazy('password_change_done')
    success_url = 'password_change_done'
    template_name = 'accounts/password_change.html'

class PasswordChangeDone(LoginRequiredMixin, PasswordChangeDoneView):
    """パスワード変更しました"""
    template_name = 'accounts/password_change_done.html'
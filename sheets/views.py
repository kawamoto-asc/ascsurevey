from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, FormView
from .models import Sheets

# Create your views here.
# ユーザーマスタメンテナンス 一覧
class SheetsListView(LoginRequiredMixin, ListView):
    template_name = 'sheets/sheet_list.html'
    model = Sheets

from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView

from sheets.models import Items
# 集約一覧
class SummarizeListView(LoginRequiredMixin, ListView):
    template_name = 'summarize/summarize_list.html'
    model = Items

    def get_queryset(self):

        return Items.objects.none()
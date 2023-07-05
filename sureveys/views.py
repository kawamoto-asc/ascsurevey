from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView
from sureveys.models import Information, CustomUser

# トップ画面
@login_required
def top(request):
    # 降順で10件
    informations = Information.objects.order_by('-created_at')[:10]
    # 作成日が7日以内ならNEWを表示
    dsp_new_day = timezone.now() - timedelta(days=7)

    context = {"informations": informations,
               "dsp_new_day": dsp_new_day}
    return render(request, "sureveys/top.html", context)

# ユーザーマスタメンテナンス
class CUsersListView(LoginRequiredMixin, ListView):
    template_name = 'sureveys/customuser_list.html'
    model = CustomUser
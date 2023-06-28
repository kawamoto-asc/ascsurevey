from django.contrib.auth.decorators import login_required
from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from sureveys.models import Information

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
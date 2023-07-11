from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from datetime import datetime, timedelta
from django.shortcuts import render
from django.utils import timezone
from django.views.generic import ListView
from sureveys.models import *
from sureveys.forms import CustomUserQueryForm

# トップ画面
@login_required
def top(request):
    # インフォメーション情報 降順で10件
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
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        query_form = CustomUserQueryForm()  # 検索フォーム

        # 年度リスト作成
        nendo_user = CustomUser.objects.values_list('nendo')
        nendo_ujf = Ujf.objects.filter(key1=1, key2='1').values_list('naiyou4')
        nendo_list = sorted(nendo_user.union(nendo_ujf), key=lambda obj:obj, reverse=True)  # 降順
        nendolst = []
        for i in range(len(nendo_list)):
            nendolst.append((nendo_list[i][0], nendo_list[i][0]))

        query_form.fields['nendo'].choices = nendolst

        first_nendo = nendo_list[0][0]    # 年度リストの先頭値

        # 部署リスト
        blist = Busyo.objects.filter(nendo=first_nendo).values_list('bu_code', 'bu_name').order_by('bu_code')
        query_form.fields['busyo'].choices = blist

        # 勤務地リスト
        llist = Location.objects.filter(nendo=first_nendo).values_list('location_code', 'location_name').order_by('location_code')
        query_form.fields['location'].choices = llist

        # 役職リスト
        plist = Post.objects.filter(nendo=first_nendo).values_list('post_code', 'post_name').order_by('post_code')
        query_form.fields['post'].choices = plist

        context['query_form'] = query_form

        return context

def getCustomerPostList(request):
        pnendo = request.POST.get('nendo')

        # 役職リスト作成
        post_list = Post.objects.filter(nendo=pnendo).values_list('post_code', 'post_name').order_by('post_code')

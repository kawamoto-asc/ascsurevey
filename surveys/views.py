from datetime import datetime, timedelta

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, FormView

from sheets.models import Sheets, Items
from surveys.forms import Edit2Form
from surveys.models import Information, Status

# トップ画面
@login_required
def top(request):
    # インフォメーション情報 降順で10件
    informations = Information.objects.order_by('-created_at')[:10]
    # 作成日が7日以内ならNEWを表示
    dsp_new_day = timezone.now() - timedelta(days=7)

    context = {"informations": informations,
               "dsp_new_day": dsp_new_day}
    return render(request, "surveys/top.html", context)

# アンケート入力対象一覧
class InputListView(LoginRequiredMixin, ListView):
    template_name = 'surveys/input_list.html'
    model = Status

    def get_queryset(self):
        sheet_name = self.kwargs['pshname']

        #queryset = Sheets.objects.filter(sheet_name=sheet_id).order_by('-nendo')

        sql = """
            select sh.id, sh.nendo,
                coalesce(st.status, 0) as status,
                case when sc.itemcount is null or sc.itemcount = 0 then '未登録'
                    else to_char(sc.itemcount, 'FM999') || '件' end as entrycount,
                sh.created_at, sh.updated_at
            from surveys_sheet sh
            left outer join (
                select nendo, user_id, sheet_id, status
                from surveys_status
            ) st on (sh.nendo = st.nendo and sh.id = st.sheet_id)
            left outer join (
                select nendo, user_id, sheet_id, count(*) as itemcount
                from surveys_score
                group by nendo, user_id, sheet_id
            ) sc on (st.nendo = sc.nendo and st.user_id = sc.user_id and st.sheet_id = sc.sheet_id)
            where sheet_name = %(shname)s and (st.user_id is null or st.user_id = %(userid)s)
            order by nendo desc
        """
        params = {"shname": sheet_name, "userid": self.request.user.username}

        queryset = Sheets.objects.raw(sql, params)

        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # シート情報を渡す
        qsheet = Sheets.objects.filter(sheet_name=self.kwargs['pshname'],).order_by('-nendo')
        context['qsheet'] = qsheet[0]

        return context

EFORM_NUM = 1       # フォーム数
EFORM_VALUES = {}   # 前回のPOST値

# 一問多答形式入力画面
class InputEdit2View(LoginRequiredMixin, FormView):
    template_name = 'surveys/input_edit2.html'
    EditFormSet = forms.formset_factory(
        form = Edit2Form,
        extra = 1,
        max_num = 50,
    )
    form_class = EditFormSet

    # success_urlへ動的にパラメータを渡すオーバーライド
    def get_success_url(self):
        sht = Sheets.objects.get(id=self.kwargs['psheetid'])

        url = reverse_lazy(
            'input-list',
             kwargs={'pshname': sht.sheet_name}
            )
        return url


    def get_context_data(self, **kwargs):
        print('get_context_data')
        context = super().get_context_data(**kwargs)

        # シート情報を渡す
        sheet_id = self.kwargs['psheetid']
        qsheet = Sheets.objects.get(id=sheet_id,)
        qitem = Items.objects.filter(nendo=self.kwargs['pnendo'], sheet_id=sheet_id)
        context['qsheet'] = qsheet
        context['qitem'] = qitem[0]

        return context

    def get_form_kwargs(self, *args, **kwargs):
        print("get_form_kwargs")
        kwargs = super().get_form_kwargs()

        if EFORM_VALUES:
            kwargs['data'] = EFORM_VALUES

        return kwargs


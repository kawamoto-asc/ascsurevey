from datetime import datetime, timedelta

from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, FormView

from sheets.models import Sheets, Items
from surveys.forms import Edit2Form
from surveys.models import CustomUser, Information, Status, Score

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
                st.created_at, st.updated_at
            from surveys_sheet sh
            left outer join (
                select nendo, user_id, login_id, sheet_id, status, created_at, updated_at
                from surveys_status
                where login_id = %(userid)s
            ) st on (sh.nendo = st.nendo and sh.id = st.sheet_id)
            left outer join (
                select nendo, user_id, login_id, sheet_id, count(*) as itemcount
                from surveys_score
                where login_id = %(userid)s
                group by nendo, user_id, login_id, sheet_id
            ) sc on (st.nendo = sc.nendo and st.user_id = sc.user_id and st.sheet_id = sc.sheet_id)
            where sheet_name = %(shname)s
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
        extra = 0,
        max_num = 50,
    )
    form_class = EditFormSet

    # 一覧、シート（Session）情報をクリアするフラグ
    ini_flg = True

    # success_urlへ動的にパラメータを渡すオーバーライド
    # 正常終了でも画面遷移なし
    def get_success_url(self):
        url = reverse_lazy(
            'input-edit2',
             kwargs={'pnendo': self.kwargs['pnendo'],
                     'psheetid': self.kwargs['psheetid'],
                     'pflg': 'False',}
            )
        return url

    def get_context_data(self, **kwargs):
        global EFORM_NUM
        global EFORM_VALUES

        # 初期化フラグをパラメータから更新
        if self.kwargs['pflg'] == 'False':
            self.ini_flg = False
        else:
            self.ini_flg = True

        # 初期化フラグからformset,formデータを削除
        if self.ini_flg:
            EFORM_NUM = 0
            EFORM_VALUES = {}

        context = super().get_context_data(**kwargs)

        # 更新完了メッセージ
        if self.request.method == 'GET':
            if 'update' in self.request.GET:
                context['message'] = '更新しました'

        # シート情報を渡す
        sheet_id = self.kwargs['psheetid']
        qsheet = Sheets.objects.get(id=sheet_id,)
        qitem = Items.objects.filter(nendo=self.kwargs['pnendo'], sheet_id=sheet_id)
        context['qsheet'] = qsheet
        context['qitem'] = qitem[0]

        # フォームデータがあれば
        if EFORM_VALUES:
            context['data'] = EFORM_VALUES
        # なければ 初回表示で、パラメータからformset作成
        else:
            ilst = Score.objects.filter(
                nendo=self.kwargs['pnendo'], sheet_id=self.kwargs['psheetid'], login_id=self.request.user.username
            ).order_by('dsp_no')
            EFORM_NUM = len(ilst)
            initial_data = []
            if EFORM_NUM == 0:
                EFORM_NUM = 1
                initial_data.append({'content': '',})
            else:
                for dat in ilst:
                    initial_data.append({'content': dat.inp_data,})
            
            formset = self.form_class(initial=initial_data)
            context['form'] = formset

        return context

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()

        if EFORM_VALUES:
            kwargs['data'] = EFORM_VALUES

        return kwargs

    def post(self, request, *args, **kwargs):
        global EFORM_NUM
        global EFORM_VALUES

        # 一度Submitしたので、初期化フラグをOFF
        self.kwargs['pflg'] = 'False'

        # リストデータ表示用保存
        EFORM_VALUES = request.POST.copy()

        # 追加ボタン押下なら
        if 'btn_add' in request.POST:
            EFORM_NUM += 1   # formsetのフォーム数インクリメント
            EFORM_VALUES['form-TOTAL_FORMS'] = EFORM_NUM

        # 削除ボタン押下なら
        if 'btn_del' in request.POST:
            # １件だけは消さない
            if EFORM_NUM > 1:
                to_cnt = 0
                del_cnt = 0
                newdic = {}
                delkeyist = []
                # EFORM_VALUES form Noを削除行をのけて作り直し
                for i in range(EFORM_NUM):
                    frm_ck_delete = 'form-' + str(i) + '-ck_delete'
                    # チェックされていなければ
                    if frm_ck_delete not in EFORM_VALUES:
                        to_str = 'form-' + str(to_cnt) + '-content'
                        newdic[to_str] = EFORM_VALUES[frm_ck_delete.replace('ck_delete', 'content')]
                        to_cnt += 1
                    else :
                        delkeyist.append(frm_ck_delete)
                        del_cnt += 1
                # 項目No.での並べ変えはしない
                for key, val in newdic.items():
                    EFORM_VALUES[key] = val
                for keystr in delkeyist:
                    del EFORM_VALUES[keystr]
                EFORM_NUM -= del_cnt
                EFORM_VALUES['form-TOTAL_FORMS'] = EFORM_NUM

        # 更新ボタン押下なら
        if 'btn_update' in request.POST:
            form = self.form_class(request.POST)
            # 入力チェック
            self.datCheck_update(form)

            errcnt = 0
            for err in form.errors:
                if len(err):
                    errcnt += 1
            if errcnt > 0:
                return self.form_invalid(form)
            
            # データ保存
            self.dataEntry()
            #self.message = "更新しました"
            url = reverse_lazy(
                'input-edit2',
                kwargs={'pnendo': self.kwargs['pnendo'],
                        'psheetid': self.kwargs['psheetid'],
                        'pflg': 'False',}
                )
            url += "?update"
            return redirect(url)

        return super().post(request, args, kwargs)

    # 入力チェック処理
    def datCheck_update(self, form):
        global EFORM_NUM
        global EFORM_VALUES

        for i in range(EFORM_NUM):
            if not EFORM_VALUES['form-' + str(i) + '-content']:
                form.forms[i].errors[''] = '内容の入力がありません(' + str(i + 1) + '行目)'

    # データ保存処理
    def dataEntry(self):
        global EFORM_NUM
        global EFORM_VALUES

        with transaction.atomic():
            nendo = self.kwargs['pnendo']
            sheet_id = self.kwargs['psheetid']
            login_id = self.request.user.username
            if CustomUser.objects.filter(nendo=nendo, user_id=login_id).exists():
                user_id = CustomUser.objects.filter(nendo=nendo, user_id=login_id)[0]
            else:
                user_id = CustomUser.objects.filter(user_id=login_id).order_by('-nenod')[0]

            # 状態管理データの保存
            if Status.objects.filter(nendo=nendo, login_id=login_id, sheet_id=sheet_id).exists():
                # 更新
                statusdat = Status.objects.get(nendo=nendo, login_id=login_id, sheet_id=sheet_id)
                statusdat.update_by = login_id
                statusdat.save()
            else :
                # 新規作成
                statusdat = Status()
                statusdat.nendo = nendo
                statusdat.user_id = user_id
                statusdat.login_id = login_id
                statusdat.sheet_id = Sheets.objects.get(id=sheet_id)
                statusdat.status = 0
                statusdat.created_by = login_id
                statusdat.update_by = login_id
                statusdat.save()

            # 項目データの保存 Delete&Insert
            if Score.objects.filter(nendo=nendo, login_id=login_id, sheet_id=sheet_id).exists():
                Score.objects.filter(nendo=nendo, login_id=login_id, sheet_id=sheet_id).delete()
            for i in range(EFORM_NUM):
                scoredat = Score()
                scoredat.nendo = nendo
                scoredat.user_id = user_id
                scoredat.login_id = login_id
                scoredat.sheet_id = Sheets.objects.get(id=sheet_id)
                scoredat.item_id = Items.objects.filter(nendo=nendo, sheet_id=sheet_id)[0]
                scoredat.dsp_no = i + 1
                scoredat.inp_data = EFORM_VALUES['form-' + str(i) + '-content']
                scoredat.created_by = login_id
                scoredat.update_by = login_id
                scoredat.save()

        
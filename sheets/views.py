from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView, CreateView
from surveys.models import Ujf
from sheets.models import Sheets
from sheets.forms import SheetQueryForm, SheetForm, ItemForm

FORM_NUM = 1        # フォーム数
FORM_VALUES = {}    # 前回のform_setのPSOT値
SHEET_VALUES = {}   # シート情報

# 検索条件(セッション値）から（検索クエリを発行）該当リストを返す
def makeSheetList(request):
    form_value = request.session['form_value']
    nendo = form_value[0]

    # 検索条件
    exact_nendo = Q()
    if len(nendo) != 0 and nendo[0]:
        exact_nendo = Q(nendo__exact=nendo)

    return (Sheets.objects.select_related()
            .filter(exact_nendo)
            .order_by('dsp_no')
        )

# シートマスタメンテナンス 一覧
class SheetsListView(LoginRequiredMixin, ListView):
    template_name = 'sheets/sheet_list.html'
    model = Sheets

    # 検索条件をクリアするためのフラグ
    ini_flg = True

    def post(self, request, *args, **kwargs):
        # 一度検索したので、初期化フラグをOFF
        self.ini_flg = False

        # フォームの内容をセッション情報へ
        form_value = [
            self.request.POST.get('nendo', None),
        ]
        request.session['form_value'] = form_value

        # 検索時にページネーションに関連したエラーを防ぐ(ページネーションしないけど一応)
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 年度リスト作成
        nendo_sheet = Sheets.objects.values_list('nendo')
        nendo_ujf = Ujf.objects.filter(key1=1, key2='1').values_list('naiyou4')
        nendo_list = sorted(nendo_sheet.union(nendo_ujf), key=lambda obj:obj, reverse=True)  # 降順
        nendolst = []
        for i in range(len(nendo_list)):
            nendolst.append((nendo_list[i][0], nendo_list[i][0]))

        nendo = nendo_list[0][0]    # 年度リストの先頭値
        # sessionに値がある場合
        if 'form_value' in self.request.session:
            # 初期化フラグがTrueなら
            if self.ini_flg:
                # セッションをクリアする
                del self.request.session['form_value']
            else:
                # 初期化フラグがFalseなら、セッションの値をセットする
                form_value = self.request.session['form_value']
                nendo = form_value[0]

        default_data = {'nendo': nendo,}
        query_form = SheetQueryForm(initial=default_data)  # 検索フォーム

        # リスト
        query_form.fields['nendo'].choices = nendolst

        context['query_form'] = query_form
        context['ini_flg'] = self.ini_flg

        return context

    def get_queryset(self):
        # 初期化フラグをURLパラメータから取得
        flg_wrk = self.request.GET.get('ini_flg')
        # パラメータにあったら
        if flg_wrk:
            # 上書き
            if flg_wrk == 'False':
                self.ini_flg = False
            else:
                self.ini_flg = True

        # sessionに値があって、検索ボタン押下なら、セッション値でクエリ発行する。
        if not self.ini_flg and 'form_value' in self.request.session:
            return makeSheetList(self.request)
        else:
            # 何も返さない
            return Sheets.objects.none()

# 新規登録
class SheetsCreateView(LoginRequiredMixin, FormView):
    template_name = 'sheets/sheet_new.html'
    form_class = SheetForm
    ItemFormSet = forms.formset_factory(
        form = ItemForm,
        extra=1,
        max_num = 50,
    )
    form_class2 = ItemFormSet

    # 一覧、シート（Session）情報をクリアするフラグ
    ini_flg = True

    # success_urlは動的にパラメータを渡さないといけないのでオーバーライド
    def get_success_url(self):
        url = reverse_lazy(
            'sheet-new',
             kwargs={'pnendo': self.kwargs['pnendo'],
                     'pflg': 'False',
                     }
            )
        return url

    # formにパラメータを渡す為のオーバーライド
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()

        # パラメータ年度、編集モード(新規）をフォームへ渡す
        pnendo = self.kwargs['pnendo']
        mod = "new"
        kwargs.update({'pnendo': pnendo, 'mod': mod})

        return kwargs

    # ２個目のフォームを返す為のオーバーライド
    def get_context_data(self, **kwargs):
        global FORM_NUM
        global FORM_VALUES
        global SHEET_VALUES

        # 初期化フラグをパラメータから更新
        if self.kwargs['pflg'] == 'False':
            self.ini_flg = False
        else:
            self.ini_flg = True

        # 初期化フラグからformset,formデータを削除
        if self.ini_flg:
            FORM_NUM = 1
            FORM_VALUES = {}
            SHEET_VALUES = {}

        # ２個目のフォームを渡す
        context = super().get_context_data(**kwargs)

        # フォームデータがあれば
        if FORM_VALUES:
            context.update({
                'form': self.form_class(SHEET_VALUES),
                'formset': self.form_class2(FORM_VALUES),
                })
        # なければ 新規にformset作成
        else:
            context.update({
                'formset': self.form_class2(self.request.GET or None),
                })

        return context

    def post(self, request, *args, **kwargs):
        global FORM_NUM
        global FORM_VALUES
        global SHEET_VALUES

        # 一度Submitしたので、初期化フラグをOFF
        self.ini_flg = False

        # シートデータ項目データ表示用保存
        fsetwork = request.POST.copy()
        fsetdic = {}
        shtdic = {}
        for key, val in fsetwork.items():
            if key.startswith('form-'):
                fsetdic[key] = val
            else:
                shtdic[key] = val
        # 別フォームなので、シート情報と項目情報を分けて保持
        FORM_VALUES = fsetdic
        SHEET_VALUES = shtdic

        # 追加ボタン押下なら
        print('before')
        if 'btn_add' in request.POST:
            FORM_NUM += 1   # formsetのフォーム数インクリメント
            FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM

        return super().post(request, args, kwargs)

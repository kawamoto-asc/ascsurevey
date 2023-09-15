from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, FormView, CreateView
from surveys.models import Ujf
from sheets.models import Sheets
from sheets.forms import SheetQueryForm, SheetForm, ItemForm

FORM_NUM = 1        # フォーム数
FORM_VALUES = {}    # 前回のPSOT値

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
    #success_url = '/sheets?ini_flg=False'

    # formにパラメータを渡す為のオーバーライド
    def get_form_kwargs(self, *args, **kwargs):
        print('get_form_kwargs')
        kwargs = super().get_form_kwargs()

        # パラメータ年度、編集モード(新規）をフォームへ渡す
        pnendo = self.kwargs['pnendo']
        mod = "new"
        kwargs.update({'pnendo': pnendo, 'mod': mod})

        # FORM_VALUESが空でない場合（入力中のフォームがある場合）、dataキーにFORM_VALUESを設定
        if FORM_VALUES:
            kwargs['data'] = FORM_VALUES
            print(FORM_VALUES)

        return kwargs

    # ２個目のフォームを返す為のオーバーライド
    '''
    def get_context_data(self, **kwargs):
        print('get_context_data')
        # ２個目のフォームを渡す
        context = super().get_context_data(**kwargs)
        context.update({
            #'form': self.form_class(self.request.GET or None),
            'formset': self.form_class2(self.request.GET or None),
            })

        return context'''

    def post(self, request, *args, **kwargs):
        print('post')
        global FORM_NUM
        global FORM_VALUES

        # 追加ボタン押下なら
        if 'btn_add' in request.POST:
            FORM_NUM += 1   # フォーム数インクリメント
            FORM_VALUES = request.POST.copy()   # リクエストの内容コピー
            print(FORM_VALUES)
            FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM
            print(FORM_VALUES)

        return super().post(request, args, kwargs)

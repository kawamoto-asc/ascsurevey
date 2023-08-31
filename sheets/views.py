from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.views.generic import ListView, FormView
from sureveys.models import Ujf
from sheets.models import Sheets
from sheets.forms import SheetQueryForm, SheetForm

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
    success_url = '/sheets?ini_flg=False'

    # formにパラメータを渡す為のオーバーライド
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(SheetsCreateView, self).get_form_kwargs()

        # パラメータ年度、編集モード(新規）をフォームへ渡す
        pnendo = self.kwargs['pnendo']
        mod = "new"
        kwargs.update({'pnendo': pnendo, 'mod': mod})

        return kwargs

'''
    def form_valid(self, form):
        data = form.cleaned_data

        # ユーザマスタに登録
        cuser = CustomUser()
        cuser.nendo = data['nendo']
        cuser.user_id = data['user_id']
        cuser.first_name = data['first_name']
        cuser.last_name = data['last_name']
        cuser.email = data['email']
        cuser.is_staff = data['is_staff']
        cuser.post_id = Post.objects.get(nendo=data['nendo'], post_code=data['post'])
        cuser.busyo_id = Busyo.objects.get(nendo=data['nendo'], bu_code=data['busyo'])
        cuser.location_id = Location.objects.get(nendo=data['nendo'], location_code=data['location'])
        cuser.created_by = self.request.user.username

        cuser.save()

        # ログインマスタに登録があれば更新、なければ登録
        if User.objects.filter(username=cuser.user_id).exists():
            auser = User.objects.get(username=cuser.user_id)
            auser.first_name = cuser.first_name
            auser.last_name = cuser.last_name
            auser.email = cuser.email
            auser.is_staff = cuser.is_staff
            auser.save()
        else:
            new_user = User()
            new_user.username = cuser.user_id
            new_user.password = make_password(cuser.user_id)
            new_user.first_name = cuser.first_name
            new_user.last_name = cuser.last_name
            new_user.email = cuser.email
            new_user.is_staff = cuser.is_staff
            new_user.is_active = True
            new_user.is_superuser = False
            new_user.save()

        return super().form_valid(form)
'''
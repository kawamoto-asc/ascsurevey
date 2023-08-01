from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.generic import ListView, FormView
from customuser.forms import CustomUserQueryForm, CustomUserForm
from sureveys.models import Ujf, Busyo, Location, Post, CustomUser

# 部署リスト取得処理 FetchAPI用
# パラメータ：nendo 年度
def getBusyoList(request):
        pnendo = request.POST.get('nendo')
        plistid = request.POST.get('list_id')

        # リスト作成
        busyo_list = llist = [('', '')] + list(Busyo.objects.filter(nendo=pnendo).values_list('bu_code', 'bu_name').order_by('bu_code'))
        bulst = []
        for pdat in busyo_list:
             bulst.append(list(pdat))

        data = {
             'list_id': plistid,
             'rlist': bulst,
        }
        return JsonResponse(data)

# 勤務地リスト取得処理 FetchAPI用
# パラメータ：nendo 年度
def getLocationList(request):
        pnendo = request.POST.get('nendo')
        plistid = request.POST.get('list_id')

        # リスト作成
        location_list = llist = [('', '')] + list(Location.objects.filter(nendo=pnendo).values_list('location_code', 'location_name').order_by('location_code'))
        loclst = []
        for pdat in location_list:
             loclst.append(list(pdat))

        data = {
             'list_id': plistid,
             'rlist': loclst,
        }
        return JsonResponse(data)

# 役職リスト取得処理 FetchAPI用
# パラメータ：nendo 年度
def getPostList(request):
        pnendo = request.POST.get('nendo')
        plistid = request.POST.get('list_id')

        # リスト作成
        post_list = llist = [('', '')] + list(Post.objects.filter(nendo=pnendo).values_list('post_code', 'post_name').order_by('post_code'))
        pstlst = []
        for pdat in post_list:
             pstlst.append(list(pdat))

        data = {
             'list_id': plistid,
             'rlist': pstlst,
        }
        return JsonResponse(data)

# ユーザーマスタメンテナンス 一覧
class CUsersListView(LoginRequiredMixin, ListView):
    template_name = 'customuser/customuser_list.html'
    model = CustomUser

    # 検索条件をクリアするためのフラグ
    ini_flg = True

    def post(self, request, *args, **kwargs):
        # 一度検索したので、初期化フラグをOFF
        self.ini_flg = False

        # フォームの内容をセッション情報へ
        form_value = [
            self.request.POST.get('nendo', None),
            self.request.POST.get('busyo', None),
            self.request.POST.get('location', None),
            self.request.POST.get('post', None),
        ]
        request.session['form_value'] = form_value

        # 検索時にページネーションに関連したエラーを防ぐ(ページネーションしないけど一応)
        self.request.GET = self.request.GET.copy()
        self.request.GET.clear()
        return self.get(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # 年度リスト作成
        nendo_user = CustomUser.objects.values_list('nendo')
        nendo_ujf = Ujf.objects.filter(key1=1, key2='1').values_list('naiyou4')
        nendo_list = sorted(nendo_user.union(nendo_ujf), key=lambda obj:obj, reverse=True)  # 降順
        nendolst = []
        for i in range(len(nendo_list)):
            nendolst.append((nendo_list[i][0], nendo_list[i][0]))

        nendo = nendo_list[0][0]    # 年度リストの先頭値
        busyo = ''
        location = ''
        post = ''
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
                busyo = form_value[1]
                location = form_value[2]
                post = form_value[3]

        default_data = {'nendo': nendo,
                        'busyo': busyo,
                        'location': location,
                        'post': post,
                        }

        # 部署リスト作成
        blist = [('', '')] + list(Busyo.objects.filter(nendo=nendo).values_list('bu_code', 'bu_name').order_by('bu_code'))

        # 勤務地リスト作成
        llist = [('', '')] + list(Location.objects.filter(nendo=nendo).values_list('location_code', 'location_name').order_by('location_code'))

        # 役職リスト作成
        plist = [('', '')] + list(Post.objects.filter(nendo=nendo).values_list('post_code', 'post_name').order_by('post_code'))

        query_form = CustomUserQueryForm(initial=default_data)  # 検索フォーム

        # リスト
        query_form.fields['nendo'].choices = nendolst
        query_form.fields['busyo'].choices = blist
        query_form.fields['location'].choices = llist
        query_form.fields['post'].choices = plist

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
            form_value = self.request.session['form_value']
            nendo = form_value[0]
            busyo = form_value[1]
            location = form_value[2]
            post = form_value[3]

            # 検索条件
            exact_nendo = Q()
            exact_busyo = Q()
            exact_location = Q()
            exact_post = Q()
            if len(nendo) != 0 and nendo[0]:
                exact_nendo = Q(nendo__exact=nendo)
            if len(busyo) != 0 and busyo[0]:
                busyoid = Busyo.objects.filter(nendo=nendo, bu_code=busyo)[:1]
                exact_busyo = Q(busyo_id__exact=busyoid)
            if len(location) != 0 and location[0]:
                locationid = Location.objects.filter(nendo=nendo, location_code=location)[:1]
                exact_location = Q(location_id__exact=locationid)
            if len(post) != 0 and post[0]:
                postid = Post.objects.filter(nendo=nendo, post_code=post)[:1]
                exact_post = Q(post_id__exact=postid)

            return (CustomUser.objects.select_related()
                    .filter(exact_nendo & exact_busyo & exact_location & exact_post)
                    .order_by('busyo_id__bu_code', 'location_id__location_code', 'post_id__post_code', 'user_id')
                )
        else:
            # 何も返さない
            return CustomUser.objects.none()

# 新規登録
class CUsersCreateView(LoginRequiredMixin, FormView):
    template_name = 'customuser/customuser_new.html'
    form_class = CustomUserForm
    success_url = '/customusers?ini_flg=False'

    # formにパラメータを渡す為のオーバーライド
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(CUsersCreateView, self).get_form_kwargs()

        # パラメータ年度、編集モード(新規）をフォームへ渡す
        pnendo = self.kwargs['pnendo']
        mod = "new"
        kwargs.update({'pnendo': pnendo, 'mod': mod})

        return kwargs

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
            new_user.password = cuser.user_id
            new_user.first_name = cuser.first_name
            new_user.last_name = cuser.last_name
            new_user.email = cuser.email
            new_user.is_staff = cuser.is_staff
            new_user.is_active = True
            new_user.is_superuser = False
            new_user.save()

        return super().form_valid(form)

# 編集・削除
class CUsersEditView(LoginRequiredMixin, FormView):
    template_name = 'customuser/customuser_edit.html'
    form_class = CustomUserForm
    success_url = '/customusers?ini_flg=False'

    # formにパラメータを渡す為のオーバーライド
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super(CUsersEditView, self).get_form_kwargs()

        # パラメータ年度、編集モード(更新）、オブジェクト情報をフォームへ渡す
        pnendo = self.kwargs['pnendo']
        uid = self.kwargs['id']
        mod = "edit"
        uobj = CustomUser.objects.get(id=uid)

        kwargs.update({'pnendo': pnendo, 'mod': mod, 'uobj': uobj})

        return kwargs

    def form_valid(self, form):
        data = form.cleaned_data

        # 更新の時
        if "btn_update" in self.request.POST:
            # ユーザマスタに更新
            cuser = CustomUser.objects.get(nendo=data['nendo'], user_id=data['user_id'])
            cuser.first_name = data['first_name']
            cuser.last_name = data['last_name']
            cuser.email = data['email']
            cuser.is_staff = data['is_staff']
            cuser.post_id = Post.objects.get(nendo=data['nendo'], post_code=data['post'])
            cuser.busyo_id = Busyo.objects.get(nendo=data['nendo'], bu_code=data['busyo'])
            cuser.location_id = Location.objects.get(nendo=data['nendo'], location_code=data['location'])
            cuser.update_by = self.request.user.username

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
                new_user.password = cuser.user_id
                new_user.first_name = cuser.first_name
                new_user.last_name = cuser.last_name
                new_user.email = cuser.email
                new_user.is_staff = cuser.is_staff
                new_user.is_active = True
                new_user.is_superuser = False
                new_user.save()
        # 削除の時
        elif "btn_delete" in self.request.POST:
            cuser = CustomUser.objects.get(nendo=data['nendo'], user_id=data['user_id'])
            cuser.delete()

        return super().form_valid(form)

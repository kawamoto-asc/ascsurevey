from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import render
from django.views.generic import ListView
from customuser.forms import CustomUserQueryForm
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

# ユーザーマスタメンテナンス
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

        first_nendo = nendo_list[0][0]    # 年度リストの先頭値

        # 部署リスト作成
        blist = [('', '')] + list(Busyo.objects.filter(nendo=first_nendo).values_list('bu_code', 'bu_name').order_by('bu_code'))

        # 勤務地リスト作成
        llist = [('', '')] + list(Location.objects.filter(nendo=first_nendo).values_list('location_code', 'location_name').order_by('location_code'))

        # 役職リスト作成
        plist = [('', '')] + list(Post.objects.filter(nendo=first_nendo).values_list('post_code', 'post_name').order_by('post_code'))

        nendo = first_nendo
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
                exact_post = Q(post_id__exact=post)

            return (CustomUser.objects.select_related()
                    .filter(exact_nendo & exact_busyo & exact_location & exact_post)
                    .order_by('busyo_id__bu_code', 'location_id__location_code', 'post_id__post_code', 'user_id')
                )
        else:
            # 何も返さない
            return CustomUser.objects.none()
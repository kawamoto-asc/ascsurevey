from django.conf import settings
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, Max
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import ListView, FormView
from sheets.consts import INPUT_TYPE_CHOICES, FIELD_TYPE_CHOICES, INPUT_URL, AGGRE_URL
from sheets.models import Sheets, Items
from sheets.forms import SheetQueryForm, SheetForm, ItemForm
from surveys.models import Ujf, Menu
from pytz import timezone
import re
import openpyxl
import pandas as pd

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
        extra = 1,
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
            if self.request.method == 'GET':
                context.update({
                    'form': self.form_class(SHEET_VALUES),
                    'formset': self.form_class2(FORM_VALUES),
                    })
            else:
                context.update({
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
        if 'btn_add' in request.POST:
            FORM_NUM += 1   # formsetのフォーム数インクリメント
            FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM

        # 削除ボタン押下なら
        if 'btn_del' in request.POST:
            #cnt_frm = 0
            to_cnt = 0
            del_cnt = 0
            newdic = {}
            delkeyist = []
            # FORM_VALUES form Noを削除行をのけて作り直し
            for i in range(FORM_NUM):
                frm_ck_delete = 'form-' + str(i) + '-ck_delete'
                # チェックされていなければ
                if frm_ck_delete not in FORM_VALUES:
                    to_itemno_str = 'form-' + str(to_cnt) + '-item_no'
                    newdic[to_itemno_str] = FORM_VALUES[frm_ck_delete.replace('ck_delete', 'item_no')]
                    newdic[to_itemno_str.replace('item_no', 'content')] = FORM_VALUES[frm_ck_delete.replace('ck_delete', 'content')]
                    newdic[to_itemno_str.replace('item_no', 'input_type')] = FORM_VALUES[frm_ck_delete.replace('ck_delete', 'input_type')]
                    to_cnt += 1
                else :
                    delkeyist.append(frm_ck_delete)
                    del_cnt += 1
            # 項目No.での並べ変えはしない
            for key, val in newdic.items():
                FORM_VALUES[key] = val
            for keystr in delkeyist:
                del FORM_VALUES[keystr]
            FORM_NUM -= del_cnt
            FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM

        # 登録ボタン押下なら
        if 'btn_entry' in request.POST:
            form = self.form_class(request.POST)
            # 入力チェック
            self.datCheck_new(form, fsetwork)

            # エラーは全部シート部分に出力
            if form.non_field_errors():
                return self.form_invalid(form)
            
            # データ保存
            self.dataEntry(fsetwork)
            return redirect('/sheets?ini_flg=False')

        return super().post(request, args, kwargs)

    # 入力チェック処理
    def datCheck_new(self, form, frmdic):
        # 半角英数字と_@-.だけ入力可のチェック用
        reg = re.compile(r'^[A-Za-z0-9_@\-\.]+$')

        # シート部分のエラーチェック
        if not frmdic['sheet_name']:
            form.add_error(None, 'シート名を入力してください。')
        else:
            sheetname = frmdic['sheet_name']
            if reg.match(sheetname) is None:
                form.add_error(None, 'シート名は半角英数字か_-@で入力してください。')
            else:
                nen = frmdic['nendo']
                sheet = Sheets.objects.filter(
                        nendo = nen,
                        sheet_name = sheetname,
                ).exists()
                if sheet:
                    form.add_error(None, nen + 'の' + sheetname + 'は既に登録済みです。')

        if not frmdic['title']:
            form.add_error(None, 'アンケート名を入力してください。')

        # 一問多答形式の場合は項目数は1件のみ
        if frmdic['input_type'] == '2' and FORM_NUM > 1:
            form.add_error(None, '一問多答形式で登録出来る項目数は１件のみです。')

        # 項目リスト部分のエラーチェック
        if FORM_NUM <= 0:
            form.add_error(None, 'アンケート項目がありません。')
        list_ino = []
        for i in range(FORM_NUM):
            if not frmdic['form-' + str(i) + '-item_no']:
                form.add_error(None, '項目Noの入力がありません(' + str(i + 1) + '行目)')
            else:
                ino = frmdic['form-' + str(i) + '-item_no']
                if ino in list_ino:
                    form.add_error(None, '項目Noが重複しています(' + str(i + 1) + '行目)')
                else :
                    list_ino.append(ino)

            if not frmdic['form-' + str(i) + '-content']:
                form.add_error(None, '内容の入力がありません(' + str(i + 1) + '行目)')

    # データ保存処理
    def dataEntry(self, frmdic):
        with transaction.atomic():
            # シート情報を保存
            sheetdat = Sheets()
            sheetdat.nendo = frmdic['nendo']
            sheetdat.sheet_name = frmdic['sheet_name']
            sheetdat.title = frmdic['title']
            sheetdat.input_type = frmdic['input_type']
            # 表示順
            dno = 1
            if frmdic['dsp_no']:
                # 入力があればその数値
                dno = frmdic['dsp_no']
            else:
                # 入力がなくて登録レコードがあればMax＋1
                rno = Sheets.objects.all().count()
                if rno > 0:
                    nodic = Sheets.objects.all().aggregate(Max('dsp_no'))
                    dno = nodic['dsp_no__max'] + 1
            sheetdat.dsp_no = dno
            rstaff = False
            if 'req_staff' in frmdic:
                rstaff = True
            sheetdat.req_staff = rstaff

            sheetdat.created_by = self.request.user.username
            sheetdat.save()

            # 項目情報保存
            nendo = frmdic['nendo']
            sheetid = Sheets.objects.get(nendo=nendo, sheet_name=frmdic['sheet_name'])
            for i in range(FORM_NUM):
                itemdat = Items()
                itemdat.nendo = nendo
                itemdat.sheet_id = sheetid
                itemdat.item_no = frmdic['form-' + str(i) + '-item_no']
                itemdat.content = frmdic['form-' + str(i) + '-content']
                itemdat.input_type = frmdic['form-' + str(i) + '-input_type']
                itemdat.created_by = self.request.user.username
                itemdat.save()

            # メニューへの登録
            inpurl = INPUT_URL + frmdic['sheet_name']
            aggurl = AGGRE_URL + frmdic['sheet_name']

            # 入力画面のURLの登録がなければ
            imenu = Menu.objects.filter(
                        url = inpurl,
                ).exists()
            if not imenu:
                imenudat = Menu()
                imenudat.title = frmdic['title']
                imenudat.url = inpurl
                imenudat.kbn = 1
                imenudat.dsp_no = dno
                imenudat.req_staff = False
                imenudat.created_by = self.request.user.username
                imenudat.save()

            # 集計画面のURLの登録がなければ
            amenu = Menu.objects.filter(
                        url = aggurl,
                ).exists()
            if not amenu:
                amenudat = Menu()
                amenudat.title = frmdic['title'] + ' 集計'
                amenudat.url = aggurl
                amenudat.kbn = 2
                amenudat.dsp_no = dno
                amenudat.req_staff = rstaff
                amenudat.created_by = self.request.user.username
                amenudat.save()

# 変更・削除
class SheetsEditView(LoginRequiredMixin, FormView):
    template_name = 'sheets/sheet_edit.html'
    form_class = SheetForm
    ItemFormSet = forms.formset_factory(
        form = ItemForm,
        extra = 0,
        max_num = 50,
    )
    form_class2 = ItemFormSet

    # 一覧、シート（Session）情報をクリアするフラグ
    ini_flg = True

    # success_urlは動的にパラメータを渡さないといけないのでオーバーライド
    def get_success_url(self):
        url = reverse_lazy(
            'sheet-edit',
             kwargs={'pnendo': self.kwargs['pnendo'],
                     'id': self.kwargs['id'],
                     'pflg': 'False',
                     }
            )
        return url

    # formにパラメータを渡す為のオーバーライド
    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs()

        # パラメータ年度、編集モード(新規）をフォームへ渡す
        pnendo = self.kwargs['pnendo']
        mod = "edit"
        sid = self.kwargs['id']
        sobj = Sheets.objects.get(nendo=pnendo, id=sid)

        kwargs.update({'pnendo': pnendo, 'mod': mod, 'sobj': sobj})

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
            FORM_NUM = 0
            FORM_VALUES = {}
            SHEET_VALUES = {}

        context = super().get_context_data(**kwargs)

        context.update({
            'pnendo': self.kwargs['pnendo'],
            'id': self.kwargs['id'],
            })

        # フォームデータがあれば
        if FORM_VALUES:
            if self.request.method == 'GET':
                context.update({
                    'form': self.form_class(SHEET_VALUES),
                    'formset': self.form_class2(FORM_VALUES),
                    })
            else:
                context.update({
                    'formset': self.form_class2(FORM_VALUES),
                    })

        # なければ 初回表示で、パラメータからformset作成
        else:
            ilst = Items.objects.filter(nendo=self.kwargs['pnendo'], sheet_id=self.kwargs['id']).order_by('item_no')
            FORM_NUM = len(ilst)
            initial_data = []
            for dat in ilst:
                initial_data.append({'item_no': dat.item_no, 'content': dat.content, 'input_type': dat.input_type})
            formset = self.form_class2(initial=initial_data)
            context.update({
                'formset': formset,
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

        # 項目追加ボタン押下なら
        if 'btn_add' in request.POST:
            FORM_NUM += 1   # formsetのフォーム数インクリメント
            FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM

        # 項目削除ボタン押下なら
        if 'btn_del' in request.POST:
            #cnt_frm = 0
            to_cnt = 0
            del_cnt = 0
            newdic = {}
            delkeyist = []
            # FORM_VALUES form Noを削除行をのけて作り直し
            for i in range(FORM_NUM):
                frm_ck_delete = 'form-' + str(i) + '-ck_delete'
                # チェックされていなければ
                if frm_ck_delete not in FORM_VALUES:
                    to_itemno_str = 'form-' + str(to_cnt) + '-item_no'
                    newdic[to_itemno_str] = FORM_VALUES[frm_ck_delete.replace('ck_delete', 'item_no')]
                    newdic[to_itemno_str.replace('item_no', 'content')] = FORM_VALUES[frm_ck_delete.replace('ck_delete', 'content')]
                    newdic[to_itemno_str.replace('item_no', 'input_type')] = FORM_VALUES[frm_ck_delete.replace('ck_delete', 'input_type')]
                    to_cnt += 1
                else :
                    delkeyist.append(frm_ck_delete)
                    del_cnt += 1
            # 項目No.での並べ変えはしない
            for key, val in newdic.items():
                FORM_VALUES[key] = val
            for keystr in delkeyist:
                del FORM_VALUES[keystr]
            FORM_NUM -= del_cnt
            FORM_VALUES['form-TOTAL_FORMS'] = FORM_NUM

        # 更新ボタン押下なら
        if 'btn_update' in request.POST:
            form = self.form_class(request.POST)
            # 入力チェック
            self.datCheck_update(form, fsetwork)

            # エラーは全部シート部分に出力
            if form.non_field_errors():
                return self.form_invalid(form)
            
            # データ保存
            self.dataEntry(fsetwork)
            return redirect('/sheets?ini_flg=False')
        
        # 削除ボタン押下なら
        if 'btn_delete' in request.POST:
            self.dataDelete()
            return redirect('/sheets?ini_flg=False')

        return super().post(request, args, kwargs)

    # 入力チェック処理
    def datCheck_update(self, form, frmdic):

        if not frmdic['title']:
            form.add_error(None, 'アンケート名を入力してください。')

        # 一問多答形式の場合は項目数は1件のみ
        if frmdic['input_type'] == '2' and FORM_NUM > 1:
            form.add_error(None, '一問多答形式で登録出来る項目数は１件のみです。')

        # 項目リスト部分のエラーチェック
        if FORM_NUM <= 0:
            form.add_error(None, 'アンケート項目がありません。')
        list_ino = []
        for i in range(FORM_NUM):
            if not frmdic['form-' + str(i) + '-item_no']:
                form.add_error(None, '項目Noの入力がありません(' + str(i + 1) + '行目)')
            else:
                ino = frmdic['form-' + str(i) + '-item_no']
                if ino in list_ino:
                    form.add_error(None, '項目Noが重複しています(' + str(i + 1) + '行目)')
                else :
                    list_ino.append(ino)

            if not frmdic['form-' + str(i) + '-content']:
                form.add_error(None, '内容の入力がありません(' + str(i + 1) + '行目)')

    # データ保存処理
    def dataEntry(self, frmdic):
        with transaction.atomic():
            nendo = self.kwargs['pnendo']
            sheet_id=self.kwargs['id']

            # シート情報を保存
            sheetdat = Sheets.objects.get(nendo=nendo, id=sheet_id)
            sheetdat.title = frmdic['title']
            sheetdat.input_type = frmdic['input_type']
            # 表示順
            dno = 1
            if frmdic['dsp_no']:
                # 入力があればその数値
                dno = frmdic['dsp_no']
            else:
                # 入力がなくて登録レコードがあればMax＋1
                rno = Sheets.objects.all().count()
                if rno > 0:
                    dno = Sheets.objects.all().aggregate(Max('dsp_no')) + 1
            sheetdat.dsp_no = dno
            rstaff = False
            if 'req_staff' in frmdic:
                rstaff = True
            sheetdat.req_staff = rstaff

            sheetdat.update_by = self.request.user.username
            sheetdat.save()

            # 項目情報保存 delete&Insert
            items = Items.objects.filter(nendo=nendo, sheet_id=sheet_id)
            items.delete()
            for i in range(FORM_NUM):
                itemdat = Items()
                itemdat.nendo = nendo
                itemdat.sheet_id = sheetdat
                itemdat.item_no = frmdic['form-' + str(i) + '-item_no']
                itemdat.content = frmdic['form-' + str(i) + '-content']
                itemdat.input_type = frmdic['form-' + str(i) + '-input_type']
                itemdat.update_by = self.request.user.username
                itemdat.save()

            # メニューへの更新
            inpurl = INPUT_URL + frmdic['sheet_name']
            aggurl = AGGRE_URL + frmdic['sheet_name']

            # 入力画面のURLの登録があれば
            imenu = Menu.objects.filter(
                        url = inpurl,
                ).exists()
            if imenu:
                imenudat = Menu.objects.get(url=inpurl)
                imenudat.title = frmdic['title']
                imenudat.kbn = 1
                imenudat.dsp_no = dno
                imenudat.req_staff = False
                imenudat.update_by = self.request.user.username
                imenudat.save()

            # 集計画面のURLの登録があれば
            amenu = Menu.objects.filter(
                        url = aggurl,
                ).exists()
            if amenu:
                amenudat = Menu.objects.get(url=aggurl)
                amenudat.title = frmdic['title'] + ' 集計'
                amenudat.kbn = 2
                amenudat.dsp_no = dno
                amenudat.req_staff = rstaff
                amenudat.update_by = self.request.user.username
                amenudat.save()

    # データ削除処理
    def dataDelete(self):
        with transaction.atomic():
            nendo = self.kwargs['pnendo']
            sheet_id=self.kwargs['id']

            # シート情報削除
            sheet = Sheets.objects.get(nendo=nendo, id=sheet_id)
            sheet.delete()

            # 項目情報削除
            items = Items.objects.filter(nendo=nendo, sheet_id=sheet_id)
            items.delete()

# Excelダウンロード
def SheetsDownloadExcel(request, pnendo, id):
    wb = openpyxl.load_workbook(str(settings.BASE_DIR) + '/media/sheet.xlsx')
    ws = wb.active

    # データ出力開始行
    row = 2
    # 列数
    col_max = 14

    # スタイルを取得
    cellstylelist = []
    for i in range(col_max):
        cellstyle = ws.cell(row, (i+1))._style
        cellstylelist.append(cellstyle)

    print(pnendo)
    print(id)
    sheet = Sheets.objects.get(id=id)
    itemlist = Items.objects.filter(nendo=pnendo, sheet_id=sheet)

    # セレクトボックス値からのdicを作成
    ityp_dic = {}
    for ival, ilabel in INPUT_TYPE_CHOICES:
        ityp_dic[ival] = ilabel

    for idat in itemlist:
        # 値を設定
        ws.cell(row, 1).value = sheet.nendo
        ws.cell(row, 2).value = sheet.sheet_name
        ws.cell(row, 3).value = sheet.title
        ws.cell(row, 4).value = sheet.input_type
        ws.cell(row, 5).value = ityp_dic[sheet.input_type]
        ws.cell(row, 6).value = sheet.dsp_no
        ws.cell(row, 7).value = sheet.req_staff
        ws.cell(row, 8).value = idat.item_no
        ws.cell(row, 9).value = idat.content
        ws.cell(row, 10).value = idat.input_type
        ws.cell(row, 11).value = idat.created_by
        ws.cell(row, 12).value = idat.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')
        ws.cell(row, 13).value = idat.update_by
        ws.cell(row, 14).value = idat.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')
        # スタイルを設定
        for i in range(col_max):
            ws.cell(row, (i+1))._style = cellstylelist[i]
        row += 1
        
    # ダウンロード
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=%s' % 'sheet.xlsx'
    wb.save(response)

    return response

'''
# Excel アップロード
class FileUploadView(LoginRequiredMixin, FormView):
    template_name = 'customuser/fileupload.html'
    form_class = FileUploadForm
    success_url = '/customusers?ini_flg=False'

    def form_valid(self, form):
        # Excel取込み
        df = pd.read_excel(form.cleaned_data['file'], header=0)

        # エラーチェック
        # 組合せチェック用
        budic = dict()
        lodic = dict()
        podic = dict()
        # 行数はIndexが0からで、ヘッダ1行を除くので+2
        for i in range(df.shape[0]) :
            ldat = df.iloc[i]

            # 年度チェック
            strnendo = str(ldat['年度'])
            nendo = int('0')
            if strnendo == 'nan':
                form.add_error(None, '年度の入力がありません。(%s行目)' % str((i+2)))
            elif not strnendo.isdecimal():
                form.add_error(None, '年度に数字以外の文字の入力があります。(%s行目)' % str((i+2)))
            else:
                nendo = int(strnendo)
            
            # 部署チェック
            str_bucode = str(ldat['部署'])
            if str_bucode == 'nan':
                form.add_error(None, '部署コードの入力がありません。(%s行目)' % str((i+2)))
            else:
                # コードが文字列じゃなかったら
                if type(ldat['部署']) is not str:
                    # x.0を消す
                    if str_bucode.endswith('.0'):
                        str_bucode = str_bucode[:(len(str_bucode)-2)]
            str_buname = str(ldat[2])
            if str_buname == 'nan':
                form.add_error(None, '部署名の入力がありません。(%s行目)' % str((i+2)))

            if nendo != 0 and str_bucode != 'nan' and str_buname != 'nan':
                # 年度と部署コードを半角に変換してキーを作成
                bukey = str(nendo) + '_' + unicodedata.normalize('NFKC', str_bucode)
                # キーを検索
                if bukey in budic:
                    # キーが登録済みなのに、名前が違ったらエラー
                    if budic[bukey] != str_buname:
                        form.add_error(None, '異なる部署名の部署コードが存在します。(%s行目)' % str((i+2)))
                else:
                    # 未登録なら登録
                    budic[bukey] = str_buname

            # 勤務地チェック
            str_loccode = str(ldat['勤務地'])
            if str_loccode == 'nan':
                form.add_error(None, '勤務地コードの入力がありません。(%s行目)' % str((i+2)))
            else:
                # コードが文字列じゃなかったら
                if type(ldat['勤務地']) is not str:
                    # x.0を消す
                    if str_loccode.endswith('.0'):
                        str_loccode = str_loccode[:(len(str_loccode)-2)]
            str_locname = str(ldat[4])
            if str_locname == 'nan':
                form.add_error(None, '勤務地名の入力がありません。(%s行目)' % str((i+2)))

            if nendo != 0 and str_loccode != 'nan' and str_locname != 'nan':
                # 年度と勤務地コードを半角に変換してキーを作成
                lockey = str(nendo) + '_' + unicodedata.normalize('NFKC', str_loccode)
                # キーを検索
                if lockey in lodic:
                    # キーが登録済みなのに、名前が違ったらエラー
                    if lodic[lockey] != str_locname:
                        form.add_error(None, '異なる勤務地名の勤務地コードが存在します。(%s行目)' % str((i+2)))
                else:
                    # 未登録なら登録
                    lodic[lockey] = str_locname
            
            # 役職チェック
            str_pstcode = str(ldat['役職'])
            if str_pstcode == 'nan':
                form.add_error(None, '役職コードの入力がありません。(%s行目)' % str((i+2)))
            else:
                # コードが文字列じゃなかったら
                if type(ldat['役職']) is not str:
                    # x.0を消す
                    if str_pstcode.endswith('.0'):
                        str_pstcode = str_pstcode[:(len(str_pstcode)-2)]
            str_pstname = str(ldat[6])
            if str_pstname == 'nan':
                form.add_error(None, '役職名の入力がありません。(%s行目)' % str((i+2)))

            if nendo != 0 and str_pstcode != 'nan' and str_pstname != 'nan':
                # 年度と役職コードを半角に変換してキーを作成
                pstkey = str(nendo) + '_' + unicodedata.normalize('NFKC', str_pstcode)
                # キーを検索
                if pstkey in podic:
                    # キーが登録済みなのに、名前が違ったらエラー
                    if podic[pstkey] != str_pstname:
                        form.add_error(None, '異なる役職名の役職コードが存在します。(%s行目)' % str((i+2)))
                else:
                    # 未登録なら登録
                    podic[pstkey] = str_pstname

            # ユーザ情報必須入力チェック
            str_userid = str(ldat['ユーザーID'])
            if str_userid == 'nan':
                form.add_error(None, 'ユーザーIDの入力がありません。(%s行目)' % str((i+2)))
            str_name1 = str(ldat['氏名'])
            if str_name1 == 'nan':
                form.add_error(None, '氏名の入力がありません。(%s行目)' % str((i+2)))
            str_name2 = str(ldat[9])
            if str_name2 == 'nan':
                form.add_error(None, '氏名の入力がありません。(%s行目)' % str((i+2)))

        # エラーがあったら終了
        if form.non_field_errors():
            return super().form_invalid(form)

        # エラーがなければ登録処理
        # 部署
        for bkey in budic.keys():
            splist = bkey.split('_')
            nendo = splist[0]
            code = splist[1]
            name = budic[bkey]
            # 部署マスタにあれば更新、なければ登録
            if Busyo.objects.filter(nendo=nendo, bu_code=code).exists():
                busyodat = Busyo.objects.get(nendo=nendo, bu_code=code)
                busyodat.bu_name = name
                busyodat.update_by = self.request.user.username
                busyodat.save()
            else:
                busyodat = Busyo()
                busyodat.nendo = nendo
                busyodat.bu_code = code
                busyodat.bu_name = name
                busyodat.created_by = self.request.user.username
                busyodat.save()

        # 勤務地
        for lkey in lodic.keys():
            splist = lkey.split('_')
            nendo = splist[0]
            code = splist[1]
            name = lodic[lkey]
            # 勤務地マスタにあれば更新、なければ登録
            if Location.objects.filter(nendo=nendo, location_code=code).exists():
                locdat = Location.objects.get(nendo=nendo, location_code=code)
                locdat.location_name = name
                locdat.update_by = self.request.user.username
                locdat.save()
            else:
                locdat = Location()
                locdat.nendo = nendo
                locdat.location_code = code
                locdat.location_name = name
                locdat.created_by = self.request.user.username
                locdat.save()

        # 役職
        for pkey in podic.keys():
            splist = pkey.split('_')
            nendo = splist[0]
            code = splist[1]
            name = podic[pkey]
            # 役職マスタにあれば更新、なければ登録
            if Post.objects.filter(nendo=nendo, post_code=code).exists():
                locdat = Post.objects.get(nendo=nendo, post_code=code)
                locdat.post_name = name
                locdat.update_by = self.request.user.username
                locdat.save()
            else:
                locdat = Post()
                locdat.nendo = nendo
                locdat.post_code = code
                locdat.post_name = name
                locdat.created_by = self.request.user.username
                locdat.save()

        # ユーザマスタはファイルから
        for i in range(df.shape[0]) :
            ldat = df.iloc[i]

            nendo = int(ldat['年度'])
            bu_code = int(ldat['部署'])
            loc_code = int(ldat['勤務地'])
            post_code = int(ldat['役職'])
            user_id = ldat['ユーザーID']
            last_name = ldat['氏名']
            first_name = ldat[9]
            email = ldat['メールアドレス']
            if type(email) is not str and str(email) == 'nan':
                email = ''
            staff = False
            if ldat['管理者権限'] == True:
                staff = True

            # ユーザマスタに登録があれば更新、なければ登録
            if CustomUser.objects.filter(nendo=nendo, user_id=user_id).exists():
                cuser = CustomUser.objects.get(nendo=nendo, user_id=user_id)
                cuser.last_name = last_name
                cuser.first_name = first_name
                cuser.email = email
                cuser.is_staff = staff
                cuser.post_id = Post.objects.get(nendo=nendo, post_code=post_code)
                cuser.busyo_id = Busyo.objects.get(nendo=nendo, bu_code=bu_code)
                cuser.location_id = Location.objects.get(nendo=nendo, location_code=loc_code)
                cuser.update_by = self.request.user.username
                cuser.save()
            else:
                cuser = CustomUser()
                cuser.nendo = nendo
                cuser.user_id = user_id
                cuser.last_name = last_name
                cuser.first_name = first_name
                cuser.email = email
                cuser.is_staff = staff
                cuser.post_id = Post.objects.get(nendo=nendo, post_code=post_code)
                cuser.busyo_id = Busyo.objects.get(nendo=nendo, bu_code=bu_code)
                cuser.location_id = Location.objects.get(nendo=nendo, location_code=loc_code)
                cuser.created_by = self.request.user.username
                cuser.save()

            # ログインマスタに登録があれば更新、なければ登録
            if User.objects.filter(username=user_id).exists():
                auser = User.objects.get(username=user_id)
                auser.first_name = first_name
                auser.last_name = last_name
                auser.email = email
                auser.is_staff = staff
                auser.save()
            else:
                new_user = User()
                new_user.username = user_id
                new_user.password = make_password(user_id)
                new_user.first_name = first_name
                new_user.last_name = last_name
                new_user.email = email
                new_user.is_staff = staff
                new_user.is_active = True
                new_user.is_superuser = False
                new_user.save()

        return super().form_valid(form)
'''
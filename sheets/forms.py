from django import forms
from django.core.exceptions import ValidationError
from sheets.consts import INPUT_TYPE_CHOICES, FIELD_TYPE_CHOICES, AGGRE_TYPE_CHOICES
from surveys.models import Busyo

# シートマスタメンテナンス 検索フォーム
class SheetQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)

# シートマスタ 登録・編集フォーム
# 追加ボタン押下時にエラーにしないようrequiredはFalse
class SheetForm(forms.Form):
    nendo = forms.CharField(label='年度',
        widget=forms.NumberInput(attrs={'class': 'ShortNumberInput'}),
        )
    sheet_name = forms.CharField(label='シート名', required=False,)
    title = forms.CharField(label='アンケート名', required=False,)
    dsp_no = forms.IntegerField(
        label='表示順', required=False,
        widget=forms.NumberInput(attrs={'class': 'ShortNumberInput'}),
    )
    input_type = forms.ChoiceField(label='入力形式', choices=INPUT_TYPE_CHOICES, required=False,)
    aggre_type = forms.ChoiceField(label='集計タイプ', choices=AGGRE_TYPE_CHOICES, required=False,)
    req_staff = forms.BooleanField(label='集計画面管理者権限要', required=False,)
    busyo = forms.ChoiceField(label='部署', required=False,)
    remarks1 = forms.CharField(label='備考1', required=False,
        widget=forms.Textarea(attrs={
            'cols': 70,
             'rows': 2,
             'placeholder': '500文字',
            })
    )
    remarks2 = forms.CharField(label='備考2', required=False,
        widget=forms.Textarea(attrs={
            'cols': 70,
             'rows': 2,
             'placeholder': '250文字',
            })
    )

    def __init__(self, *args, **kwargs):
        # viewからのパラメータ受け取り
        self.pnendo = kwargs.pop('pnendo', None)
        self.mod = kwargs.pop('mod', None)
        self.sobj = kwargs.pop('sobj', None)
        super().__init__(*args, **kwargs)

        # 年度はパラメータ値
        nendo = self.pnendo
        self.fields['nendo'].initial = nendo

        # 部署リスト作成
        blist = [('', '')] + list(Busyo.objects.filter(nendo=nendo).values_list('bu_code', 'bu_name').order_by('bu_code'))
        self.fields['busyo'].choices = blist

        # 編集モードの場合
        if self.mod == 'edit':
            # 年度とシート名はリードオンリー
            self.fields['nendo'].widget.attrs['readonly'] = 'readonly'
            self.fields['sheet_name'].widget.attrs['readonly'] = 'readonly'

            sobj = self.sobj
            # シート情報初期化
            self.fields['sheet_name'].initial = sobj.sheet_name
            self.fields['title'].initial = sobj.title
            self.fields['dsp_no'].initial = sobj.dsp_no
            self.fields['input_type'].initial = sobj.input_type
            self.fields['aggre_type'].initial = sobj.aggre_type
            self.fields['req_staff'].initial = sobj.req_staff
            self.fields['busyo'].initial = sobj.busyo_id
            self.fields['remarks1'].initial = sobj.remarks1
            self.fields['remarks2'].initial = sobj.remarks2
           
# カラムマスタ 登録・編集フォーム
# 追加ボタン押下時にエラーにしないようrequiredはFalse
class ItemForm(forms.Form):
    ck_delete = forms.BooleanField(
        label='削除',
        widget=forms.CheckboxInput(attrs={'class': 'check'}),
    )
    item_no = forms.IntegerField(
        label='項目No.', required=True,
        widget=forms.NumberInput(attrs={'class': 'ShortNumberInput'}),
    )
    content = forms.CharField(
        label='内容', required=True,
        widget=forms.Textarea(attrs={
            'cols': 50,
             'rows': 3,
             'placeholder': '500文字',
            })
    )
    input_type = forms.ChoiceField(label='入力タイプ', choices=FIELD_TYPE_CHOICES,required=True,)
    answer = forms.CharField(label='解答', required=False)
    haiten = forms.CharField(label='配点', required=False)


# Excel入力フォーム
class FileUploadForm(forms.Form):
    file = forms.FileField(label='ファイル', required=True,)

    def clean_file(self):
        # Excelファイルかどうかのチェック
        file = self.cleaned_data['file']
        if not file.name.endswith('xlsx'):
            raise ValidationError('xlsxファイルを選択してください。')
        return file

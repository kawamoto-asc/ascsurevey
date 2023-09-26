from django import forms
from sheets.consts import INPUT_TYPE_CHOICES, FIELD_TYPE_CHOICES

# シートマスタメンテナンス 検索フォーム
class SheetQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)

# シートマスタ 登録・編集フォーム
# 追加ボタン押下時にエラーにしないようrequiredはFalse
class SheetForm(forms.Form):
    nendo = forms.CharField(label='年度',
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'size': '3'}),
        )
    sheet_name = forms.CharField(label='シート名', required=False,)
    title = forms.CharField(label='アンケート名', required=False,)
    input_type = forms.ChoiceField(label='入力形式', choices=INPUT_TYPE_CHOICES, required=False,)
    dsp_no = forms.IntegerField(
        label='表示順', required=False,
        widget=forms.NumberInput(attrs={'class': 'ShortNumberInput'}),
    )

    def __init__(self, *args, **kwargs):
        # viewからのパラメータ受け取り
        self.pnendo = kwargs.pop('pnendo', None)
        self.mod = kwargs.pop('mod', None)
        self.sobj = kwargs.pop('sobj', None)
        super().__init__(*args, **kwargs)

        # 年度はパラメータ値でリードオンリー
        nendo = self.pnendo
        self.fields['nendo'].initial = nendo
        self.fields['nendo'].widget.attrs['readonly'] = 'readonly'

        # 編集モードの場合
        if self.mod == 'edit':
            # シート名もリードオンリー
            self.fields['sheet_name'].widget.attrs['readonly'] = 'readonly'
           
# カラムマスタ 登録・編集フォーム
# 追加ボタン押下時にエラーにしないようrequiredはFalse
class ItemForm(forms.Form):
    item_no = forms.IntegerField(
        label='項目No.', required=True,
        widget=forms.NumberInput(attrs={'class': 'ShortNumberInput'}),
    )
    content = forms.CharField(
        label='内容', required=True,
        widget=forms.Textarea(attrs={
            'cols': 50,
             'rows': 3,
             'placeholder': '300文字',
            })
    )
    input_type = forms.ChoiceField(label='入力タイプ', choices=FIELD_TYPE_CHOICES,required=True,)
    ck_delete = forms.BooleanField(
        label='削除',
        widget=forms.CheckboxInput(attrs={'class': 'check'}),
    )

'''
# Excel入力フォーム
class FileUploadForm(forms.Form):
    file = forms.FileField(label='ファイル', required=True,)

    def clean_file(self):
        # Excelファイルかどうかのチェック
        file = self.cleaned_data['file']
        if not file.name.endswith('xlsx'):
            raise ValidationError('xlsxファイルを選択してください。')
        return file
'''
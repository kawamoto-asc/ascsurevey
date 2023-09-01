from django import forms
from django.core.exceptions import ValidationError
from sheets.consts import INPUT_TYPE_CHOICES

# シートマスタメンテナンス 検索フォーム
class SheetQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)

# シートマスタ 登録・編集フォーム
class SheetForm(forms.Form):
    nendo = forms.CharField(label='年度',
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'size': '3'}),
        )
    sheet_name = forms.CharField(label='シート名', required=True,)
    title = forms.CharField(label='アンケート名', required=True,)
    input_type = forms.ChoiceField(label='入力形式', choices=INPUT_TYPE_CHOICES, required=True,)
    dsp_no = forms.IntegerField(
        label='表示順', required=True,
        widget=forms.NumberInput(attrs={'class': 'ShortNumberInput'}),
    )

    def __init__(self, *args, **kwargs):
        # viewからのパラメータ受け取り
        self.pnendo = kwargs.pop('pnendo', None)
        self.mod = kwargs.pop('mod', None)
        self.sobj = kwargs.pop('sobj', None)
        super().__init__(*args, **kwargs)

        nendo = self.pnendo
        self.fields['nendo'].initial = nendo


'''
        # 編集モードの場合
        if self.mod == 'edit':
            # ユーザIDもリードオンリー
            self.fields['user_id'].widget.attrs['readonly'] = 'readonly'

            uobj = self.uobj
            # ユーザ情報初期化
            self.fields['busyo'].initial = uobj.busyo_id.bu_code
            self.fields['location'].initial = uobj.location_id.location_code
            self.fields['post'].initial = uobj.post_id.post_code
            self.fields['user_id'].initial = uobj.user_id
            self.fields['last_name'].initial = uobj.last_name
            self.fields['first_name'].initial = uobj.first_name
            self.fields['email'].initial = uobj.email
            self.fields['is_staff'].initial = uobj.is_staff

    def clean(self):
        # 半角英数字と_@-.だけ入力可のチェック用
        reg = re.compile(r'^[A-Za-z0-9_@\-\.]+$')

        # 新規登録時だけのチェック
        if self.mod == 'new':
            nendo = self.cleaned_data['nendo']
            uid = self.cleaned_data['user_id']

            if reg.match(uid) is None:
                raise ValidationError('ユーザーIDは半角英数字か_-@で入力してください。')

            user = CustomUser.objects.filter(
                nendo = nendo,
                user_id = uid,
            ).exists()
            if user:
                raise ValidationError('入力した年度のユーザIDは既に登録済みです。')
        
        # 新規、編集共通チェック
        email = self.cleaned_data['email']
        if email:
            if reg.match(email) is None:
                raise ValidationError('メールアドレスは半角英数字か_-@で入力してください。')
'''
                
# カラムマスタ 登録・編集フォーム
class ItemForm(forms.Form):
    item_no = forms.IntegerField(
        label='項目No.', required=True,
        widget=forms.NumberInput(attrs={'class': 'ShortNumberInput'}),
    )
    content = forms.CharField(
        label='内容', required=True,
        widget=forms.Textarea(attrs={'cols': 50, 'rows': 3,})
    )
    input_type = forms.ChoiceField(label='入力タイプ', choices=INPUT_TYPE_CHOICES,required=True,)
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
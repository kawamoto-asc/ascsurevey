from django import forms
from django.core.exceptions import ValidationError
from surveys.models import Busyo, Location, Post, CustomUser
import re

# ユーザーマスタメンテナンス 検索フォーム
class CustomUserQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)
    busyo = forms.ChoiceField(label='部署', required=False,)
    location = forms.ChoiceField(label='勤務地', required=False,)
    post = forms.ChoiceField(label='役職', required=False,)

# ユーザマスタメンテ 登録・編集フォーム
class CustomUserForm(forms.Form):
    nendo = forms.CharField(label='年度',
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'size': '3'}),
        )
    busyo = forms.ChoiceField(label='部署', required=True,)
    location = forms.ChoiceField(label='勤務地', required=True,)
    post = forms.ChoiceField(label='役職', required=True,)
    user_id = forms.CharField(
        label='ユーザーID', max_length=128, required=True,
        widget=forms.TextInput(attrs={'size': '5'}),
        )
    last_name =  forms.CharField(
        label='氏', max_length=128, required=True,
        widget=forms.TextInput(attrs={'size': '5'}),
        )
    first_name = forms.CharField(
        label='名', max_length=128, required=True,
        widget=forms.TextInput(attrs={'size': '5'}),
        )
    email = forms.CharField(label='メールアドレス', max_length=128, required=False)
    is_staff = forms.BooleanField(label='管理者権限', required=False)

    def __init__(self, *args, **kwargs):
        # viewからのパラメータ受け取り
        self.pnendo = kwargs.pop('pnendo', None)
        self.mod = kwargs.pop('mod', None)
        self.uobj = kwargs.pop('uobj', None)
        super().__init__(*args, **kwargs)

        nendo = self.pnendo
        self.fields['nendo'].initial = nendo

        # 部署リスト作成
        blist = [('', '')] + list(Busyo.objects.filter(nendo=nendo).values_list('bu_code', 'bu_name').order_by('bu_code'))
        self.fields['busyo'].choices = blist

        # 勤務地リスト作成
        llist = [('', '')] + list(Location.objects.filter(nendo=nendo).values_list('location_code', 'location_name').order_by('location_code'))
        self.fields['location'].choices = llist

        # 役職リスト作成
        plist = [('', '')] + list(Post.objects.filter(nendo=nendo).values_list('post_code', 'post_name').order_by('post_code'))
        self.fields['post'].choices = plist

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

# Excel入力フォーム
class FileUploadForm(forms.Form):
    file = forms.FileField(label='ファイル', required=True,)

    def clean_file(self):
        # Excelファイルかどうかのチェック
        file = self.cleaned_data['file']
        if not file.name.endswith('xlsx'):
            raise ValidationError('xlsxファイルを選択してください。')
        return file
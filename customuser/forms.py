from django import forms
#from sureveys.models import *

# ユーザーマスタメンテナンス 検索フォーム
class CustomUserQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)
    busyo = forms.ChoiceField(label='部署', required=False,)
    location = forms.ChoiceField(label='勤務地', required=False,)
    post = forms.ChoiceField(label='役職', required=False,)

# ユーザマスタメンテ 新規登録フォーム
class CustomUserForm(forms.Form):
    nendo = forms.CharField(label='年度',
        widget=forms.TextInput(attrs={'readonly': 'readonly', 'size': '5'}),
        )
    busyo = forms.ChoiceField(label='部署', required=False,)
    location = forms.ChoiceField(label='勤務地', required=False,)
    post = forms.ChoiceField(label='役職', required=False,)
    user_id = forms.CharField(
        label='ユーザーID', max_length=128,
        widget=forms.TextInput(attrs={'size': '5'}),
        )
    first_name = forms.CharField(
        label='名', max_length=128,
        widget=forms.TextInput(attrs={'size': '5'}),
        )
    last_name =  forms.CharField(
        label='氏', max_length=128,
        widget=forms.TextInput(attrs={'size': '5'}),
        )
    email = forms.CharField(label='メールアドレス', max_length=128)
    is_staff = forms.BooleanField(label='管理者権限')

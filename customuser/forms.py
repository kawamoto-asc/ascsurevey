from django import forms
#from sureveys.models import *

# ユーザーマスタメンテナンス 検索フォーム
class CustomUserQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)
    busyo = forms.ChoiceField(label='部署', required=False,)
    location = forms.ChoiceField(label='勤務地', required=False,)
    post = forms.ChoiceField(label='役職', required=False,)

# ユーザマスタメンテ新規フォーム
#class CustomUserForm(forms.Form):
#    nendo 
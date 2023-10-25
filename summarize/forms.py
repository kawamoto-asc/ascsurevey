from django import forms

# 集計画面 検索フォーム
class SummarizeQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)
    busyo = forms.ChoiceField(label='部署', required=False,)
    location = forms.ChoiceField(label='勤務地', required=False,)
    post = forms.ChoiceField(label='役職', required=False,)
    shname = forms.CharField(label='シート名', max_length=128, required=False,)

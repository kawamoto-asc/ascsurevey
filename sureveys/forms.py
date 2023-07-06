from django import forms

class CustomUserQueryForm(forms.Form):
    nendo = forms.CharField(label='年度', max_length=4)
    post = forms.CharField(label='役職', max_length=256)
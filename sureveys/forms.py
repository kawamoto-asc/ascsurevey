from django import forms
from sureveys.models import *

class CustomUserQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,)
    busyo = forms.ChoiceField(label='部署',)
    location = forms.ChoiceField(label='勤務地',)
    post = forms.ChoiceField(label='役職',)

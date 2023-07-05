from django import forms

class CustomUserQueryForm(forms.Form):
    nendo = forms.CharField()
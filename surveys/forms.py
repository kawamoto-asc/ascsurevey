from django import forms

class Edit2Form(forms.Form):
    ck_delete = forms.BooleanField(
        label='削除',
        widget=forms.CheckboxInput(attrs={'class': 'check'}),
    )
    content = forms.CharField(
        label='内容', required=True,
        widget=forms.Textarea(attrs={
            'cols': 50,
             'rows': 3,
             'placeholder': '500文字',
            })
    )

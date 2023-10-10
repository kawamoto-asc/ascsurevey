from django import forms

# 一問多答形式入力フォーム
# 追加ボタン押下時にエラーにしないようrequiredはFalse
class Edit2Form(forms.Form):
    ck_delete = forms.BooleanField(
        label='削除', required=False,
        widget=forms.CheckboxInput(attrs={'class': 'check'}),
    )
    content = forms.CharField(
        label='内容', required=False,
        widget=forms.Textarea(attrs={
            'cols': 50,
             'rows': 3,
             'placeholder': '500文字',
            })
    )

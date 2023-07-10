from django import forms
from sureveys.models import Post

class CustomUserQueryForm(forms.Form):
    nendo = forms.ChoiceField(label='年度', required=True, disabled=False,
                              widget=forms.Select(attrs={
                                  'id': 'nendo'
                              }))
    post = forms.ChoiceField(label='役職',)
#                             choices=lambda : [
#                                 (post.post_code, post.post_name) for post in Post.objects.filter(nendo=ujf_nendo)
#                                 ])


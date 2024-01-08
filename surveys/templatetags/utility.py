from django import template
from surveys.models import CustomUser

register = template.Library()

@register.filter(name="get_BuCode")
def get_BuCode(request, unendo):

    luser = CustomUser.objects.get(nendo=unendo, user_id=request.user.username)
    request.session['sbu_code'] = luser.busyo_id.bu_code     # 部コードをセッション情報にセット
    print(request.session['sbu_code'])

    return luser.busyo_id.bu_code

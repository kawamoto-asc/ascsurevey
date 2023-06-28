from sureveys.models import Menu

# メニュー情報
def global_menu_data(request):
    input_menu = Menu.objects.filter(kbn=1).order_by('dsp_no')
    totalling_menu = Menu.objects.filter(kbn=2).order_by('dsp_no')
    admin_menu = Menu.objects.filter(kbn=8).order_by('dsp_no')

    return {
        'imenu': input_menu,
        'tmenu': totalling_menu,
        'amenu': admin_menu,
    }

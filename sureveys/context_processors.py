from sureveys.models import Menu, Ujf

# メニュー情報
def global_menu_data(request):
    input_menu = Menu.objects.filter(kbn=1).order_by('dsp_no')
    totalling_menu = Menu.objects.filter(kbn=2).order_by('dsp_no')
    admin_menu = Menu.objects.filter(kbn=8).order_by('dsp_no')

    # 集計画面メニュー
    # 全体の件数
    totalling_ttl_count = Menu.objects.filter(kbn=2).count()
    # 一般権限の数
    totalling_gene_count = Menu.objects.filter(kbn=2, req_staff=False).count()

    return {
        'imenu': input_menu,
        'tmenu': totalling_menu,
        'amenu': admin_menu,
        'skttl_count': totalling_ttl_count,
        'skgene_count': totalling_gene_count,
    }

# 運用条件情報
def global_ujf(request):
    # 今年度取得
    nobj = Ujf.objects.get(key1=1, key2='1')

    return {
        'ujf_nendo': nobj.naiyou4,
    }
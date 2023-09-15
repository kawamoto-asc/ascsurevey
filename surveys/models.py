from django.conf import settings
from django.db import models

from .consts import MENU_KBN_CHOICES

# Create your models here.
# Information
class Information(models.Model):
    info = models.CharField('情報', max_length=256)

    created_by = models.CharField('作成者', max_length=128)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.info

# メニューマスタ
class Menu(models.Model):
    title = models.CharField('アンケート名', max_length=128)
    url = models.CharField('URL', max_length=256)
    # 区分 1:アンケート入力画面 2:アンケート集計画面 8:アンケートメンテナンス画面
    kbn = models.IntegerField ('区分', choices=MENU_KBN_CHOICES)
    dsp_no = models.IntegerField ('表示順')
    req_staff = models.BooleanField('スタッフ権限要否')

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self) -> str:
        return self.title
    
# 運用条件
class Ujf(models.Model):
    key1 = models.IntegerField()
    key2 = models.CharField(max_length=128)
    naiyou1 = models.CharField('内容1', max_length=256, blank=True, null=True)
    naiyou2 = models.CharField('内容2', max_length=256, blank=True, null=True)
    naiyou3 = models.CharField('内容3', max_length=256, blank=True, null=True)
    naiyou4 = models.IntegerField('内容4', blank=True, null=True)
    naiyou5 = models.DecimalField('内容5', max_digits=12, decimal_places=2, blank=True, null=True)
    bikou = models.TextField('備考', blank=True, null=True)

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # ユニークキー設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields = ['key1', 'key2'],
            name = 'ujf_unique'
            ),
        ]

    def __str__(self) -> str:
        return super().__str__()

# 役職マスタ
class Post(models.Model):
    nendo = models.IntegerField('年度')
    post_code = models.IntegerField('役職コード')
    post_name = models.CharField('役職名')

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # ユニークキー設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields = ['nendo', 'post_code'],
            name = 'post_unique'
            ),
        ]

    def __str__(self) -> str:
        return str(self.nendo) + '_' + self.post_name

# 部署マスタ
class Busyo(models.Model):
    nendo = models.IntegerField('年度')
    bu_code = models.IntegerField('部署コード')
    bu_name = models.CharField('部名称')

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # ユニークキー設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields = ['nendo', 'bu_code'],
            name = 'busyo_unique'
            ),
        ]

    def __str__(self) -> str:
        return str(self.nendo) + '_' + self.bu_name

# 勤務地マスタ
class Location(models.Model):
    nendo = models.IntegerField('年度')
    location_code = models.IntegerField('勤務地コード')
    location_name = models.CharField('勤務地名')

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # ユニークキー設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields = ['nendo', 'location_code'],
            name = 'location_unique'
            ),
        ]

    def __str__(self) -> str:
        return str(self.nendo) + '_' + self.location_name

# ユーザマスタ
class CustomUser(models.Model):
    nendo = models.IntegerField('年度')
    user_id = models.CharField('ユーザーID', max_length=128)
    first_name = models.CharField('氏', max_length=128)
    last_name =  models.CharField('名', max_length=128)
    email = models.CharField('メールアドレス', max_length=128, blank=True, null=True)
    post_id = models.ForeignKey(Post, on_delete=models.DO_NOTHING, db_column='post_id')
    busyo_id = models.ForeignKey(Busyo, on_delete=models.DO_NOTHING, db_column='busyo_id')
    location_id = models.ForeignKey(Location, on_delete=models.DO_NOTHING, db_column='location_id')
    is_staff = models.BooleanField('管理者権限')

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # ユニークキー設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields = ['nendo', 'user_id'],
            name = 'cmuser_unique'
            ),
        ]

    def __str__(self) -> str:
        return str(self.nendo) + '_' + self.user_id

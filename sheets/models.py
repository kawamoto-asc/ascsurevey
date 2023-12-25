from django.db import models

from sheets.consts import INPUT_TYPE_CHOICES, FIELD_TYPE_CHOICES,AGGRE_TYPE_CHOICES

# シートマスタ
class Sheets(models.Model):
    nendo = models.IntegerField('年度')
    sheet_name = models.CharField('シート名', max_length=128)
    title = models.CharField('アンケート名', max_length=128)
    dsp_no = models.IntegerField ('表示順')
    input_type = models.IntegerField ('入力形式', choices=INPUT_TYPE_CHOICES)
    aggre_type = models.IntegerField ('集計タイプ', choices=AGGRE_TYPE_CHOICES)
    req_staff = models.BooleanField('集計画面スタッフ権限要否')
    busyo_id = models.ForeignKey('surveys.Busyo', on_delete=models.DO_NOTHING, db_column='busyo_id', blank=True, null=True)
    remarks1 = models.TextField('備考1', max_length=512, blank=True, null=True)
    remarks2 = models.TextField('備考2', max_length=256, blank=True, null=True)

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # ユニークキー設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields = ['nendo', 'sheet_name'],
            name = 'sheet_unique'
            ),
        ]

    def __str__(self):
        return self.sheet_name

    class Meta:
        db_table = 'surveys_sheet'

# 項目マスタ
class Items(models.Model):
    nendo = models.IntegerField('年度')
    sheet_id = models.ForeignKey(Sheets, on_delete=models.DO_NOTHING, db_column='sheet_id')
    item_no = models.IntegerField ('項目No.')
    content = models.TextField('内容', max_length=512)
    input_type = models.CharField ('入力タイプ', choices=FIELD_TYPE_CHOICES)
    answer = models.CharField ('解答', max_length=128, blank=True, null=True)
    haiten = models.FloatField('配点', blank=True, null=True)

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    # ユニークキー設定
    class Meta:
        constraints = [
            models.UniqueConstraint(
            fields = ['nendo', 'sheet_id', 'item_no'],
            name = 'item_unique'
            ),
        ]

    def __str__(self):
        return str(self.nendo) + '_' + self.sheet_id.sheet_name + '_' + str(self.item_no)

    class Meta:
        db_table = 'surveys_item'

from django.db import models

from .consts import INPUT_TYPE_CHOICES

# シートマスタ
class Sheets(models.Model):
    nendo = models.IntegerField('年度')
    sheet_name = models.CharField('シート名', max_length=128)
    title = models.CharField('アンケートタイトル', max_length=128)
    input_type = models.IntegerField ('入力形式', choices=INPUT_TYPE_CHOICES)
    dsp_no = models.IntegerField ('表示順')

    created_by = models.CharField('作成者', max_length=128, blank=True, null=True)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField('作成日', auto_now_add=True)
    updated_at = models.DateTimeField('更新日', auto_now=True)

    def __str__(self):
        return self.sheet_name

    class Meta:
        db_table = 'sureveys_sheet'
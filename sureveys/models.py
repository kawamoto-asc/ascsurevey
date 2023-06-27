from django.conf import settings
from django.db import models

# Create your models here.
# Information
class Information(models.Model):
    info = models.CharField('情報', max_length=256)
    created_by = models.CharField('作成者', max_length=128)
    update_by = models.CharField('更新者', max_length=128, blank=True, null=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)
    updated_at = models.DateTimeField("更新日", auto_now=True)

    def __str__(self):
        return self.info

# メニューマスタ
#class Menu(models.Model):
#    title = models.CharField('アンケート名', max_length=128)
#    url = models.CharField('URL', max_length=128)
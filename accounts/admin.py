from django.contrib import admin
from sureveys.models import Information

# 管理画面でのメンテクラス
# Information画面
class InformationAdmin(admin.ModelAdmin):
    list_display = ('info', 'created_by', 'created_at', 'update_by', 'updated_at')
    ordering = ['-created_at']      # -で降順 -なしは昇順

# Register your models here.
admin.site.register(Information, InformationAdmin)
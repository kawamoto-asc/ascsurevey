from django.contrib import admin
from pytz import timezone
from sureveys.models import *

# 管理画面でのメンテクラス
# Informationメンテナンス画面
class InformationAdmin(admin.ModelAdmin):
    # 一覧設定
    list_display = ('info', 'created_by', 'created_format', 'update_by', 'updated_format')
    ordering = ['-created_at']      # -で降順 -なしは昇順

    def created_format(self, obj):
        return obj.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    def updated_format(self, obj):
        return obj.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    created_format.short_description = '作成日'
    updated_format.short_description = '更新日'
    
    # 入力設定
    fields = ('info',)   # 入力するのは情報カラムだけ

    # 保存の処理を上書き
    def save_model(self, request, obj, form, change):
        # 作成者が空なら新規
        if not obj.created_by:
            # 作成者へログインIDをセット
            obj.created_by = request.user.username
        else:
            # 更新者へログインIDをセット
            obj.update_by = request.user.username

        # 保存
        super().save_model(request, obj, form, change)

# メニュマスタ メンテナンス画面
class MenuAdmin(admin.ModelAdmin):
    # 一覧設定
    list_display = ('title', 'url', 'kbn', 'dsp_no', 'created_by', 'created_format', 'update_by', 'updated_format')
    ordering = ['kbn', 'dsp_no']

    def created_format(self, obj):
        return obj.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    def updated_format(self, obj):
        return obj.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    created_format.short_description = '作成日'
    updated_format.short_description = '更新日'
    
    # 入力設定
    fields = ('title', 'url', 'kbn', 'dsp_no')
#    fieldsets = (
#        ('title', 'url', {'kbn': (1, 2, 8)}, 'dsp_no'),
#    )

    # 保存の処理を上書き
    def save_model(self, request, obj, form, change):
        # 作成者が空なら新規
        if not obj.created_by:
            # 作成者へログインIDをセット
            obj.created_by = request.user.username
        else:
            # 更新者へログインIDをセット
            obj.update_by = request.user.username

        # 保存
        super().save_model(request, obj, form, change)

# Register models
admin.site.register(Information, InformationAdmin)
admin.site.register(Menu, MenuAdmin)
from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin
from import_export.fields import Field
from import_export.formats import base_formats
from pytz import timezone
from sureveys.models import Information, Menu

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

# メニュマスタ メンテナンス impoort/export 定義
class MenuResource(resources.ModelResource):
    title = Field(attribute='title', column_name='title')
    url = Field(attribute='url', column_name='url')
    kbn = Field(attribute='kbn', column_name='kbn')
    dsp_no = Field(attribute='dsp_no', column_name='dsp_no')
    created_by = 'aaa'

    class Meta:
        model = Menu
        fields = ('title', 'url', 'kbn', 'dsp_no')
        import_id_fields = ('url',)     # キーとするのはURL
        skip_unchanged = True           # 変更のあったものだけ取込み
        use_bulk = True

# メニュマスタ メンテナンス画面
class MenuAdmin(ImportExportMixin, admin.ModelAdmin):
    # 一覧設定
    list_display = ('title', 'url', 'kbn', 'dsp_no', 'created_by', 'created_format', 'update_by', 'updated_format')
    ordering = ['kbn', 'dsp_no']

    def created_format(self, obj):
        return obj.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    def updated_format(self, obj):
        return obj.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    created_format.short_description = '作成日'
    updated_format.short_description = '更新日'

    # インポートエクスポート設定
    resource_class = MenuResource
    formats = [base_formats.XLSX]   # 出力形式はxlsxのみ

    # 入力設定
    fields = ('title', 'url', 'kbn', 'dsp_no')

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
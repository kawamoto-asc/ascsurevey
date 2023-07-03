from django.contrib import admin
from import_export import resources
from import_export.admin import ImportExportMixin
from import_export.fields import Field
from import_export.formats import base_formats
from pytz import timezone
from sureveys.models import Information, Menu, Ujf, Post, Busyo, Location

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
    class Meta:
        model = Menu
        fields = ('title', 'url', 'kbn', 'dsp_no', 'req_staff')
        import_id_fields = ('url',)     # キー項目
        skip_unchanged = True           # 変更のあったものだけ取込み
        use_bulk = True

# メニュマスタ メンテナンス画面
class MenuAdmin(ImportExportMixin, admin.ModelAdmin):
    # 一覧設定
    list_display = ('title', 'url', 'kbn', 'dsp_no', 'req_staff', 'created_by', 'created_format', 'update_by', 'updated_format')
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
    fields = ('title', 'url', 'kbn', 'req_staff', 'dsp_no')

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

# 運用条件 メンテナンス impoort/export 定義
class UjfResource(resources.ModelResource):
    class Meta:
        model = Ujf
        fields = ('key1', 'key2', 'naiyou1', 'naiyou2', 'naiyou3', 'naiyou4', 'naiyou5', 'bikou')
        import_id_fields = ('key1', 'key2',)     # キー項目
        skip_unchanged = True           # 変更のあったものだけ取込み
        use_bulk = True

# 運用条件 メンテナンス画面
class UjfAdmin(ImportExportMixin, admin.ModelAdmin):
    # 一覧設定
    list_display = ('key1', 'key2', 'naiyou1', 'naiyou2', 'naiyou3', 'naiyou4', 'naiyou5', 'bikou', 'created_by', 'created_format', 'update_by', 'updated_format')
    ordering = ['key1', 'key2']

    def created_format(self, obj):
        return obj.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    def updated_format(self, obj):
        return obj.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    created_format.short_description = '作成日'
    updated_format.short_description = '更新日'

    # インポートエクスポート設定
    resource_class = UjfResource
    formats = [base_formats.XLSX]   # 出力形式はxlsxのみ

    # 入力設定
    fields = ('key1', 'key2', 'naiyou1', 'naiyou2', 'naiyou3', 'naiyou4', 'naiyou5', 'bikou')

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

# 役職マスタ メンテナンス impoort/export 定義
class PostResource(resources.ModelResource):
    class Meta:
        model = Post
        fields = ('nendo', 'post_code', 'post_name', 'post_name')
        import_id_fields = ('nendo', 'post_code',)     # キー項目
        skip_unchanged = True           # 変更のあったものだけ取込み
        use_bulk = True

# 役職 メンテナンス画面
class PostAdmin(ImportExportMixin, admin.ModelAdmin):
    # 一覧設定
    list_display = ('nendo', 'post_code', 'post_name', 'created_by', 'created_format', 'update_by', 'updated_format')
    ordering = ['nendo', 'post_code']

    def created_format(self, obj):
        return obj.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    def updated_format(self, obj):
        return obj.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    created_format.short_description = '作成日'
    updated_format.short_description = '更新日'

    # インポートエクスポート設定
    resource_class = PostResource
    formats = [base_formats.XLSX]   # 出力形式はxlsxのみ

    # 入力設定
    fields = ('nendo', 'post_code', 'post_name')

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

# 部署マスタ メンテナンス impoort/export 定義
class BusyoResource(resources.ModelResource):
    class Meta:
        model = Busyo
        fields = ('nendo', 'bu_code', 'bu_name')
        import_id_fields = ('nendo', 'bu_code',)     # キー項目
        skip_unchanged = True           # 変更のあったものだけ取込み
        use_bulk = True

# 部署 メンテナンス画面
class BusyoAdmin(ImportExportMixin, admin.ModelAdmin):
    # 一覧設定
    list_display = ('nendo', 'bu_code', 'bu_name', 'created_by', 'created_format', 'update_by', 'updated_format')
    ordering = ['nendo', 'bu_code']

    def created_format(self, obj):
        return obj.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    def updated_format(self, obj):
        return obj.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    created_format.short_description = '作成日'
    updated_format.short_description = '更新日'

    # インポートエクスポート設定
    resource_class = BusyoResource
    formats = [base_formats.XLSX]   # 出力形式はxlsxのみ

    # 入力設定
    fields = ('nendo', 'bu_code', 'bu_name')

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

# 勤務地マスタ メンテナンス impoort/export 定義
class LocationResource(resources.ModelResource):
    class Meta:
        model = Location
        fields = ('nendo', 'location_code', 'location_name')
        import_id_fields = ('nendo', 'location_code',)     # キー項目
        skip_unchanged = True           # 変更のあったものだけ取込み
        use_bulk = True

# 勤務地 メンテナンス画面
class LocationAdmin(ImportExportMixin, admin.ModelAdmin):
    # 一覧設定
    list_display = ('nendo', 'location_code', 'location_name', 'created_by', 'created_format', 'update_by', 'updated_format')
    ordering = ['nendo', 'location_code']

    def created_format(self, obj):
        return obj.created_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    def updated_format(self, obj):
        return obj.updated_at.astimezone(timezone('Asia/Tokyo')).strftime('%Y/%m/%d %H:%M:%S')

    created_format.short_description = '作成日'
    updated_format.short_description = '更新日'

    # インポートエクスポート設定
    resource_class = LocationResource
    formats = [base_formats.XLSX]   # 出力形式はxlsxのみ

    # 入力設定
    fields = ('nendo', 'location_code', 'location_name')

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
admin.site.register(Ujf, UjfAdmin)
admin.site.register(Post, PostAdmin)
admin.site.register(Busyo, BusyoAdmin)
admin.site.register(Location, LocationAdmin)
from django.contrib import admin

from . import models


@admin.register(models.Verify)
class VerifyAdmin(admin.ModelAdmin):
    list_display = ('create_time', 'category', 'target_type', 'name', 'user', 'status', 'update_time')
    list_filter = ('status', )
    raw_id_fields = ('user', 'operator')
    search_fields = ("name",)

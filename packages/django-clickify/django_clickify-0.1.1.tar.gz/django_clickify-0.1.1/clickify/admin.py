from django.contrib import admin
from .models import TrackedLink, ClickLog


@admin.register(TrackedLink)
class TrackedLinkAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'target_url', 'created_at')
    search_fields = ('name', 'slug', 'target_url')
    prepopulated_fields = {'slug': ('name')}
    list_filter = ('created_at')


@admin.register(ClickLog)
class ClickLogAdmin(admin.ModelAdmin):
    list_display = ('target', 'ip_address', 'country', 'city', 'timestamp')
    search_fields = ('target__name', 'ip_address', 'country', 'city')
    list_filter = ('target', 'country', 'timestamp')
    readonly_fields = [field.name for field in ClickLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=...):
        return False

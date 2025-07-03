from django.contrib import admin
from .models import Technology, ProjectTemplate

@admin.register(Technology)
class TechnologyAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'description')
    search_fields = ('name', 'type')
    list_filter = ('type',)

@admin.register(ProjectTemplate)
class ProjectTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'backend_technology', 'frontend_technology')
    search_fields = ('name',)
    list_filter = ('backend_technology', 'frontend_technology')
    raw_id_fields = ('backend_technology', 'frontend_technology')

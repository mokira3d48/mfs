from django.contrib import admin
from .models import Dir


class AbstractFileModelAdmin(admin.ModelAdmin):
    """
    Administrative model of the server file system 
    server file system.
    """
    list_display = ['relpath', 'visibility', 'size', 'created_at']
    search_fields = ['relpath']
    list_filter = ['visibility']
    ordering = ['created_at']
    fields = [('relpath', 'size'),
              'parent_dir',
              'visibility',
              'created_at',
              'updated_at']


@admin.register(Dir)
class DirModelAdmin(admin.ModelAdmin):
    """
    Administrative model of the server directory system
    server file system.
    """
    list_display = ['relpath', 'visibility', 'created_at']
    search_fields = ['relpath']
    list_filter = ['visibility']
    ordering = ['created_at']
    fields = ['relpath',
              'visibility',
              'created_at',
              'updated_at']



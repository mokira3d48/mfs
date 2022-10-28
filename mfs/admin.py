from django.contrib import admin


class AbstractFileModelAdmin(admin.ModelAdmin):
    """
    Modèle administratif des fichiers du système 
    de fichier du serveur.
    """
    list_display = ['name', 'ext', 'size', 'visibility', 'filedir'];
    search_fields = ['name', 'ext'];
    list_filter   = ['visibility', 'filedir'];
    ordering      = ['created_at'];
    fields        = [('name', 'ext'), 'filedir', 'visibility'];


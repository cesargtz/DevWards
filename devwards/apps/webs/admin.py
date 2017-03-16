from django.contrib import admin
from .models import WebSite, Vote   # Importar los modelos, esto para que pueda ser visible para el administrador


@admin.register(WebSite)   # Registras el modelo WebSite
class WebSiteAdmin(admin.ModelAdmin):
    pass

@admin.register(Vote)   # Registras el modelo WebSite
class WebSiteAdmin(admin.ModelAdmin):
    pass

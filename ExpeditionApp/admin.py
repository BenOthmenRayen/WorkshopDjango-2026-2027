from django.contrib import admin
from .models import Expedition
# Register your models here.
@admin.register(Expedition)
class ExpeditionAdmin(admin.ModelAdmin):
    list_display=('reference','ville_depart','ville_arrive','poid_kg','date_souhaitée','statut','entreprise')
    list_filter=('statut','date_souhaitée')
    search_fields=('reference','ville_depart','ville_arrive','entreprise__raison_sociale')
    readonly_fields=('reference',)
    ordering=('-created_at',)
    list_per_page=10
    date_hierarchy='created_at'

from django.contrib import admin
from .models import Offre, Expedition
# Register your models here.
@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display=('prix','statut','expedition','transporteur','vehicule','date_proposition')
    list_display_links=('expedition',)
    list_filter=('prix',)
    list_editable=('prix',)
    search_fields=('prix',)
    ordering=('-date_proposition',)
    list_per_page=10
    date_hierarchy='date_proposition'


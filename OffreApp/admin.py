from django.contrib import admin
from .models import Offre, Expedition
# Register your models here.
from django.utils.html import format_html
@admin.register(Offre)
class OffreAdmin(admin.ModelAdmin):
    list_display = ('prix', 'statut_colore', 'expedition', 'transporteur', 'vehicule', 'date_proposition')
    list_display_links=('expedition',)
    list_filter=('prix',)
    list_editable=('prix',)
    search_fields=('prix',)
    ordering=('-date_proposition',)
    list_per_page=10
    date_hierarchy='date_proposition'
    fieldsets = (
        ('Détails de l\'offre', {'fields': ('expedition', 'transporteur', 'vehicule')}),
        ('Conditions', {'fields': ('prix', 'delai_jours')}),
        ('Suivi', {'fields': ('statut', 'date_proposition', 'created_at', 'updated_at')}),
    )
   
    autocomplete_fields = ('expedition', 'transporteur', 'vehicule')
    readonly_fields = ('created_at', 'updated_at', 'date_proposition')
    @admin.display(description='Statut')
    def statut_colore(self, obj):
        couleurs = {
            'proposee': '#F0AD4E', 'acceptee': '#5CB85C',
            'refusee': '#D9534F', 'retiree': '#777777',
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, '#999'), obj.get_statut_display(),
        )

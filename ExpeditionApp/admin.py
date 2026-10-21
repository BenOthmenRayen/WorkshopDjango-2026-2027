from django.contrib import admin, messages
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.utils.html import format_html
from .models import Expedition
from OffreApp.models import Offre
# Register your models here.
class EnRetardFilter(admin.SimpleListFilter):
    title = 'En retard'
    parameter_name = 'en_retard'
    def lookups(self, request, model_admin):
        return (
            ('oui', 'Oui'),
            ('non', 'Non'),
        )
    def queryset(self, request, queryset):
        if self.value() == 'oui':
            return queryset.filter(date_souhaitée__lt=timezone.now())
        elif self.value() == 'non':
            return queryset.filter(date_souhaitée__gte=timezone.now())
        return queryset

class OffreInline(admin.StackedInline):
    model = Offre
    extra = 0
    fk_name = 'expedition'
    readonly_fields = ('transporteur', 'vehicule', 'prix', 'delai_jours', 'statut')
    show_change_link = True
    can_delete = False

@admin.register(Expedition) 
class ExpeditionAdmin(admin.ModelAdmin):
    list_display=('reference','ville_depart','ville_arrive','poid_kg','date_souhaitée','statut_colore','entreprise')
    list_filter=('statut','date_souhaitée',EnRetardFilter)
    search_fields=('reference','ville_depart','ville_arrive','entreprise__raison_sociale')
    readonly_fields=('reference',)
    ordering=('-created_at',)
    list_per_page=10
    date_hierarchy='created_at'
    inlines = [OffreInline]

    fieldsets=(
                ('informations', {
                    'fields': ('ville_depart', 'ville_arrive')
                }),
                ('Expedition Information', {
                    'fields': ('poid_kg', 'date_souhaitée', 'statut', 'entreprise')
                }),
                ('dates', {
                    'fields': ('created_at', 'updated_at')
                })
            )
    readonly_fields = ('created_at', 'updated_at')
    actions = ['make_it_delivered']

    @admin.display(description='Statut', ordering='statut')
    def statut_colore(self, obj):
        couleurs = {
            'publiee': '#5BC0DE',
            'Attribue': '#337AB7',
            'attribue': '#337AB7',
            'en_cours': '#F0AD4E',
            'livrée': '#5CB85C',
            'Annulée': '#D9534F',
        }
        return format_html(
            '<span style="color:white;background:{};padding:3px 8px;border-radius:4px;">{}</span>',
            couleurs.get(obj.statut, '#999'), obj.get_statut_display(),
        )

    @admin.action(description='Marquer comme livrée')
    def make_it_delivered(self, request, queryset):
        liste=queryset.filter(statut='en_cours')
        liste_ignored_el=queryset.exclude(statut='en_cours').count()
        errors=[]
        nb_succes=0
        for expd in liste:
            expd.statut = 'livrée'
            try:
                expd.save()
                nb_succes+=1
            except ValidationError as error:
                errors.append(f"{expd.reference}: {error}")
        if nb_succes:
            self.message_user(request, f"{nb_succes} expéditions ont été marquées comme livrées avec succès.", messages.SUCCESS)
            
        if liste_ignored_el:
            self.message_user(request, f"{liste_ignored_el} expéditions ont été ignorées.", messages.WARNING)
        for e in errors:
            self.message_user(request, e, messages.ERROR)
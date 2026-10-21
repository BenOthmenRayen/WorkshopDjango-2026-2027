from datetime import timedelta

from django.contrib import admin
from django.db.models import Count
from django.shortcuts import render
from django.urls import path
from django.utils import timezone

from VehiculesApp.models import Vehicule
from ExpeditionApp.models import Expedition
from OffreApp.models import Offre
from .models import Utilisateur ,Entreprise
from django.contrib.auth.admin import UserAdmin
@admin.register(Utilisateur)
class AdminUtilisateur(admin.ModelAdmin):
    list_display = ('username', 'user_id', 'first_name', 'last_name', 'roles', 'email', 'is_staff', 'is_active')
    list_filter = ('email',)
    list_editable = ( 'last_name', 'first_name')
    search_fields = ('telephone','email')
    ordering = ('-created_at',)
    list_per_page = 10
    date_hierarchy = 'created_at'

    fieldsets=(
            ('informations', {
                'fields': ('username', 'first_name', 'last_name')
            }),
            ('User Information', {
                'fields': ('roles', 'email','is_staff')
            }),
            ('dates', {
                'fields': ('created_at', 'updated_at')
            })
        )
    readonly_fields = ('created_at', 'updated_at')
#admin.site.register(Utilisateur,AdminUtilisateur)  either this or the  decorator

#class vehiculeInline(admin.StackedInline):
class VehiculeInline(admin.TabularInline):
    model=Vehicule
    extra=1
    #fields=('',)
admin.site.site_title="TransConnect"
admin.site.site_header="dashboard admin TransConnect"
admin.site.index_title="Espace opérations TransConnect"

@admin.register(Entreprise)
class AdminEntreprise(admin.ModelAdmin):
    inlines = [VehiculeInline]
    list_display = ('matricule_fiscal', 'type_entreprise', 'adresse')
    list_filter = ('matricule_fiscal',)
    list_editable = ('type_entreprise', 'adresse')
    search_fields = ('matricule_fiscal',)
    ordering = ('-created_at',)
    list_per_page = 10
    date_hierarchy = 'created_at'
    fieldsets=(
        ('informations', {
            'fields': ('matricule_fiscal', 'raison_sociale')
        }),
        ('Entreprise Information', {
            'fields': ('type_entreprise', 'adresse','gerant')
        }),
        ('dates', {
            'fields': ('created_at', 'updated_at')
        })
    )
    readonly_fields = ('created_at', 'updated_at')
    
# Register your models here.


# ==================== Tableau de bord de contrôle d'intégrité ====================

def health_check_view(request):
    il_y_a_7_jours = timezone.now() - timedelta(days=7)

    # 1. Offres orphelines (proposee/acceptee sur une expédition qui n'est plus publiee/attribuee)
    orphelines = (
        Offre.objects
        .filter(statut__in=['proposee', 'acceptee'])
        .exclude(expedition__statut__in=['publiee', 'Attribue', 'attribue'])
        .select_related('expedition', 'transporteur')
    )

    # 2. Expéditions bloquées (publiee depuis plus de 7 jours)
    bloquees = (
        Expedition.objects
        .filter(statut='publiee', created_at__lt=il_y_a_7_jours)
        .select_related('entreprise')
    )

    # 3. Transporteurs sans flotte
    sans_flotte = (
        Entreprise.objects
        .filter(type_entreprise='transporteur')
        .annotate(nb_vehicules=Count('vehicules'))
        .filter(nb_vehicules=0)
    )

    # 4. Véhicules disponibles mais assignés à une offre acceptee
    incoherents = (
        Vehicule.objects
        .filter(disponibilite=True, offre__statut='acceptee')
        .select_related('entreprise')
        .distinct()
    )

    # 5. Doublons de proposition (plus d'une offre proposee par entreprise sur la même expédition)
    doublons = (
        Offre.objects
        .filter(statut='proposee')
        .values('transporteur__raison_sociale', 'expedition__reference')
        .annotate(nb=Count('id'))
        .filter(nb__gt=1)
    )

    controles = [
        {
            'titre': "Offres orphelines",
            'regle': "Règles 3 et 5 : une offre active n'existe que sur une expédition publiee/attribuee",
            'lignes': [f"{o.expedition.reference} ({o.expedition.statut}) — offre de "
                       f"{o.transporteur.raison_sociale} au statut {o.statut}" for o in orphelines],
        },
        {
            'titre': "Expéditions bloquées (publiee depuis plus de 7 jours)",
            'regle': "Suivi métier : une expédition publiée doit être attribuée dans un délai raisonnable",
            'lignes': [f"{e.reference} — {e.entreprise.raison_sociale}, publiée le "
                       f"{e.created_at:%d/%m/%Y}" for e in bloquees],
        },
        {
            'titre': "Transporteurs sans flotte",
            'regle': "Règles 1 et 2 : un transporteur doit avoir des véhicules pour proposer des offres",
            'lignes': [f"{e.raison_sociale} ({e.matricule_fiscal})" for e in sans_flotte],
        },
        {
            'titre': "Incohérence de disponibilité",
            'regle': "Règle 6 : un véhicule engagé sur une offre acceptée ne devrait plus être disponible",
            'lignes': [f"{v.immatriculation} ({v.type_vehicule}) — {v.entreprise.raison_sociale}"
                       for v in incoherents],
        },
        {
            'titre': "Doublons de proposition",
            'regle': "Règle 4 : une seule offre proposee par entreprise et par expédition",
            'lignes': [f"{d['expedition__reference']} — {d['transporteur__raison_sociale']} : "
                       f"{d['nb']} offres proposee" for d in doublons],
        },
    ]

    context = {
        **admin.site.each_context(request),
        'title': "Contrôle d'intégrité",
        'controles': controles,
    }
    return render(request, 'admin/health_check.html', context)


_get_urls_original = admin.site.get_urls

def get_urls_avec_health_check():
    urls_perso = [
        path('health-check/', admin.site.admin_view(health_check_view), name='health-check'),
    ]
    return urls_perso + _get_urls_original()

admin.site.get_urls = get_urls_avec_health_check
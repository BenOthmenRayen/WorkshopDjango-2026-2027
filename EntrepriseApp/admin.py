from django.contrib import admin
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
#admin.site.register(Utilisateur,AdminUtilisateur)  either this or the  decorator

@admin.register(Entreprise)
class AdminEntreprise(admin.ModelAdmin):
    list_display = ('matricule_fiscal', 'type_entreprise', 'adresse')
    list_filter = ('matricule_fiscal',)
    list_editable = ('type_entreprise', 'adresse')
    search_fields = ('matricule_fiscal',)
    ordering = ('-created_at',)
    list_per_page = 10
    date_hierarchy = 'created_at'

# Register your models here.

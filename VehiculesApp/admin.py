from django.contrib import admin
from .models import Vehicule

@admin.register(Vehicule)
class AdminVehicule(admin.ModelAdmin):
    list_display = ('immatriculation', 'type_vehicule', 'entreprise', 'disponibilite','capacite_kg')
    list_filter = ('type_vehicule',)
    list_editable = ('type_vehicule',)
    search_fields = ('immatriculation', 'type_vehicule')
    ordering = ('-created_at',)
    list_per_page = 10
    date_hierarchy = 'created_at'
    fieldsets=(
                        ('informations', {
                            'fields': ('immatriculation','type_vehicule','capacite_kg')
                        }),
                        ('vehicules Information', {
                            'fields': ('entreprise','disponibilite')
                        }),
                        ('dates', {
                            'fields': ('created_at', 'updated_at')
                        })
                    )
    readonly_fields = ('created_at', 'updated_at')
    
    
    



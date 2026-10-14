from django.db import models
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError


TYPES_VEHICULE = [
    ('camionnette', 'Camionnette / utilitaire léger'),
    ('fourgon', 'Fourgon'),
    ('camion_porteur', 'Camion porteur'),
    ('semi_remorque', 'Semi-remorque'),
]
class Vehicule(models.Model):
    immatriculation=models.CharField(max_length=15,unique=True)
    type_vehicule = models.CharField(max_length=14, choices=TYPES_VEHICULE)
    capacite_kg=models.PositiveIntegerField(validators=[MinValueValidator(1,"une capacité nulle ne peut pas être acceptée")])
    disponibilite=models.BooleanField(default=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',on_delete=models.CASCADE,related_name='vehicules')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.type_vehicule} ({self.immatriculation})"
    def clean(self):
        super().clean()
        if self.entreprise_id and self.entreprise.type_entreprise !='transporteur':
            raise ValidationError("un véhicule ne peut être rattraché qu'a une entreprise de type transporteur")
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
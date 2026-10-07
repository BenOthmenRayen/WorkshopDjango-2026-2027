from django.db import models
# Create your models here.

class Vehicule(models.Model):
    immatriculation=models.CharField(max_length=15,unique=True)
    type_vehicule=models.CharField(max_length=14,choices=[('camion','camion'),('fourgon','fourgon'),(('camion porteur','camion porteur')),('semi-remorque','semi-remorque')])
    capacite_kg=models.PositiveIntegerField()
    disponibilite=models.BooleanField(default=True)
    entreprise=models.ForeignKey('EntrepriseApp.Entreprise',on_delete=models.CASCADE,related_name='vehicules')

    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
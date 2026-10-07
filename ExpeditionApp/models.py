from django.db import models
from EntrepriseApp.models import Entreprise
# Create your models here.

class Expedition(models.Model):
    reference=models.CharField(max_length=20,editable=False)
    ville_depart=models.CharField(max_length=20)
    ville_arrive=models.CharField(max_length=20)
    date_souhaitée=models.DateTimeField()
    poid_kg=models.DecimalField(decimal_places=2,max_digits=10)
    statut=models.CharField(max_length=10,choices=[('Publiée','publiée'),('Attribue','attribue'),('en_cours',"En_cours"),('livrée','Livrée'),('Annulée','annulée')],default='publiée')
    entreprise=models.ForeignKey(Entreprise, on_delete=models.CASCADE, related_name='expeditions')
    created_at=models.DateTimeField(auto_now_add=True)
    description=models.CharField(max_length=100)
    updated_at=models.DateTimeField(auto_now=True)

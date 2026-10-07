from django.db import models
from django.contrib.auth.models import AbstractUser

class Utilisateur(AbstractUser):
    user_id=models.CharField(max_length=100,primary_key=True,editable=False)
    email=models.EmailField(unique=True)
    telephone=models.CharField(max_length=15,blank=True,null=True)
    roles=models.CharField(max_length=12,choices=[('chargeur','chargeur'),('transporteur','Transporteur '),(' admin',' administrateur')])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

class Entreprise(models.Model):
    raison_sociale=models.CharField(max_length=100)
    matricule_fiscale=models.CharField(max_length=17,unique=True)
    type_entreprise=models.CharField(max_length=12,choices=[('chargeur','chargeur'),('transporteur','Transporteur ')],default='chargeur')
    adresse=models.TextField()
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(Utilisateur,on_delete=models.CASCADE,related_name='entreprise')
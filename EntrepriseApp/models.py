from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
def validate_email(value):
    if not value:
        raise ValidationError("L'email ne peut pas être vide")
    if not value.endswith('@gmail.com'):
        raise ValidationError("Format d'email invalide, doit se terminer par @gmail.com")
    
def regexValidator(regex,message):
    return RegexValidator(regex=regex,message=message)

class Utilisateur(AbstractUser):
    user_id=models.CharField(max_length=100,primary_key=True,editable=False)
    email=models.EmailField(unique=True,validators=[validate_email])
    telephone=models.CharField(max_length=15,blank=True,null=True)
    roles=models.CharField(max_length=12,choices=[('chargeur','chargeur'),('transporteur','Transporteur '),(' admin',' administrateur')])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)


class Entreprise(models.Model):
    raison_sociale=models.CharField(max_length=100)
    matricule_fiscal=models.CharField(max_length=17,unique=True, validators=[regexValidator(regex='\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',message='invalide format')])
    type_entreprise=models.CharField(max_length=12,choices=[('chargeur','chargeur'),('transporteur','Transporteur ')],default='chargeur')
    adresse=models.CharField(validators=[MinLengthValidator(20,"L'adresse doit contenir au moins 20 caractères")])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(Utilisateur,on_delete=models.CASCADE,related_name='entreprise')


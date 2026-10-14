from django.utils import timezone
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
def validate_email(value):
    if not value:
        raise ValidationError("L'email ne peut pas être vide")
    if not value.endswith('@gmail.com'):
        raise ValidationError("Format d'email invalide, doit se terminer par @gmail.com")
    def save(self, *args, **kwargs):
            self.full_clean()
            super().save(*args, **kwargs)
    
def regexValidator(regex,message):
    return RegexValidator(regex=regex,message=message)

class Utilisateur(AbstractUser):
    user_id=models.CharField(max_length=100,primary_key=True,editable=False)
    email=models.EmailField(unique=True,validators=[validate_email])
    telephone=models.CharField(max_length=15,blank=True,null=True)
    roles=models.CharField(max_length=12,choices=[('chargeur','chargeur'),('transporteur','Transporteur '),(' admin',' administrateur')],default='chargeur')
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    
    @classmethod
    def _generate_user_id(cls):
        annee = timezone.now().strftime('%y')
        prefixe = f"{annee}user"

        dernier = (
            cls.objects
            .filter(user_id__startswith=prefixe)
            .order_by('-user_id')
            .first()
        )
        compteur = int(dernier.user_id[-2:]) + 1 if dernier else 0

        if compteur > 99:
            raise ValueError(
                f"Limite de 100 utilisateurs atteinte pour l'année 20{annee}."
            )

        return f"{prefixe}{compteur:02d}"

    def save(self, *args, **kwargs):
                if not self.user_id:self.user_id=self._generate_user_id()
                self.full_clean()
                super().save(*args, **kwargs)
    


class Entreprise(models.Model):
    raison_sociale=models.CharField(max_length=100)
    matricule_fiscal=models.CharField(max_length=17,unique=True, validators=[regexValidator(regex='\d{7}[/ -]?[A-Za-z][/ -]?[ABDNPEabdnpe][/ -]?[MPCNEmpcne][/ -]?\d{3}$',message='invalide format')])
    type_entreprise=models.CharField(max_length=12,choices=[('chargeur','chargeur'),('transporteur','Transporteur ')],default='chargeur')
    adresse=models.CharField(validators=[MinLengthValidator(20,"L'adresse doit contenir au moins 20 caractères")])
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)
    gerant=models.OneToOneField(Utilisateur,on_delete=models.CASCADE,related_name='entreprise')




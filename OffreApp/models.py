
from django.db import models
from EntrepriseApp.models import Entreprise
from ExpeditionApp.models import Expedition
from VehiculesApp.models import Vehicule
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
class Offre(models.Model):
    STATUT_CHOICES = [
        ('proposee', 'Proposée'),
        ('acceptee', 'Acceptée'),
        ('refusee', 'Refusée'),
        ('retiree', 'Retirée'),
    ]
    """prix = models.CharField(max_length=10) charfield prix=decimal"""
    prix=models.DecimalField(decimal_places=2,max_digits=10, validators=[MinValueValidator(1,message='Le prix doit être supérieur à 0')])
    """delai_jours = models.IntegerField()  delai_jours=PositiveIntegerField"""
    delai_jours=models.PositiveIntegerField(validators=[MinValueValidator(1,message='Une valeur supérieur ou égale à 1 est requise')])
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='proposee')
    """date_proposition = models.DateField(auto_now=True) auto_now_add=True"""
    date_proposition = models.DateField(auto_now_add=True)
    expedition = models.ForeignKey(Expedition, on_delete=models.CASCADE)
    transporteur = models.ForeignKey(Entreprise, on_delete=models.CASCADE)
    """vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE, null=True)"""
    vehicule = models.ForeignKey(Vehicule,on_delete=models.CASCADE)
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def clean(self):
        super().clean()
        #Règle 1
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({
                'transporteur': "Seule une entreprise de type transporteur peut faire une offre."
            })
        #Règle 2
        if self.vehicule_id and self.transporteur_id:
            if self.vehicule.entreprise_id != self.transporteur_id:
                raise ValidationError({
                'vehicule': "Ce véhicule n'appartient pas au transporteur de l'offre."
            })
        #Règle 3
        if self._state.adding and self.expedition_id:
            if self.expedition.statut != 'publiee':
                raise ValidationError({
                'expedition': "Cette expédition n'accepte plus de nouvelles offres."
            })

        #Règle 4
        if self.statut == 'proposee' and self.expedition_id and self.transporteur_id:
            doublon = Offre.objects.filter(
            expedition_id=self.expedition_id,
            transporteur_id=self.transporteur_id,
            statut='proposee',
        ).exclude(pk=self.pk).exists()

        if doublon:
            raise ValidationError(
                "Ce transporteur a déjà une offre active sur cette expédition."
            )
        #Règle 5
        if self.statut == 'acceptee':
            # 1. L'expédition devient attribuée
            self.expedition.statut = 'attribuee'
            self.expedition.save()

            # 2. Les autres offres proposées deviennent refusées
            for autre in Offre.objects.all():
                if (autre.pk != self.pk
                        and autre.expedition_id == self.expedition_id
                        and autre.statut == 'proposee'):
                    autre.statut = 'refusee'
                    autre.save()
        #Règle 6
        if self.pk is None and self.vehicule_id:
            if not self.vehicule.disponibilite:
                raise ValidationError({
                'vehicule': "Ce véhicule n'est pas disponible."
            })
        #Règle 7
        if self.vehicule_id and self.expedition_id:
            if not self.vehicule.accepte_poids(self.expedition.poids_kg):
                raise ValidationError(
                "Le type de véhicule n'est pas compatible avec le poids de l'expédition."
            )
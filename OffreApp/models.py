
from decimal import Decimal

from django.db import models
from EntrepriseApp.models import Entreprise
from ExpeditionApp.models import Expedition
from VehiculesApp.models import Vehicule
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator

PLAGES_POIDS_PAR_TYPE_VEHICULE = {
    'camionnette': (Decimal(0), Decimal(1500)),
    'fourgon': (Decimal(1500), Decimal(3500)),
    'camion_porteur': (Decimal(3500), Decimal(19000)),
    'semi_remorque': (Decimal(19000), Decimal(26000)),
}
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
    def __str__(self):
        return f"Offre de {self.transporteur.raison_sociale} sur {self.expedition.reference}"
    def clean(self):
        super().clean()

        
        if self.transporteur_id and self.transporteur.type_entreprise != 'transporteur':
            raise ValidationError({
                'transporteur': "Une offre ne peut être créée que par une entreprise de type transporteur."
            })

        
        if self.vehicule_id and self.transporteur_id and self.vehicule.entreprise_id != self.transporteur_id:
            raise ValidationError({
                'vehicule': "Le véhicule doit appartenir à l'entreprise transporteur de l'offre."
            })

        
        if self.pk is None and self.expedition_id and self.expedition.statut != 'publiee':
            raise ValidationError({
                'expedition': "Cette expédition ne peut plus recevoir de nouvelles offres (statut différent de 'publiee')."
            })

        
        if self.statut == 'proposee' and self.transporteur_id and self.expedition_id:
            duplicate_exists = Offre.objects.filter(
                transporteur_id=self.transporteur_id,
                expedition_id=self.expedition_id,
                statut='proposee',
            ).exclude(pk=self.pk).exists()
            if duplicate_exists:
                raise ValidationError({
                    'statut': "Cette entreprise a déjà une offre 'proposee' active sur cette expédition."
                })

        
        if self.pk is None and self.vehicule_id and not self.vehicule.disponible:
            raise ValidationError({
                'vehicule': "Ce véhicule n'est pas disponible et ne peut pas être proposé sur une nouvelle offre."
            })

        
        if self.vehicule_id and self.expedition_id:
            plage = PLAGES_POIDS_PAR_TYPE_VEHICULE.get(self.vehicule.type_vehicule)
            poids_kg = self.expedition.poids_kg
            if plage and not (plage[0] < poids_kg <= plage[1]):
                raise ValidationError({
                    'vehicule': (
                        f"Le type de véhicule '{self.vehicule.type_vehicule}' n'est pas adapté "
                        f"au poids de l'expédition ({poids_kg} kg)."
                    )
                })
    def save(self, *args, **kwargs):
        self.full_clean()
        previous_statut = None
        if self.pk:
            previous_statut = Offre.objects.filter(pk=self.pk).values_list('statut', flat=True).first()

        with transaction.atomic():
            super().save(*args, **kwargs)
            if self.statut == 'acceptee' and previous_statut != 'acceptee':
                self._appliquer_cascade_acceptation()

    def _appliquer_cascade_acceptation(self):
        Expedition = apps.get_model('ExpeditionsApp', 'Expedition')
        Expedition.objects.filter(pk=self.expedition_id).update(
            statut='attribuee'
        )
        Offre.objects.filter(
            expedition_id=self.expedition_id,
            statut='proposee',
        ).exclude(pk=self.pk).update(statut='refusee', updated_at=timezone.now())
   

    
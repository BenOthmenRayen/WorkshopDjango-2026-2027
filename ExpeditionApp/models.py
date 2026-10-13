from django.db import models
from EntrepriseApp.models import Entreprise
import django.utils.timezone as timezone

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
    def save(self, *args, **kwargs):
        self.reference=self._generate_reference()
        return super().save()
    @classmethod
    def _generate_reference(cls):
        annee = timezone.now().strftime("%y")
        prefixe = f"EXP-{annee}-"
        last_element = (cls.objects.filter(reference__startswith=prefixe).order_by('-reference').first())
        compteur=int(last_element.reference[-5:])+1 if last_element else 1
        if compteur >9999:
            raise ValueError(f"Le compteur a dépassé la limite de 9999 par annee {annee}")
        return f"{prefixe}{compteur:05d}"


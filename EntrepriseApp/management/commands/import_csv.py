"""
Commande de gestion : remplit la base TransConnect à partir des fichiers CSV du dossier data/.

    uv run python manage.py import_csv            # import normal
    uv run python manage.py import_csv --reset    # vide les données (sauf superusers) puis réimporte

Principe : chaque objet passe par full_clean() + save(), JAMAIS par bulk_create() ou update().
Ainsi les validateurs (gmail, regex matricule, adresse >= 20...) et les règles métier
(clean/save des modèles : transporteur/chargeur, cascade d'acceptation...) s'exécutent pour chaque ligne.
"""
import csv
from datetime import datetime
from decimal import Decimal
from pathlib import Path

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from EntrepriseApp.models import Utilisateur, Entreprise
from VehiculesApp.models import Vehicule
from ExpeditionApp.models import Expedition
from OffreApp.models import Offre


def lire_csv(nom_fichier):
    """Lit data/<nom_fichier> et renvoie une liste de dictionnaires (une ligne = un dict)."""
    chemin = Path(settings.BASE_DIR) / 'data' / nom_fichier
    if not chemin.exists():
        raise CommandError(f"Fichier introuvable : {chemin}")
    with open(chemin, encoding='utf-8-sig', newline='') as f:
        premiere_ligne = f.readline()
        f.seek(0)
        separateur = ';' if ';' in premiere_ligne else ','   # Excel FR enregistre avec ';'
        return list(csv.DictReader(f, delimiter=separateur))


def cle_de_choix(modele, nom_champ, valeur):
    """Retrouve la clé exacte d'un champ à choix (ignore les espaces en trop)."""
    choix = modele._meta.get_field(nom_champ).choices
    correspondance = {cle.strip(): cle for cle, _ in choix}
    return correspondance.get(valeur.strip(), valeur)


class Command(BaseCommand):
    help = "Remplit la base TransConnect à partir des fichiers CSV du dossier data/"

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true',
                            help="Supprime les données existantes (sauf les superusers) avant l'import")

    def enregistrer(self, objet, fichier, numero_ligne):
        """full_clean() + save() avec un message d'erreur clair en cas de problème."""
        try:
            objet.full_clean()
            objet.save()
        except ValidationError as erreur:
            raise CommandError(f"{fichier}, ligne {numero_ligne} : {erreur.message_dict}")

    @transaction.atomic   # tout ou rien : à la moindre erreur, rien n'est enregistré
    def handle(self, *args, **options):
        if options['reset']:
            Offre.objects.all().delete()
            Expedition.objects.all().delete()
            Vehicule.objects.all().delete()
            Entreprise.objects.all().delete()
            Utilisateur.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING("Données existantes supprimées (superusers conservés)."))
        elif Entreprise.objects.exists():
            raise CommandError("La base contient déjà des entreprises. Relancez avec --reset pour réimporter.")

        # ---------- 1. Utilisateurs ----------
        utilisateurs = {}
        for n, ligne in enumerate(lire_csv('utilisateurs.csv'), start=2):
            u = Utilisateur(
                username=ligne['username'],
                first_name=ligne['first_name'],
                last_name=ligne['last_name'],
                email=ligne['email'],
                telephone=ligne['telephone'],
                roles=cle_de_choix(Utilisateur, 'roles', ligne['roles']),
            )
            u.set_password(ligne['password'])           # mot de passe haché, jamais en clair
            self.enregistrer(u, 'utilisateurs.csv', n)  # Utilisateur.save() génère aussi le user_id (26userNN)
            utilisateurs[u.username] = u
        self.stdout.write(f"  {len(utilisateurs)} utilisateurs")

        # ---------- 2. Entreprises ----------
        entreprises = {}
        for n, ligne in enumerate(lire_csv('entreprises.csv'), start=2):
            e = Entreprise(
                raison_sociale=ligne['raison_sociale'],
                matricule_fiscal=ligne['matricule_fiscal'],
                type_entreprise=ligne['type_entreprise'],
                adresse=ligne['adresse'],
                gerant=utilisateurs[ligne['gerant_username']],
            )
            self.enregistrer(e, 'entreprises.csv', n)   # Entreprise n'a pas de save() perso : full_clean() ici
            entreprises[e.matricule_fiscal] = e
        self.stdout.write(f"  {len(entreprises)} entreprises")

        # ---------- 3. Véhicules ----------
        vehicules = {}
        for n, ligne in enumerate(lire_csv('vehicules.csv'), start=2):
            v = Vehicule(
                immatriculation=ligne['immatriculation'],
                type_vehicule=ligne['type_vehicule'],
                capacite_kg=int(ligne['capacite_kg']),
                disponibilite=ligne['disponibilite'].strip().lower() == 'true',
                entreprise=entreprises[ligne['entreprise_matricule']],
            )
            self.enregistrer(v, 'vehicules.csv', n)
            vehicules[v.immatriculation] = v
        self.stdout.write(f"  {len(vehicules)} véhicules")

        # ---------- 4. Expéditions (toutes créées 'publiee' pour pouvoir recevoir des offres : règle 3) ----------
        expeditions, statuts_finaux = {}, {}
        lignes_exp = lire_csv('expeditions.csv')
        for n, ligne in enumerate(lignes_exp, start=2):
            date = datetime.strptime(ligne['date_souhaitee'], '%Y-%m-%d %H:%M')
            exp = Expedition(
                ville_depart=ligne['ville_depart'],
                ville_arrive=ligne['ville_arrive'],
                poid_kg=Decimal(ligne['poid_kg']),
                description=ligne['description'],
                statut='publiee',
                entreprise=entreprises[ligne['entreprise_matricule']],
            )
            setattr(exp, 'date_souhaitée', timezone.make_aware(date))   # nom du champ avec accent
            self.enregistrer(exp, 'expeditions.csv', n)                  # save() génère la référence EXP-AA-NNNNN
            expeditions[ligne['cle']] = exp
            statuts_finaux[ligne['cle']] = ligne['statut_final'].strip()
        self.stdout.write(f"  {len(expeditions)} expéditions")

        # ---------- 5. Offres (toutes créées 'proposee') ----------
        offres = []
        for n, ligne in enumerate(lire_csv('offres.csv'), start=2):
            o = Offre(
                expedition=expeditions[ligne['expedition_cle']],
                transporteur=entreprises[ligne['transporteur_matricule']],
                vehicule=vehicules[ligne['vehicule_immatriculation']],
                prix=Decimal(ligne['prix']),
                delai_jours=int(ligne['delai_jours']),
                statut='proposee',
            )
            self.enregistrer(o, 'offres.csv', n)   # Offre.clean() vérifie les règles 1, 2, 3, 4, 6, 7
            offres.append((n, o, ligne['statut_final'].strip()))
        self.stdout.write(f"  {len(offres)} offres")

        # ---------- 6. Acceptations : save() déclenche la cascade (règle 5) ----------
        for n, o, statut in offres:
            if statut == 'acceptee':
                o.statut = 'acceptee'
                self.enregistrer(o, 'offres.csv', n)

        # ---------- 7. Autres statuts d'offres (retiree, refusee non couvertes par la cascade) ----------
        for n, o, statut in offres:
            o.refresh_from_db()   # la cascade a pu modifier l'offre en base
            if statut and o.statut != statut:
                o.statut = statut
                self.enregistrer(o, 'offres.csv', n)

        # ---------- 8. Statut final des expéditions (vide = laisser ce que les règles métier ont décidé) ----------
        for cle, exp in expeditions.items():
            exp.refresh_from_db()   # la cascade a pu passer l'expédition à 'attribue'
            statut = cle_de_choix(Expedition, 'statut', statuts_finaux[cle]) if statuts_finaux[cle] else ''
            if statut and exp.statut != statut:
                exp.statut = statut
                self.enregistrer(exp, 'expeditions.csv', cle)

        # ---------- Résumé ----------
        self.stdout.write(self.style.SUCCESS("\nImport terminé. Expéditions :"))
        for exp in Expedition.objects.order_by('reference'):
            nb = Offre.objects.filter(expedition=exp).count()
            self.stdout.write(f"  {exp.reference}  {exp.ville_depart:>9} -> {exp.ville_arrive:<9} "
                              f"statut={exp.statut:<9} offres={nb}")

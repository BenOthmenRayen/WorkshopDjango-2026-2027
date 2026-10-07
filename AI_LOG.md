## Entrée 2026-10-2
- Outil IA utilisé : Claude (Anthropic)
- Prompt : « Analyser le snippet code du modèle Offre fourni dans le workshop TransConnect. Identifie les 4 anomalies par rapport au cahier des charges communiqué et proposer les solutions avec les justifications. » (cahier des charges et snippet joints)
- Sortie obtenue (résumé) : Claude a repéré 4 anomalies dans le modèle, signalé un point en plus (le `null=True` sur `vehicule`) et proposé une version corrigée de `Offre`, avec `STATUT_CHOICES`, `created_at` / `updated_at` et un `save()` qui gère l'acceptation d'une offre.
- Écarts identifiés vs cahier des charges :
  1. `prix` est en `CharField(max_length=10)`, alors que le sujet demande un `DecimalField`.
  2. `delai_jours` est en `IntegerField`, alors que le sujet demande un `PositiveIntegerField`.
  3. `date_proposition` utilise `auto_now=True`, alors qu'il faut `auto_now_add=True`.
  4. Le `save()` ne fait qu'appeler `super().save()`, donc accepter une offre ne déclenche rien, alors que le sujet parle d'effets en cascade.
  5. En plus : `vehicule` a `null=True`, alors qu'une offre doit être liée à un véhicule du transporteur. Il manque aussi `STATUT_CHOICES`, `created_at` et `updated_at`.
- Correction apportée et justification :
  1. `DecimalField(max_digits=10, decimal_places=2)`. Avec un `CharField`, on ne peut pas trier ni faire de sommes ou de comparaisons sur les prix, et n'importe quelle chaîne est acceptée.
  2. `PositiveIntegerField()`. Un délai en jours ne peut pas être négatif, et Django ajoute une contrainte en base.
  3. `auto_now_add=True`. Avec `auto_now`, la date serait écrasée à chaque sauvegarde, par exemple quand l'offre passe à `acceptee`, alors qu'on veut la date de la proposition.
  4. Logique ajoutée dans `save()` avec `transaction.atomic()` : si le statut est `acceptee`, l'expédition passe à `attribuee` et les autres offres `proposee` de cette expédition passent à `refusee`. Les effets en cascade ne sont pas détaillés dans la Part 1 du sujet, donc c'est une hypothèse à vérifier.
  5. Suppression de `null=True`, définition de `STATUT_CHOICES` et ajout de `created_at` et `updated_at`, comme le sujet l'impose pour tous les modèles.
# Deal Intelligence Copilot

## Objectif

Deal Intelligence Copilot transforme un pitch entrant et des sources publiques ciblées en brief de pré-analyse VC sourcé, avec une évaluation en entrant en adéquation avec la thèse d’investissement.

## Périmètre du MVP

- Interface : application web simple.
- Entrées : pitch ou e-mail, nom de la startup, site officiel et nom du dirigeant facultatif.
- Recherche : site officiel et quelques sources publiques limitées.
- Sortie : fiche de deal, sources, questions de diligence et score d’adéquation.
- Données : uniquement fictives ou publiques.
- Décision : l’outil ne prend jamais une décision d’investissement.
  Une validation humaine reste obligatoire.

## Hors périmètre

- Connexion à une boîte e-mail ou à un CRM.
- Scraping massif du web, de LinkedIn ou de bases de données payantes.
- Utilisation de données confidentielles.
- Décision automatisée d’investissement.

## État du projet

Ce projet est réalisé dans le cadre du Family Ventures AI Agent Challenge.

## Tests de scénarios

| Scénario | Nature des données | Sources analysées | Résultat |
|---|---|---|---|
| Upcyclea | Démonstration construite à partir d'informations publiques | Pitch, site officiel, article Batiactu | 9/10 ; plusieurs critères triangulés |
| GreenLedger | Cas fictif | Pitch uniquement | 10/10 ; adéquation déclarée, non corroborée |
| CityMoods | Cas fictif volontairement hors thèse | Pitch uniquement | 0/10 ; absence d'éléments compatibles avec les critères configurés |

### Interprétation

Le score mesure uniquement la correspondance avec la thèse configurée.
Le niveau de confiance indique séparément si les éléments sont déclarés dans le pitch,
corroborés par le site officiel, ou triangulés avec une source publique complémentaire.

Le prototype ne formule pas de recommandation d'investissement.
Toute décision nécessite une revue humaine.
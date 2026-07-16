# Guide Produit OpsForge

## OpsForge En Une Phrase

OpsForge est une console locale mono-operateur qui permet de declarer, qualifier, traiter et auditer des incidents sur un catalogue de services de demonstration.

## A Quel Probleme Le Produit Repond

Dans une equipe d'exploitation, plusieurs signaux peuvent annoncer un probleme : une sauvegarde echoue, un service ralentit ou une API ne repond plus. Le signal seul ne raconte pas qui prend le probleme en charge, ce qui a ete verifie, quelle procedure a ete suivie ni comment la resolution a ete confirmee.

OpsForge rassemble ce parcours dans une meme interface :

```text
Service -> Alerte -> Incident -> Runbook -> Journal d'audit
```

L'outil aide l'operateur a repondre a cinq questions :

1. Quel service est concerne ?
2. Quel signal a ete detecte ?
3. Ce signal necessite-t-il un incident ?
4. Quelle procedure peut aider au diagnostic ou a la resolution ?
5. Quelles actions et quels resultats peuvent etre prouves ensuite ?

OpsForge n'est ni un outil de ticketing client, ni un clone de PagerDuty, ni une plateforme SaaS de production. Son perimetre est volontairement local, mono-operateur et demonstratif.

## Les Objets Metier

### Service

Un service est un composant logique represente dans OpsForge, par exemple `Backup Service` ou `Payment Service`.

Son statut metier est saisi pour la demonstration. Il ne provient pas automatiquement de Prometheus.

### Alerte

Une alerte est un signal qui indique une anomalie potentielle. Elle appartient eventuellement a un service et suit le cycle :

```text
new -> acknowledged -> resolved
```

Acquitter une alerte signifie que l'operateur l'a vue. La resoudre signifie que le signal est clos. Une alerte resolue n'est pas rouverte dans cette version.

### Incident

Un incident est un probleme officiellement pris en charge. Il peut provenir d'une alerte ou etre declare manuellement.

Il suit le cycle :

```text
open -> investigating -> resolved
```

Une alerte ne peut avoir qu'un seul incident actif. Resoudre l'incident ne resout pas automatiquement son alerte, car le cycle du signal et celui de la prise en charge restent distincts.

### Runbook

Un runbook est une procedure de diagnostic ou de traitement.

- Un runbook manuel contient des instructions et une checklist. L'operateur confirme les etapes et le resultat.
- Un runbook automatise appelle uniquement une action Python connue et approuvee par OpsForge.

OpsForge n'accepte et n'execute aucun script ou commande systeme arbitraire.

### Journal D'Audit

Le journal d'audit enregistre l'acteur, l'action, l'objet concerne, l'heure et les details utiles. Sur un incident, ces traces composent une timeline lisible.

## Navigation Operateur

### Vue D'Ensemble

La page `/overview` indique ce qui demande une attention immediate : incidents actifs ou critiques, nouvelles alertes, alertes sans incident, services en difficulte, activite recente et etat reel de la plateforme OpsForge.

### Alertes

La page `/alerts` est la file des signaux. Elle permet de rechercher, filtrer, lire le message complet, acquitter, ouvrir l'incident lie ou resoudre une alerte. Une nouvelle alerte de demonstration peut etre creee sans passer par Swagger.

### Incidents

La page `/incidents` est la file de prise en charge. Chaque incident ouvre un Command Center qui regroupe le contexte, le responsable, les transitions de statut, les runbooks compatibles, les executions et la timeline.

### Services

La page `/services` est le catalogue des composants representes. Elle separe la gestion de reference du traitement urgent des incidents et rappelle que les statuts affiches sont simules.

### Runbooks

La page `/runbooks` presente les procedures, leur mode, leur contexte requis, leur niveau de risque et leur historique. Elle permet de creer et maintenir des procedures dans les limites de securite du produit.

### Activite

La page `/activity` est le journal d'audit global. Elle permet de retrouver qui a fait quoi, quand et sur quel objet.

### Monitoring

La page `/monitoring` separe explicitement :

- les controles reels de la plateforme : `/health`, `/ready`, `/metrics`, Prometheus, Grafana et `OpsForgeApiDown` ;
- les donnees metier simulees : statut de `Backup Service`, alertes et certaines actions de runbook.

Prometheus ne cree pas automatiquement d'alerte metier dans OpsForge dans cette version.

### Aide

La page `/help` contient les premiers pas, le scenario guide, le glossaire, l'architecture simplifiee et les limites connues.

## Scenario Principal De Demonstration

Le scenario principal est generique et ne contient aucune donnee professionnelle reelle :

```text
Backup Service
-> echec de sauvegarde de demonstration
-> alerte critique
-> incident de sauvegarde
-> investigation
-> runbook de diagnostic
-> resultat audite
-> resolution de l'incident
-> resolution separee de l'alerte
```

Le parcours detaille a executer avant l'oral se trouve dans [`PHASE6_MANUAL_TEST.md`](PHASE6_MANUAL_TEST.md).

## Reel Et Simule

| Element | Nature actuelle |
| --- | --- |
| API FastAPI et base PostgreSQL | Reel |
| Creation et transitions des objets | Reel |
| Audit et historique des executions | Reel |
| `/health`, `/ready` et `/metrics` | Reel |
| Deploiement k3d, Prometheus et Grafana | Reel dans l'environnement local valide |
| Regle Prometheus `OpsForgeApiDown` | Reelle dans k3d |
| Statut des services metier | Simule et saisi dans OpsForge |
| Alertes metier | Creees ou semees pour la demonstration |
| Controle de sauvegarde et redemarrage de service | Simules, sans commande hote |
| Rapport d'incident | Genere a partir des donnees OpsForge |

## Presentation Courte Pour Le Jury

> OpsForge est une console locale de gestion d'incidents. Un signal est rattache a un service, qualifie comme alerte, transforme en incident lorsqu'une prise en charge est necessaire, traite avec une procedure controlee, puis chaque decision et chaque resultat sont traces. Autour du produit, j'ai industrialise les tests, l'image Docker, le deploiement k3d, la sauvegarde PostgreSQL et le monitoring Prometheus/Grafana. Le projet montre donc a la fois une application metier exploitable et son cycle DevOps.

## Limites Assumees

- Pas d'authentification ni de gestion de comptes.
- Pas de multi-tenant ni de collaboration temps reel.
- Pas d'execution arbitraire de scripts.
- Pas de synchronisation automatique Prometheus vers les alertes metier.
- Pas de migration Alembic ; une compatibilite additive de demarrage accompagne encore `metadata.create_all()`.
- Pas de registre d'images ni de deploiement Kubernetes automatise depuis CI.
- Pas de notification Alertmanager.

Ces limites sont des choix de perimetre connus, pas des fonctions pretendues puis absentes.

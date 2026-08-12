# Dossier de projet — OpsForge

## Titre professionnel visé : Administrateur système DevOps (niveau 6)

**Code titre : TP-01414 — RNCP36061**

| |     |
|---|---|
| **Candidat** | Dyllan Thouvignon |
| **Projet** | OpsForge — console locale de gestion d'incidents et sa chaîne DevOps de bout en bout, en local |
| **Type de projet** | Projet fil rouge indépendant réalisé dans le cadre de la préparation au titre, avec cahier des charges conçu par le candidat |
| **Organisme de formation** | Liora (ex DataScientest) |
| **Entreprise d'alternance** | BlueBearsIT (entreprise d'alternance uniquement : OpsForge n'est ni commandité, ni utilisé par elle — voir section 2.1) |
| **Session d'examen** | 7 septembre 2026 à 09h30 — Campus Omnes Cœur Défense II, Courbevoie |
| **Dépôt Git** | `ThDyllan/opsforge` — état technique gelé : branche `phase6-operator-ux`, commit `8ab0f70` |
| **Version du dossier** | Brouillon v1 — contenu à relire, mise en page et captures à finaliser |

---

## Sommaire

- **Introduction**
1. **Liste des compétences du référentiel couvertes par le projet**
   - 1.1 Les trois compétences obligatoires
   - 1.2 Matrice compétences ↔ critères ↔ réalisations ↔ preuves ↔ limites
   - 1.3 Compétences partiellement mises en pratique
   - 1.4 Compétences non couvertes par le projet
2. **Cahier des charges**
   - 2.1 Contexte et origine du projet
   - 2.2 Problématique et objectifs
   - 2.3 Utilisateur cible et cas d'usage
   - 2.4 Besoins fonctionnels
   - 2.5 Besoins techniques
   - 2.6 Contraintes
   - 2.7 Livrables et critères d'acceptation
   - 2.8 Hors périmètre (exclusions volontaires)
   - 2.9 Évolution du périmètre : l'histoire réelle du projet
3. **Spécifications techniques du projet**
   - 3.1 Vue d'ensemble de l'architecture
   - 3.2 L'application : domaine métier et modèle de données
   - 3.3 Deux chaînes distinctes : intégration continue et automatisation d'infrastructure
   - 3.4 La couche conteneurs
   - 3.5 La couche Kubernetes (k3d)
   - 3.6 La couche supervision
   - 3.7 Sauvegarde et restauration
   - 3.8 Sécurité
   - 3.9 Environnements et versions
4. **Démarche de travail et outils utilisés**
   - 4.1 Une démarche par phases, chacune avec sa Definition of Done
   - 4.2 Le protocole appliqué avant / pendant / après chaque phase
   - 4.3 L'évolution du workflow Git
   - 4.4 Outillage
   - 4.5 Collaborations
5. **Réalisations significatives (scripts et configurations argumentés)**
   - 5.1 Instrumentation Prometheus de l'application
   - 5.2 Règle d'alerte `OpsForgeApiDown`
   - 5.3 Image Docker durcie de l'API
   - 5.4 Manifests Kubernetes durcis (Deployment API et StatefulSet PostgreSQL)
   - 5.5 Pipeline d'intégration continue GitHub Actions
   - 5.6 Playbook Ansible d'automatisation du déploiement
   - 5.7 Control node Ansible conteneurisé (`ansible/run.sh`)
   - 5.8 Scripts de sauvegarde et de restauration PostgreSQL
6. **Situation de travail ayant nécessité une recherche**
   - Le fichier `ansible.cfg` ignoré : diagnostic, recherche, correction, validation
7. **Synthèse des validations et preuves**
8. **Limites assumées et pistes d'évolution**
9. **Conclusion**
- **Annexe A** — Chronologie du projet (issue de l'historique Git)
- **Annexe B** — Liste consolidée des captures d'écran du dossier
- **Annexe C** — Glossaire

---

## Introduction

Je m'appelle Dyllan Thouvignon. Mon parcours était initialement orienté développement, notamment à travers un BTS SIO option SLAM ; j'ai ensuite suivi une formation DevOps en alternance chez BlueBearsIT (contrat d'apprentissage d'octobre 2024 à mai 2026, CFA DataScientest — aujourd'hui Liora). Durant cette alternance, mon activité en entreprise est restée principalement orientée support technique : elle ne m'a pas fourni un projet DevOps d'entreprise suffisamment complet pour servir honnêtement de support certificatif.

À l'issue de ma formation, j'ai donc conçu et réalisé **OpsForge**, un projet fil rouge indépendant construit de juin à août 2026 pour préparer la certification, avec un cahier des charges que j'ai défini moi-même à partir des compétences et des attendus du référentiel. OpsForge est une console locale de gestion d'incidents (services → alertes → incidents → runbooks → journal d'audit), entourée d'une chaîne DevOps de bout en bout, en local : conteneurisation, intégration continue, sauvegarde/restauration, déploiement Kubernetes local, supervision Prometheus/Grafana, et automatisation du déploiement de l'infrastructure avec Ansible — la chaîne couvre les trois compétences obligatoires du titre, sans revendiquer ce qui n'existe pas (ni cloud, ni registre d'images, ni déploiement continu distant).

Le parti pris du projet est l'honnêteté technique : chaque phase a une définition de fin explicite, chaque validation est documentée avec sa date dans le dépôt, et chaque limite est assumée par écrit plutôt que masquée. Ce dossier suit le plan demandé par les modalités officielles du titre ; il présente ce qui existe réellement, ce qui a réellement été testé, et ce qui a volontairement été laissé hors périmètre.

---

# 1. Liste des compétences du référentiel couvertes par le projet

## 1.1 Les trois compétences obligatoires

Les modalités d'évaluation du titre imposent que le projet couvre obligatoirement trois compétences. OpsForge les couvre toutes les trois, chacune avec une preuve distincte et identifiable :

| Compétence obligatoire (REAC TP-01414) | Réalisation OpsForge | Où dans ce dossier |
|---|---|---|
| **Automatiser le déploiement d'une infrastructure** (CP n°2) | Playbook Ansible (`ansible/deploy.yml`, collection `kubernetes.core`) qui provisionne le cluster k3d, construit et importe l'image, applique les manifests Kubernetes dans l'ordre avec attente de disponibilité, puis vérifie `/health` et `/ready` — le tout en une commande, de façon idempotente | Sections 3.3, 5.6, 5.7, 6 |
| **Gérer des containers** (CP n°7) | Image Docker durcie (non-root, digest épinglé, healthcheck), orchestration Docker Compose avec démarrage conditionné à la santé de la base, workloads Kubernetes durcis (securityContext complet, probes, ressources), stockage persistant PVC avec preuve de persistance, mise à jour par rebuild + import + rollout | Sections 3.4, 3.5, 5.3, 5.4 |
| **Exploiter une solution de supervision** (CP n°10) | Application instrumentée (`/metrics` Prometheus), serveur Prometheus qui scrape l'API dans k3d, règle d'alerte `OpsForgeApiDown` réellement déclenchée lors d'une panne provoquée (cycle `inactive → firing → résolu` observé), console Grafana avec dashboard provisionné | Sections 3.6, 5.1, 5.2 |

## 1.2 Matrice compétences ↔ critères ↔ réalisations ↔ preuves ↔ limites

Pour chacune des trois compétences obligatoires, j'ai confronté le projet aux **critères de performance exacts du REAC** (Référentiel Emploi Activités Compétences du titre — « CP » désigne ci-dessous une compétence professionnelle de ce référentiel ; le découpage du projet en phases est détaillé en section 4.1) :

### CP n°2 — Automatiser le déploiement d'une infrastructure

| Critère REAC | Comment OpsForge y répond | Preuve |
|---|---|---|
| « Les serveurs déployés sont fonctionnels » | Le rôle Ansible `verify` échoue si un pod API n'est pas `Running` ou si `/health` et `/ready` ne répondent pas HTTP 200 (`/ready` exécute un `SELECT 1` sur PostgreSQL) ; chaque étage est appliqué avec `wait: true` | Récapitulatif du rôle `verify` (`/health -> 200`, `/ready -> 200`) ; run idempotent `ok=21, changed=2` documenté dans `docs/ANSIBLE.md` |
| « L'architecture est conforme au cahier des charges » | Le playbook déploie exactement l'architecture documentée (namespaces, StatefulSet PostgreSQL + PVC + Service, Deployment API + NodePort, Prometheus + Grafana) en orchestrant les manifests versionnés de `k8s/` — il ne redéfinit rien | Comparaison `k8s/` ↔ ressources déployées ; `docs/ARCHITECTURE.md`, `docs/KUBERNETES.md` |
| « Les scripts sont documentés » | Cinq rôles courts et commentés, variables centralisées dans `group_vars/all.yml`, usage dans `ansible/README.md`, justification et correspondance RNCP dans `docs/ANSIBLE.md`, décision d'architecture n°029 dans `docs/DECISIONS.md` | Les fichiers eux-mêmes |
| Savoir associé : « outil d'automatisation de type Ansible ou Terraform » | Ansible + collection `kubernetes.core` (le choix Ansible plutôt que Terraform est argumenté en section 5.6) | `ansible/requirements.yml`, ADR 029 |

**Limite assumée** : le déploiement cible un cluster **k3d local**, pas un fournisseur cloud. L'activité-type du REAC s'intitule « Automatiser le déploiement d'une infrastructure *dans le cloud* » ; je démontre la compétence CP n°2 d'automatisation sur une infrastructure locale et je ne revendique pas la mise en production cloud (CP n°4), qui relèvera du questionnement à l'entretien technique.

### CP n°7 — Gérer des containers

| Critère REAC | Comment OpsForge y répond | Preuve |
|---|---|---|
| « Les containers sont opérationnels » | Compose : API + PostgreSQL avec healthchecks (`pg_isready`, `/health`), démarrage de l'API conditionné à `service_healthy`. Kubernetes : pods `1/1 Ready` avec probes liveness/readiness distinctes | `docker compose ps` ; `kubectl get pods` ; validations Phase 4 (2026-07-09) et audit du 2026-08-07 |
| « Les containers sont connectés au réseau » | Réseau Compose interne (l'API joint `db:5432`) ; Services Kubernetes ClusterIP (PostgreSQL interne uniquement) et NodePort 30080 exposé sur `127.0.0.1:8080` | Manifests `k8s/*service*.yaml` ; `curl /health` via NodePort |
| « Les containers sont connectés au stockage distant » | Volume nommé `postgres_data` en Compose ; PVC `postgres-data` (1 Gi, `ReadWriteOnce`, StorageClass `local-path`) monté par le StatefulSet — stockage externe au conteneur, dont la persistance a été **prouvée** (donnée survivant à la suppression du pod) | Preuve de persistance documentée (`docs/PHASE4_VERIFICATION.md`) : marqueur inséré, pod supprimé et recréé avec un autre UID, marqueur retrouvé |
| « Les containers sont mis à jour » | Cycle de mise à jour explicite : rebuild de l'image (`opsforge-api:phase4` → `phase5` → `phase6`), `k3d image import`, rollout du Deployment ; l'`imagePullPolicy: Never` documente l'absence volontaire de registre | Historique des tags d'image dans les vérifications de phases ; rôle Ansible `image` |

**Limite assumée** : le stockage `local-path` est local au nœud (pas de stockage réseau distribué) et il n'y a pas de registre d'images — l'import k3d local en tient lieu, ce qui est documenté comme une décision de périmètre (ADR 015).

### CP n°10 — Exploiter une solution de supervision

| Critère REAC | Comment OpsForge y répond | Preuve |
|---|---|---|
| « Les indicateurs définis sont pertinents » | Métriques applicatives réelles : `opsforge_http_requests_total` et `opsforge_http_request_duration_seconds` (labels méthode / route template / code HTTP), plus la métrique `up` du job de scrape ; dashboard Grafana : disponibilité, volume de requêtes, répartition par code, latence p95, répartition par route | `app/main.py` ; dashboard `OpsForge Monitoring` (5 panneaux) |
| « Les alertes sont correctement interprétées » | Règle `OpsForgeApiDown` (`up{job="opsforge-api"} == 0` pendant 30 s) ; panne provoquée par `scale --replicas=0` : l'alerte est passée `inactive → firing`, puis est revenue `inactive` après restauration — cycle complet observé et documenté le 2026-07-14 | `docs/PHASE5_VERIFICATION.md` (5D) ; procédure rejouable documentée dans `docs/MONITORING.md` |
| « Les échanges avec les développeurs sont réguliers » | Projet individuel : je tiens les deux rôles. La boucle « supervision → développement » existe néanmoins réellement et elle est tracée : ajout de `/ready` après analyse du besoin de distinguer liveness et readiness (ADR 022) ; choix du label de route en *template* côté application pour éviter l'explosion de cardinalité côté Prometheus (ADR 017) ; configuration de scrape statique assumée après analyse du coût du service discovery (ADR 018). Le cycle de revue décrit en 4.3 et 4.5 matérialise le reste de ces allers-retours | `docs/DECISIONS.md` ; historique Git |

**Limites assumées** : pas d'Alertmanager ni de canal de notification (l'alerte se déclenche mais n'est routée vers aucun canal) ; stockage Prometheus/Grafana éphémère ; accès par `kubectl port-forward` ; métriques techniques HTTP, pas encore de métriques métier ; et surtout **les statuts métier des services affichés dans OpsForge sont simulés** — Prometheus supervise réellement l'API OpsForge elle-même, pas les services de démonstration (distinction détaillée en 3.6).

## 1.3 Compétences partiellement mises en pratique

Je ne revendique pas ces compétences comme couvertes : le projet en met en pratique une partie, ce que je peux expliquer à l'entretien technique, mais les critères du REAC ne sont pas remplis en totalité.

| Compétence REAC | Ce que le projet met en pratique | Ce qui manque pour la couvrir |
|---|---|---|
| CP n°1 — Automatiser la création de serveurs à l'aide de scripts | Le rôle Ansible `cluster` crée le nœud k3d de manière scriptée et idempotente ; scripts PowerShell de sauvegarde/restauration ; scripts bash (`run.sh`) | Pas de création de machines virtuelles serveur au sens du REAC (le « nœud » est un conteneur k3d) |
| CP n°3 — Sécuriser l'infrastructure | Conteneur non-root (UID 10001), rootfs en lecture seule, capabilities supprimées, seccomp, secrets hors Git, scan Trivy, PostgreSQL lié à `127.0.0.1` | Pas de recommandations ANSSI appliquées formellement, pas de pare-feu ni de certificats/TLS, pas d'authentification |
| CP n°5 — Préparer un environnement de test | Base PostgreSQL éphémère et isolée pour le test d'intégration ; cluster k3d jetable `opsforge-ansible-test` pour valider l'automatisation sans toucher à l'existant ; conteneur de service PostgreSQL en CI | Pas d'environnement de test mis à disposition d'une équipe de développement, pas de pré-production distincte |
| CP n°6 — Gérer le stockage des données | PostgreSQL opérationnel dans deux environnements, PVC persistant prouvé, sauvegardes `pg_dump` au format custom réellement produites, restauration testée vers une base temporaire, garde-fou explicite avant restauration destructive | Pas de réplication, pas de gestion formalisée des droits d'accès selon un cahier des charges, pas de sauvegardes planifiées/externalisées |
| CP n°8 — Automatiser la mise en production d'une application avec une plateforme | L'application est déployée sur Kubernetes (plateforme de type attendu) et ce déploiement est automatisé par Ansible avec vérification de bout en bout | Pas d'environnements de pré-production/production distincts, pas de publication d'image, pas de mise en production continue des évolutions |
| CP n°9 — Définir et mettre en place des statistiques de services | Indicateurs choisis et justifiés (ADR 017) : volume, latence p95, disponibilité, répartition par route et par code | Pas de SLA formalisés, indicateurs non exhaustifs (pas de CPU/stockage/sécurité) |

## 1.4 Compétences non couvertes par le projet

- **CP n°4 — Mettre l'infrastructure en production dans le cloud** : non couverte. OpsForge ne déploie sur aucun fournisseur cloud. Je l'assume explicitement : la même logique d'automatisation viserait un Kubernetes managé dans une évolution cloud (et Terraform y deviendrait pertinent), mais cela n'a pas été réalisé.
- **CP n°11 — Échanger sur des réseaux professionnels éventuellement en anglais** : évaluée par le questionnaire professionnel, pas par le projet. Je note simplement que la documentation technique du dépôt et les messages de commit sont rédigés en anglais, conformément aux usages professionnels.

Conformément aux modalités, les compétences non couvertes par le projet feront l'objet d'un questionnement lors de l'entretien technique.

---

# 2. Cahier des charges

## 2.1 Contexte et origine du projet

OpsForge est un **projet fil rouge indépendant**, réalisé dans le cadre de ma préparation au titre Administrateur système DevOps. Il ne s'agit pas d'un projet d'entreprise : j'en ai conçu le cahier des charges moi-même, à partir des compétences et des attendus du référentiel. Mon activité en entreprise étant restée principalement orientée support technique et ne m'ayant pas fourni un projet DevOps suffisamment complet pour couvrir les attendus certificatifs, j'ai choisi de construire ce projet indépendant, dimensionné précisément pour mettre en œuvre — réellement, pas sur le papier — les compétences du référentiel. Il a été réalisé à l'issue de ma formation en alternance, de juin à août 2026 (premier commit du dépôt le 17 juin 2026).

Trois clarifications importantes :

- OpsForge **n'est pas un projet interne BlueBearsIT** : l'entreprise n'en est ni le client, ni le commanditaire, ni l'utilisateur, et le projet ne contient aucune donnée professionnelle réelle.
- Le domaine choisi (gestion d'incidents) est inspiré de mon expérience de support : je connais le cycle « signal → prise en charge → procédure → traçabilité » pour l'avoir vécu au quotidien, ce qui m'a permis de concevoir un domaine métier crédible sans copier un outil existant.
- Le projet est **pédagogique et démonstratif** : c'est une plateforme locale d'apprentissage appliqué, pas un produit destiné à la production.

## 2.2 Problématique et objectifs

**Problématique retenue.** Quand un service supervisé se dégrade, comment garantir qu'un opérateur puisse qualifier le signal, décider d'une prise en charge, appliquer une procédure sûre et prouver ensuite chaque décision — et comment livrer cette application avec une chaîne DevOps complète : tests automatisés, conteneurisation, déploiement automatisé, supervision réelle et sauvegardes vérifiées ?

**Objectifs du projet :**

1. Construire une application métier fonctionnelle et démontrable : la console d'incidents OpsForge, avec un cycle de vie strict des objets et un audit systématique.
2. L'entourer d'une chaîne DevOps couvrant les trois compétences obligatoires du titre : automatisation du déploiement de l'infrastructure, gestion des conteneurs, exploitation d'une solution de supervision.
3. Produire pour chaque brique une **preuve d'exécution réelle** (et pas seulement du code) : tests verts, endpoints vérifiés, alerte réellement déclenchée, persistance réellement prouvée, déploiement réellement rejoué.
4. Garder l'ensemble **simple, explicable et défendable** à l'oral : chaque choix doit pouvoir être justifié en quelques phrases, chaque limite doit être connue et assumée.

## 2.3 Utilisateur cible et cas d'usage

L'utilisateur cible est un **opérateur unique** (moi, dans le rôle d'un technicien d'exploitation). Son parcours type, entièrement réalisable dans l'interface sans outil externe :

1. Un signal arrive sur un service du catalogue (ex. « Backup Service ») → il est enregistré comme **alerte** (`new`).
2. L'opérateur qualifie l'alerte : il l'**acquitte**, puis décide si elle justifie une prise en charge.
3. Si oui, il ouvre un **incident** depuis l'alerte (une alerte ne peut avoir qu'un seul incident actif), s'en attribue la responsabilité et le passe en **investigation**.
4. Il applique un **runbook** : soit une procédure manuelle à étapes cochées, soit une automatisation limitée à une liste d'actions approuvées dans le code — jamais de commande arbitraire.
5. Chaque action produit une entrée d'**audit** ; l'incident dispose d'une timeline complète.
6. Il **résout** l'incident, puis résout séparément l'alerte : le cycle du signal et celui de la prise en charge restent indépendants.

## 2.4 Besoins fonctionnels

| Réf. | Besoin | Détail |
|---|---|---|
| BF-1 | Catalogue de services | Créer et gérer des services de démonstration (nom, slug, environnement, statut métier saisi, propriétaire) |
| BF-2 | File d'alertes | Créer, rechercher, filtrer, acquitter, résoudre des alertes ; cycle `new → acknowledged → resolved` strictement en avant (résolution directe possible) |
| BF-3 | Gestion d'incidents | Ouvrir un incident depuis une alerte ou manuellement ; cycle `open → investigating → resolved` strictement séquentiel ; un seul incident actif par alerte source ; incident résolu en lecture seule |
| BF-4 | Runbooks | Procédures manuelles à checklist (succès impossible si étapes incomplètes) et automatisations limitées à une liste de clés approuvées ; les runbooks définis dans le code sont « managés » (lecture seule) |
| BF-5 | Audit | Chaque mutation significative et chaque tentative d'exécution de runbook (y compris les échecs contrôlés) crée une entrée d'audit ; timeline par incident ; journal global |
| BF-6 | Console opérateur | Interface multipage utilisable sans Swagger : Vue d'ensemble, Alertes, Incidents (avec Command Center), Services, Runbooks, Activité, Monitoring, Aide |
| BF-7 | Honnêteté de l'interface | La page Monitoring distingue explicitement les contrôles réels de la plateforme (`/health`, `/ready`, `/metrics`, Prometheus, Grafana) des données métier simulées |

## 2.5 Besoins techniques

| Réf. | Besoin | Détail |
|---|---|---|
| BT-1 | API et persistance | API FastAPI documentée, modèle SQLAlchemy, PostgreSQL comme base d'exécution |
| BT-2 | Conteneurisation | Image Docker de l'API (non-root, healthcheck) ; environnement local Docker Compose complet |
| BT-3 | Intégration continue | Pipeline GitHub Actions à chaque push/PR : lint, tests unitaires, test d'intégration PostgreSQL, build d'image, scan de vulnérabilités |
| BT-4 | Tests | Suite rapide (SQLite en mémoire) couvrant le domaine, plus un test d'intégration de bout en bout sur PostgreSQL réel dans une base éphémère |
| BT-5 | Sauvegarde | Sauvegarde `pg_dump` scriptée, restauration vérifiée par défaut dans une base temporaire, garde-fou explicite avant toute restauration destructive |
| BT-6 | Déploiement Kubernetes | Cluster k3d local : Deployment API, StatefulSet PostgreSQL, ConfigMap, Secret, PVC persistant, sondes liveness/readiness distinctes, exposition NodePort |
| BT-7 | Supervision | `/metrics` Prometheus dans l'application ; Prometheus et Grafana déployés dans le cluster ; une règle d'alerte démontrable sur panne réelle |
| BT-8 | Automatisation d'infrastructure | Déploiement complet de l'infrastructure locale en une commande, idempotent, avec vérification finale automatique (ajouté en cours de projet — voir 2.9) |
| BT-9 | Traçabilité | Historique Git propre ; documentation par phase ; décisions d'architecture consignées (ADR) ; preuves de validation datées |

## 2.6 Contraintes

- **Poste de travail Windows 11** avec Docker Desktop : les choix (k3d plutôt qu'une VM, scripts PowerShell pour la sauvegarde, control node Ansible conteneurisé) découlent directement de cette contrainte réelle.
- **Projet individuel** mené en parallèle de mon activité professionnelle, sur une période resserrée (juin à août 2026) : le temps disponible impose des phases courtes, finies et validées une par une plutôt qu'un chantier global.
- **Aucune donnée réelle** : ni données client, ni références à l'outillage interne de l'entreprise ; le scénario de démonstration est générique.
- **Budget zéro cloud** : tout tourne localement ; aucune ressource cloud n'est provisionnée.
- **Sécurité par conception du périmètre** : l'application ne doit jamais exécuter de commande système arbitraire (contrainte vérifiée par inspection et par test automatisé).
- **Changement de poste de travail en cours de projet** : le projet a changé de machine entre les phases 5 et 6 ; la reproductibilité (Git, images, manifests) devait le permettre sans perte.

## 2.7 Livrables et critères d'acceptation

**Livrables :**

1. Le dépôt Git `opsforge` complet : application, tests, Dockerfile, Compose, manifests `k8s/`, automatisation `ansible/`, scripts `scripts/`, pipeline `.github/workflows/ci.yml`.
2. La documentation projet dans `docs/` : architecture, guides par domaine (Kubernetes, monitoring, CI/CD, sauvegarde, sécurité, Ansible), 29 décisions d'architecture, registre des risques et dettes, un fichier de vérification daté par phase.
3. Le présent dossier de projet et son support de présentation.

**Critères d'acceptation globaux** (chaque phase ayant en plus sa propre Definition of Done, cf. section 4) :

- `docker compose up --build` produit un environnement fonctionnel ; `/health`, `/ready` et la console répondent.
- La suite de tests passe localement et dans GitHub Actions (y compris le test PostgreSQL).
- Le déploiement Kubernetes aboutit à des pods `1/1 Ready` et une application joignable depuis Windows.
- La persistance des données PostgreSQL survit à la recréation du pod (preuve exigée, pas supposée).
- L'alerte de supervision se déclenche réellement lors d'une panne provoquée, puis se résout.
- Le déploiement complet de l'infrastructure est rejouable en une commande et se vérifie lui-même.
- Une sauvegarde est produite et sa restauration est vérifiée sans toucher à la base principale.
- Chaque validation de phase est explicite, datée et documentée dans le dépôt.

## 2.8 Hors périmètre (exclusions volontaires)

Ces exclusions sont des décisions documentées (ADR et `docs/RISKS_AND_TECHNICAL_DEBT.md`), pas des oublis :

- Pas de déploiement cloud, pas de Terraform (pertinent pour une évolution cloud, pas pour ce périmètre local — argumenté en 5.6).
- Pas de registre d'images ni de déploiement continu distant : la CI prépare et valide la livraison, elle ne publie pas.
- Pas d'authentification ni de gestion d'utilisateurs (application locale mono-opérateur ; les champs « acteur » sont déclaratifs).
- Pas d'Alembic : `metadata.create_all()` plus un pont de compatibilité additif au démarrage (ADR 006 et 028).
- Pas d'Alertmanager ni de notifications ; pas de Helm ; pas de React ; pas de Redis/Celery.
- Pas de haute disponibilité : un seul nœud, une seule réplique de chaque workload.

## 2.9 Évolution du périmètre : l'histoire réelle du projet

Ce cahier des charges n'a pas été écrit en totalité le premier jour, et je préfère le montrer que le cacher : le périmètre a évolué de manière contrôlée, phase par phase, et chaque extension est tracée.

**Le point de départ (juin 2026)** était un MVP volontairement réduit : l'application FastAPI + PostgreSQL sous Docker Compose, le flux `Service → Alerte → Incident → Runbook → Audit`, un tableau de bord simple, 7 tests. Dès ce stade, un document de cadrage fixait la règle du jeu : six phases prévisionnelles (MVP, CI/CD, sauvegarde/sécurité, Kubernetes, monitoring, documentation d'examen), une Definition of Done par phase, une validation explicite par phase, et l'interdiction par défaut de tout ce qui n'est pas demandé.

**Les extensions décidées en cours de route**, toutes documentées :

- **Phase 6 élargie** : initialement prévue comme une simple phase de documentation d'examen, elle est devenue une phase produit (« Operational Product and Exam Evidence ») quand j'ai constaté que le tableau de bord unique ne permettait pas une démonstration opérateur crédible : console multipage, Command Center par incident, runbooks managés, transitions strictement contrôlées, audit renforcé, et une campagne de tests étendue (7 tests au MVP, 8 à l'issue de la phase 5, 35 au terme de la phase 6).
- **L'ajout d'Ansible (août 2026)** : en confrontant le projet aux critères exacts du REAC pour la compétence obligatoire « Automatiser le déploiement d'une infrastructure », j'ai constaté que ma séquence de déploiement k3d, documentée mais **manuelle** (`k3d cluster create`, puis une série de `kubectl apply`), ne constituait pas une preuve solide d'automatisation. J'ai donc ajouté un périmètre ciblé : automatiser ce déploiement existant avec Ansible, sans rien redéfinir de l'architecture. C'est l'objet du besoin BT-8, de la décision ADR 029, et de la section 6 de ce dossier.

Cette progression n'est pas une faiblesse du cahier des charges : c'est une démarche itérative assumée, où chaque phase validée fige un socle avant d'ouvrir la suivante, et où une relecture du référentiel a déclenché une correction de périmètre au bon moment — avant l'examen, pas après.

---

# 3. Spécifications techniques du projet

## 3.1 Vue d'ensemble de l'architecture

Le schéma ci-dessous présente l'architecture complète : l'application, la supervision qui l'observe, et les deux chaînes distinctes qui l'entourent — intégration continue d'un côté, automatisation du déploiement local de l'autre. Ces deux chaînes sont **indépendantes** : l'image validée par la CI n'est pas transmise au déploiement (pas de registre) ; le rôle Ansible `image` reconstruit l'image localement. *(Mise en page finale : ce schéma sera exporté en image pour le PDF remis au jury.)*

```mermaid
flowchart LR
    subgraph Application["Application OpsForge"]
        User[Opérateur unique] --> Web[Console Jinja2 multipage]
        Web --> API[API FastAPI]
        API --> Domain[Domaine : transitions + runbooks approuvés]
        Domain --> DB[(PostgreSQL)]
        API --> Audit[AuditLog / timeline incident]
        API --> Metrics["/metrics"]
    end

    subgraph Supervision["Supervision (dans k3d)"]
        Metrics --> Prometheus[Prometheus]
        Prometheus --> Grafana[Dashboard Grafana]
        Prometheus --> Rule[Règle OpsForgeApiDown]
    end

    subgraph CI["Intégration continue (GitHub Actions)"]
        Push[push / pull request] --> Lint[Ruff]
        Lint --> Unit[35 tests SQLite]
        Unit --> Integ[1 test d'intégration PostgreSQL]
        Integ --> Build[Build image Docker]
        Build --> Trivy[Scan Trivy - advisory]
    end

    subgraph Infra["Automatisation d'infrastructure (Ansible)"]
        RunSh[Control node conteneurisé ./ansible/run.sh] --> Cluster[k3d cluster create - idempotent]
        RunSh --> Import[Build + import de l'image]
        RunSh --> Apply[Apply ordonné des manifests k8s/ avec wait]
        Apply --> Verify[Vérification /health + /ready]
    end
```

Points structurants :

- **Une seule application, deux environnements d'exécution** : Docker Compose pour le développement, les tests et les sauvegardes ; Kubernetes (k3d) pour le déploiement orchestré local et la supervision.
- **Deux chaînes distinctes et non confondues** : la CI valide le code et l'image mais ne publie ni ne déploie rien ; l'automatisation Ansible déploie l'infrastructure locale mais ne fait pas partie de la CI. Il n'y a ni registre d'images ni déploiement continu distant, et je le présente ainsi.
- **La supervision est réelle et porte sur OpsForge lui-même** : Prometheus scrape l'API déployée dans k3d ; les statuts métier affichés dans la console sont, eux, des données de démonstration.

`[CAPTURE À PRODUIRE — Console : page /overview avec données opérationnelles actives]`
Commande / écran à reproduire : `docker compose up --build -d` puis ouvrir `http://localhost:8000/overview`.

## 3.2 L'application : domaine métier et modèle de données

### Les six objets du domaine

| Objet | Rôle | Champs clés |
|---|---|---|
| `Service` | Élément du catalogue supervisé (démonstration) | nom, slug unique, environnement, statut métier saisi (`healthy/degraded/down/unknown`), propriétaire |
| `Alert` | Signal entrant, éventuellement rattaché à un service | source, titre, message, sévérité (`info/warning/critical`), statut (`new/acknowledged/resolved`) |
| `Incident` | Prise en charge officielle d'un problème | service, alerte source, sévérité (`low→critical`), statut (`open/investigating/resolved`), responsable, horodatages |
| `Runbook` | Procédure : manuelle (checklist) ou automatisée (clé approuvée) | clé unique, mode, instructions, étapes, contexte requis, niveau de risque, clé d'automatisation |
| `RunbookExecution` | Trace de chaque tentative d'exécution, succès ou échec contrôlé | runbook, service, incident, statut, demandeur, sortie, détails |
| `AuditLog` | Journal en append-only de toutes les mutations significatives | action, type et id d'objet, acteur, détails, horodatage |

### Les règles de domaine (appliquées côté serveur, testées négativement)

- Transitions d'alerte **strictement en avant** : `new → acknowledged → resolved` (résolution directe autorisée, jamais de retour en arrière) ; transitions d'incident **strictement séquentielles** : `open → investigating → resolved`, sans réouverture. Toute transition invalide renvoie HTTP 409.
- **Une alerte n'a qu'un seul incident actif** : la création d'un second incident sur la même alerte source renvoie 409 avec l'identifiant de l'incident déjà actif.
- Un incident créé depuis une alerte **hérite du service de l'alerte** ; fournir un service différent est rejeté.
- **Résoudre un incident ne résout pas l'alerte source** : le cycle du signal et celui de la prise en charge sont indépendants (c'est un choix de modélisation que je peux défendre : un correctif peut être appliqué alors que le signal doit encore être confirmé puis clos séparément).
- **Aucune exécution arbitraire** : un runbook automatisé ne peut référencer qu'une clé de la liste approuvée dans le code (5 clés) ; proposer une clé inconnue (`shell_command`, par exemple) est rejeté en 422. Les runbooks définis dans le code sont « managés » : re-synchronisés au démarrage et en lecture seule (PATCH → 409).
- **Tout est audité**, y compris les échecs contrôlés d'exécution de runbook.

Ces règles sont couvertes par la suite de tests (35 tests SQLite dont de nombreux tests négatifs : transition interdite, doublon d'incident, clé non approuvée, checklist incomplète, édition d'un runbook managé) et par un test d'intégration PostgreSQL qui rejoue le flux complet `service → alerte → incident → exécution de runbook → audit` dans une base éphémère créée puis supprimée par le test lui-même.

`[CAPTURES À PRODUIRE — Console, parcours opérateur complet (5 écrans) : file d'alertes avec une alerte dépliée ; Incident Command Center avant résolution ; checklist du runbook manuel avec résultat en succès ; timeline de l'incident ; journal global Activité]`
Commande / écran à reproduire : dérouler le scénario opérateur de `docs/ORAL_PREPARATION.md` (étape 2) sur `http://localhost:8000` — captures n°2 à 6 de l'annexe B.

### Structure du code

| Fichier | Responsabilité |
|---|---|
| `app/main.py` | démarrage (création du schéma + pont de compatibilité + seed), `/health`, `/ready`, `/metrics`, middleware de métriques |
| `app/api.py` | les 22 routes JSON sous `/api` (services, alertes, incidents, runbooks, exécutions, audit) et leurs gardes (409/422) — 26 endpoints au total avec `/health`, `/ready`, `/metrics` et la redirection `/` portés par `main.py` |
| `app/web.py` | composition des 8 sections de la console (18 routes HTML au total : listes, vues de détail, formulaires ; lecture seule — les mutations passent par la même API JSON que les tests) |
| `app/domain.py` | tables de transitions, acteur de la requête, aides d'audit |
| `app/runbooks.py` | définitions seedées, liste d'automatisations approuvées, moteur d'exécution |
| `app/models.py` / `app/schemas.py` | persistance SQLAlchemy / contrats Pydantic (littéraux de statuts, validations croisées) |
| `app/seed.py` | scénario de démonstration générique et idempotent |
| `app/migrations.py` | pont additif de compatibilité de schéma exécuté au démarrage |

## 3.3 Deux chaînes distinctes : intégration continue et automatisation d'infrastructure

C'est la distinction la plus importante du projet, et je la présente explicitement parce qu'elle est souvent source de confusion.

### La chaîne d'intégration continue (GitHub Actions)

À chaque `push` et `pull request`, un pipeline unique (« Lint, test, build, and scan ») exécute dans l'ordre :

1. **Ruff** (`ruff check .`) — le lint échoue vite, avant les tests ;
2. **35 tests unitaires SQLite** (`pytest tests/test_app.py`) — retour rapide sur le domaine ;
3. **1 test d'intégration PostgreSQL** (`pytest tests/postgres_integration.py`) contre un conteneur de service `postgres:16-alpine` démarré par le job — le flux central est prouvé sur le moteur de base réel ;
4. **Build de l'image Docker** taguée avec le SHA du commit ;
5. **Scan Trivy** en mode advisory (détaillé en 5.5).

Ce que cette chaîne **ne fait pas**, volontairement : elle ne pousse pas l'image vers un registre et ne déploie rien. C'est de l'intégration continue avec préparation de livraison, pas du déploiement continu distant.

### La chaîne d'automatisation du déploiement d'infrastructure (Ansible)

Indépendamment de la CI, une seule commande locale déploie toute l'infrastructure :

```text
./ansible/run.sh
   └── control node conteneurisé (image opsforge-ansible-control)
         └── ansible-playbook deploy.yml
               ├── rôle prerequisites   : outils requis présents, sinon échec immédiat
               ├── rôle cluster         : création k3d idempotente + kubeconfig adapté
               ├── rôle image           : docker build + k3d image import
               ├── rôle kubernetes_resources :
               │      namespaces → Secret généré → ConfigMap + PVC
               │      → PostgreSQL (wait) → API (wait) → Prometheus + Grafana (wait)
               └── rôle verify          : pod Running + /health = 200 + /ready = 200
```

Le run ne réussit **que si l'application répond** : le rôle `verify` interroge `/health` et `/ready` à travers le NodePort, et `/ready` prouve la connectivité PostgreSQL (`SELECT 1`). Un second run converge sans rien recréer (idempotence observée : `ok=21, changed=2`). Un playbook `teardown.yml` symétrique supprime le cluster.

`[CAPTURE À PRODUIRE — Terminal : PLAY RECAP Ansible d'un déploiement complet + messages du rôle verify (/health -> 200, /ready -> 200)]`
Commande / écran à reproduire : `./ansible/run.sh deploy.yml -e cluster_name=opsforge-ansible-test -e api_host_port=8090 -e kubeapi_host_port=6446` (cluster jetable, ne touche pas au cluster `opsforge` existant).

`[CAPTURE À PRODUIRE — Terminal : second run idempotent, PLAY RECAP montrant ok=21 changed=2 (ou valeurs équivalentes constatées)]`
Commande / écran à reproduire : relancer la même commande `./ansible/run.sh deploy.yml -e cluster_name=opsforge-ansible-test ...` immédiatement après le premier run.

`[CAPTURE À PRODUIRE — Terminal : teardown du cluster jetable]`
Commande / écran à reproduire : `./ansible/run.sh teardown.yml -e cluster_name=opsforge-ansible-test`.

## 3.4 La couche conteneurs

### Image de l'API

L'image applicative est construite depuis un `Dockerfile` court et durci : base `python:3.12-slim` **épinglée par digest** (reproductibilité des builds et des scans), utilisateur **non-root dédié UID 10001**, `HEALTHCHECK` intégré appelant `/health` sans dépendance à curl, port 8000, démarrage `uvicorn`. Le détail argumenté est en section 5.3.

### Environnement Docker Compose

Deux services : `db` (`postgres:16-alpine`) et `api` (build local). Trois mécanismes méritent l'attention :

- le **healthcheck PostgreSQL** (`pg_isready`) combiné à `depends_on: condition: service_healthy` : l'API ne démarre qu'une fois la base réellement prête — c'est l'équivalent Compose de l'init container utilisé ensuite côté Kubernetes ;
- la base est publiée sur **`127.0.0.1:5432` uniquement** : accessible aux outils locaux, pas au réseau ;
- le répertoire `tests/` est monté **en lecture seule** dans le conteneur API, ce qui permet `docker compose exec api pytest` sans embarquer les tests dans l'image.

### Cycle de vie et mise à jour

La mise à jour d'un conteneur suit un cycle explicite et démontrable : modification du code → rebuild de l'image (nouveau tag de phase : `phase4`, `phase5`, `phase6`) → `k3d image import` → rollout Kubernetes. L'absence de registre est un choix documenté (ADR 015) : `imagePullPolicy: Never` rend cette contrainte visible dans les manifests au lieu de la masquer.

## 3.5 La couche Kubernetes (k3d)

### Topologie

- Cluster **k3d** (k3s dans Docker) nommé `opsforge` : 1 nœud serveur, API Kubernetes sur `127.0.0.1:6445`, port Windows `127.0.0.1:8080` mappé vers le NodePort `30080`. k3d a été choisi (ADR 014) parce qu'il réutilise Docker Desktop sous Windows : pas de VM ni de configuration réseau séparée, cluster reproductible en une commande.
- Namespace `opsforge` pour l'application, namespace `monitoring` pour la supervision.

### Ressources applicatives

| Ressource | Choix notables |
|---|---|
| `Deployment opsforge-api` (1 réplique) | init container `wait-for-postgres` (`pg_isready` en boucle — remplace le `depends_on` de Compose sans modifier l'application) ; probes distinctes : **readiness `/ready`** (base joignable) et **liveness `/health`** (processus vivant) ; requests/limits CPU-mémoire ; securityContext complet (détaillé en 5.4) |
| `StatefulSet postgres` (1 réplique) | probes readiness **et** liveness `pg_isready` ; volume monté depuis le PVC |
| `PVC postgres-data` | 1 Gi, `ReadWriteOnce`, StorageClass `local-path` — la persistance a été prouvée (voir ci-dessous) |
| `ConfigMap` / `Secret` | configuration non sensible d'un côté ; de l'autre `k8s/secret.example.yaml` versionné avec des valeurs à remplacer, le vrai `secret.local.yaml` étant ignoré par Git (et généré à la volée par Ansible dans le déploiement automatisé) |
| `Service` NodePort 30080 | « le plus petit mécanisme local satisfaisant l'accès externe » (ADR 015) ; pas d'Ingress ni de TLS dans ce périmètre |

### Pourquoi un StatefulSet pour PostgreSQL

Un Deployment convient à l'API parce qu'elle est sans état : n'importe quel pod équivalent peut la remplacer. PostgreSQL, lui, possède un état sur disque : le StatefulSet fournit une identité stable (`postgres-0`) et un attachement stable au stockage persistant, ce qui correspond au cycle de vie d'une base de données.

### La preuve de persistance

Je n'ai pas voulu me contenter d'un PVC `Bound` : la persistance a été **prouvée** lors de la validation de la phase 4 (documentée dans `docs/PHASE4_VERIFICATION.md`) : insertion d'un marqueur (`phase4a-persisted`) dans une table, suppression du pod `postgres-0`, recréation automatique par le StatefulSet (l'UID du pod change, prouvant qu'il s'agit d'un nouveau pod), et le marqueur est toujours présent. La limite est énoncée dans la même documentation : cette preuve couvre la recréation du pod, pas la suppression complète du cluster — c'est précisément le rôle des sauvegardes de la phase 3.

`[CAPTURE À PRODUIRE — Terminal : kubectl -n opsforge get pods,svc,pvc montrant les pods 1/1 Running et le PVC Bound]`
Commande / écran à reproduire : `kubectl -n opsforge get pods,svc,pvc` sur le cluster déployé.

`[CAPTURE À PRODUIRE — Terminal : preuve de persistance PostgreSQL — marqueur présent avant suppression du pod, pod recréé (UID différent), marqueur retrouvé]`
Commande / écran à reproduire : suivre la procédure « persistence check » de `docs/KUBERNETES.md` (création table + insert, `kubectl delete pod postgres-0`, `rollout status`, select du marqueur, drop de la table).

## 3.6 La couche supervision

### Ce qui est supervisé — et ce qui ne l'est pas

C'est le point d'honnêteté central du projet :

- **Réel** : Prometheus supervise l'API OpsForge déployée dans k3d. Les métriques `opsforge_http_requests_total` et `opsforge_http_request_duration_seconds` sont produites par un vrai middleware applicatif ; la métrique `up` du job de scrape alimente une vraie règle d'alerte ; Grafana affiche ces données réelles.
- **Simulé** : les statuts métier des services du catalogue (« Backup Service » en panne, etc.) sont des données de démonstration saisies dans OpsForge. Prometheus ne crée pas d'alerte métier dans OpsForge. La page `/monitoring` de la console affiche explicitement cette distinction à l'utilisateur.

### Chaîne de collecte

```text
FastAPI (middleware) ──> /metrics ──> Prometheus (scrape 15 s, job "opsforge-api",
   cible statique opsforge-api.opsforge.svc.cluster.local:8000)
        ├──> Grafana (datasource provisionnée par ConfigMap, uid opsforge-prometheus)
        │       └──> dashboard "OpsForge Monitoring" (5 panneaux)
        └──> règle OpsForgeApiDown : up{job="opsforge-api"} == 0 pendant 30 s
```

- La configuration de scrape est **statique** (ADR 018) : pas de service discovery ni de RBAC — complexité non justifiée pour un cluster local à cible unique, et configuration plus facile à expliquer.
- Le dashboard comporte cinq panneaux : disponibilité (`up`), volume de requêtes (`rate` sur 1 min), répartition par code HTTP, **latence p95** (`histogram_quantile(0.95, ...)`), répartition par route.
- Le seuil `for: 30s` de l'alerte est justifié : avec un scrape et une évaluation toutes les 15 s, 30 s évitent le faux positif d'un raté de scrape isolé tout en restant démontrables à l'oral.
- Accès par `kubectl port-forward` (Prometheus 9090, Grafana 3000) : choix documenté qui évite de recréer le cluster ou d'ajouter un Ingress prématurément.

### La démonstration de panne (réellement exécutée)

Lors de la validation de la phase 5 (2026-07-14), le cycle complet a été observé et documenté : API à l'état normal (`up` = 1, alerte `inactive`) → `kubectl -n opsforge scale deployment/opsforge-api --replicas=0` → `up` = 0 → l'alerte `OpsForgeApiDown` passe à **`firing`** (visible dans l'interface de Prometheus et via son API `/api/v1/alerts` — à ne pas confondre avec les alertes métier d'OpsForge) → restauration `--replicas=1` → `/health` répond de nouveau → `up` = 1 → alerte de retour à `inactive`. La procédure est rejouable telle quelle pour la démonstration devant le jury.

`[CAPTURE À PRODUIRE — Prometheus : page Targets montrant le job opsforge-api UP]`
Commande / écran à reproduire : `kubectl -n monitoring port-forward svc/prometheus 9090:9090` puis `http://localhost:9090/targets`.

`[CAPTURE À PRODUIRE — Prometheus : OpsForgeApiDown en état FIRING après scale de l'API à 0]`
Commande / écran à reproduire : `kubectl -n opsforge scale deployment/opsforge-api --replicas=0`, attendre ~1 min, ouvrir `http://localhost:9090/alerts` ; **puis restaurer** avec `--replicas=1` et vérifier le retour à `inactive`.

`[CAPTURE À PRODUIRE — Grafana : dashboard "OpsForge Monitoring" avec ses 5 panneaux alimentés]`
Commande / écran à reproduire : `kubectl -n monitoring port-forward svc/grafana 3000:3000`, `http://localhost:3000`, dossier OpsForge.

`[CAPTURE À PRODUIRE — Console : page /monitoring montrant la distinction données réelles / données simulées]`
Commande / écran à reproduire : ouvrir `http://localhost:8000/monitoring` (Compose) ou `http://localhost:8080/monitoring` (k3d).

## 3.7 Sauvegarde et restauration

Deux scripts PowerShell ciblent le PostgreSQL de l'environnement Docker Compose :

- **`scripts/backup.ps1`** : lit l'utilisateur et la base depuis le conteneur `db` en cours d'exécution, vérifie `pg_isready`, exécute `pg_dump --format=custom --no-owner --no-privileges` **dans** le conteneur, copie l'archive vers `backups/opsforge_backup_<horodatage>.dump`, nettoie le fichier temporaire et refuse une archive vide. Des archives réelles produites le 2026-07-06 attestent l'exécution (validation de phase 3 : archive de 19 785 octets).
- **`scripts/restore.ps1`** : valide d'abord l'archive (`pg_restore --list`), puis restaure **par défaut dans une base temporaire de vérification** (`opsforge_restore_verify`), compte les tables restaurées (6 tables publiques lors de la validation), et supprime la base temporaire. La restauration dans la base principale exige le drapeau `-MainDatabase` **et** la saisie exacte du mot `RESTORE` (comparaison sensible à la casse) ; le script arrête alors l'API avant la restauration et la redémarre ensuite.

Limites énoncées dans la documentation : sauvegardes locales, non chiffrées, non planifiées, sans rotation ni copie externe — un mécanisme démontrable et sûr, pas une stratégie de sauvegarde d'entreprise. Ces scripts ne couvrent pas le PostgreSQL du cluster k3d (la persistance y repose sur le PVC, et les données de démonstration sont reproductibles par le seed).

`[CAPTURE À PRODUIRE — Terminal : exécution de backup.ps1 (archive créée avec taille) puis restore.ps1 en mode vérification (base temporaire, tables comptées, nettoyage)]`
Commande / écran à reproduire : `.\scripts\backup.ps1` puis `.\scripts\restore.ps1 -BackupFile backups\<fichier>.dump` avec Compose démarré.

## 3.8 Sécurité

La sécurité du projet est une sécurité de périmètre, appliquée en couches et documentée :

1. **Par conception applicative** : aucune exécution de commande arbitraire — les runbooks automatisés ne peuvent appeler que 5 comportements Python approuvés dans le code ; l'absence de `subprocess`/`os.system`/`eval`/`exec` est vérifiée ; un test rejette explicitement une clé d'automatisation non approuvée.
2. **Conteneur** : utilisateur non-root UID 10001, image de base épinglée par digest, healthcheck.
3. **Kubernetes** : securityContext complet (non-root, rootfs lecture seule, capabilities toutes supprimées, seccomp `RuntimeDefault`, pas d'escalade), requests/limits, vérifié en conditions réelles (écriture dans `/app` refusée, application fonctionnelle en lecture seule).
4. **Secrets** : `.env` et `k8s/secret.local.yaml` ignorés par Git ; seuls des exemples à valeurs de démonstration sont versionnés ; dans le déploiement Ansible, le Secret PostgreSQL est généré à la volée depuis des variables (valeur par défaut locale non sensible, surchargeable par `-e` ou externalisable dans `ansible-vault`).
5. **Chaîne d'approvisionnement** : scan Trivy à chaque build. Politique assumée : le scan est **advisory** (visible mais non bloquant) ; le dernier scan de l'image épinglée rapportait **19 vulnérabilités HIGH et 3 CRITICAL** d'origine Debian, sans correctif disponible. Une CI verte ne signifie donc pas « image sans vulnérabilité », et je le dis tel quel.

Limites énoncées : pas d'authentification, pas de TLS, pas de gestionnaire de secrets d'entreprise, pas de seuil de blocage de vulnérabilités défini.

## 3.9 Environnements et versions

| Composant | Version | Épinglage |
|---|---|---|
| Python / FastAPI app | Python 3.12 (image `python:3.12-slim@sha256:c3d81d25…`) — app OpsForge v0.2.0 | digest + `requirements.txt` résolu |
| PostgreSQL | `postgres:16-alpine` (Compose, CI et k3d) | tag |
| k3d / k3s | k3d v5.9.0 / k3s v1.35.5-k3s1 (validation phase 4) | — |
| Prometheus / Grafana | `prom/prometheus:v2.55.1` / `grafana/grafana:11.3.1` | tags |
| Control node Ansible | `ansible-core==2.17.14`, client Python `kubernetes==36.0.3`, collection `kubernetes.core:6.5.0`, kubectl v1.31.5, k3d v5.9.0, CLI Docker 27.5.1 | versions exactes validées, épinglées dans `ansible/Dockerfile` |
| CI | GitHub Actions, `actions/checkout@v5`, `setup-python@v6`, `trivy-action@v0.36.0` | tags d'actions |
| Poste de travail | Windows 11 + Docker Desktop (Git Bash pour `run.sh`, PowerShell pour les scripts) | — |

Note honnête sur les versions : le kubectl embarqué dans le control node (v1.31.5) est plus ancien que le k3s du cluster (v1.35.x), au-delà de la fenêtre de compatibilité officielle (±1 version mineure). Les opérations utilisées (lecture `/healthz`, apply via `kubernetes.core`) fonctionnent et ont été validées telles quelles ; l'alignement de ces versions est une évolution identifiée (section 8).

---

# 4. Démarche de travail et outils utilisés

## 4.1 Une démarche par phases, chacune avec sa Definition of Done

Le projet a été découpé en six phases, définies dès le cadrage initial puis affinées. Chaque phase possède un périmètre écrit, une **Definition of Done** vérifiable, un fichier de preuve daté (`docs/PHASE<i>_VERIFICATION.md`) et une **validation explicite** avant de passer à la suivante :

| Phase | Contenu | Validation |
|---|---|---|
| 1 — MVP local | FastAPI + PostgreSQL + Compose, flux `Service → Alerte → Incident → Runbook → Audit`, 7 tests | validée le 2026-06-16 |
| 2 — CI/CD | GitHub Actions : tests, build d'image, scan Trivy | validée le 2026-06-18 (run vert sur GitHub) |
| 3 — Sauvegarde & sécurité | scripts backup/restore, stratégie de secrets, documentation sécurité | validée le 2026-07-06 |
| 4 — Kubernetes | cluster k3d, PostgreSQL StatefulSet + PVC (4A) puis API (4B), preuve de persistance | validée le 2026-07-09 (4A vérifiée le 07-07, 4B le 07-08) |
| 5 — Supervision | `/metrics` (5A), Prometheus (5B), Grafana (5C), règle d'alerte + panne provoquée (5D) | validée le 2026-07-14 sur l'état du commit `23194f0` (validation documentée par le commit `9bcb271`) |
| 6 — Produit opérateur & preuves d'examen | console multipage, règles de domaine renforcées, runbooks managés, audit, 35 tests, durcissement Kubernetes, puis ajout ciblé d'Ansible (sous-étape CP n°2) | **en cours de finalisation** : l'audit d'intégration du 2026-08-07 et l'automatisation Ansible sont faits ; restent la revue visuelle manuelle et la collecte des captures finales (les placeholders de ce dossier) |

Je tiens à cette dernière ligne telle qu'elle est : la documentation du projet dit explicitement ce qui reste à faire, et ce dossier ne déclare pas la phase 6 « validée » tant que la revue manuelle et les captures ne sont pas terminées.

## 4.2 Le protocole appliqué avant / pendant / après chaque phase

Un protocole écrit (`docs/PHASE_SYNC_PROTOCOL.md`) encadre chaque phase :

- **Avant** : relire l'état du projet (contexte, roadmap, décisions, risques, vérification de la phase précédente), partir d'un dépôt propre, confirmer l'objectif et la Definition of Done, figer le périmètre exact.
- **Pendant** : petits changements vérifiables ; toute idée nouvelle est soit rejetée, soit documentée comme travail futur, soit explicitement approuvée avant implémentation — « aucune idée nouvelle n'entre silencieusement dans la phase en cours ».
- **Après** : vérifier chaque item de la Definition of Done, consigner les preuves dans le fichier de vérification, mettre à jour la documentation (roadmap, index, décisions), valider explicitement, pousser, puis vérifier que GitHub Actions est vert.

Deux règles de ce protocole ont particulièrement structuré le projet :

- **La règle d'apprentissage pour l'oral** : une phase n'est pas terminée tant que je ne peux pas répondre clairement à « qu'est-ce qui a été construit ? pourquoi ? comment ça marche ? comment ça a été vérifié ? quelles sont les limites ? qu'améliorer ensuite ? ». C'est ce qui a produit les 29 décisions d'architecture (ADR) du dépôt : chaque choix technique important y est consigné avec son contexte, sa décision, sa raison et ses conséquences.
- **La règle d'honnêteté des preuves** : ne jamais déclarer testé ce qui a seulement été inspecté. C'est ce qui distingue, dans tout le dépôt comme dans ce dossier, « validé à l'exécution, à telle date » de « présent dans le code ».

## 4.3 L'évolution du workflow Git

Le workflow Git a évolué avec le projet, et cette évolution est elle-même instructive :

1. **Phases 1 à 5 et début de phase 6 (juin – juillet 2026)** : workflow solo simple, commits directs sur `main`, un commit de validation par phase (`Validate Phase X …`), vérification de la CI après chaque push. C'est le workflow décrit dans `docs/GIT_WORKFLOW.md`. La phase 6 a ensuite inauguré la première branche dédiée du projet (`phase6-operator-ux`), sur laquelle le candidat produit a été construit.
2. **Audit de la phase 6 (7 août 2026)** : passage à un vrai travail par branches. Une branche d'expérimentation a servi de terrain de revue — auto-revue documentée, puis seconde passe de revue assistée par IA (dispositif décrit en 4.5) ; elle n'a **jamais été fusionnée** : à la place, une branche d'intégration propre (`integration/phase6-audit`) a été ré-implémentée en 6 commits revus, intégrant directement les corrections identifiées — dont une vraie régression détectée en revue (le verrouillage du champ service pour une alerte sans service) et la restauration du signal d'échec Trivy.
3. **Intégration finale (10-11 août 2026)** : workflow complet par Pull Requests avec commits de merge (pas de squash, l'historique des branches est préservé) : PR #1 (audit, merge `489552f`), PR #2 (Ansible, merge `0becdf8`), PR #3 (synchronisation documentaire, merge `8ab0f70`). La branche `main` n'a pas encore reçu cette intégration : le candidat d'examen est figé sur `phase6-operator-ux` (la branche dédiée de la phase 6, cible des trois Pull Requests) au commit `8ab0f70`. [À CONFIRMER AVEC DYLLAN — avant la session : fusionner vers `main` ou poser un tag (ex. `jury-2026-09`), pour que le clonage par défaut ne montre pas un état obsolète]

À noter honnêtement : `docs/GIT_WORKFLOW.md` décrit toujours le workflow solo de la première période et n'a pas été mis à jour pour refléter le passage aux Pull Requests — c'est un écart documentaire connu, visible dans l'historique, que j'assume comme tel.

## 4.4 Outillage

| Domaine | Outils |
|---|---|
| Développement | Python 3.12, FastAPI, SQLAlchemy 2.x, Pydantic, Jinja2, JavaScript sans framework |
| Tests & qualité | pytest (SQLite en mémoire + intégration PostgreSQL), Ruff |
| Conteneurs | Docker, Docker Compose, image durcie non-root |
| CI | GitHub Actions, Trivy (scan d'image advisory) |
| Orchestration | Kubernetes via k3d (k3s dans Docker), kubectl |
| Automatisation d'infrastructure | Ansible (`ansible-core` 2.17.14), collection `kubernetes.core` 6.5.0, control node conteneurisé |
| Supervision | prometheus-client (instrumentation), Prometheus v2.55.1, Grafana 11.3.1 |
| Sauvegarde | pg_dump/pg_restore via scripts PowerShell |
| Traçabilité | Git + GitHub (branches, Pull Requests), documentation Markdown versionnée, ADR |

## 4.5 Collaborations

OpsForge est un **projet individuel** : il n'y a ni client, ni équipe de développement, ni équipe d'exploitation distincte — je tiens l'ensemble des rôles, de la définition du besoin à la validation finale, et chaque validation de phase est ma décision, tracée dans le dépôt.

OpsForge étant un projet individuel, j'ai utilisé des **assistants d'IA comme outils** d'aide à la conception, à l'implémentation et à la revue, selon des règles écrites dans le dépôt (`docs/ENGINEERING_CHARTER.md`, `docs/PHASE_SYNC_PROTOCOL.md`). Je suis resté responsable du cadrage, des choix techniques, des arbitrages et de la validation des résultats ; les changements importants ont été vérifiés et testés avant leur intégration.

C'est ce processus qui donne au projet son cycle de revue, visible dans l'historique Git : chaque évolution substantielle est passée par « proposition → implémentation → revue → correction → validation » — branche d'expérimentation revue puis ré-implémentée proprement, corrections explicitement attribuées à la revue dans les messages de commit, rapport de revue conservé sur la branche d'expérimentation. Dans la suite du dossier, « revue » désigne cette revue outillée, conduite sous ma responsabilité.

---

# 5. Réalisations significatives (scripts et configurations argumentés)

Cette section présente les réalisations les plus significatives du projet, avec pour chacune : le besoin, l'extrait utile (jamais le fichier entier), l'explication, la justification du choix, la preuve de fonctionnement et la limite éventuelle. Les extraits proviennent du dépôt au commit `8ab0f70` ; ils sont condensés pour la lecture — les lignes non essentielles sont élidées et les coupures signalées par `# […]` — sans altération du contenu cité.

## 5.1 Instrumentation Prometheus de l'application

**Besoin.** Superviser réellement OpsForge suppose que l'application expose ses propres métriques — pas seulement des métriques système génériques.

**Extrait — `app/main.py` (définition des métriques et middleware) :**

```python
HTTP_REQUESTS_TOTAL = Counter(
    "opsforge_http_requests_total",
    "Total HTTP requests handled by OpsForge.",
    ["method", "route", "status_code"],
)
HTTP_REQUEST_DURATION_SECONDS = Histogram(
    "opsforge_http_request_duration_seconds",
    "HTTP request latency in seconds for OpsForge.",
    ["method", "route", "status_code"],
)
```

```python
@app.middleware("http")
async def collect_http_metrics(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    start_time = perf_counter()
    response = await call_next(request)
    elapsed = perf_counter() - start_time
    labels = {
        "method": request.method,
        "route": _route_label(request),
        "status_code": str(response.status_code),
    }
    HTTP_REQUESTS_TOTAL.labels(**labels).inc()
    HTTP_REQUEST_DURATION_SECONDS.labels(**labels).observe(elapsed)
    return response
```

**Explication.** Un middleware HTTP chronomètre chaque requête et incrémente un compteur et un histogramme, avec trois labels : méthode, route et code de statut. Deux détails comptent :

- le label `route` utilise le **template de route FastAPI** (`/api/services/{service_id}` et non `/api/services/42`) : sans cela, chaque identifiant créerait une série de métriques distincte et ferait exploser la cardinalité côté Prometheus ;
- les requêtes vers `/metrics` sont exclues du comptage, pour que la supervision ne se mesure pas elle-même.

**Preuve.** Test automatisé (`test_metrics_endpoint_exposes_prometheus_metrics`) ; lors de la validation de la phase 5, la cible Prometheus était `UP` et les requêtes PromQL sur ces deux métriques retournaient des séries.

**Lien avec `/health` et `/ready`.** La même couche expose la liveness (`/health` : le processus répond, sans toucher la base) et la readiness (`/ready` : `SELECT 1` sur PostgreSQL, 503 sinon). Cette séparation (ADR 022) permet à Kubernetes de ne pas router de trafic vers une API vivante mais privée de sa base — et c'est `/ready` qui sert de preuve de connectivité dans la vérification Ansible.

**Limite.** Métriques techniques HTTP uniquement ; les indicateurs métier (nombre d'incidents ouverts, etc.) sont une évolution identifiée, pas une réalisation.

## 5.2 Règle d'alerte `OpsForgeApiDown`

**Besoin.** Le critère « les alertes sont correctement interprétées » exige une alerte qui se déclenche réellement, pas une capture d'un état vert.

**Extrait — `k8s/prometheus-rules-configmap.yaml` (règle complète) :**

```yaml
groups:
  - name: opsforge-alerts
    rules:
      - alert: OpsForgeApiDown
        expr: up{job="opsforge-api"} == 0
        for: 30s
        labels:
          severity: critical
          service: opsforge-api
        annotations:
          summary: OpsForge API is down
          description: Prometheus cannot scrape the OpsForge API metrics endpoint.
```

**Explication et choix.** La règle s'appuie sur la métrique synthétique `up` du job de scrape : elle se déclenche dès que Prometheus **ne parvient plus à joindre** l'API, quelle qu'en soit la cause — c'est plus robuste qu'une règle sur une métrique applicative, qui disparaît en même temps que l'application. Le `for: 30s` est calibré sur l'intervalle de scrape (15 s) : assez long pour ignorer un raté isolé, assez court pour une démonstration.

**Preuve.** Cycle complet observé et documenté le 2026-07-14 : scale à 0 → `up`=0 → état `firing` (constaté dans l'interface de Prometheus et via son API `/api/v1/alerts`) → restauration → retour `inactive`. Rejouable en démonstration.

**Limite.** Pas d'Alertmanager : l'alerte est visible dans Prometheus mais ne notifie personne. C'est une décision de périmètre (ADR 020) : la règle suffit à prouver la détection ; le routage de notifications est une évolution.

## 5.3 Image Docker durcie de l'API

**Besoin.** L'image applicative doit être reproductible et ne pas tourner en root — dans Compose comme dans Kubernetes.

**Extrait — `Dockerfile` (l'essentiel des 22 lignes ; `HEALTHCHECK` replié sur deux lignes pour la lisibilité) :**

```dockerfile
FROM python:3.12-slim@sha256:c3d81d25b3154142b0b42eb1e61300024426268edeb5b5a26dd7ddf64d9daf28
# […]
RUN useradd --create-home --shell /usr/sbin/nologin --uid 10001 opsforge \
    && chown opsforge:opsforge /app

COPY --chown=opsforge:opsforge app ./app

USER opsforge
# […]
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Explication et choix.**

- **Digest épinglé** : `python:3.12-slim` est figé par son SHA-256 (ADR 024). Deux builds espacés dans le temps produisent la même base ; le scan Trivy porte sur une image identifiée, pas sur un tag mouvant.
- **Utilisateur non-root UID 10001** : créé sans shell de connexion ; le même UID est réutilisé dans le securityContext Kubernetes (`runAsUser: 10001`), ce qui rend le durcissement cohérent entre les deux environnements.
- **HEALTHCHECK en Python pur** : appelle `/health` via la bibliothèque standard — aucune dépendance (curl/wget) ajoutée à l'image juste pour la sonde.

**Preuve.** Image construite en CI à chaque commit ; conteneur `healthy` dans Compose ; la même image (importée dans k3d) tourne sous contrainte `readOnlyRootFilesystem` sans modification.

**Limite.** Build mono-stage (suffisant ici : les dépendances sont installées via wheels, sans toolchain de compilation à séparer) ; les 19 HIGH / 3 CRITICAL Debian résiduels du scan restent visibles et sans correctif disponible — assumés, pas masqués.

## 5.4 Manifests Kubernetes durcis (Deployment API et StatefulSet PostgreSQL)

**Besoin.** Déployer l'application dans Kubernetes avec des workloads qui redémarrent bien, ne reçoivent du trafic que lorsqu'ils sont prêts, et appliquent le principe du moindre privilège.

**Extrait — `k8s/api-deployment.yaml` (securityContext et probes du conteneur API) :**

```yaml
          securityContext:
            runAsNonRoot: true
            runAsUser: 10001
            runAsGroup: 10001
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities:
              drop: ["ALL"]
            seccompProfile:
              type: RuntimeDefault
          # […]
          readinessProbe:
            httpGet:
              path: /ready
              port: http
            initialDelaySeconds: 3
            periodSeconds: 5
            # […]
          livenessProbe:
            httpGet:
              path: /health
              port: http
            initialDelaySeconds: 10
            periodSeconds: 10
            # […]
```

**Explication et choix.**

- Le conteneur tourne **non-root, sans capabilities, sous seccomp, avec un système de fichiers racine en lecture seule** ; seul `/tmp` (un `emptyDir`) est inscriptible. Une compromission de l'application ne permettrait ni élévation ni modification de l'image en cours d'exécution.
- Les **deux probes sont différentes** et c'est voulu : la readiness (`/ready`) retire l'API du Service quand PostgreSQL est injoignable ; la liveness (`/health`) ne redémarre le conteneur que si le processus lui-même ne répond plus. Utiliser `/ready` en liveness provoquerait des redémarrages en boucle pendant une panne de base — exactement ce qu'il faut éviter.
- Un **init container** `wait-for-postgres` (boucle `pg_isready`) sérialise le démarrage : l'équivalent Kubernetes du `depends_on: service_healthy` de Compose, sans modifier l'application.
- Côté PostgreSQL, le StatefulSet a reçu une **livenessProbe** `pg_isready` (un postmaster bloqué est redémarré, pas seulement retiré des endpoints du Service), avec la réserve documentée que `pg_isready` teste l'acceptation de connexion, pas l'exécution de requêtes.

**Preuve.** Vérifié sur le cluster k3d réel dans un namespace isolé (audit du 2026-08-07) : les deux pods `1/1 Ready`, `/health`, `/ready` et `/overview` en HTTP 200 sous rootfs en lecture seule, et une tentative d'écriture dans `/app` refusée comme attendu.

**Limite.** Une réplique de chaque workload, `local-path` mono-nœud : la disponibilité n'est pas l'objectif de ce périmètre. Suivi documenté : `runAsNonRoot` pour PostgreSQL (l'image officielle abandonne ses privilèges via son entrypoint) et le mot de passe Grafana en Secret.

## 5.5 Pipeline d'intégration continue GitHub Actions

**Besoin.** Vérifier chaque commit automatiquement : qualité du code, comportement du domaine, compatibilité avec le vrai moteur de base, construction de l'image, et visibilité des vulnérabilités.

**Extrait — `.github/workflows/ci.yml` (enchaînement des vérifications et politique Trivy) :**

```yaml
      - name: Lint with Ruff
        run: ruff check .

      - name: Run SQLite unit tests
        run: pytest tests/test_app.py

      - name: Run PostgreSQL integration test
        env:
          DATABASE_URL: postgresql+psycopg://opsforge:opsforge@127.0.0.1:5432/opsforge
        run: pytest tests/postgres_integration.py

      - name: Build Docker image
        run: docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

      - name: Run Trivy image scan (advisory)
        uses: aquasecurity/trivy-action@v0.36.0
        continue-on-error: true
        with:
          scan-type: image
          image-ref: opsforge-api:${{ github.sha }}
          # […]
          exit-code: "1"
          severity: HIGH,CRITICAL
```

**Explication et choix.**

- **Ordre voulu** : le lint échoue en premier (rapide), puis les 35 tests SQLite (retour en secondes), puis le test PostgreSQL contre un conteneur de service `postgres:16-alpine` démarré par le job — le flux central est prouvé sur le moteur d'exécution réel avant de dépenser du temps en build et scan.
- **Le test PostgreSQL est isolé par construction** : il crée une base au nom unique, y rejoue le flux complet, puis la supprime — la CI ne peut pas polluer une base de démonstration, et le test le vérifie lui-même.
- **La subtilité Trivy** : `exit-code: "1"` fait échouer **l'étape** quand des HIGH/CRITICAL sont trouvés (le signal reste visible, l'étape s'affiche en échec), tandis que `continue-on-error: true` maintient **le job** vert (non bloquant). J'obtiens ainsi les deux propriétés voulues : un signal de sécurité impossible à rater, et une politique assumée de non-blocage tant qu'un seuil n'a pas été explicitement décidé. Un commentaire dans le fichier documente comment en faire un jour un vrai portail bloquant.
- Un groupe `concurrency` annule les runs rendus obsolètes par un push plus récent sur la même référence.

**Preuve.** Runs verts sur GitHub Actions ; premier run documenté dès le commit racine (phase 2, validée sur run vert), pipeline rejoué en clean-room lors de l'audit du 2026-08-07.

**Limite.** Pas de publication d'image ni de déploiement : c'est de l'intégration continue, et le dossier ne prétend pas autre chose.

`[CAPTURE À PRODUIRE — GitHub Actions : run vert du commit final montrant les étapes Lint / SQLite / PostgreSQL / Build / Trivy (étape Trivy en échec advisory, job vert)]`
Commande / écran à reproduire : onglet Actions du dépôt `ThDyllan/opsforge`, run du commit `8ab0f70` (ou dernier run de la branche `phase6-operator-ux`), vue du job « Lint, test, build, and scan » dépliée.

## 5.6 Playbook Ansible d'automatisation du déploiement

**Besoin.** Remplacer la séquence manuelle documentée (`k3d cluster create` puis huit `kubectl apply` et des vérifications à la main) par une automatisation en une commande, idempotente et auto-vérifiée — la preuve de la compétence obligatoire CP n°2.

**Pourquoi Ansible plutôt que Terraform.** Les deux outils sont cités par le référentiel et les deux sont légitimes ; ils n'ont simplement pas la même force — et Terraform n'est pas « réservé au cloud ». Terraform est **déclaratif et à état** : on décrit un état cible, il réconcilie le monde réel via des providers. Ma tâche est une **orchestration procédurale multi-outils locale** : préparer le control node → créer le cluster k3d → construire et importer l'image → appliquer des manifests dans un ordre imposé par les dépendances → attendre → vérifier en HTTP. C'est exactement la forme d'exécution qu'Ansible exprime naturellement (et la collection `kubernetes.core` m'apporte le déclaratif là où il le faut, sur les ressources Kubernetes). Terraform deviendrait le choix le plus pertinent pour une évolution de provisioning d'infrastructure cloud — direction CP n°4, non réalisée ici. Ce raisonnement est consigné dans la décision ADR 029.

**Extrait 1 — `ansible/roles/cluster/tasks/main.yml` (création idempotente du cluster) :**

```yaml
- name: List existing k3d clusters
  ansible.builtin.command: k3d cluster list -o json
  register: k3d_clusters
  changed_when: false

- name: Create the k3d cluster
  ansible.builtin.command: >-
    k3d cluster create {{ cluster_name }}
    --servers 1
    --api-port 127.0.0.1:{{ kubeapi_host_port }}
    --port "{{ api_host_port }}:{{ node_port }}@server:0"
    --wait
  when: cluster_name not in (k3d_clusters.stdout | from_json | map(attribute='name') | list)
```

Le cluster n'est créé **que s'il n'existe pas** : le playbook peut être rejoué sans détruire l'existant. Tous les paramètres (nom, ports) sont des variables : le même playbook déploie le cluster de démonstration `opsforge` (port 8080) ou un cluster jetable isolé `opsforge-ansible-test` (port 8090) pour tester sans risque.

**Extrait 2 — `ansible/roles/kubernetes_resources/tasks/main.yml` (Secret généré, déploiement ordonné et attendu) :**

```yaml
- name: Create the PostgreSQL Secret from variables
  # Injected at deploy time so no credential file is committed to Git.
  kubernetes.core.k8s:
    state: present
    definition:
      apiVersion: v1
      kind: Secret
      metadata:
        name: opsforge-postgres-secret
        namespace: "{{ app_namespace }}"
      type: Opaque
      stringData:
        POSTGRES_USER: "{{ db_user }}"
        POSTGRES_PASSWORD: "{{ db_password }}"
        DATABASE_URL: "postgresql+psycopg://{{ db_user }}:{{ db_password }}@postgres:5432/{{ db_name }}"

# […]
- name: Deploy PostgreSQL and wait until it is ready
  kubernetes.core.k8s:
    state: present
    src: "{{ manifests_path }}/{{ item }}"
    wait: true
    wait_timeout: "{{ wait_timeout }}"
  loop:
    - postgres-statefulset.yaml
    - postgres-service.yaml
```

Deux idées ici. D'abord, **aucun manifest de Secret n'est versionné** : le Secret Kubernetes est généré au déploiement depuis les variables — la valeur par défaut, non sensible et réservée à la démonstration locale, vit dans `ansible/group_vars/all.yml`, et elle est surchargeable par `-e db_password=…` ou externalisable dans `ansible-vault` pour tout usage réel. Ensuite, chaque étage est appliqué avec **`wait: true`** : Ansible bloque jusqu'à ce que la ressource soit réellement prête, ce qui impose l'ordre des dépendances (PostgreSQL prêt → API prête → supervision) au lieu d'un `kubectl apply` aveugle de tout le répertoire.

**Extrait 3 — `ansible/roles/verify/tasks/main.yml` (le déploiement se prouve lui-même) :**

```yaml
- name: Check /ready through the NodePort (proves PostgreSQL connectivity)
  ansible.builtin.uri:
    url: "http://host.docker.internal:{{ api_host_port }}/ready"
    return_content: true
  register: ready
  retries: 12
  delay: 3
  until: ready.status is defined and ready.status == 200
```

Le run ne se termine avec succès que si un pod API est `Running` **et** si `/health` puis `/ready` répondent 200 — `/ready` exécutant un `SELECT 1`, la réussite du playbook prouve la chaîne complète jusqu'à la base.

**Preuve.** Validations documentées dans `docs/ANSIBLE.md` et dans les messages de commit : déploiement complet depuis zéro sur le cluster isolé `opsforge-ansible-test` (`/health = 200`, `/ready = 200`), second run idempotent (`ok=21, changed=2`), cycle teardown/recréation, le cluster `opsforge` préexistant restant intact. Captures listées en annexe B à produire lors de la répétition finale.

**Limites.** Cible k3d locale uniquement (pas de cloud) ; `validate_certs: false` limité à la connexion de contrôle locale vers le cluster éphémère ; la méthode supportée et validée est le control node conteneurisé (section 5.7) — l'exécution directe du playbook sur un hôte Linux n'a pas été validée et n'est pas revendiquée.

## 5.7 Control node Ansible conteneurisé (`ansible/run.sh`)

**Besoin.** Ansible ne s'exécute pas nativement sous Windows. J'ai défini le **control node comme du code** : une image Docker qui embarque exactement les versions validées — le même environnement d'exécution, reproductible sur tout poste disposant de Docker (décision consignée dans l'ADR 029 et `docs/ANSIBLE.md`).

**Extrait — `ansible/Dockerfile` (versions épinglées ; le fichier épingle aussi kubectl v1.31.5, k3d v5.9.0 et la CLI Docker 27.5.1 en binaires) et `ansible/run.sh` (câblage) :**

```dockerfile
    ANSIBLE_CONFIG=/work/ansible/ansible.cfg
# […]
RUN pip install "ansible-core==2.17.14" "kubernetes==36.0.3"
# […]
RUN ansible-galaxy collection install kubernetes.core:6.5.0
```

```bash
export MSYS_NO_PATHCONV=1

docker run --rm \
  --add-host=host.docker.internal:host-gateway \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v "$repo":/work \
  opsforge-ansible-control \
  ansible-playbook -i inventory.ini "$playbook" "$@"
```

**Explication et choix.**

- Le conteneur monte **la socket Docker de l'hôte** : le `docker build`, le `k3d cluster create` et l'import d'image lancés depuis le conteneur agissent sur le démon Docker du poste — le control node pilote l'hôte sans rien y installer.
- `--add-host=host.docker.internal:host-gateway` rend l'hôte joignable **depuis** le conteneur : c'est par ce nom que le playbook atteint l'API Kubernetes du cluster k3d (le rôle `cluster` réécrit le kubeconfig en conséquence) et que le rôle `verify` appelle `/health` et `/ready` via le NodePort.
- `MSYS_NO_PATHCONV=1` neutralise la réécriture de chemins de Git Bash sous Windows, qui corrompait les chemins de montage (`/var/run/docker.sock`, `/work`).
- La ligne `ENV ANSIBLE_CONFIG=…` et le `-i inventory.ini` explicite sont le résultat direct de la situation de recherche racontée en section 6.

**Preuve.** C'est par ce chemin (`./ansible/run.sh`) que toutes les validations Ansible ont été rejouées de bout en bout après correction, y compris après l'épinglage des versions.

**Limite.** Cette méthode est la seule validée, et la documentation le dit explicitement — une exécution directe sur un hôte Linux exigerait de revalider le contexte réseau.

## 5.8 Scripts de sauvegarde et de restauration PostgreSQL

**Besoin.** Pouvoir prouver qu'une sauvegarde existe **et** qu'elle est restaurable — sans jamais risquer la base de démonstration par une fausse manœuvre.

**Comportements clés (scripts PowerShell `scripts/backup.ps1` et `scripts/restore.ps1`) :**

- La sauvegarde s'exécute **dans** le conteneur (`pg_dump --format=custom --no-owner --no-privileges`), est copiée vers `backups/` puis contrôlée (fichier non vide). Le format custom permet l'inspection (`pg_restore --list`) et la restauration sélective.
- La restauration **par défaut ne touche jamais la base principale** : elle valide l'archive, restaure dans une base temporaire `opsforge_restore_verify`, compte les tables restaurées, puis supprime la base temporaire.
- La restauration réelle exige deux actions volontaires :

```powershell
if ($MainDatabase) {
    $confirmation = Read-Host "This will replace objects in database '$dbName'. Type RESTORE to continue"
    if ($confirmation -cne "RESTORE") {
        Write-Host "Restore cancelled."
        return
    }
}
```

Le drapeau `-MainDatabase` **et** la saisie exacte de `RESTORE` (comparaison sensible à la casse `-cne`) ; le script arrête alors l'API le temps de la restauration puis la redémarre. Un simple appui sur Entrée, pressé trop vite, annule : il ne détruit pas.

**Preuve.** Validation de la phase 3 (2026-07-06) : archive réelle produite (19 785 octets — conservée localement sur le poste de démonstration, le répertoire `backups/` étant volontairement ignoré par Git ; l'exécution est documentée avec taille et horodatage dans `docs/PHASE3_VERIFICATION.md`), archive validée par `pg_restore --list`, restauration de vérification réussie (6 tables publiques restaurées dans la base temporaire, puis nettoyage), et vérification que `backups/*` est bien ignoré par Git.

**Limite.** Sauvegarde locale du PostgreSQL Compose uniquement : ni chiffrement, ni planification, ni rotation, ni copie externe, ni couverture du PostgreSQL k3d — un mécanisme démontrable, pas une stratégie d'entreprise, et c'est écrit tel quel dans la documentation.

---

# 6. Situation de travail ayant nécessité une recherche

## Le fichier `ansible.cfg` ignoré dans le control node conteneurisé

Cette situation s'est produite lors de l'intégration finale d'Ansible (10-11 août 2026). Elle est entièrement traçable dans le dépôt : les commits `9d04fc4`, `0b21505`, `732d6fa` et `e808ccf` en portent le déroulé, et les fichiers `ansible/Dockerfile` et `ansible/run.sh` en conservent les traces commentées.

### Le problème

Pour exécuter Ansible depuis mon poste Windows, j'avais choisi un control node conteneurisé : une image Docker embarquant Ansible et les CLI nécessaires, le dépôt étant monté dans le conteneur en `/work`. À la première exécution du playbook dans ce conteneur, le résultat a été déroutant :

```text
skipping: no hosts matched
```

Le play ne trouvait **aucun hôte** — alors que l'inventaire (`inventory.ini`, un simple `localhost ansible_connection=local`) existait bel et bien, déclaré dans `ansible.cfg` juste à côté du playbook.

### L'analyse

J'ai vérifié les hypothèses dans l'ordre :

1. *L'inventaire est-il mal écrit ?* Non — le même inventaire fonctionnait quand je le passais à la main.
2. *Ansible s'exécute-t-il dans le bon répertoire ?* Oui — le `WORKDIR` du conteneur était bien `/work/ansible`.
3. *Le fichier `ansible.cfg` est-il seulement lu ?* C'était la bonne piste : `ansible --version` affichait `config file = None`. Ansible ignorait silencieusement le `ansible.cfg` du répertoire courant — et donc la déclaration d'inventaire qu'il contient, d'où le « no hosts matched ».

### La recherche

La documentation officielle d'Ansible, sur la résolution du fichier de configuration, décrit un comportement de sécurité précis : **Ansible refuse de charger un `ansible.cfg` situé dans un répertoire courant inscriptible par tous** (*world-writable*), pour empêcher qu'un fichier de configuration malveillant déposé dans un répertoire partagé soit exécuté à l'insu de l'utilisateur. Un chemin de configuration désigné **explicitement** via la variable d'environnement `ANSIBLE_CONFIG` reste en revanche honoré.

Or c'était exactement mon contexte, sans que je l'aie provoqué : un dépôt Windows monté par bind-mount Docker apparaît, côté Linux, avec des permissions *world-writable*. Le comportement d'Ansible était donc correct et documenté — c'est mon environnement d'exécution qui le déclenchait.

### Les solutions envisagées et le choix

| Option | Analyse |
|---|---|
| `chmod` du répertoire dans le conteneur avant chaque run | Fragile : à refaire à chaque montage, et modifie les permissions perçues d'un dépôt monté |
| Tout passer en ligne de commande, sans `ansible.cfg` | Fonctionne, mais disperse la configuration (inventaire, chemins de rôles, sortie) dans le wrapper |
| Fixer `ANSIBLE_CONFIG` dans l'image du control node | La solution prévue par Ansible pour ce cas : le chemin explicite est honoré malgré le montage world-writable |

J'ai retenu la troisième option, **doublée d'une ceinture de sécurité** : `ENV ANSIBLE_CONFIG=/work/ansible/ansible.cfg` cuit dans l'image du control node, plus un `-i inventory.ini` explicite dans `run.sh` — l'inventaire est ainsi résolu quelle que soit la manière dont la configuration est chargée. Le commentaire du `ansible/Dockerfile` documente ce choix pour un lecteur futur :

```dockerfile
    # Point Ansible at our config explicitly. The repo is bind-mounted from a
    # world-writable location, so Ansible would otherwise ignore ansible.cfg
    # (and thus its inventory) for safety. An explicit ANSIBLE_CONFIG is honoured.
    ANSIBLE_CONFIG=/work/ansible/ansible.cfg
```

### Le deuxième enseignement de la même situation

En corrigeant, j'ai découvert un problème plus embarrassant que le bug lui-même : mes validations initiales avaient été faites avec des commandes ajustées à la main pendant le débogage, et le wrapper `run.sh` **documenté** ne portait pas ces réglages (ni `-i inventory.ini`, ni `--add-host=host.docker.internal:host-gateway`, ni `MSYS_NO_PATHCONV=1` pour neutraliser la réécriture de chemins de Git Bash). Autrement dit : si quelqu'un — le jury, par exemple — avait exécuté le `./run.sh` documenté, il aurait reproduit l'échec initial, alors même que ma documentation affirmait que « ça marchait ».

Le message du commit de correction (`0b21505`) le dit sans détour : *« run.sh did not carry the settings the successful runs actually used, so the documented `./run.sh` would have reproduced the first 'no hosts matched' failure »*. J'ai donc :

1. aligné `run.sh` sur le chemin réellement validé (config explicite, inventaire explicite, résolution `host.docker.internal`, neutralisation MSYS) ;
2. **re-testé l'intégralité du parcours en n'utilisant que `./run.sh`**, sur un cluster isolé : déploiement complet (`/health = 200`, `/ready = 200`), second run idempotent (`ok=21, changed=2`), teardown ;
3. épinglé ensuite les versions exactes du control node validé (`ansible-core==2.17.14`, `kubernetes==36.0.3`, `kubernetes.core:6.5.0`, kubectl v1.31.5, k3d v5.9.0 — commit `732d6fa`) pour que la validation reste reproductible ;
4. retiré de la documentation une affirmation que je ne pouvais pas prouver : le commit initial prétendait que le playbook « tourne aussi directement sur un hôte Linux/WSL » — ce chemin n'avait jamais été validé et n'aurait pas fonctionné tel quel (le kubeconfig est réécrit vers `host.docker.internal`, un nom fourni par le conteneur). Le commit `e808ccf` rétracte cette phrase et fait du control node conteneurisé **la seule méthode supportée et validée**.

### Ce que j'en retiens

- Un comportement de sécurité d'un outil peut n'apparaître que dans un contexte d'exécution particulier ; le diagnostic passe par la lecture de la documentation de l'outil, pas par des essais au hasard.
- **L'artefact documenté doit être exactement celui qui a été validé.** « Ça a fonctionné chez moi avec d'autres commandes » n'est pas une validation.
- Retirer une affirmation non prouvée de sa propre documentation est une correction de qualité au même titre qu'un correctif de code.

---

# 7. Synthèse des validations et preuves

## 7.1 Ce qui a été validé, quand, et où c'est documenté

| Date | Validation | Preuve documentée |
|---|---|---|
| 2026-06-16 | Phase 1 (MVP) : 7 tests verts, 7 endpoints en HTTP 200, flux complet exécuté en conditions réelles via l'API (service → alerte → incident → exécution de runbook → entrée d'audit retrouvée) | `docs/MVP1_VERIFICATION.md` |
| 2026-06-18 | Phase 2 (CI) : run GitHub Actions vert sur le dépôt `ThDyllan/opsforge` (tests, build d'image, scan Trivy dans les logs) | `docs/PHASE2_VERIFICATION.md`, `docs/CI_CD.md` |
| 2026-07-06 | Phase 3 (sauvegarde) : archive réelle produite (19 785 octets), validée par `pg_restore --list`, restauration de vérification (6 tables) dans une base temporaire puis nettoyée, base principale jamais touchée | `docs/PHASE3_VERIFICATION.md` (archives conservées localement — `backups/` est volontairement ignoré par Git) |
| 2026-07-07 → 09 | Phase 4 (Kubernetes) : cluster k3d, pod PostgreSQL `1/1`, PVC `Bound`, **preuve de persistance** (marqueur survivant à la recréation du pod, UID changé), API déployée et joignable (`/health`, `/dashboard` en 200) depuis Windows | `docs/PHASE4_VERIFICATION.md` |
| 2026-07-14 | Phase 5 (supervision) : cible Prometheus `UP`, requêtes PromQL retournant des séries, dashboard Grafana provisionné (5 panneaux alimentés), **cycle d'alerte complet observé** : `inactive` → scale à 0 → `firing` → restauration → `inactive` — état validé : commit `23194f0` (validation documentée par `9bcb271`) | `docs/PHASE5_VERIFICATION.md` |
| 2026-07-17 | Candidat phase 6 : 29 tests SQLite + 1 test PostgreSQL verts, build image, scan Trivy local (19 HIGH / 3 CRITICAL, sans correctif connu), 17 pages HTML représentatives en 200 (sur les 18 routes de la console), 53 liens internes vérifiés, parcours opérateur complet rejoué sur une instance PostgreSQL isolée (dont rejet 409 du doublon d'incident) | `docs/PHASE6_VERIFICATION.md` |
| 2026-08-07 | Audit d'intégration : suite portée à **35 tests** (tests ajoutés : runbooks managés, seed, alerte sans service), Ruff propre, pipeline CI rejoué en clean-room, durcissement Kubernetes vérifié sur cluster réel (pods `1/1 Ready`, HTTP 200 sous rootfs lecture seule, écriture refusée), régression du verrou de service corrigée et testée | `docs/PHASE6_VERIFICATION.md` (section audit) |
| 2026-08-10 → 11 | Automatisation Ansible : déploiement complet depuis zéro sur cluster isolé (`/health = 200`, `/ready = 200`), second run idempotent (`ok=21, changed=2`), teardown/recréation, cluster préexistant intact — re-testé intégralement via `./ansible/run.sh` après les corrections de la section 6 | `docs/ANSIBLE.md` (§ Validation performed — sans date : les dates sont portées par l'horodatage Git des commits `9d04fc4`, `0b21505`, `732d6fa`, `e808ccf`) |

## 7.2 Ce qui reste à faire avant la session (et qui est déjà identifié dans le dépôt)

La documentation du projet (roadmap, `docs/PHASE6_MANUAL_TEST.md`) liste explicitement ce qui reste ouvert, et je le reprends ici sans le maquiller :

- dérouler la **revue manuelle** du parcours opérateur (desktop + responsive) selon la procédure écrite — procédure rendue nécessaire par un fait consigné : l'outil de revue automatisée dans le navigateur n'avait pas pu démarrer le 2026-07-17 (`docs/RISKS_AND_TECHNICAL_DEBT.md`) ;
- produire les **captures d'écran finales** — ce sont les placeholders `[CAPTURE À PRODUIRE]` de ce dossier, consolidés en annexe B ;
- capturer le **run GitHub Actions du commit final** (`8ab0f70`) ;
- prononcer la **validation explicite de la phase 6**, comme pour chacune des phases précédentes.

Ces éléments relèvent de la préparation de l'examen, pas du développement : le candidat technique est gelé, aucune évolution de code n'est prévue d'ici la session.

---

# 8. Limites assumées et pistes d'évolution

Toutes les limites ci-dessous sont documentées dans le dépôt (`docs/RISKS_AND_TECHNICAL_DEBT.md`, ADR, sections « limits » des guides). Ce sont des décisions de périmètre connues — pas des fonctionnalités prétendues puis absentes.

| Domaine | Limite assumée | Évolution naturelle |
|---|---|---|
| Infrastructure | Kubernetes local k3d mono-nœud ; pas de cloud ; stockage `local-path` local au nœud | Kubernetes managé + provisioning Terraform (direction CP n°4) |
| Livraison | Pas de registre d'images ; pas de CD distant ; import k3d manuel ou via Ansible | Registre + déploiement déclenché par la CI |
| Application | Pas d'authentification (champs acteur déclaratifs) ; règle « un incident actif par alerte » garantie au niveau applicatif (409), pas par contrainte d'unicité partielle en base — une course reste possible en multi-workers | Authentification, contrainte PostgreSQL partielle |
| Schéma | `metadata.create_all()` + pont additif de compatibilité ; pas d'historique de migrations ni de retour arrière | Alembic si le schéma continue d'évoluer |
| Supervision | Pas d'Alertmanager ni de notifications ; stockage Prometheus/Grafana éphémère ; Grafana `admin/admin` local ; accès par port-forward ; métriques techniques, pas métier ; **statuts métier simulés** (Prometheus supervise OpsForge lui-même) | Alertmanager + routage, persistance, métriques métier, ingestion des alertes Prometheus dans OpsForge |
| Sécurité | Trivy advisory (19 HIGH / 3 CRITICAL Debian sans correctif visibles, non bloquants) ; pas de TLS ; pas de gestionnaire de secrets d'entreprise | Seuil de blocage explicite (`ignore-unfixed`), gestion de secrets dédiée |
| Sauvegardes | Locales, non chiffrées, non planifiées, sans rotation ni copie externe ; ciblent le PostgreSQL Compose | Planification, chiffrement, externalisation |
| Tests | Majorité SQLite + un test d'intégration PostgreSQL : couverture ciblée, pas une preuve de compatibilité PostgreSQL exhaustive | Étendre les scénarios d'intégration |
| Outillage | Écart de versions entre le kubectl du control node (v1.31.5) et le k3s du cluster (v1.35.x), au-delà de la fenêtre de compatibilité officielle — fonctionnel sur les opérations utilisées et validé tel quel (cf. 3.9) | Aligner les versions épinglées du control node |
| Produit | Files d'attente dimensionnées pour la démonstration (pas de pagination ni temps réel) ; alerte résolue non réouvrable | Selon usage réel |

---

# 9. Conclusion

**Ce que ce projet démontre.** OpsForge couvre les trois compétences obligatoires du titre avec des preuves distinctes et rejouables : une infrastructure locale complète déployée, vérifiée et re-déployée par Ansible en une commande idempotente ; des conteneurs construits, durcis, orchestrés et mis à jour dans deux environnements, avec une persistance prouvée plutôt que supposée ; une supervision réelle dont l'alerte s'est réellement déclenchée lors d'une panne provoquée, puis résolue. Autour de ce cœur, la chaîne couvre le cycle complet en local : 35 tests unitaires et un test d'intégration PostgreSQL, intégration continue avec scan de vulnérabilités, sauvegardes restaurables, documentation et décisions versionnées.

**Mes satisfactions.** D'abord la méthode : six phases finies et validées une à une, chacune avec sa preuve datée — c'est elle qui a permis au projet de survivre sans dégât à un changement de poste de travail en cours de route, et de rester expliquable de bout en bout. Ensuite la correction de trajectoire de la phase 6 : confronter le projet aux critères exacts du référentiel, constater qu'un déploiement documenté mais manuel ne prouvait pas la compétence d'automatisation, et fermer cet écart proprement — avant l'examen. Enfin l'exigence d'honnêteté : le dépôt distingue partout ce qui a été testé de ce qui a seulement été écrit, et il m'est arrivé de retirer de ma propre documentation une affirmation que je ne pouvais pas prouver.

**Mes difficultés.** Le débogage du control node Ansible conteneurisé (section 6) a été la plus formatrice : un comportement de sécurité documenté d'Ansible, déclenché par un contexte de montage Windows que je n'avais pas anticipé, et derrière lui une leçon plus large sur la valeur d'une validation — l'artefact documenté doit être exactement celui qui a été testé. L'impossibilité d'automatiser la revue visuelle dans le navigateur (cf. 7.2) m'a imposé une procédure de test manuelle écrite, encore à dérouler avant la session. Et en continu, la difficulté la plus utile : tenir le périmètre — dire non à Helm, à ArgoCD, au cloud, à tout ce qui aurait grossi le projet sans le rendre plus défendable.

**La suite.** Les évolutions sont identifiées et hiérarchisées (section 8) ; aucune n'est nécessaire pour démontrer les compétences visées. Le projet est gelé au commit `8ab0f70`, et c'est cet état, reproductible et documenté, que je présente au jury.

---

# Annexe A — Chronologie du projet (issue de l'historique Git)

| Date | Événement | Références |
|---|---|---|
| 2026-06-16 | Validation du MVP (travail pré-Git : l'application existe avant le premier commit) | `docs/MVP1_VERIFICATION.md` |
| 2026-06-17 | Premier commit du dépôt : application MVP + workflow CI (`ad9b9df`) | racine de l'historique |
| 2026-06-18 | Validation phase 2 sur run GitHub Actions vert | `9e0666f` |
| 2026-06-18 | Gouvernance du projet : index documentaire, risques, protocole | `b3a80a5`, `917378b` |
| 2026-07-06 | Phase 3 : sauvegarde/restauration + workflow Git documenté | `a317969`, `34f785b` |
| 2026-07-07 → 09 | Phase 4 : fondation k3d/PostgreSQL (4A, vérifiée localement le 07-07) puis API (4B), validation le 09 | `c386c84`, `2772b50` |
| 2026-07-09 → 14 | Phase 5 : métriques (5A), Prometheus (5B), Grafana (5C), règle d'alerte + panne provoquée (5D), validation | `84fb228` → `23194f0`, `9bcb271` |
| 2026-07-15 → 17 | Phase 6 : candidat produit opérateur (console multipage, domaine durci) — débuté sur `main` (07-15), poursuivi sur la première branche dédiée du projet, `phase6-operator-ux` (07-17) | `83469cb` → `230d07a` |
| 2026-08-07 | Audit : branche d'expérimentation revue (jamais fusionnée, conservée comme trace) puis ré-implémentation propre en 6 commits sur `integration/phase6-audit` | `8554232`…`b81cb60` / `fb4d77c`…`fd3dca9` |
| 2026-08-10 | Ajout de l'automatisation Ansible (CP n°2) sur `feature/ansible-infra` | `9d04fc4` |
| 2026-08-11 | Corrections Ansible (situation de recherche), épinglage, honnêteté documentaire | `0b21505`, `732d6fa`, `e808ccf` |
| 2026-08-11 | Intégration finale par Pull Requests avec commits de merge : PR #1 (audit), PR #2 (Ansible), PR #3 (synchronisation documentaire) | `489552f`, `0becdf8`, `8ab0f70` |

État final : **47 commits** toutes branches confondues, 3 commits de merge, candidat d'examen gelé sur `phase6-operator-ux @ 8ab0f70`.

# Annexe B — Liste consolidée des captures d'écran du dossier

Chaque capture ci-dessous correspond à un placeholder du corps du dossier (certains placeholders regroupent plusieurs captures, comme le parcours opérateur de la section 3.2). Aucune ne doit contenir de donnée personnelle ou professionnelle réelle.

| # | Capture | Commande / écran à reproduire |
|---|---|---|
| 1 | Console — `/overview` avec données actives | `docker compose up --build -d` puis `http://localhost:8000/overview` |
| 2 | Console — file d'alertes avec filtres et une alerte dépliée | `http://localhost:8000/alerts` |
| 3 | Console — Incident Command Center avant résolution | ouvrir un incident en investigation depuis `/incidents` |
| 4 | Console — checklist du runbook manuel et résultat en succès | exécuter « Diagnostiquer un échec de sauvegarde » depuis l'incident |
| 5 | Console — timeline de l'incident (responsable, statuts, runbooks) | panneau timeline du Command Center |
| 6 | Console — journal global Activité | `http://localhost:8000/activity` |
| 7 | Console — page Monitoring (réel vs simulé) | `http://localhost:8000/monitoring` |
| 8 | GitHub Actions — run vert du commit final, étapes dépliées (dont Trivy advisory en échec d'étape, job vert) | onglet Actions de `ThDyllan/opsforge`, run de `8ab0f70` |
| 9 | Terminal — Ansible : PLAY RECAP du déploiement complet + messages `verify` (`/health -> 200`, `/ready -> 200`) | `./ansible/run.sh deploy.yml -e cluster_name=opsforge-ansible-test -e api_host_port=8090 -e kubeapi_host_port=6446` |
| 10 | Terminal — Ansible : second run idempotent (`ok=21 changed=2` ou valeurs constatées) | relancer la même commande immédiatement |
| 11 | Terminal — Ansible : teardown du cluster jetable | `./ansible/run.sh teardown.yml -e cluster_name=opsforge-ansible-test` |
| 12 | Terminal — `kubectl -n opsforge get pods,svc,pvc` (pods `1/1`, PVC `Bound`) | sur le cluster déployé |
| 13 | Terminal — preuve de persistance PostgreSQL (marqueur, suppression du pod, marqueur retrouvé) | procédure « persistence check » de `docs/KUBERNETES.md` |
| 14 | Prometheus — page Targets, job `opsforge-api` `UP` | `kubectl -n monitoring port-forward svc/prometheus 9090:9090` → `http://localhost:9090/targets` |
| 15 | Prometheus — `OpsForgeApiDown` en état **FIRING** après scale à 0 | `kubectl -n opsforge scale deployment/opsforge-api --replicas=0` puis `http://localhost:9090/alerts` ; **restaurer ensuite** (`--replicas=1`) |
| 16 | Grafana — dashboard « OpsForge Monitoring », 5 panneaux alimentés | `kubectl -n monitoring port-forward svc/grafana 3000:3000` → `http://localhost:3000` |
| 17 | Terminal — `backup.ps1` (archive créée) puis `restore.ps1` (vérification en base temporaire) | `.\scripts\backup.ps1` ; `.\scripts\restore.ps1 -BackupFile backups\<fichier>.dump` |

# Annexe C — Glossaire

| Terme | Définition dans le contexte du projet |
|---|---|
| **ADR** | *Architecture Decision Record* : décision d'architecture consignée (contexte, décision, raison, conséquences) — 29 dans `docs/DECISIONS.md` |
| **Advisory (scan)** | Scan de sécurité dont les résultats sont visibles mais ne bloquent pas le pipeline |
| **Command Center** | Vue de travail dédiée à un incident dans la console OpsForge : contexte, responsable, transitions, runbooks compatibles, exécutions et timeline |
| **Control node** | Machine (ici : conteneur) depuis laquelle Ansible s'exécute et pilote les cibles |
| **CP** | Compétence professionnelle du REAC (ex. CP n°2 « Automatiser le déploiement d'une infrastructure ») |
| **DoD** | *Definition of Done* : liste vérifiable des conditions de fin d'une phase |
| **Idempotence** | Propriété d'une automatisation qui, rejouée, converge vers le même état sans rien recréer ni casser |
| **k3d** | Outil qui exécute un cluster Kubernetes k3s à l'intérieur de conteneurs Docker |
| **Liveness / readiness** | Sondes Kubernetes : « le processus vit-il ? » (redémarrage si non) / « peut-il servir du trafic ? » (retrait du Service si non) |
| **NodePort** | Type de Service Kubernetes exposant un port du nœud vers l'extérieur (ici 30080, mappé sur `127.0.0.1:8080`) |
| **PVC** | *PersistentVolumeClaim* : demande de stockage persistant, ici 1 Gi en StorageClass `local-path` pour PostgreSQL |
| **REAC** | Référentiel Emploi Activités Compétences : le référentiel officiel du titre professionnel, qui définit les compétences et leurs critères de performance |
| **Runbook** | Procédure opérationnelle : manuelle (checklist) ou automatisée (action approuvée dans le code) |
| **Scrape** | Collecte périodique des métriques par Prometheus (ici toutes les 15 s sur `/metrics`) |
| **Seed** | Insertion idempotente de données de démonstration au démarrage de l'application |
| **StatefulSet** | Contrôleur Kubernetes pour les workloads à état : identité et stockage stables (ici PostgreSQL) |




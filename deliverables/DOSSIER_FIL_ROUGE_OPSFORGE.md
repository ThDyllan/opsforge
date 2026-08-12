# Dossier de projet — OpsForge

## Titre professionnel visé : Administrateur système DevOps (niveau 6)

**Code titre : TP-01414 — RNCP 36061**

| | |
|---|---|
| **Candidat** | Dyllan Thouvignon |
| **Projet** | OpsForge — console locale de gestion d'incidents et sa chaîne DevOps de bout en bout, en local |
| **Type de projet** | Projet fil rouge indépendant, cahier des charges conçu par le candidat |
| **Organisme de formation** | Liora (ex DataScientest) |
| **Session d'examen** | 7 septembre 2026 à 09h30 — Campus Omnes Cœur Défense II, Courbevoie |
| **Dépôt Git** | `ThDyllan/opsforge` — candidat technique gelé : branche `phase6-operator-ux`, commit `8ab0f70` |
| **Version du document** | V2 |

---

## Le projet en 60 secondes

**OpsForge** est une console locale de gestion d'incidents : un opérateur y qualifie des signaux (alertes), ouvre et traite des incidents, applique des procédures contrôlées (runbooks) et conserve la preuve de chaque action (journal d'audit). Autour de cette application, j'ai construit et validé une chaîne DevOps locale complète : conteneurisation, intégration continue, sauvegarde/restauration, déploiement Kubernetes, supervision, et automatisation du déploiement de l'infrastructure.

Les **trois compétences obligatoires** du titre sont couvertes, chacune avec une preuve distincte :

| Compétence obligatoire | Preuve principale | Où |
|---|---|---|
| **Automatiser le déploiement d'une infrastructure** | Playbook Ansible : toute l'infrastructure locale (cluster k3d, PostgreSQL, API, supervision) déployée et vérifiée en une commande idempotente — `/health` et `/ready` en 200 sinon échec | §5.5, §6 |
| **Gérer des containers** | Image durcie non-root, orchestration Compose puis Kubernetes (securityContext complet, probes), stockage persistant dont la persistance est **prouvée** après destruction du pod | §5.2, §5.3, §3.5 |
| **Exploiter une solution de supervision** | Application instrumentée, Prometheus qui la scrape, dashboard Grafana, et une alerte réelle (`OpsForgeApiDown`) observée `inactive → pending → firing → résolue` lors d'une panne provoquée puis réparée | §5.1, §3.6 |

Le périmètre est assumé : tout est local et démontrable ; il n'y a ni cloud, ni registre d'images, ni déploiement continu distant, ni authentification — ce sont des choix documentés, pas des oublis (§8).

---

## Sommaire

- Introduction
- **1. Compétences du référentiel couvertes par le projet**
- **2. Cahier des charges**
- **3. Spécifications techniques** (architecture, schémas, environnements)
- **4. Démarche de travail et outils**
- **5. Réalisations significatives** (scripts et configurations argumentés)
- **6. Situation de travail ayant nécessité une recherche**
- **7. Synthèse des validations**
- **8. Limites assumées et évolutions**
- Conclusion
- Annexe A — Chronologie détaillée du projet
- Annexe B — Inventaire des preuves
- Annexe C — Glossaire

---

## Introduction

Je m'appelle Dyllan Thouvignon. Mon parcours était initialement orienté développement (BTS SIO option SLAM), puis j'ai suivi une formation DevOps en alternance. Mon activité en entreprise étant restée principalement orientée support technique, elle ne m'a pas fourni un projet DevOps suffisamment complet pour couvrir les attendus certificatifs.

À l'issue de ma formation, j'ai donc conçu et réalisé **OpsForge**, un projet fil rouge indépendant, construit de juin à août 2026 pour préparer la certification. Ce n'est pas un projet de mon entreprise d'alternance : il n'utilise aucune donnée ni infrastructure professionnelle, et j'en ai défini le cahier des charges moi-même, à partir des compétences et des attendus du référentiel.

Le fil conducteur du projet : chaque brique doit être **réellement démontrée** — tests exécutés, alerte réellement déclenchée, persistance réellement prouvée, déploiement réellement rejoué — et chaque limite est écrite noir sur blanc dans le dépôt.

---

# 1. Compétences du référentiel couvertes par le projet

## 1.1 Les trois compétences obligatoires, critère par critère

Le REAC (Référentiel Emploi Activités Compétences — « CP » = compétence professionnelle) définit des critères de performance précis. Voici la confrontation exacte d'OpsForge à ces critères.

### CP n°2 — Automatiser le déploiement d'une infrastructure

| Critère REAC | Réponse OpsForge |
|---|---|
| « Les serveurs déployés sont fonctionnels » | Le rôle Ansible `verify` échoue si un pod API n'est pas `Running` ou si `/health` et `/ready` ne répondent pas HTTP 200 (`/ready` exécute un `SELECT 1` sur PostgreSQL). Chaque étage est appliqué avec `wait: true`. Preuve rejouée le 12/08/2026 : `ok=22 changed=9 failed=0`, `/health → 200`, `/ready → 200` |
| « L'architecture est conforme au cahier des charges » | Le playbook orchestre les manifests versionnés de `k8s/` (namespaces, StatefulSet PostgreSQL + PVC, Deployment API + NodePort, Prometheus + Grafana) — il déploie l'architecture documentée, sans rien redéfinir |
| « Les scripts sont documentés » | Cinq rôles courts et commentés, variables centralisées, `ansible/README.md`, justification et correspondance RNCP dans `docs/ANSIBLE.md`, décision d'architecture ADR 029 |
| Savoir associé : « outil de type Ansible ou Terraform » | Ansible + collection `kubernetes.core` (choix argumenté en §5.5) |

*Limite :* cible **k3d local**, pas un fournisseur cloud — l'activité-type « …dans le cloud » n'est pas revendiquée (CP n°4 relèvera de l'entretien technique).

### CP n°7 — Gérer des containers

| Critère REAC | Réponse OpsForge |
|---|---|
| « Les containers sont opérationnels » | Compose : API + PostgreSQL avec healthchecks, démarrage de l'API conditionné à la santé de la base. Kubernetes : pods `1/1 Running` avec probes liveness/readiness distinctes (état constaté le 12/08/2026, §3.5) |
| « Les containers sont connectés au réseau » | Réseau Compose interne (`db:5432`) ; Services Kubernetes ClusterIP (PostgreSQL interne uniquement) et NodePort 30080 exposé sur `127.0.0.1:8080` |
| « Les containers sont connectés au stockage distant » | Stockage **externalisé du cycle de vie du conteneur** et porté par l'hôte — exactement le savoir-faire REAC « connecter le container au système hôte (réseau et stockage) » : volume nommé en Compose, PVC 1 Gi (`local-path`) monté par le StatefulSet en Kubernetes. La persistance est **prouvée** : une donnée survit à la destruction/recréation du pod (§3.5). *Limite énoncée : stockage local au nœud, non distribué (pas de NFS/SAN)* |
| « Les containers sont mis à jour » | Cycle explicite : rebuild de l'image (tags `phase4` → `phase5` → `phase6`), `k3d image import`, rollout du Deployment ; `imagePullPolicy: Never` rend visible l'absence volontaire de registre |

### CP n°10 — Exploiter une solution de supervision

| Critère REAC | Réponse OpsForge |
|---|---|
| « Les indicateurs définis sont pertinents » | Métriques applicatives réelles (`opsforge_http_requests_total`, `opsforge_http_request_duration_seconds` — labels méthode / route template / code) + métrique `up` du scrape ; dashboard : disponibilité, volume, répartition par code, latence p95, répartition par route |
| « Les alertes sont correctement interprétées » | Règle `OpsForgeApiDown` (`up{job="opsforge-api"} == 0` pendant 30 s). Panne provoquée, cycle complet observé et journalisé : `inactive → pending → firing → restauration → inactive` (validé en phase 5, **rejoué en direct le 12/08/2026** — §3.6) |
| « Les échanges avec les développeurs sont réguliers » | *Limite du contexte individuel, assumée :* il n'y a pas d'équipe de développement — je tiens les deux rôles. La boucle supervision → développement existe réellement et elle est **tracée** dans les décisions du dépôt : ajout de `/ready` (ADR 022), labels de route en template pour maîtriser la cardinalité (ADR 017), configuration de scrape statique (ADR 018). En contexte d'équipe, ces constats seraient précisément le contenu des échanges avec les développeurs |

## 1.2 Compétences partiellement mises en pratique

Je ne revendique pas ces compétences comme couvertes ; le projet en met en œuvre une partie, exploitable à l'entretien technique :

| CP | Mis en pratique | Ce qui manque |
|---|---|---|
| CP1 — Créer des serveurs par scripts | Création scriptée et idempotente du nœud k3d ; scripts PowerShell/bash | Pas de création de VM serveur au sens strict |
| CP3 — Sécuriser l'infrastructure | Non-root, rootfs lecture seule, capabilities supprimées, seccomp, secrets hors Git, scan Trivy, bind loopback | Pas d'ANSSI formalisé, ni pare-feu, ni TLS, ni authentification |
| CP5 — Environnement de test | Base PostgreSQL éphémère par test, cluster k3d jetable, conteneur de service en CI | Pas d'environnement mis à disposition d'une équipe |
| CP6 — Stockage des données | PostgreSQL sur deux environnements, PVC prouvé, sauvegarde/restauration testées | Pas de réplication ni de gestion formalisée des droits |
| CP8 — Mise en production avec une plateforme | Déploiement Kubernetes automatisé par Ansible, vérifié de bout en bout | Pas de pré-production/production distinctes, pas de CD |
| CP9 — Statistiques de services | Indicateurs choisis et justifiés (ADR 017) | Pas de SLA formalisés |

**Non couvertes :** CP4 (mise en production cloud — aucun cloud déployé) ; CP11 (anglais — évaluée par le questionnaire ; la documentation du dépôt et les messages de commit sont rédigés en anglais). Conformément aux modalités, ces compétences feront l'objet du questionnement complémentaire à l'entretien technique.

---

# 2. Cahier des charges

## 2.1 Contexte

OpsForge est un projet fil rouge indépendant, réalisé dans le cadre de ma préparation au titre. J'en ai conçu le cahier des charges à partir du référentiel. Le domaine choisi — la gestion d'incidents — est inspiré de mon expérience de support : je connais le cycle « signal → prise en charge → procédure → traçabilité » pour l'avoir vécu au quotidien, ce qui m'a permis de définir un domaine métier crédible sans copier un outil existant ni utiliser la moindre donnée professionnelle réelle.

## 2.2 Problématique et objectifs

**Problématique.** Quand un service supervisé se dégrade, comment garantir qu'un opérateur puisse qualifier le signal, décider d'une prise en charge, appliquer une procédure sûre et prouver ensuite chaque décision — et comment livrer cette application avec une vraie chaîne DevOps : tests automatisés, conteneurs, déploiement automatisé, supervision réelle, sauvegardes vérifiées ?

**Objectifs.**

1. Une application métier fonctionnelle et démontrable, au cycle de vie strict et à l'audit systématique.
2. Une chaîne DevOps locale couvrant les trois compétences obligatoires du titre.
3. Une **preuve d'exécution réelle** pour chaque brique — pas seulement du code.
4. Un ensemble simple, explicable et défendable à l'oral, aux limites connues et écrites.

## 2.3 Utilisateur et cas d'usage

L'utilisateur est un **opérateur unique** (rôle : technicien d'exploitation). Parcours type, entièrement réalisable dans l'interface :

1. Un signal arrive sur un service du catalogue → enregistré comme **alerte** (`new`) ;
2. L'opérateur **acquitte** l'alerte, puis décide s'il ouvre un **incident** (une alerte n'a qu'un incident actif à la fois) ;
3. Il s'attribue l'incident, le passe en **investigation**, applique un **runbook** — checklist manuelle ou automatisation limitée à une liste d'actions approuvées dans le code ;
4. Chaque action alimente le **journal d'audit** et la timeline de l'incident ;
5. Il **résout** l'incident, puis résout l'alerte séparément : le cycle du signal et celui de la prise en charge sont indépendants.

![Vue d'ensemble OpsForge — la console au démarrage d'une prise de poste](assets/screenshots/01_overview.png)
*Figure 1 — Vue d'ensemble : incidents à traiter, alertes récentes avec leur état, état réel de la plateforme (à droite, « contrôles de la plateforme elle-même ») et services de démonstration.*

## 2.4 Besoins

**Fonctionnels :** catalogue de services ; file d'alertes (cycle `new → acknowledged → resolved`, strictement en avant) ; incidents (cycle `open → investigating → resolved`, un seul incident actif par alerte, incident résolu en lecture seule) ; runbooks manuels à checklist et automatisations sur liste approuvée (jamais de commande arbitraire) ; audit de toutes les mutations, y compris les échecs contrôlés ; console multipage utilisable sans outil externe ; distinction affichée entre contrôles réels de la plateforme et états métier simulés.

**Techniques :** API FastAPI + PostgreSQL ; image Docker non-root avec healthcheck ; environnement Docker Compose complet ; CI à chaque push (lint, tests SQLite, test d'intégration PostgreSQL, build, scan de vulnérabilités) ; sauvegarde `pg_dump` scriptée avec restauration de vérification sans risque ; déploiement Kubernetes local (Deployment, StatefulSet, ConfigMap, Secret, PVC, probes, NodePort) ; supervision Prometheus/Grafana avec une alerte démontrable ; **déploiement complet de l'infrastructure en une commande idempotente** (besoin ajouté en cours de projet — §2.7) ; traçabilité générale (Git, documentation par phase, décisions d'architecture).

## 2.5 Contraintes

- Poste **Windows 11 + Docker Desktop** : ce choix contraint directement l'outillage (k3d plutôt qu'une VM, PowerShell pour les sauvegardes, control node Ansible conteneurisé).
- **Projet individuel** mené en parallèle de mon activité professionnelle, sur une période resserrée (juin → août 2026) : phases courtes, finies et validées une à une.
- **Aucune donnée réelle**, budget **zéro cloud**, et **aucune exécution de commande arbitraire** par l'application (vérifié par inspection et par test).
- Changement de poste de travail en cours de projet : la reproductibilité (Git, images, manifests) devait le permettre — et l'a permis.

## 2.6 Livrables et critères d'acceptation

**Livrables :** le dépôt Git complet (application, tests, Dockerfile, Compose, `k8s/`, `ansible/`, scripts, CI) ; la documentation projet (`docs/` : architecture, guides, 29 décisions d'architecture, risques, un fichier de vérification daté par phase) ; le présent dossier et son support de présentation.

**Critères d'acceptation globaux :** environnement Compose fonctionnel (`/health`, `/ready`, console) ; tests verts en local et en CI ; pods Kubernetes `1/1 Ready` et application joignable depuis Windows ; persistance PostgreSQL prouvée après recréation du pod ; alerte de supervision réellement déclenchée puis résolue ; déploiement d'infrastructure rejouable en une commande auto-vérifiée ; sauvegarde produite et restauration vérifiée sans toucher la base principale ; chaque phase validée explicitement et documentée.

## 2.7 Hors périmètre et évolution du périmètre

**Exclusions volontaires** (décisions documentées — ADR, `docs/RISKS_AND_TECHNICAL_DEBT.md`) : cloud et Terraform ; registre d'images et déploiement continu distant ; authentification ; Alembic ; Alertmanager et notifications ; Helm ; React ; haute disponibilité.

**Évolution du périmètre — l'histoire réelle.** Le projet est parti d'un MVP volontairement réduit (application + Compose + 7 tests, cadré par un document initial fixant six phases prévisionnelles et une règle : rien n'entre dans une phase sans décision explicite). Deux extensions ont été décidées en cours de route, tracées dans le dépôt :

- **La phase 6 est devenue une phase produit** : le tableau de bord unique ne permettait pas une démonstration opérateur crédible → console multipage, Command Center par incident, runbooks managés, règles de domaine durcies, campagne de tests portée de 8 à 35 tests.
- **Ansible a été ajouté en fin de projet** : en confrontant le projet aux critères exacts du REAC, j'ai constaté que mon déploiement k3d, documenté mais **manuel**, ne prouvait pas la compétence obligatoire d'automatisation. J'ai fermé cet écart par un périmètre ciblé — automatiser le déploiement existant, sans rien redéfinir (ADR 029, §5.5, §6).

Cette progression itérative est une caractéristique du projet : chaque phase validée fige un socle, et une relecture du référentiel a déclenché une correction de périmètre au bon moment.

---

# 3. Spécifications techniques

## 3.1 Architecture logique

```mermaid
flowchart LR
    subgraph App["Application OpsForge"]
        User[Opérateur] --> Web[Console Jinja2]
        Web --> API[API FastAPI]
        API --> Domain[Domaine : transitions strictes + runbooks approuvés]
        Domain --> DB[(PostgreSQL)]
        API --> Audit[Journal d'audit / timeline]
        API --> Metrics["/metrics"]
    end

    subgraph Supervision["Supervision réelle (k3d)"]
        Metrics --> Prometheus[Prometheus]
        Prometheus --> Grafana[Dashboard Grafana]
        Prometheus --> Rule[Règle OpsForgeApiDown]
    end

    subgraph CI["Chaîne 1 — Intégration continue (GitHub Actions)"]
        Push[push / PR] --> Pipeline[Ruff → 35 tests SQLite → 1 test PostgreSQL → build image → scan Trivy advisory]
    end

    subgraph Infra["Chaîne 2 — Automatisation d'infrastructure (Ansible)"]
        RunSh[Control node conteneurisé ./ansible/run.sh] --> Steps[k3d cluster → build+import image → apply k8s/ ordonné avec wait → verify /health + /ready]
    end
```

Les deux chaînes du bas sont **indépendantes** : la CI valide le code et l'image mais ne publie ni ne déploie rien (pas de registre) ; Ansible reconstruit l'image localement et déploie l'infrastructure locale. *(Les schémas seront exportés en image lors de la mise en page finale.)*

## 3.2 Topologie de déploiement

```mermaid
flowchart TB
    subgraph Host["Poste Windows 11 — Docker Desktop"]
        CN[Control node Ansible<br/>conteneur éphémère] -- pilote --> K3D
        Browser[Navigateur / kubectl] -- "127.0.0.1:8080 → NodePort 30080" --> SVC
        subgraph K3D["Cluster k3d « opsforge » (1 nœud)"]
            subgraph NSApp["namespace opsforge"]
                SVC[Service NodePort 30080] --> DEP[Deployment opsforge-api<br/>non-root, rootfs RO, probes]
                DEP --> PSVC[Service postgres ClusterIP 5432]
                PSVC --> STS[StatefulSet postgres-0]
                STS --> PVC[(PVC postgres-data<br/>1 Gi local-path)]
            end
            subgraph NSMon["namespace monitoring"]
                PROM[Prometheus] -- "scrape :8000/metrics (15 s)" --> DEP
                GRAF[Grafana] --> PROM
            end
        end
    end
```

Accès à la supervision par `kubectl port-forward` (Prometheus 9090, Grafana 3000) — choix documenté qui évite d'exposer davantage un environnement local.

## 3.3 Le domaine applicatif

Six objets : `Service`, `Alert`, `Incident`, `Runbook`, `RunbookExecution`, `AuditLog`. Les règles sont appliquées **côté serveur** et testées négativement :

- transitions strictement en avant (alerte `new → acknowledged → resolved`, résolution directe possible ; incident `open → investigating → resolved`, sans réouverture) — transition invalide → HTTP 409 ;
- une alerte n'a qu'un **seul incident actif** (le doublon → 409 avec l'identifiant de l'incident existant) ; l'incident hérite du service de son alerte source ; résoudre l'incident ne résout pas l'alerte ;
- **aucune exécution arbitraire** : 5 clés d'automatisation approuvées dans le code, clé inconnue → 422 ; les runbooks définis dans le code sont « managés » (lecture seule, PATCH → 409) ; un runbook manuel ne peut pas être déclaré réussi avec une checklist incomplète ;
- toute mutation significative et toute tentative d'exécution — y compris les échecs contrôlés — produisent une entrée d'audit.

Structure du code : `main.py` (démarrage, `/health`, `/ready`, `/metrics`, middleware de métriques), `api.py` (22 routes JSON + gardes), `web.py` (8 sections de console, 18 routes HTML), `domain.py` (transitions), `runbooks.py` (liste approuvée + moteur), `models.py`/`schemas.py`, `seed.py` (scénario de démonstration idempotent), `migrations.py` (pont additif de schéma au démarrage).

![Incident Command Center](assets/screenshots/03_incident_command_center.png)
*Figure 2 — Le Command Center d'un incident : contexte opérationnel, alerte source, runbooks compatibles (manuel/automatisé, niveau de risque), chronologie issue du journal d'audit, historique des exécutions.*

## 3.4 Conteneurs : de Compose à Kubernetes

- **Image API** : base `python:3.12-slim` épinglée par digest, utilisateur non-root UID 10001, `HEALTHCHECK` intégré (§5.2).
- **Compose** (développement, tests, sauvegardes) : PostgreSQL avec healthcheck `pg_isready` et API démarrée seulement quand la base est saine (`depends_on: service_healthy`) ; base publiée sur `127.0.0.1` uniquement ; `tests/` monté en lecture seule.
- **Kubernetes** (déploiement orchestré local) : mêmes conteneurs, contraintes renforcées — init container `wait-for-postgres`, probes distinctes (`/ready` = base joignable, `/health` = processus vivant), securityContext complet, requests/limits (§5.3).
- **Mise à jour** : rebuild → `k3d image import` → rollout ; pas de registre (`imagePullPolicy: Never`, ADR 015).

## 3.5 Stockage et persistance (prouvée)

PostgreSQL utilise un **StatefulSet** (identité stable `postgres-0`, attachement stable au stockage) avec un **PVC de 1 Gi** en StorageClass `local-path` : le stockage est externalisé du cycle de vie du conteneur et porté par l'hôte. État constaté sur le cluster déployé par Ansible (12/08/2026, extrait de `deliverables/evidence/kubernetes_state.txt`) :

```text
pod/opsforge-api-68cbc5b54b-wrdqg   1/1     Running
pod/postgres-0                      1/1     Running
service/opsforge-api   NodePort    8000:30080/TCP
persistentvolumeclaim/postgres-data   Bound   1Gi   RWO   local-path
```

**Preuve de persistance** (rejouée le 12/08/2026, `deliverables/evidence/pvc_persistence.txt`) : un marqueur est inséré, le pod est détruit, le StatefulSet le recrée — l'UID change, la donnée survit :

```text
pod UID avant  : 554c3801-0b0e-42b7-8bf2-99ced94fd488
INSERT INTO persistence_check VALUES ('dossier-v2-persisted');
pod "postgres-0" deleted  →  StatefulSet recrée le pod
pod UID après  : e035ce38-526f-4b3b-9ef5-91aadb3c09f1   (pod réellement nouveau)
SELECT marker  : dossier-v2-persisted                    (donnée retrouvée)
```

*Limite :* `local-path` est local au nœud — la persistance couvre la recréation du pod, pas la destruction du cluster ; c'est le rôle des sauvegardes (§3.7).

## 3.6 Supervision : réel vs simulé

**Le point d'honnêteté central du projet :** Prometheus supervise **OpsForge lui-même** (l'API déployée dans k3d). Les statuts métier des services du catalogue sont des données de démonstration saisies dans l'application, et la console l'affiche explicitement.

![Page Monitoring de la console](assets/screenshots/05_monitoring.png)
*Figure 3 — La page Monitoring sépare la « Supervision réelle » (health, readiness, métriques, Prometheus/Grafana, règle testée) des « États métier simulés » (source : saisie OpsForge), et affiche la limite (pas d'ingestion des alertes Prometheus dans OpsForge).*

La chaîne réelle : middleware FastAPI → `/metrics` → scrape Prometheus toutes les 15 s (cible statique, job `opsforge-api`) → dashboard Grafana provisionné par ConfigMaps (5 panneaux : disponibilité, volume, codes, latence p95, routes) → règle `OpsForgeApiDown` (`up == 0` pendant 30 s, calibrée sur l'intervalle de scrape).

![Cible Prometheus UP](assets/screenshots/06_prometheus_targets_up.png)
*Figure 4 — Prometheus scrape réellement l'API : cible `opsforge-api (1/1 up)` sur `/metrics`.*

**Panne provoquée et alerte réelle** — cycle complet journalisé (12/08/2026, `deliverables/evidence/prometheus_alert_cycle.txt`) :

```text
$ kubectl -n opsforge scale deployment/opsforge-api --replicas=0
t+20s : up=0  OpsForgeApiDown=inactive
t+40s : up=0  OpsForgeApiDown=pending
t+70s : up=0  OpsForgeApiDown=firing      >>> FIRING observé <<<
$ kubectl -n opsforge scale deployment/opsforge-api --replicas=1
t+20s : up=1  OpsForgeApiDown=firing
t+40s : up=1  OpsForgeApiDown=inactive    >>> rétabli, alerte résolue <<<
```

![OpsForgeApiDown en FIRING](assets/screenshots/07_prometheus_alert_firing.png)
*Figure 5 — L'alerte `OpsForgeApiDown` en état FIRING pendant la panne provoquée.*

![Dashboard Grafana OpsForge Monitoring](assets/screenshots/08_grafana_dashboard.png)
*Figure 6 — Le dashboard « OpsForge Monitoring » pendant la session de preuve : disponibilité UP, volume de requêtes (le creux correspond à la panne provoquée), 319 réponses 200 et 2 réponses 503 (redémarrage), latence p95, répartition par route.*

*Limites :* pas d'Alertmanager (l'alerte est visible dans Prometheus, non routée) ; stockage Prometheus/Grafana éphémère ; métriques techniques HTTP, pas métier.

## 3.7 Sauvegarde et restauration

Deux scripts PowerShell ciblent le PostgreSQL de Compose : `backup.ps1` (`pg_dump --format=custom` exécuté dans le conteneur, archive copiée vers `backups/`, refus d'une archive vide) et `restore.ps1` (validation `pg_restore --list`, puis **par défaut** restauration dans une base temporaire de vérification ; la base principale exige `-MainDatabase` **et** la saisie exacte de `RESTORE`). Preuve rejouée le 12/08/2026 (`deliverables/evidence/backup_restore.txt`) :

```text
Backup created: backups\opsforge_backup_20260812_133513.dump   (24 543 octets)
Restore verified in temporary database 'opsforge_restore_verify' (6 public tables).
```

*Limite :* sauvegarde locale, non planifiée, non chiffrée, sans rotation — un mécanisme démontrable, pas une stratégie d'entreprise.

## 3.8 Sécurité

En couches, toutes documentées : (1) par conception — aucune exécution de commande arbitraire, liste d'automatisations approuvées, absence de `subprocess`/`eval` vérifiée ; (2) conteneur — non-root UID 10001, digest épinglé ; (3) Kubernetes — securityContext complet vérifié en conditions réelles (§5.3) ; (4) secrets — `.env` et `secret.local.yaml` ignorés par Git, Secret généré à la volée par Ansible ; (5) chaîne d'approvisionnement — scan Trivy **advisory** à chaque build : le dernier scan de l'image épinglée rapportait 19 HIGH / 3 CRITICAL d'origine Debian sans correctif disponible — une CI verte ne signifie pas « image sans vulnérabilité », et c'est assumé (ADR 013, §5.4).

## 3.9 Environnements et versions

| Composant | Version |
|---|---|
| Application | Python 3.12 (digest épinglé), FastAPI/SQLAlchemy 2.x, OpsForge v0.2.0 |
| Base de données | PostgreSQL 16 (`postgres:16-alpine`) partout |
| Cluster | k3d v5.9.0 / k3s v1.35.x, kubectl client v1.34 |
| Supervision | Prometheus v2.55.1, Grafana 11.3.1 |
| Control node Ansible | ansible-core 2.17.14, kubernetes.core 6.5.0, client Python kubernetes 36.0.3, kubectl v1.31.5, k3d v5.9.0, CLI Docker 27.5.1 — versions validées, épinglées dans `ansible/Dockerfile` |
| CI | GitHub Actions (checkout@v5, setup-python@v6, trivy-action@v0.36.0) |
| Poste | Windows 11 + Docker Desktop |

*Note :* le kubectl du control node (v1.31.5) est plus ancien que le k3s du cluster (v1.35.x), au-delà de la fenêtre officielle ±1 version mineure ; fonctionnel sur les opérations utilisées et validé tel quel — alignement listé en évolution (§8).

---

# 4. Démarche de travail et outils

## 4.1 Six phases, chacune finie et validée

| Phase | Contenu | Validation |
|---|---|---|
| 1 — MVP local | Application + Compose + 7 tests | 16/06/2026 |
| 2 — CI/CD | GitHub Actions : tests, build, scan Trivy | 18/06/2026 (run vert) |
| 3 — Sauvegarde & sécurité | backup/restore, stratégie de secrets | 06/07/2026 |
| 4 — Kubernetes | Cluster k3d, PostgreSQL + PVC, API, **preuve de persistance** | 09/07/2026 |
| 5 — Supervision | `/metrics`, Prometheus, Grafana, **alerte réellement déclenchée** | 14/07/2026 |
| 6 — Produit opérateur & preuves | Console multipage, domaine durci, 35 tests, durcissement K8s, puis **Ansible** (sous-étape CP n°2) | En cours de finalisation : audit d'intégration et Ansible faits ; preuves du présent dossier produites le 12/08/2026 ; reste la revue visuelle/responsive manuelle avant validation explicite |

Chaque phase a un périmètre écrit, une **Definition of Done** vérifiable, un fichier de preuve daté (`docs/PHASE<i>_VERIFICATION.md`) et une validation explicite. Un protocole écrit encadre l'avant/pendant/après (relecture de l'état, départ propre, périmètre figé ; « aucune idée nouvelle n'entre silencieusement dans la phase en cours » ; preuves consignées puis validation). Les choix techniques importants sont consignés dans **29 décisions d'architecture** (ADR) — contexte, décision, raison, conséquences — qui servent aussi de préparation à l'oral.

## 4.2 Workflow Git

Le workflow a évolué avec le projet : commits directs sur `main` pour les phases 1 à 5 (workflow solo simple, un commit de validation par phase), première branche dédiée pour le candidat produit de la phase 6, puis — pour l'audit final et l'ajout d'Ansible — un vrai cycle par branches et **Pull Requests avec commits de merge** (l'historique des branches est préservé). Une branche d'expérimentation a servi de terrain de revue puis n'a **jamais été fusionnée** : une branche d'intégration propre a été ré-implémentée en six commits revus, intégrant les corrections identifiées en revue (dont une vraie régression d'interface et la restauration du signal d'échec Trivy). Le détail commité par commit est en annexe A.

## 4.3 Outils

Python 3.12 / FastAPI / SQLAlchemy / Pydantic / Jinja2 · pytest (SQLite en mémoire + intégration PostgreSQL) · Ruff · Docker & Docker Compose · GitHub Actions · Trivy · k3d/k3s · kubectl · Ansible + `kubernetes.core` · prometheus-client, Prometheus, Grafana · pg_dump/pg_restore (PowerShell) · Git/GitHub.

## 4.4 Collaborations

OpsForge est un **projet individuel** : pas de client, pas d'équipe — je tiens tous les rôles et chaque validation de phase est ma décision, tracée dans le dépôt.

OpsForge étant un projet individuel, j'ai utilisé des assistants d'IA comme outils d'aide à la conception, à l'implémentation et à la revue, selon des règles écrites dans le dépôt (`docs/ENGINEERING_CHARTER.md`, `docs/PHASE_SYNC_PROTOCOL.md`). Je suis resté responsable du cadrage, des choix techniques, des arbitrages et de la validation des résultats ; les changements importants ont été vérifiés et testés avant leur intégration. C'est ce processus qui donne au projet son cycle de revue visible dans l'historique Git (« proposition → implémentation → revue → correction → validation ») ; dans la suite du dossier, « revue » désigne cette revue outillée, conduite sous ma responsabilité.

---

# 5. Réalisations significatives (scripts et configurations argumentés)

Chaque réalisation suit le même fil : besoin → extrait utile → choix → preuve → limite. Les extraits proviennent du dépôt au commit `8ab0f70`, condensés pour la lecture (coupures signalées par `# […]`) ; les fichiers complets sont dans Git.

## 5.1 Instrumentation et alerte de supervision (CP n°10)

**Besoin.** Superviser réellement OpsForge : des métriques produites par l'application elle-même, et une alerte qui se déclenche vraiment.

```python
HTTP_REQUESTS_TOTAL = Counter(
    "opsforge_http_requests_total",
    "Total HTTP requests handled by OpsForge.",
    ["method", "route", "status_code"],
)
# […] middleware : chronomètre chaque requête et alimente compteur + histogramme
labels = {"method": request.method, "route": _route_label(request),
          "status_code": str(response.status_code)}
```

```yaml
- alert: OpsForgeApiDown
  expr: up{job="opsforge-api"} == 0
  for: 30s
  labels: {severity: critical, service: opsforge-api}
```

**Choix.** Le label `route` utilise le *template* FastAPI (`/api/services/{service_id}`), pas l'URL réelle : sans cela, chaque identifiant créerait une série Prometheus distincte (explosion de cardinalité — ADR 017). `/metrics` est exclu de son propre comptage. La règle s'appuie sur la métrique `up` du scrape — elle détecte l'injoignabilité quelle qu'en soit la cause, là où une métrique applicative disparaît avec l'application ; `for: 30s` est calibré sur le scrape de 15 s (un raté isolé ne déclenche pas).

**Preuve.** Cible `UP`, dashboard alimenté, et cycle `inactive → pending → firing → résolu` observé en direct (figures 4-6, §3.6). **Limite.** Pas de routage de notification (pas d'Alertmanager).

## 5.2 Image Docker durcie (CP n°7)

**Besoin.** Une image reproductible qui ne tourne jamais en root, dans Compose comme dans Kubernetes.

```dockerfile
FROM python:3.12-slim@sha256:c3d81d25b3154142b0b42eb1e61300024426268edeb5b5a26dd7ddf64d9daf28
# […]
RUN useradd --create-home --shell /usr/sbin/nologin --uid 10001 opsforge \
    && chown opsforge:opsforge /app
USER opsforge
# […]
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://127.0.0.1:8000/health', timeout=3)"]
```

**Choix.** Digest épinglé (deux builds espacés donnent la même base ; le scan porte sur une image identifiée — ADR 024) ; UID 10001 réutilisé tel quel dans le securityContext Kubernetes ; healthcheck en Python pur (aucune dépendance ajoutée pour la sonde). **Preuve.** Construite à chaque commit en CI ; conteneur `healthy` en Compose ; la même image tourne sous rootfs en lecture seule dans k3d. **Limite.** Les 19 HIGH / 3 CRITICAL Debian résiduels du scan restent visibles et sans correctif disponible — assumés.

## 5.3 Workloads Kubernetes durcis et stockage persistant (CP n°7)

**Besoin.** Déployer avec le principe du moindre privilège, des démarrages ordonnés, et un stockage qui survit aux pods.

```yaml
          securityContext:
            runAsNonRoot: true
            runAsUser: 10001
            runAsGroup: 10001
            allowPrivilegeEscalation: false
            readOnlyRootFilesystem: true
            capabilities: {drop: ["ALL"]}
            seccompProfile: {type: RuntimeDefault}
          # […]
          readinessProbe: {httpGet: {path: /ready, port: http}}
          livenessProbe:  {httpGet: {path: /health, port: http}}
```

**Choix.** Les deux probes sont **différentes**, et c'est le point clé : `/ready` (SELECT 1 sur PostgreSQL) retire l'API du Service quand la base est injoignable ; `/health` ne redémarre le conteneur que si le processus ne répond plus — utiliser `/ready` en liveness provoquerait des redémarrages en boucle pendant une panne de base. Un init container `pg_isready` sérialise le démarrage (l'équivalent du `depends_on` de Compose). PostgreSQL est un **StatefulSet** adossé au PVC (§3.5) ; seul `/tmp` (emptyDir) est inscriptible.

**Preuve.** Vérifié sur cluster réel : pods `1/1 Ready`, pages en 200 sous rootfs lecture seule, écriture dans `/app` refusée (audit du 07/08/2026) ; état re-constaté et persistance re-prouvée le 12/08/2026 (§3.5). **Limite.** Une réplique de chaque workload — la haute disponibilité n'est pas l'objectif du périmètre.

## 5.4 Pipeline d'intégration continue (chaîne 1)

**Besoin.** Vérifier chaque commit : qualité, comportement du domaine, compatibilité avec le moteur de base réel, image, vulnérabilités.

```yaml
      - name: Lint with Ruff
        run: ruff check .
      - name: Run SQLite unit tests
        run: pytest tests/test_app.py
      - name: Run PostgreSQL integration test
        env: {DATABASE_URL: postgresql+psycopg://opsforge:opsforge@127.0.0.1:5432/opsforge}
        run: pytest tests/postgres_integration.py
      - name: Build Docker image
        run: docker build -t "${IMAGE_NAME}:${IMAGE_TAG}" .
      - name: Run Trivy image scan (advisory)
        uses: aquasecurity/trivy-action@v0.36.0
        continue-on-error: true
        with: {scan-type: image, image-ref: "opsforge-api:${{ github.sha }}",
               exit-code: "1", severity: "HIGH,CRITICAL"}  # […]
```

**Choix.** Ordre voulu : lint (échec rapide) → 35 tests SQLite (secondes) → test d'intégration contre un conteneur `postgres:16-alpine` démarré par le job — ce test crée une base au nom unique, rejoue le flux complet, puis la supprime : la CI ne peut pas polluer une base de démonstration. La subtilité Trivy : `exit-code: "1"` garde le signal visible quand des HIGH/CRITICAL existent, `continue-on-error: true` maintient le job vert — politique advisory explicite (ADR 013), transformable en portail bloquant par une décision documentée.

**Preuve.** Run du candidat gelé `8ab0f70` vérifié le 12/08/2026 via l'API GitHub (`deliverables/evidence/github_actions_run.txt`) :

```text
run 31493449973 - CI - branch phase6-operator-ux - sha 8ab0f70 - conclusion: success
Lint with Ruff ................ success      Build Docker image ............. success
Run SQLite unit tests ......... success      Run Trivy image scan (advisory)  success*
Run PostgreSQL integration test success
```

*\* l'API GitHub aplatit l'issue d'une étape `continue-on-error` ; l'interface web, elle, affiche l'état advisory de l'étape.*

`[CAPTURE À PRODUIRE — GitHub Actions : vue graphique du run 31493449973 (job « Lint, test, build, and scan » déplié) — nécessite une session navigateur authentifiée]`

**Limite.** La CI ne publie pas l'image et ne déploie rien : intégration continue, pas de CD distant.

## 5.5 Automatisation du déploiement d'infrastructure avec Ansible (CP n°2, chaîne 2)

**Besoin.** Remplacer la séquence manuelle documentée (`k3d cluster create` + une série de `kubectl apply`) par une commande unique, idempotente et auto-vérifiée.

**Pourquoi Ansible plutôt que Terraform.** Les deux sont cités par le référentiel et légitimes — et Terraform n'est pas « réservé au cloud ». Terraform est déclaratif et à état : on décrit un état cible qu'il réconcilie via des providers. Ma tâche est une **orchestration procédurale multi-outils locale** (préparer le control node → créer le cluster → construire/importer l'image → appliquer des manifests dans un ordre imposé → attendre → vérifier en HTTP) : la forme d'exécution qu'Ansible exprime naturellement, la collection `kubernetes.core` apportant le déclaratif sur les ressources Kubernetes. Terraform deviendrait pertinent pour un provisioning cloud (direction CP n°4, non réalisée). — ADR 029.

```yaml
# rôle cluster — création idempotente
- name: Create the k3d cluster
  ansible.builtin.command: >-
    k3d cluster create {{ cluster_name }} --servers 1
    --api-port 127.0.0.1:{{ kubeapi_host_port }}
    --port "{{ api_host_port }}:{{ node_port }}@server:0" --wait
  when: cluster_name not in (k3d_clusters.stdout | from_json | map(attribute='name') | list)
```

```yaml
# rôle kubernetes_resources — Secret généré, déploiement ordonné et attendu
- name: Create the PostgreSQL Secret from variables
  kubernetes.core.k8s:
    definition:
      kind: Secret
      stringData: {POSTGRES_USER: "{{ db_user }}", POSTGRES_PASSWORD: "{{ db_password }}"}  # […]
- name: Deploy PostgreSQL and wait until it is ready
  kubernetes.core.k8s: {src: "{{ manifests_path }}/{{ item }}", wait: true}  # […]
```

```yaml
# rôle verify — le déploiement se prouve lui-même
- name: Check /ready through the NodePort (proves PostgreSQL connectivity)
  ansible.builtin.uri:
    url: "http://host.docker.internal:{{ api_host_port }}/ready"
  retries: 12
  until: ready.status is defined and ready.status == 200
```

**Choix.** Cluster créé seulement s'il n'existe pas (rejouable sans danger) ; **aucun manifest de Secret versionné** — généré au déploiement depuis des variables (défaut local non sensible, surchargeable `-e` / `ansible-vault`) ; chaque étage appliqué avec `wait: true` (PostgreSQL prêt → API prête → supervision), pas un apply aveugle ; le run ne réussit **que si l'application répond** (`/ready` = preuve de la chaîne complète jusqu'à la base). Le tout s'exécute depuis un **control node conteneurisé** (`./ansible/run.sh`) aux versions épinglées — indispensable sous Windows, et né d'une vraie situation de recherche (§6).

**Preuve.** Rejouée intégralement le 12/08/2026 sur cluster isolé (`deliverables/evidence/ansible_*.txt`) :

```text
Déploiement complet  : PLAY RECAP  ok=22  changed=9  failed=0
                       "/health -> 200 {'status': 'ok', 'service': 'opsforge'}"
                       "/ready  -> 200 {'status': 'ready', 'service': 'opsforge'}"
Second run (idempotence) : PLAY RECAP  ok=21  changed=2  failed=0
Teardown                 : PLAY RECAP  ok=3   changed=1  failed=0
```

**Limites.** Cible k3d locale uniquement ; le control node conteneurisé est la seule méthode validée ; `validate_certs: false` limité à la connexion de contrôle locale vers le cluster éphémère.

## 5.6 Sauvegarde et restauration sûres

**Besoin.** Prouver qu'une sauvegarde existe **et** qu'elle est restaurable, sans jamais risquer la base par une fausse manœuvre.

```powershell
if ($MainDatabase) {
    $confirmation = Read-Host "This will replace objects in database '$dbName'. Type RESTORE to continue"
    if ($confirmation -cne "RESTORE") { Write-Host "Restore cancelled." ; return }
}
```

**Choix.** Format custom (inspectable par `pg_restore --list`) ; restauration **par défaut dans une base temporaire** de vérification, comptage des tables, nettoyage ; la base principale exige le drapeau `-MainDatabase` **et** la saisie exacte de `RESTORE` (sensible à la casse) — un Entrée pressé trop vite annule ; l'API est arrêtée pendant une restauration réelle puis redémarrée. **Preuve.** Rejouée le 12/08/2026 : archive de 24 543 octets créée puis restauration vérifiée (6 tables) dans `opsforge_restore_verify` (§3.7). **Limite.** Locale, non planifiée, non chiffrée.

---

# 6. Situation de travail ayant nécessité une recherche

## Le fichier `ansible.cfg` silencieusement ignoré dans le control node conteneurisé

Situation survenue lors de l'intégration d'Ansible (10-11 août 2026), entièrement traçable dans le dépôt (commits `9d04fc4`, `0b21505`, `732d6fa`, `e808ccf` ; commentaires conservés dans `ansible/Dockerfile` et `ansible/run.sh`).

**Le problème.** Ansible ne s'exécutant pas nativement sous Windows, j'avais choisi un control node conteneurisé : une image Docker embarquant Ansible et les CLI, le dépôt monté en `/work`. Première exécution du playbook dans ce conteneur :

```text
skipping: no hosts matched
```

Aucun hôte trouvé — alors que l'inventaire (`localhost ansible_connection=local`) existait, déclaré dans `ansible.cfg` juste à côté du playbook.

**Le diagnostic.** Hypothèses testées dans l'ordre : inventaire mal écrit ? — non, il fonctionnait passé à la main. Mauvais répertoire de travail ? — non, le `WORKDIR` était correct. Le fichier `ansible.cfg` est-il seulement lu ? — `ansible --version` affichait `config file = None` : Ansible ignorait silencieusement la configuration, donc l'inventaire qu'elle déclare.

**La recherche.** La documentation officielle d'Ansible décrit un comportement de sécurité précis : **un `ansible.cfg` situé dans un répertoire courant inscriptible par tous (*world-writable*) est refusé**, pour empêcher l'injection d'une configuration malveillante dans un répertoire partagé ; un chemin désigné explicitement via `ANSIBLE_CONFIG` reste honoré. Or c'était exactement mon contexte sans que je l'aie provoqué : un dépôt Windows monté par bind-mount Docker apparaît world-writable côté Linux. Le comportement d'Ansible était correct et documenté — c'est mon environnement qui le déclenchait.

**Les options et le choix.** Trois pistes : `chmod` du répertoire à chaque run (fragile) ; tout passer en ligne de commande sans `ansible.cfg` (disperse la configuration) ; fixer `ANSIBLE_CONFIG` dans l'image — la solution prévue par l'outil pour ce cas. J'ai retenu la troisième, doublée d'une ceinture de sécurité : `ENV ANSIBLE_CONFIG=/work/ansible/ansible.cfg` cuit dans l'image, **plus** un `-i inventory.ini` explicite dans `run.sh`.

**Le second enseignement — le plus important.** En corrigeant, j'ai découvert plus embarrassant que le bug : mes validations initiales avaient été faites avec des commandes ajustées à la main pendant le débogage, et le wrapper `run.sh` documenté ne portait pas ces réglages (ni l'inventaire explicite, ni `--add-host=host.docker.internal:host-gateway`, ni `MSYS_NO_PATHCONV=1` qui neutralise la réécriture de chemins de Git Bash). Quiconque aurait exécuté le `./run.sh` documenté — le jury, par exemple — aurait reproduit l'échec initial. Le message du commit de correction le dit sans détour : *« run.sh did not carry the settings the successful runs actually used »*. J'ai donc :

1. aligné `run.sh` sur le chemin réellement validé ;
2. **re-testé l'intégralité du parcours en n'utilisant que `./run.sh`** sur un cluster isolé (déploiement complet, second run idempotent, teardown) ;
3. épinglé les versions exactes du control node validé pour garder la validation reproductible ;
4. retiré de la documentation une affirmation que je ne pouvais pas prouver — le commit initial prétendait que le playbook « tourne aussi directement sur un hôte Linux/WSL » ; ce chemin n'avait jamais été validé et n'aurait pas fonctionné tel quel (le kubeconfig est réécrit vers `host.docker.internal`, un nom fourni par le conteneur). Le control node conteneurisé est devenu **la seule méthode supportée et validée**.

**Ce que j'en retiens.** Un comportement de sécurité d'un outil peut n'apparaître que dans un contexte d'exécution particulier — le diagnostic passe par la documentation, pas par des essais au hasard. Et surtout : **l'artefact documenté doit être exactement celui qui a été validé** ; retirer une affirmation non prouvée de sa propre documentation est une correction de qualité au même titre qu'un correctif de code.

---

# 7. Synthèse des validations

| Domaine | Preuve principale | Résultat |
|---|---|---|
| Application & tests | 35 tests SQLite + 1 test d'intégration PostgreSQL (base éphémère) | Verts en local et en CI |
| Intégration continue | Run GitHub Actions du candidat gelé `8ab0f70` | `success` (toutes étapes) — vérifié le 12/08/2026 |
| Conteneurs & Kubernetes | Pods `1/1 Running`, PVC `Bound`, durcissement vérifié sous rootfs lecture seule | Constaté le 07/08 et re-constaté le 12/08/2026 |
| Persistance | Donnée survivant à la destruction/recréation du pod PostgreSQL (UID différent) | Prouvée en phase 4, **re-prouvée le 12/08/2026** |
| Supervision | Cible UP, dashboard alimenté, cycle d'alerte `inactive → firing → résolu` | Validé en phase 5, **rejoué en direct le 12/08/2026** |
| Automatisation d'infrastructure | Déploiement complet en une commande + idempotence + teardown, `/health` et `/ready` en 200 | Validé aux commits Ansible, **rejoué le 12/08/2026** (`ok=22/9`, `ok=21/2`) |
| Sauvegarde | Archive produite + restauration vérifiée en base temporaire (6 tables) | Validée en phase 3, **rejouée le 12/08/2026** |

Les preuves du 12/08/2026 (logs bruts et captures) sont versionnées sous `deliverables/evidence/` et `deliverables/assets/screenshots/` ; l'historique détaillé phase par phase reste dans `docs/PHASE<i>_VERIFICATION.md` (chronologie en annexe A).

**État de la phase 6 :** l'audit d'intégration, l'automatisation Ansible et les preuves ci-dessus sont faits ; la **revue visuelle et responsive manuelle** du parcours opérateur (procédure `docs/PHASE6_MANUAL_TEST.md`) reste à dérouler avant la validation explicite de la phase — elle sera effectuée lors de la répétition générale.

---

# 8. Limites assumées et évolutions

Toutes documentées dans le dépôt (`docs/RISKS_AND_TECHNICAL_DEBT.md`, ADR) — des choix de périmètre, pas des fonctions prétendues :

| Domaine | Limite | Évolution naturelle |
|---|---|---|
| Infrastructure | k3d mono-nœud local, pas de cloud ; stockage `local-path` local au nœud, non distribué | Kubernetes managé + Terraform (CP n°4) ; stockage réseau |
| Livraison | Pas de registre, pas de CD distant ; import k3d (manuel ou Ansible) | Registre + déploiement déclenché par la CI |
| Application | Pas d'authentification (acteurs déclaratifs) ; unicité d'incident actif garantie par l'application (409), pas par contrainte en base | Authentification ; contrainte PostgreSQL partielle |
| Schéma | `create_all()` + pont additif, pas d'historique de migrations | Alembic |
| Supervision | Pas d'Alertmanager/notifications ; stockage éphémère ; Grafana `admin/admin` local ; port-forward ; métriques techniques ; **états métier simulés** | Alertmanager, persistance, métriques métier, ingestion d'alertes dans OpsForge |
| Sécurité | Trivy advisory (19 HIGH / 3 CRITICAL sans correctif, visibles, non bloquants) ; pas de TLS | Seuil de blocage explicite ; TLS |
| Sauvegardes | Locales, non planifiées, non chiffrées, sans rotation | Planification, chiffrement, externalisation |
| Outillage | Écart de versions kubectl control node (v1.31) / k3s (v1.35) | Alignement des versions épinglées |
| Contexte | Projet individuel : le critère relationnel « échanges avec les développeurs » (CP n°10) est porté par des décisions tracées, pas par une équipe | — |

---

# Conclusion

**Ce que le projet démontre.** Les trois compétences obligatoires, chacune avec une preuve distincte, rejouable et rejouée : une infrastructure locale complète déployée et vérifiée par Ansible en une commande idempotente ; des conteneurs durcis et orchestrés dans deux environnements avec une persistance prouvée plutôt que supposée ; une supervision réelle dont l'alerte s'est déclenchée puis résolue lors d'une panne provoquée. Autour : 35 tests unitaires et un test d'intégration PostgreSQL, une CI avec scan de vulnérabilités, des sauvegardes restaurables, 29 décisions d'architecture documentées.

**Mes satisfactions.** La méthode — six phases finies, validées et datées, qui ont permis au projet de survivre sans dégât à un changement de poste de travail. La correction de trajectoire de la fin de projet : confronter le travail aux critères exacts du référentiel, constater qu'un déploiement documenté mais manuel ne prouvait pas la compétence d'automatisation, et fermer l'écart proprement, avant l'examen. Et une exigence tenue de bout en bout : distinguer partout ce qui a été testé de ce qui a seulement été écrit.

**Mes difficultés.** Le débogage du control node Ansible (§6), le plus formateur — avec sa leçon : l'artefact documenté doit être exactement celui qui a été validé. La revue visuelle qui n'a pas pu être automatisée et reste à dérouler manuellement. Et, en continu, tenir le périmètre : dire non à tout ce qui aurait grossi le projet sans le rendre plus défendable.

Le projet est gelé au commit `8ab0f70` : c'est cet état, reproductible et documenté, que je présente au jury.

---

# Annexe A — Chronologie détaillée du projet

| Date | Événement | Commits |
|---|---|---|
| 16/06/2026 | Validation du MVP (7 tests ; travail pré-Git) | — |
| 17/06/2026 | Premier commit : application MVP + workflow CI | `ad9b9df` |
| 18/06/2026 | Phase 2 validée sur run GitHub Actions vert ; gouvernance (index, risques, protocole) | `9e0666f`, `917378b` |
| 06/07/2026 | Phase 3 : sauvegarde/restauration, workflow Git | `a317969`, `34f785b` |
| 07-09/07/2026 | Phase 4 : k3d + PostgreSQL/PVC (4A, vérifiée le 07), API (4B), preuve de persistance, validation | `c386c84`, `2772b50` |
| 09-14/07/2026 | Phase 5 : métriques (5A), Prometheus (5B), Grafana (5C), alerte + panne provoquée (5D), validation | `84fb228` → `23194f0`, `9bcb271` |
| 15-17/07/2026 | Phase 6 : candidat produit opérateur — débuté sur `main`, poursuivi sur la première branche dédiée `phase6-operator-ux` | `83469cb` → `230d07a` |
| 07/08/2026 | Audit : branche d'expérimentation revue (jamais fusionnée, conservée comme trace), ré-implémentation propre en 6 commits sur `integration/phase6-audit` (35 tests, durcissement K8s vérifié sur cluster réel) | `fb4d77c` → `fd3dca9` |
| 10-11/08/2026 | Ansible (CP n°2) : implémentation, corrections de la situation de recherche (§6), épinglage, honnêteté documentaire | `9d04fc4`, `0b21505`, `732d6fa`, `e808ccf` |
| 11/08/2026 | Intégration finale par Pull Requests avec commits de merge : PR #1 (audit), PR #2 (Ansible), PR #3 (synchronisation documentaire) → candidat gelé | `489552f`, `0becdf8`, `8ab0f70` |
| 12/08/2026 | Production des preuves du présent dossier : re-déploiement Ansible complet + idempotence + teardown, persistance re-prouvée, cycle d'alerte rejoué en direct, sauvegarde/restauration rejouées, CI du candidat vérifiée, captures d'écran | branche `jury/dossier-fil-rouge` |

47 commits toutes branches, 3 commits de merge. `main` porte l'état des phases 1-6 initiales ; le candidat d'examen est `phase6-operator-ux @ 8ab0f70`.

# Annexe B — Inventaire des preuves

## B.1 Captures produites (réelles, versionnées sous `deliverables/assets/screenshots/`)

| # | Fichier | Contenu | Utilisée |
|---|---|---|---|
| 1 | `01_overview.png` | Vue d'ensemble de la console | Figure 1 |
| 2 | `02_alerts.png` | File d'alertes (états Nouvelle/Acquittée/Résolu, filtres) | Réserve oral |
| 3 | `03_incident_command_center.png` | Command Center : contexte, runbooks, timeline, exécutions | Figure 2 |
| 4 | `04_activity.png` | Journal d'audit global | Réserve oral |
| 5 | `05_monitoring.png` | Page Monitoring : réel vs simulé | Figure 3 |
| 6 | `06_prometheus_targets_up.png` | Cible Prometheus `opsforge-api (1/1 up)` | Figure 4 |
| 7 | `07_prometheus_alert_firing.png` | `OpsForgeApiDown` en FIRING | Figure 5 |
| 8 | `08_grafana_dashboard.png` | Dashboard « OpsForge Monitoring » alimenté | Figure 6 |

## B.2 Preuves texte produites (logs bruts, versionnés sous `deliverables/evidence/`)

`ansible_fresh_deploy.txt` (déploiement complet, `ok=22 changed=9`, `/health`/`/ready` → 200) · `ansible_second_run.txt` (idempotence `ok=21 changed=2`) · `ansible_teardown.txt` · `kubernetes_state.txt` (pods/services/PVC/nœud) · `pvc_persistence.txt` (marqueur + UID avant/après) · `prometheus_alert_cycle.txt` (cycle complet horodaté + payload de l'alerte) · `backup_restore.txt` (archive + restauration vérifiée) · `github_actions_run.txt` (run du candidat gelé, étape par étape).

## B.3 Captures restant à faire manuellement

| Capture | Raison / commande |
|---|---|
| GitHub Actions — vue graphique du run `31493449973` | Session navigateur authentifiée requise ; onglet Actions du dépôt, job déplié (l'étape Trivy y apparaît en état advisory) |
| Console — page Aide (optionnelle) | `http://localhost:8000/help` |
| Vues responsives (mobile ~390×844) | À produire pendant la revue manuelle `docs/PHASE6_MANUAL_TEST.md` |

La checklist opérationnelle complète (commandes exactes, ordre de rejeu pour la démonstration) est tenue dans `deliverables/EVIDENCE_PLAN.md` (document de travail, non destiné au jury).

# Annexe C — Glossaire

| Terme | Définition dans le contexte du projet |
|---|---|
| **ADR** | *Architecture Decision Record* : décision consignée (contexte, décision, raison, conséquences) — 29 dans `docs/DECISIONS.md` |
| **Advisory (scan)** | Résultats visibles mais non bloquants pour le pipeline |
| **Command Center** | Vue de travail d'un incident : contexte, responsable, transitions, runbooks, exécutions, timeline |
| **Control node** | Machine (ici : conteneur) depuis laquelle Ansible s'exécute |
| **CP / REAC** | Compétence professionnelle / Référentiel Emploi Activités Compétences du titre |
| **DoD** | *Definition of Done* : conditions vérifiables de fin d'une phase |
| **Idempotence** | Une automatisation rejouée converge sans rien recréer ni casser |
| **k3d** | Cluster Kubernetes k3s exécuté dans des conteneurs Docker |
| **Liveness / readiness** | « Le processus vit-il ? » (redémarrage) / « Peut-il servir ? » (retrait du Service) |
| **NodePort** | Service Kubernetes exposant un port du nœud (30080 → `127.0.0.1:8080`) |
| **PVC** | *PersistentVolumeClaim* : demande de stockage persistant (1 Gi, `local-path`) |
| **Runbook** | Procédure : checklist manuelle ou action automatisée approuvée dans le code |
| **Scrape** | Collecte périodique des métriques par Prometheus (15 s) |
| **StatefulSet** | Contrôleur pour workloads à état : identité et stockage stables (PostgreSQL) |



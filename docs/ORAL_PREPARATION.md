# Preparation Orale OpsForge

## Objectif

Ce guide organise une demonstration RNCP honnete : commencer par le probleme operateur resolu par OpsForge, puis expliquer comment le produit est teste, livre, sauvegarde, deploye et supervise.

Avant l'oral, lire d'abord [`PRODUCT_GUIDE.md`](PRODUCT_GUIDE.md) et executer [`PHASE6_MANUAL_TEST.md`](PHASE6_MANUAL_TEST.md).

## Pitch En 60 Secondes

> OpsForge est une console locale de gestion d'incidents. Elle permet de rattacher un signal a un service, de le qualifier comme alerte, de declarer un incident lorsqu'une prise en charge est necessaire, d'executer une procedure controlee, puis de conserver la preuve de chaque decision et resultat. Autour de cette application, j'ai construit une chaine DevOps avec tests SQLite et PostgreSQL, GitHub Actions, image Docker, scan Trivy, sauvegarde/restauration, deploiement k3d et monitoring Prometheus/Grafana.

## Parcours De Demonstration Recommande

### 1. Expliquer Le Produit

1. Ouvrir `/overview`.
2. Expliquer les incidents actifs, alertes nouvelles, services en difficulte et l'etat reel d'OpsForge.
3. Presenter la chaine :

   ```text
   Service -> Alert -> Incident -> RunbookExecution -> AuditLog
   ```

4. Preciser que le statut des services metier est simule, alors que l'API, PostgreSQL, les metriques et la plateforme DevOps sont reels.

### 2. Jouer Le Scenario Operateur

1. Creer une alerte critique pour Backup Service depuis `/alerts/new`.
2. L'acquitter puis ouvrir un incident.
3. Montrer qu'un second incident actif ne peut pas etre cree depuis la meme alerte.
4. Assigner l'incident a Dyllan et le passer en investigation.
5. Executer le runbook manuel de diagnostic de sauvegarde.
6. Executer le rapport d'incident automatise.
7. Montrer l'historique des executions et la timeline d'audit.
8. Resoudre l'incident, puis montrer que l'alerte reste ouverte jusqu'a sa resolution separee.

La valeur du produit se voit ici : l'operateur reste dans un Command Center unique et n'a pas besoin de copier des identifiants dans Swagger.

### 3. Prouver La Qualite Du Code

```powershell
docker compose exec api pytest tests/test_app.py
docker compose exec api pytest tests/postgres_integration.py
```

Expliquer :

- SQLite donne un retour rapide et isole ;
- PostgreSQL verifie le flux central sur la base reelle du runtime ;
- le test PostgreSQL utilise une base temporaire puis la supprime ;
- les tests ne polluent donc pas les donnees de demonstration.

### 4. Montrer La Chaine CI

Ouvrir le dernier run GitHub Actions du commit candidat et montrer :

- tests SQLite ;
- test PostgreSQL ;
- construction de l'image Docker ;
- scan Trivy non bloquant.

Dire clairement que CI prepare la livraison, mais ne deploie pas automatiquement dans Kubernetes et ne pousse pas d'image dans un registre.

### 5. Expliquer Sauvegarde Et Restauration

Montrer `scripts/backup.ps1` et `scripts/restore.ps1`.

Le point important est que la restauration par defaut valide l'archive dans une base temporaire. Le remplacement de la base principale exige une option et une confirmation explicites.

### 6. Montrer Kubernetes

```powershell
kubectl -n opsforge get pods,svc,pvc
curl.exe http://localhost:8080/health
curl.exe http://localhost:8080/ready
```

Expliquer :

- k3d fournit un cluster k3s local ;
- l'API est un Deployment ;
- PostgreSQL est un StatefulSet avec PVC local-path ;
- `/health` prouve que le processus vit ;
- `/ready` prouve que PostgreSQL est joignable ;
- l'image est importee localement, sans registre.

### 7. Montrer Le Monitoring

Afficher Prometheus, Grafana et `OpsForgeApiDown`. Si la simulation de panne est rejouee, preparer d'abord la commande de restauration :

```powershell
kubectl -n opsforge scale deployment/opsforge-api --replicas=0
kubectl -n opsforge scale deployment/opsforge-api --replicas=1
```

Ne jamais quitter la demonstration avant d'avoir confirme le retour a `1/1`, la cible Prometheus `up`, et Grafana accessible.

## Questions Probables Du Jury

| Question | Reponse honnete |
| --- | --- |
| Pourquoi Jinja2 plutot que React ? | L'interface a besoin de files operateur et d'actions contextuelles, pas d'un second ecosysteme frontend. Jinja et un petit JavaScript gardent le produit coherent avec FastAPI et explicable. |
| Quelle difference entre alerte et incident ? | L'alerte est un signal. L'incident est la decision de prendre officiellement le probleme en charge avec un responsable, un statut, des procedures et une timeline. |
| Pourquoi l'incident ne ferme-t-il pas l'alerte ? | Les deux cycles representent des faits differents. La prise en charge peut etre terminee alors que le signal doit encore etre confirme ou clos separement. |
| Pourquoi deux types de runbook ? | Une checklist couvre les actions humaines. Une automatisation ne peut appeler qu'un comportement connu. Cela apporte de la valeur sans transformer OpsForge en execution de commandes arbitraires. |
| Comment prouvez-vous les actions ? | Chaque mutation importante et chaque tentative de runbook cree une entree AuditLog. Les traces d'un incident alimentent sa timeline. |
| Pourquoi SQLite et PostgreSQL ? | SQLite donne un feedback rapide. Un test separe avec une base PostgreSQL temporaire protege le flux central contre les differences du runtime. |
| Pourquoi `/health` et `/ready` ? | Un processus peut repondre alors que sa base est indisponible. La liveness detecte le processus ; la readiness protege le trafic si PostgreSQL n'est pas utilisable. |
| Pourquoi Trivy reste non bloquant ? | Les findings sont visibles et documentes, mais le projet local n'a pas encore une politique de risque justifiant un seuil de blocage. CI verte ne veut pas dire image sans vulnerabilite. |
| Est-ce du CD complet ? | Non. L'image est construite mais pas publiee, et le deploiement k3d reste manuel. C'est une preparation de livraison reproductible, pas un deploiement automatise. |
| Que feriez-vous en production ? | Migrations versionnees, authentification, contraintes/concurrence renforcees, registre, gestion de secrets, sauvegardes offsite, monitoring persistant, notifications et politique de vulnerabilite. |

## Preuves A Collecter

- Overview et file d'alertes.
- Incident Command Center avant resolution.
- Checklist runbook, resultat et timeline.
- Journal Activity.
- GitHub Actions du commit final.
- Creation et verification de restauration d'une sauvegarde.
- Pods, services, PVC, `/health` et `/ready` dans k3d.
- Cible Prometheus, regle `OpsForgeApiDown` et dashboard Grafana.
- Scan Trivy et explication de la politique non bloquante.
- Liste des limites dans `RISKS_AND_TECHNICAL_DEBT.md`.

La liste precise se trouve dans [`PHASE6_MANUAL_TEST.md`](PHASE6_MANUAL_TEST.md).

## Regle De Presentation

Pour chaque choix, repondre dans cet ordre :

1. Le besoin.
2. La solution mise en oeuvre.
3. La preuve de fonctionnement.
4. La limite actuelle.
5. L'amelioration possible.

Cette structure montre la maitrise du projet sans le presenter comme une production qu'il n'est pas.

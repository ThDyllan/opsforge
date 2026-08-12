# EVIDENCE_PLAN — OpsForge (document de travail interne, non destiné au jury)

État de référence : candidat technique `phase6-operator-ux @ 8ab0f70` · dossier sur `jury/dossier-fil-rouge`.
Dernière mise à jour : 12/08/2026 (session de production des preuves V2).

## 1. Statut global

| Preuve | Statut | Fichier |
|---|---|---|
| 1. Vue d'ensemble console | ✅ produite (Edge headless, Compose isolé propre) | `assets/screenshots/01_overview.png` |
| 2. File d'alertes | ✅ produite (réserve oral) | `assets/screenshots/02_alerts.png` |
| 3. Incident Command Center (contexte + runbooks + timeline + exécutions) | ✅ produite | `assets/screenshots/03_incident_command_center.png` |
| 4. Journal Activité | ✅ produite (réserve oral) | `assets/screenshots/04_activity.png` |
| 5. Page Monitoring (réel vs simulé) | ✅ produite | `assets/screenshots/05_monitoring.png` |
| 6. Prometheus target UP | ✅ produite | `assets/screenshots/06_prometheus_targets_up.png` |
| 7. OpsForgeApiDown FIRING | ✅ produite (cycle live complet) | `assets/screenshots/07_prometheus_alert_firing.png` |
| 8. Dashboard Grafana alimenté | ✅ produite (voir note §3) | `assets/screenshots/08_grafana_dashboard.png` |
| 9. Ansible fresh deploy (`ok=22 changed=9`, /health + /ready 200) | ✅ log | `evidence/ansible_fresh_deploy.txt` |
| 10. Ansible idempotence (`ok=21 changed=2`) | ✅ log | `evidence/ansible_second_run.txt` |
| 11. Ansible teardown | ✅ log | `evidence/ansible_teardown.txt` |
| 12. État K8s (pods/svc/PVC/nœud) | ✅ log | `evidence/kubernetes_state.txt` |
| 13. Persistance PVC (marqueur + UID avant/après) | ✅ log | `evidence/pvc_persistence.txt` |
| 14. Cycle d'alerte Prometheus horodaté | ✅ log | `evidence/prometheus_alert_cycle.txt` |
| 15. Backup + restore vérifié | ✅ log | `evidence/backup_restore.txt` |
| 16. Run GitHub Actions du candidat gelé (8ab0f70) | ✅ texte via `gh api` | `evidence/github_actions_run.txt` |
| 17. GitHub Actions — capture graphique du run | ⬜ MANUELLE (session authentifiée) | run `31493449973`, job déplié |
| 18. Page Aide (optionnelle) | ⬜ MANUELLE si souhaitée | `http://localhost:8000/help` |
| 19. Vues responsives (~390×844) | ⬜ MANUELLE — pendant la revue `docs/PHASE6_MANUAL_TEST.md` | — |
| 20. Revue manuelle Phase 6 (desktop + responsive + parcours humain) | ⬜ À FAIRE par Dyllan avant validation explicite de la phase 6 | procédure `docs/PHASE6_MANUAL_TEST.md` |

## 2. Conditions de production (traçabilité)

- **UI (1-5)** : environnement Compose **isolé éphémère** (`docker compose -p opsforge-shot`, API 8020 / DB 5433), seed générique + 1 alerte de démonstration créée par API. Rendu réel par Edge headless (`--headless=new --screenshot`), fenêtres 1440×1080 à 1440×1600. Environnement détruit après capture (`down -v`). Le Compose principal (8000) n'a pas été modifié.
- **K8s/Ansible/monitoring (6-14)** : cluster **jetable** `opsforge-ansible-test` (API 8090, kubeAPI 6446) déployé par `./ansible/run.sh` ; kubeconfig de test explicite pour chaque commande (`--kubeconfig`) ; le cluster `opsforge` existant n'a jamais été touché. Cycle d'alerte : scale 0 → FIRING observé à t+70 s → restauration immédiate → retour `inactive` confirmé. Teardown complet en fin de session ; port-forwards arrêtés.
- **Backup/restore (15)** : Compose principal, mode par défaut (restauration de vérification en base temporaire) — aucune écriture dans la base principale.
- **CI (16)** : `gh api` sur le run du commit `8ab0f70`. Note : l'API GitHub rapporte `success` pour l'étape Trivy car `continue-on-error` aplatit l'issue ; l'état advisory n'est visible que dans l'UI web → d'où la capture manuelle n°17.

## 3. Note Grafana (transparence)

La capture 8 a été prise sur le **cluster jetable**, après activation runtime de l'accès anonyme Viewer (`kubectl set env deployment/grafana GF_AUTH_ANONYMOUS_ENABLED=true GF_AUTH_ANONYMOUS_ORG_ROLE=Viewer`) — uniquement parce qu'un navigateur headless ne peut pas franchir le formulaire de login. **Aucun fichier du dépôt n'a été modifié** ; le cluster a été détruit ensuite. Le dashboard affiché est identique à celui obtenu après login `admin/admin` en démonstration. Les données des panneaux sont réelles : trafic généré vers l'API du cluster de test (240 requêtes) + la panne provoquée, visibles sur les graphes.

## 4. Rejeu pour la démonstration orale (commandes canoniques)

```bash
# Console (Compose)
docker compose up --build -d          # http://localhost:8000/overview

# Automatisation d'infrastructure (cluster jetable)
./ansible/run.sh deploy.yml -e cluster_name=opsforge-ansible-test -e api_host_port=8090 -e kubeapi_host_port=6446
./ansible/run.sh deploy.yml ...       # second run → idempotence
./ansible/run.sh teardown.yml -e cluster_name=opsforge-ansible-test

# Kubernetes / persistance (cluster opsforge, kubeconfig par défaut)
kubectl -n opsforge get pods,svc,pvc
# persistance : procédure docs/KUBERNETES.md (marqueur → delete pod → rollout → select)

# Supervision
kubectl -n monitoring port-forward svc/prometheus 9090:9090   # /targets, /alerts
kubectl -n monitoring port-forward svc/grafana 3000:3000      # login admin/admin
kubectl -n opsforge scale deployment/opsforge-api --replicas=0   # panne
kubectl -n opsforge scale deployment/opsforge-api --replicas=1   # TOUJOURS restaurer

# Sauvegarde
.\scripts\backup.ps1
.\scripts\restore.ps1 -BackupFile backups\<archive>.dump
```

## 5. TODO internes restants (hors dossier jury)

- [ ] Décision `main` : fusionner l'intégration vers `main` **ou** poser un tag (ex. `jury-2026-09`) avant la session — à trancher avec Dyllan/ChatGPT (le dossier V2 ne mentionne plus ce point).
- [ ] Revue manuelle Phase 6 (n°20) puis validation explicite de la phase 6 et mise à jour de §7 du dossier.
- [ ] Captures manuelles n°17 (GitHub Actions UI) et n°19 (responsive) ; n°18 optionnelle.
- [ ] Rendu des deux schémas Mermaid en images lors de la mise en page (aucun renderer disponible dans l'environnement actuel).

# EVIDENCE_PLAN — OpsForge (document de travail interne, non destiné au jury)

État de référence : candidat technique **final** `phase6-operator-ux @ a9ec694` (chaîne : `8ab0f70` → PR #4 `3fc7707` → PR #5 `f6e4a79` → PR #6 doc-only `a9ec694`) · dossier sur `jury/dossier-fil-rouge`.
Dernière mise à jour : 21/08/2026 (passe figures + annexe C « Reproduire les preuves »).

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
| 16. Run GitHub Actions du candidat final (`a9ec694`, run `32197168814`) | ✅ texte via `gh api`, régénéré le 19/08 | `evidence/github_actions_run.txt` |
| 17. GitHub Actions — capture graphique du run | ✅ produite le 21/08/2026 sur le **run final** `32197168814` : page publique du dépôt capturée en navigateur headless, sans session authentifiée ; annotation Trivy recoupée par l'API publique (`annotation_level: failure`, `Process completed with exit code 1.`) | `assets/screenshots/11_github_actions_run.png` (figure 11) |
| 18. Page Aide (optionnelle) | ✅ capturée par Dyllan pendant la revue (réserve orale) | fournie hors dépôt |
| 19. Vues responsives (~390×844) | ✅ produites sur le candidat corrigé (Edge headless, env. isolé) ; la capture de l'**état défectueux** prise pendant la revue est versionnée et sert de « avant » (figures 12/13) | `assets/screenshots/09_command_center_mobile.png`, `10_incidents_mobile.png`, `12_incidents_mobile_avant.png` |
| 20. Revue manuelle Phase 6 (desktop + responsive + parcours humain) | ✅ FAITE — PASS explicite le 19/08/2026 (2 défauts réels trouvés → PR #4/#5, 38 tests, revalidation humaine) | verdict rempli dans `PHASE6_MANUAL_REVIEW_RUNBOOK.md` §6 |

## 2. Conditions de production (traçabilité)

- **UI (1-5)** : environnement Compose **isolé éphémère** (`docker compose -p opsforge-shot`, API 8020 / DB 5433), seed générique + 1 alerte de démonstration créée par API. Rendu réel par Edge headless (`--headless=new --screenshot`), fenêtres 1440×1080 à 1440×1600. Environnement détruit après capture (`down -v`). Le Compose principal (8000) n'a pas été modifié.
- **K8s/Ansible/monitoring (6-14)** : cluster **jetable** `opsforge-ansible-test` (API 8090, kubeAPI 6446) déployé par `./ansible/run.sh` ; kubeconfig de test explicite pour chaque commande (`--kubeconfig`) ; le cluster `opsforge` existant n'a jamais été touché. Cycle d'alerte : scale 0 → FIRING observé à t+70 s → restauration immédiate → retour `inactive` confirmé. Teardown complet en fin de session ; port-forwards arrêtés.
- **Backup/restore (15)** : Compose principal, mode par défaut (restauration de vérification en base temporaire) — aucune écriture dans la base principale.
- **CI (16)** : `gh api` sur le run `32197168814` du commit final `a9ec694` (régénéré le 19/08). Note : l'API GitHub rapporte `success` pour l'étape Trivy car `continue-on-error` aplatit l'issue ; l'état advisory n'est visible que dans l'UI web → d'où la capture manuelle n°17.
- **Responsive (19)** : captures 09/10 prises le 19/08 sur l'environnement isolé `opsforge-review` (API 8021) rebuildé sur le candidat corrigé, Edge headless `--window-size=390,844` avec profil neuf (cache CSS busté). L'apparent débordement de ~17 px vu en headless est un artefact de viewport, réfuté sur vrai device (`scrollWidth <= clientWidth`).

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
- [x] Revue manuelle Phase 6 (n°20) : PASS le 19/08/2026 ; §7 du dossier, runbook et docs candidat (PR #6) synchronisés.
- [x] Capture n°17 (GitHub Actions UI du run final) : faite le 21/08/2026 — le dépôt étant public, aucune session authentifiée n'a été nécessaire.
- [x] Rendu des deux schémas en images : réécrits en SVG puis rasterisés en PNG (`assets/diagrams/`), intégrés comme figures 2 et 3 du dossier Word.
- [x] Mise en page finale : `Dossier_de_projet_OpsForge_Dyllan_Thouvignon.docx` + PDF (26 pages), générés puis relus page par page ; outillage conservé sous `tools/`.

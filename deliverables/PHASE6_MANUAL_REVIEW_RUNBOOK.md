# Runbook — Revue manuelle Phase 6 (à dérouler par Dyllan)

**Durée cible : 15 à 25 minutes.** Version opérationnelle de `docs/PHASE6_MANUAL_TEST.md` : ce runbook guide la dernière validation humaine (visuel, workflow, responsive) avant la validation explicite de la phase 6. Rien n'est pré-coché : le verdict final (§6) est à remplir par toi seul.

**Déjà fait, à ne PAS refaire** : validations Ansible / Kubernetes / persistance / cycle d'alerte Prometheus / backup-restore (rejouées le 12/08/2026, preuves sous `deliverables/evidence/` et `deliverables/assets/screenshots/`). Cette revue porte uniquement sur l'expérience opérateur dans le navigateur + 1 capture GitHub Actions.

**Interdits dans toute capture** : donnée professionnelle réelle, référence client/employeur, secret, chemin personnel sensible. Données de démonstration génériques uniquement.

---

## 0. Préparation (≈ 3 min)

Ouvre un terminal dans le dépôt (`c:\Users\DyllanTHOUVIGNON\Desktop\Work\opsforge`).

**Option recommandée — environnement propre isolé** (le Compose principal contient des résidus de tests peu présentables) :

```bash
API_PORT=8021 POSTGRES_PORT=5434 docker compose -p opsforge-review up -d
# attendre ~10 s puis vérifier :
curl.exe http://localhost:8021/health
curl.exe http://localhost:8021/ready
```

→ Travaille alors sur `http://localhost:8021`. **Teardown à la fin** : `docker compose -p opsforge-review down -v`.

*(Alternative : utiliser le Compose principal sur `http://localhost:8000` — fonctionne, mais les listes contiennent des données de test moins propres.)*

- [ ] `/health` et `/ready` répondent `{"status": "ok"...}` / `{"status": "ready"...}`
- [ ] `http://localhost:8021/overview` s'affiche

## 1. Tour desktop des vues principales (≈ 4 min)

Navigateur en fenêtre large (≥ 1440 px). Visite dans l'ordre : **Vue d'ensemble → Alertes → Incidents → Services → Runbooks → Activité → Monitoring → Aide**.

À chaque page, contrôle rapide :

- [ ] La sidebar montre bien les 8 entrées, l'entrée active est mise en évidence
- [ ] Un seul titre principal par page, pas de texte coupé ni de chevauchement
- [ ] Les icônes s'affichent (pas de carré vide)
- [ ] Aucun débordement horizontal de la page
- [ ] Le bouton global « Déclarer un incident » est visible partout
- [ ] Monitoring : la séparation « Supervision réelle » / « États métier simulés » est claire à la première lecture
- [ ] Aide : le scénario guidé et le glossaire s'affichent

## 2. Workflow opérateur complet (≈ 6-8 min)

Déroule le cycle entier depuis l'interface (aucun outil externe) :

1. **Créer une alerte** — `/alerts` → « Créer une alerte » : service **Backup Service**, source `revue-manuelle`, titre `Validation Phase 6 - 2026xxxx`, message libre de démonstration, sévérité **critique**.
   - [ ] L'alerte apparaît en statut **Nouvelle**
2. **Acquitter** l'alerte depuis la file.
   - [ ] Statut → **Acquittée**
3. **Ouvrir un incident** depuis cette alerte (bouton de la ligne).
   - [ ] Le formulaire est pré-rempli avec le service et l'alerte source (champ service verrouillé)
   - [ ] Après création, retour sur l'alerte : elle propose « Ouvrir l'incident » (pas d'option pour en créer un second)
4. **Command Center** de l'incident : passe le statut **Ouvert → En investigation**, vérifie le responsable (`Dyllan`).
   - [ ] Aucune transition arrière ni saut direct vers « Résolu » proposé
5. **Runbook manuel** « Diagnostiquer un échec de sauvegarde » : lance-le, coche **une partie seulement** des étapes, tente de conclure en succès.
   - [ ] Refusé (exécution enregistrée en échec contrôlé)
   - Recommence en cochant **toutes** les étapes → conclusion **Succès**
   - [ ] L'exécution apparaît dans l'historique + la timeline
6. **Runbook automatisé** « Générer le rapport d'incident » : exécute.
   - [ ] Résultat succès avec résumé de l'incident
7. **Résoudre l'incident** (bouton Résoudre).
   - [ ] L'incident passe en lecture seule ; l'alerte source reste **Acquittée** (pas résolue automatiquement)
8. **Résoudre l'alerte** séparément depuis `/alerts`.
   - [ ] Les deux cycles sont clos ; **Activité** montre la chaîne complète de tes actions horodatées

## 3. Responsive (≈ 4-5 min)

F12 → icône « Toggle device toolbar » (Ctrl+Shift+M).

**Mobile ~390 × 844** (profil « iPhone 12 Pro » ou dimensions manuelles) — repasse sur : Vue d'ensemble, Alertes, le Command Center de ton incident, Monitoring :

- [ ] La sidebar se replie et le menu burger fonctionne
- [ ] « Déclarer un incident » reste accessible
- [ ] Formulaires en une colonne ; panneaux du Command Center empilés
- [ ] Les tableaux défilent **dans leur propre cadre** (pas de scroll horizontal de la page)
- [ ] Rien de superposé, rien de coupé

**Contrôles rapides** : ~768 × 1024 (tablette) puis ~1440 × 900 — un coup d'œil Vue d'ensemble + Command Center à chaque taille :

- [ ] Pas d'anomalie de mise en page à ces deux tailles

## 4. Anomalies à rechercher (transversal)

Note tout ce qui suit dans le verdict, même mineur : chevauchement/texte tronqué · icône ou image manquante · débordement horizontal · bouton ou lien inaccessible/inerte · état incohérent après action (statut non rafraîchi) · erreur dans la console navigateur (F12 → Console) · page 500 · accent/encodage cassé · faute visible dans un libellé.

## 5. Captures à conserver (les seules qui valent la peine)

Les captures desktop propres existent déjà (`deliverables/assets/screenshots/01→08`). Ne conserve ici que ce qui manque :

| # | Capture | Comment |
|---|---|---|
| R1 | **Command Center en mobile** (~390×844) | Pendant l'étape 3, via la device toolbar (Ctrl+Shift+P → « Capture screenshot » dans DevTools) → `deliverables/assets/screenshots/09_command_center_mobile.png` |
| R2 | **Vue d'ensemble en mobile** (optionnelle) | Idem → `10_overview_mobile.png` |
| R3 | **GitHub Actions — run du candidat gelé** (la capture encore manquante) | Connecté sur GitHub : `https://github.com/ThDyllan/opsforge/actions/runs/31493449973` → déplier le job « Lint, test, build, and scan » → capturer la liste des étapes (l'étape Trivy y apparaît avec son marqueur advisory) → `11_github_actions_run.png` |
| R4 | Page Aide (optionnelle) | `/help` desktop → `12_help.png` |

- [ ] Aucune capture ne contient de donnée non générique

## 6. Verdict (à remplir par Dyllan — rien n'est pré-validé)

```
Date de la revue        : ____________
Navigateur / version    : ____________
Résolutions testées     : desktop ____ / mobile ____ / tablette ____
Environnement utilisé   : opsforge-review (8021) / principal (8000)   [entourer]

Bloc 1 — Tour desktop           : PASS / FAIL
Bloc 2 — Workflow opérateur     : PASS / FAIL
Bloc 3 — Responsive             : PASS / FAIL

Anomalies observées (aucune / liste, avec page + taille d'écran) :
- ____________________________________________
- ____________________________________________

Captures conservées :
[ ] 09_command_center_mobile.png
[ ] 10_overview_mobile.png (opt.)
[ ] 11_github_actions_run.png
[ ] 12_help.png (opt.)

Commentaires libres :
______________________________________________

VERDICT GLOBAL : PASS / FAIL

Si PASS : je prononce la validation explicite de la Phase 6      OUI / PAS ENCORE
(Suites si OUI : mettre à jour §7 du dossier + docs/ROADMAP/PHASE6_VERIFICATION —
 à faire dans une passe dédiée, pas pendant la revue.)
```

## 7. Nettoyage

```bash
docker compose -p opsforge-review down -v    # si l'environnement isolé a été utilisé
```

- [ ] Environnement de revue supprimé ; le Compose principal et le cluster `opsforge` n'ont pas été touchés

# Plan de parole — soutenance OpsForge

**Lundi 7 septembre 2026, 09h30** · Campus Omnes Cœur Défense II, Courbevoie
Support : `Soutenance_OpsForge_Dyllan_Thouvignon.pptx` — 18 slides de présentation + 7 slides de secours.

> Les antisèches détaillées sont dans les **notes orateur** de chaque slide.
> En présentation, `Alt+F5` ouvre le mode Présentateur : les notes s'affichent sur ton écran, pas sur celui du jury.

---

## Le déroulé de l'épreuve

| Temps | Ce qui se passe |
|---|---|
| 15 min | Le jury lit ton dossier — **tu n'es pas dans la salle**, tu prépares ta présentation |
| **30 min** | **Ta présentation** ← c'est ce support |
| 30 min | Entretien technique : questions sur le projet **et sur les compétences qu'il ne couvre pas** |
| 30 min | Questionnaire professionnel en anglais |
| 20 min | Entretien final |

---

## Le minutage

| Slides | Séquence | Durée | Cumul |
|---|---|---|---|
| 1 | Ouverture | 0:30 | 0:30 |
| 2 | Le cadre du projet | 1:30 | 2:00 |
| 3 | Le fil de la présentation | 0:30 | 2:30 |
| 4-5 | **1 — Le besoin** : le problème, le cahier des charges | 4:00 | 6:30 |
| 6-7 | **2 — La solution** : la console, les règles | 4:00 | 10:30 |
| 8-9 | **3 — L'architecture** : logique, topologie | 4:00 | 14:30 |
| 10 | **4 — CP n° 2** : Ansible, avant/après ← *pièce maîtresse* | 3:00 | 17:30 |
| 11 | **4 — CP n° 7** : conteneurs durcis, persistance prouvée | 2:30 | 20:00 |
| 12 | **4 — CP n° 10** : l'alerte déclenchée, réel vs simulé | 2:30 | 22:30 |
| 13 | **4 —** CI et sauvegardes | 2:00 | 24:30 |
| 14 | **4 —** Ce que les tests ne voyaient pas | 2:00 | 26:30 |
| 15 | **5 —** Les compétences du référentiel | 1:00 | 27:30 |
| 16 | **6 —** La situation de recherche | 2:00 | 29:30 |
| 17-18 | **7 — Le bilan** : limites, satisfactions et difficultés | 2:30 | **32:00** |

**Marge de compression : ~2 minutes.** Si tu es en retard au repère de mi-parcours :

- **repère à 15 min** → tu dois être au début de la slide 10 (Ansible) ;
- si tu as du retard : raccourcis les slides **5** (cahier des charges) et **9** (topologie), qui sont
  des slides de contexte. **Ne raccourcis jamais 10, 12 et 16** — ce sont les deux compétences
  obligatoires les plus démonstratives et le créneau de recherche imposé par le référentiel.

---

## Les quatre créneaux imposés par le référentiel

Le canevas du diaporama est fixé par les modalités officielles. Tu dois **impérativement** couvrir :

| Attendu officiel | Où c'est traité |
|---|---|
| Présentation de l'entreprise et/ou du service | **Slide 2** — le projet indépendant, assumé |
| Contexte du projet (cahier des charges, contraintes, livrables) | **Slides 4-5** |
| Présentation de l'infrastructure / de l'application | **Slides 6-9** |
| **Un exemple significatif du travail réalisé** | **Slide 10** — Ansible |
| **Un exemple de recherche effectuée** | **Slide 16** — le fichier `ansible.cfg` ignoré |
| Synthèse et conclusion (satisfactions **et** difficultés) | **Slide 18** — les deux colonnes |

Ne saute aucun de ces six points, même sous la pression du temps.

---

## Les six choses à maîtriser avant lundi

### 1. L'histoire d'Ansible, sans notes (slide 10)

C'est ta meilleure séquence, et c'est le créneau « exemple significatif ». Tu dois pouvoir la
raconter les yeux fermés :

> En confrontant mon projet aux critères exacts du référentiel, j'ai constaté que mon déploiement
> Kubernetes était documenté mais **manuel** — il ne prouvait donc pas la compétence
> d'automatisation. J'ai fermé cet écart avec un périmètre ciblé : automatiser le déploiement
> existant, sans rien redéfinir.

Les trois arguments techniques : **idempotence** (`changed=9` au premier run, `changed=2` au second),
**déploiement ordonné** (`wait: true` à chaque étage, pas un apply aveugle), **auto-vérification**
(le run échoue si `/health` et `/ready` ne répondent pas 200).

Et la question qui viendra : *pourquoi Ansible plutôt que Terraform ?* → Terraform est déclaratif et
à état ; ma tâche est une orchestration procédurale multi-outils. Terraform deviendrait pertinent
pour du provisioning cloud.

### 2. Les deux critères que tu ne peux pas cocher — et ta réponse

**« Les containers sont connectés au stockage distant » (CP n° 7).** Ne jamais prétendre que c'est
distant. La réponse :

> Le conteneur est connecté à un stockage externalisé de son cycle de vie et porté par l'hôte. Dans
> mon environnement k3d, la StorageClass `local-path` reste locale au nœud : ce n'est pas un stockage
> réseau. Une StorageClass NFS ou CSI la remplacerait sans modifier le manifest — c'est justement
> l'intérêt de l'abstraction PVC.

**« Les échanges avec les développeurs sont réguliers » (CP n° 10).**

> Projet individuel : je tiens les deux rôles, je ne peux pas revendiquer ce critère au sens strict.
> Ce que je peux montrer, c'est que la boucle supervision → développement existe et qu'elle est
> tracée dans mes décisions d'architecture : c'est la supervision qui m'a fait ajouter `/ready`, qui
> m'a fait passer les labels de route en template. En équipe, ces constats seraient le contenu des
> échanges.

### 3. Réel contre simulé (slide 12)

À dire **spontanément**, avant qu'on te le demande : Prometheus supervise **OpsForge lui-même**, pas
les services métier du catalogue. Ces états-là sont des données de démonstration, et la console
l'affiche. C'est le point qui va asseoir ta crédibilité pour tout le reste de l'entretien.

### 4. Les chiffres à donner sans hésiter

- **38 tests** unitaires + **1 test d'intégration** PostgreSQL
- **45 commits** sur la branche du candidat, dont 6 merges — candidat gelé : **`a9ec694`**
- **29 décisions d'architecture**, **6 phases** validées et datées
- Ansible : **`ok=22 changed=9`** puis **`ok=21 changed=2`**
- Trivy : **19 HIGH / 3 CRITICAL** Debian, sans correctif — visibles, non bloquants
- Phase 6 validée le **19 août 2026**

⚠️ **Piège de chronologie** : la revue manuelle a trouvé les deux défauts alors que la suite comptait
**35 tests**. Les 3 tests ajoutés en non-régression l'ont portée à 38. Ne dis jamais « 38 tests ne
voyaient pas les défauts ».

### 5. L'articulation avec ton dossier professionnel

Le jury a **les deux dossiers**. Il verra que ton DP montre de l'automatisation PowerShell, du
développement d'API et de la supervision réelle — et il peut demander pourquoi tu n'as pas présenté
ça comme projet. Réponse en trois temps :

1. Ce sont des **interventions** et un module applicatif, pas un projet cadré couvrant les trois
   compétences obligatoires.
2. Surtout : **aucune de ces missions ne porte sur les containers**. La compétence « Gérer des
   containers » est obligatoire, et rien dans ton expérience professionnelle ne la démontre.
3. Il te fallait donc un projet qui tienne les trois d'un bloc, avec des preuves rejouables.

**La slide de secours n° 20** cartographie exactement ça — sors-la si la question vient.

Deux corollaires utiles :

- **CP 2 et CP 7 reposent essentiellement sur OpsForge.** Ne survole ni la slide Ansible, ni la
  slide containers : sans elles, ces compétences ne sont couvertes nulle part.
- **Le critère « échanges avec les développeurs » (CP 10), lui, est couvert par ton DP** : supervision
  multi-clients en équipe, module développé dans un dépôt partagé. Après avoir dit que tu ne le
  revendiques pas sur OpsForge, renvoie au DP. Ne laisse pas croire que tu n'as jamais travaillé en
  équipe.

**Et un fil rouge qui relie tes deux dossiers**, à placer si l'occasion se présente : dans ton DP, un
client signale une panne Internet réelle alors que la supervision est « au vert » — la cause était une
licence de filtrage expirée, hors du champ du contrôle. Dans OpsForge, la CI est verte et les tests
passent — et une revue manuelle trouve deux défauts réels. **Même leçon, deux contextes : un voyant
vert ne dit pas que le service rend le service.** C'est ce qui donne de la cohérence à toute ta
candidature.

### 6. La question sur l'IA

Elle viendra peut-être. Réponds calmement, sans gêne :

> J'ai utilisé des assistants d'IA comme outils d'aide à la conception, à l'implémentation et à la
> revue, selon des règles que j'ai écrites dans le dépôt. Je suis resté responsable du cadrage, des
> choix techniques, des arbitrages et de la validation : chaque changement important a été vérifié et
> testé avant d'être intégré.

---

## Trois réflexes pendant la présentation

1. **Ne lis pas les slides.** Elles sont conçues pour que le jury regarde une image ou trois lignes
   pendant que tu racontes. Si tu te retrouves à lire, c'est que tu as sauté ton fil.
2. **Annonce tes limites avant qu'on te les oppose.** Chaque fois que tu le fais, tu gagnes en
   crédibilité. Chaque fois que le jury doit te la sortir, tu en perds.
3. **Ralentis sur les preuves.** Les slides 10 à 14 sont celles où tu démontres. Le reste est du
   contexte : on peut y aller vite.

---

## La phrase de fin

À placer après la slide 18, puis se taire :

> Ce projet n'est pas grand. Il est petit, local, et entièrement vérifiable. J'ai préféré un
> périmètre que je peux prouver de bout en bout à un périmètre impressionnant que je ne pourrais pas
> défendre devant vous.

# Simulation complète de l'oral — OpsForge

**30 minutes.** Écrit à la première personne, comme si je le disais.

> Ce texte n'est **pas à apprendre par cœur**. Il sert à entendre ce que donne la présentation, à
> vérifier le minutage, et à repérer les tournures qui ne sont pas les tiennes — réécris-les.
> Le jour J, tu parles avec tes mots ; ce script te dit seulement *quoi* dire et *combien de temps*.
>
> `[ ]` = indication de mise en scène, pas de texte à prononcer.

---

## SLIDE 1 — OpsForge · 0:30 · cumul 0:30

*[Debout, slide affichée, on respire une fois avant de commencer.]*

« Bonjour. Je m'appelle Dyllan Thouvignon, et je vais vous présenter OpsForge, mon projet fil rouge
pour le titre d'Administrateur Système DevOps.

OpsForge, c'est une console locale de gestion d'incidents. Mais l'application n'est que le support :
ce que je viens vous montrer, c'est la chaîne DevOps complète que j'ai construite et validée autour
d'elle.

Un mot avant de commencer, parce que c'est le fil de toute ma présentation : **tout ce que je vais
vous montrer a été exécuté et vérifié.** Pas seulement écrit. »

*[Slide suivante.]*

---

## SLIDE 2 — Le cadre du projet · 1:30 · cumul 2:00

« D'abord, qui je suis et pourquoi ce projet existe.

Mon parcours est parti du développement — un BTS SIO option SLAM — puis j'ai suivi une formation
DevOps en alternance.

Côté entreprise, je suis technicien systèmes et réseaux chez BlueBearsIT, une ESN qui gère le
système d'information de plusieurs clients. Mon activité a évolué : support et exploitation au
début, puis administration Active Directory et Microsoft 365, supervision, automatisation
PowerShell, et depuis cette année du développement et de l'intégration d'API. Mon dossier
professionnel détaille six de ces situations.

*[Carte du milieu.]*

Seulement — et c'est le point de départ d'OpsForge — **aucune de ces missions ne réunit à elle
seule les trois compétences obligatoires du titre.** Et surtout, aucune ne porte sur les containers.
La compétence « gérer des containers » est obligatoire, et rien dans mon expérience professionnelle
ne la démontre.

J'ai donc conçu un projet qui les réunit, de juin à août 2026.

*[Carte de droite.]*

Ce qui implique deux choses que je veux dire clairement : **OpsForge n'est pas un projet de mon
entreprise.** Il n'utilise aucune donnée ni aucune infrastructure professionnelle. Et j'en ai écrit
le cahier des charges moi-même, à partir du référentiel. »

---

## SLIDE 3 — Le fil de la présentation · 0:30 · cumul 2:30

« Six temps. Le besoin, la solution, l'architecture, puis les preuves — c'est là que je passerai le
plus de temps — un exemple de recherche, et le bilan. »

*[Ne pas commenter les six cases une par une. Enchaîner.]*

---

## SLIDE 4 — Le problème · 2:00 · cumul 4:30

« Le domaine que j'ai choisi vient de mon quotidien : la gestion d'incidents. Je connais ce cycle
pour l'avoir vécu au support.

Un signal arrive sur un service. Quelqu'un doit le qualifier — c'est une vraie alerte ou pas.
S'il décide de la prendre en charge, il ouvre un incident. Il applique une procédure. Et à la fin,
il faut pouvoir dire qui a fait quoi, quand, et pourquoi.

Sans outil, trois choses se perdent. **L'ordre des décisions** — au bout de deux jours, personne ne
sait plus dans quel ordre les choses ont été faites. **La sûreté de la procédure** — rien n'empêche
de sauter une étape ou de conclure trop vite. Et **la preuve** — au moment du bilan, il ne reste que
des souvenirs.

C'est ce dernier point qui m'intéressait le plus, parce qu'il rejoint exactement la façon dont j'ai
mené le projet lui-même : une application qui trace chaque action, construite avec une méthode qui
trace chaque décision. »

---

## SLIDE 5 — Le cahier des charges · 1:30 · cumul 6:00

« Je l'ai écrit à partir du référentiel, et je le résume en trois colonnes.

**Les objectifs** : une application métier réellement démontrable, une chaîne DevOps couvrant les
trois compétences obligatoires, et — c'est le plus important — une preuve d'exécution pour chaque
brique.

**Les contraintes** ont dicté l'outillage, pas l'inverse. Je travaille sur un poste Windows 11 avec
Docker Desktop. D'où k3d plutôt qu'une machine virtuelle, PowerShell pour les sauvegardes, et un
control node Ansible conteneurisé — parce qu'Ansible ne tourne pas nativement sous Windows. J'y
reviendrai, c'est de là qu'est venu mon blocage le plus formateur.

Deux autres contraintes que je me suis imposées : **zéro cloud, zéro donnée réelle**, et **aucune
exécution de commande arbitraire** par l'application. Ce dernier point, je l'ai vérifié : il n'y a
ni `subprocess` ni `eval` dans le code.

**Les livrables** : le dépôt complet, la documentation par phase, vingt-neuf décisions
d'architecture, et le dossier que vous avez entre les mains. »

---

## SLIDE 6 — La console · 2:00 · cumul 8:00

« Voici l'application. *[Laisser deux secondes, puis pointer l'écran.]*

À gauche, huit sections : vue d'ensemble, alertes, incidents, services, runbooks, activité,
monitoring, aide.

Au centre, ce qu'un opérateur voit en prenant son poste : les incidents à traiter, les alertes
récentes avec leur état, et le parcours type tient en cinq étapes. Un signal arrive et devient une
alerte. L'opérateur l'acquitte. Il décide d'ouvrir un incident. Il se l'attribue, le passe en
investigation, applique un runbook. Et il résout l'incident, puis l'alerte séparément — parce que
ce sont deux cycles distincts.

*[Pointer le panneau de droite de la capture.]*

Un détail qui compte : ce panneau à droite, « État réel d'OpsForge », ce sont les contrôles de la
plateforme elle-même — santé, disponibilité de la base. À distinguer des états des services du
catalogue, qui sont des données de démonstration. J'y reviens en détail sur la supervision.

Et tout ce parcours se fait dans l'interface. Pas de Swagger, pas de ligne de commande. C'est ce qui
rend la démonstration possible devant vous. »

---

## SLIDE 7 — Les règles · 2:00 · cumul 10:00

« Ce n'est pas une maquette. Les règles sont appliquées **côté serveur** — l'interface ne fait que
refléter ce que l'API autorise.

Les transitions sont strictement en avant : une alerte va de « nouvelle » à « acquittée » puis
« résolue », jamais en arrière. Un incident ne se rouvre pas. Une transition invalide renvoie un 409.

Une alerte n'a qu'un seul incident actif. Si on essaie d'en ouvrir un second, l'API refuse et
renvoie l'identifiant de l'incident qui existe déjà.

Aucune exécution arbitraire : il y a **cinq automatisations approuvées dans le code**. Une clé
inconnue est rejetée avec un 422.

Un runbook manuel ne peut pas être déclaré réussi avec une checklist incomplète. Et toute mutation
produit une entrée d'audit — **y compris les échecs**. Une tentative refusée est tracée, elle aussi.

*[Encadré du bas.]*

Le point que je veux souligner : chaque règle est **testée négativement**. Mes tests ne vérifient pas
seulement que le cas nominal fonctionne, ils vérifient que le refus a bien lieu. »

---

## SLIDE 8 — Architecture logique · 2:00 · cumul 12:00

« La vue d'ensemble. Trois zones.

En haut à gauche, l'application : l'opérateur, la console, l'API FastAPI, le domaine qui porte les
règles, PostgreSQL. Plus le journal d'audit, et un endpoint `/metrics`.

En haut à droite, la supervision réelle : Prometheus qui vient lire ces métriques toutes les quinze
secondes, une règle d'alerte, un dashboard Grafana.

En bas, **deux chaînes, et je veux qu'on retienne qu'elles sont indépendantes**. La première, c'est
l'intégration continue : à chaque push, lint, tests, build de l'image, scan de vulnérabilités.
**Elle ne publie rien et ne déploie rien.** La seconde, c'est l'automatisation du déploiement, avec
Ansible.

Je le dis tout de suite pour qu'il n'y ait pas d'ambiguïté : **il n'y a pas de déploiement continu
distant, et pas de registre d'images.** C'est un choix de périmètre, documenté. »

---

## SLIDE 9 — Topologie · 1:30 · cumul 13:30

« Où ça tourne, concrètement. Tout tient sur mon poste.

À gauche, le control node Ansible : un conteneur éphémère qui pilote le cluster. À droite, le
cluster k3d — un Kubernetes k3s qui tourne dans des conteneurs Docker, un seul nœud.

Dedans, deux namespaces. Celui de l'application : un service NodePort, le déploiement de l'API,
le service PostgreSQL interne, un StatefulSet et son volume persistant. Et celui de la supervision :
Prometheus et Grafana.

L'API est joignable sur `127.0.0.1:8080` via le NodePort. La supervision, par port-forward — un
choix documenté, pour ne pas exposer davantage un environnement local.

La limite est évidente et je l'assume : mono-nœud, local. Ce n'est pas de la haute disponibilité. »

---

## SLIDE 10 — CP n° 2 : Ansible · 3:00 · cumul 16:30

*[C'est la slide la plus importante. Ralentir.]*

« Première compétence obligatoire : automatiser le déploiement d'une infrastructure.

Et je vais commencer par un aveu, parce qu'il explique tout le reste.

En fin de projet, j'ai confronté mon travail aux critères exacts du référentiel. Et j'ai constaté
que mon déploiement Kubernetes était **documenté, mais manuel** : créer le cluster, construire
l'image, l'importer, appliquer les manifests un par un, attendre, vérifier à la main. C'était écrit,
c'était reproductible — mais ça ne **prouvait pas** une compétence d'automatisation.

J'ai donc fermé cet écart, avec un périmètre volontairement étroit : automatiser le déploiement
existant, sans rien redéfinir.

*[Carte de droite.]*

Résultat : une seule commande. Elle crée le cluster **seulement s'il n'existe pas**. Elle construit
et importe l'image. Elle applique les manifests dans un ordre imposé, en attendant que chaque étage
soit prêt — PostgreSQL, puis l'API, puis la supervision. Ce n'est pas un `kubectl apply` aveugle.

Et surtout, à la fin, elle vérifie en HTTP que l'application répond. `/ready` exécute un `SELECT 1`
sur PostgreSQL : si la base n'est pas joignable, le déploiement échoue. **Le déploiement se prouve
lui-même.**

*[Bloc du bas.]*

Voici le résultat rejoué le 12 août sur un cluster isolé. Premier run : vingt-deux tâches, neuf
changements, zéro échec, et les deux points de contrôle en 200. Second run, exactement la même
commande : vingt et une tâches, **deux changements**. C'est ça, l'idempotence — ce n'est pas une
affirmation, c'est un chiffre qui descend. Et le teardown, qui supprime proprement le cluster.

*[Si le temps le permet, ou en réponse à une question :]* On me demande souvent pourquoi Ansible et
pas Terraform. Les deux sont cités par le référentiel. Terraform est déclaratif et à état : on décrit
une cible qu'il réconcilie. Ma tâche est une orchestration procédurale multi-outils — préparer le
control node, créer le cluster, construire l'image, appliquer dans un ordre imposé, attendre,
vérifier en HTTP. C'est ce qu'Ansible exprime naturellement. Terraform deviendrait pertinent pour du
provisioning cloud. »

---

## SLIDE 11 — CP n° 7 : les containers · 2:30 · cumul 19:00

« Deuxième compétence obligatoire : gérer des containers.

*[Bloc de gauche.]*

L'image ne tourne jamais en root : utilisateur 10001, système de fichiers racine en **lecture
seule**, toutes les capabilities supprimées, profil seccomp par défaut. Seul `/tmp` est inscriptible.
Et je l'ai vérifié en conditions réelles : les pages répondent 200 sous ce rootfs, et une écriture
dans `/app` est refusée.

Un point sur les sondes, parce que c'est celui qui montre qu'on a compris ce qu'on fait. Les deux
sont **différentes**. `/ready` fait un `SELECT 1` sur PostgreSQL : si la base tombe, l'API est
retirée du service, mais elle n'est pas tuée. `/health` ne vérifie que le processus. Utiliser
`/ready` en liveness provoquerait des redémarrages en boucle pendant une panne de base.

*[Bloc de droite.]*

Et la persistance. Je ne me contente pas de dire que le volume persiste, je le prouve. J'insère un
marqueur en base. Je détruis le pod PostgreSQL. Le StatefulSet le recrée — **et l'identifiant du pod
change**, donc c'est bien un pod neuf. Je relis le marqueur : il est là.

*[Encadré ambre.]*

Une limite, et je préfère la dire moi-même : dans mon environnement k3d, la StorageClass
`local-path` reste locale au nœud. **Ce n'est pas du stockage réseau.** Le conteneur est bien
connecté à un stockage externalisé de son cycle de vie et porté par l'hôte, mais si je détruis le
cluster, le volume part avec. Une StorageClass NFS ou CSI la remplacerait sans modifier le manifest —
c'est justement l'intérêt de l'abstraction PVC. »

---

## SLIDE 12 — CP n° 10 : la supervision · 2:30 · cumul 21:30

« Troisième compétence obligatoire : exploiter une solution de supervision.

*[Première capture.]*

Prometheus scrape réellement mon application : la cible `opsforge-api` est up, toutes les quinze
secondes, sur l'endpoint `/metrics` que produit un middleware dans l'API.

*[Deuxième capture.]*

Et voici la règle `OpsForgeApiDown` en état **firing**.

*[Bloc de code.]*

Parce que je ne me suis pas contenté de l'écrire, je l'ai déclenchée. J'ai passé le déploiement à
zéro réplique. Vingt secondes plus tard, la métrique tombe à zéro. À quarante secondes, l'alerte
passe en *pending*. À soixante-dix secondes, elle **firing**. Je restaure, et elle revient à
*inactive*. Le cycle complet, horodaté, est dans mes preuves.

Un choix technique : la règle s'appuie sur la métrique `up` du scrape, pas sur une métrique
applicative — parce qu'une métrique applicative disparaît en même temps que l'application. Et le
délai de trente secondes est calibré sur l'intervalle de scrape, pour qu'un raté isolé ne déclenche
rien.

*[Encadré de droite — le dire posément, c'est le point de crédibilité.]*

Maintenant, le point d'honnêteté central de ce projet. **Prometheus supervise OpsForge lui-même.**
Les états des services du catalogue — Backup Service, Payment Service — sont des données de
démonstration que je saisis dans l'application. Ce ne sont pas des services réellement supervisés.
La console l'affiche explicitement, sur cette page : « supervision réelle » d'un côté, « états métier
simulés » de l'autre. Je ne veux pas que vous puissiez croire une seconde le contraire. »

---

## SLIDE 13 — CI et sauvegardes · 2:00 · cumul 23:30

« Autour de ces trois compétences, deux chaînes courtes.

*[Capture de gauche.]*

L'intégration continue, à chaque push : lint, trente-huit tests SQLite, un test d'intégration contre
un vrai PostgreSQL démarré par le job, build de l'image, scan de vulnérabilités.

Regardez cette capture : le job est **vert**, et pourtant il porte **une annotation d'erreur**.
C'est voulu. L'étape Trivy est configurée pour signaler quand elle trouve des vulnérabilités
critiques — le signal reste visible — mais `continue-on-error` empêche ce signal de bloquer la
livraison. C'est une politique *advisory*, explicite et documentée.

Et je vais au bout : le dernier scan de mon image rapportait **dix-neuf vulnérabilités hautes et
trois critiques**, d'origine Debian, sans correctif disponible. Une CI verte ne veut pas dire « image
sans vulnérabilité ». C'est de la dette de sécurité visible, pas cachée.

*[Carte de droite.]*

Les sauvegardes. Deux scripts PowerShell. Ce que je veux souligner, c'est que **le comportement par
défaut est le comportement sûr** : la restauration se fait dans une base temporaire de vérification.
Écraser la base principale demande un drapeau explicite **et** de taper « RESTORE » en respectant la
casse. Une touche Entrée pressée trop vite annule.

Limite assumée : c'est local, non planifié, non chiffré. Un mécanisme démontrable, pas une stratégie
d'entreprise. »

---

## SLIDE 14 — Ce que les tests ne voyaient pas · 2:00 · cumul 25:30

« Je veux vous raconter la fin du projet, parce que c'est ce que j'en retiens le plus.

Le produit passait ses trente-cinq tests. La CI était verte. J'aurais pu m'arrêter là.

J'ai quand même déroulé une revue manuelle, guidée par un runbook que j'avais écrit : parcours
desktop, workflow opérateur complet, comportement sur mobile.

Elle a trouvé **deux défauts réels**.

Le premier : une erreur 422 dès qu'on cliquait sur « Filtrer » sans choisir de service — le
formulaire envoyait une valeur vide que l'API refusait.

Le second, vous le voyez à gauche : la table des incidents sur mobile, avec les en-têtes qui se
chevauchent et le titre tronqué à quelques caractères. À droite, la même après correction.

*[Encadré du bas.]*

Pourquoi les tests ne les voyaient pas ? Parce qu'ils vérifient des codes de retour et des structures
de page. Ils ne cliquent pas sur un bouton, et ils ne rendent pas une page à 390 pixels.

J'ai corrigé en branches dédiées depuis le candidat gelé, ajouté **trois tests de non-régression** —
la suite est passée de trente-cinq à trente-huit — revalidé, et seulement ensuite validé la phase.

Ce que j'en tire : une procédure de test manuelle documentée n'est pas le reliquat d'un projet mal
automatisé. **C'est la couche qui attrape ce que l'automatisation ne voit pas.** »

---

## SLIDE 15 — Les compétences du référentiel · 1:00 · cumul 26:30

*[Slide de synthèse : la survoler, ne pas la lire.]*

« En résumé : les trois compétences obligatoires, chacune avec une preuve distincte. Ansible pour
l'automatisation du déploiement. Les conteneurs durcis et la persistance prouvée. La supervision et
l'alerte réellement déclenchée.

Et deux nuances que je préfère nommer moi-même. Le stockage reste local au nœud — je l'ai dit. Et le
critère « échanges réguliers avec les développeurs » n'a pas de sens dans un projet individuel : je
tiens les deux rôles. Ce que je peux montrer, c'est que la boucle supervision vers développement
existe, et qu'elle est tracée dans mes décisions d'architecture. C'est la supervision qui m'a fait
ajouter `/ready`. **En revanche, mon dossier professionnel couvre ce critère en contexte réel** :
supervision multi-clients, en équipe, et un module développé dans un dépôt partagé.

Enfin, ce que je ne revendique pas : la mise en production dans le cloud, parce que je n'ai déployé
aucun cloud. »

---

## SLIDE 16 — La situation de recherche · 2:30 · cumul 29:00

« L'exemple de recherche demandé. Un blocage réel, en trois heures de diagnostic.

Ansible ne tourne pas nativement sous Windows. J'utilise donc un control node conteneurisé, avec
mon dépôt monté dedans. Première exécution du playbook :

**« skipping: no hosts matched ».** Aucun hôte trouvé. Alors que mon inventaire existe, déclaré
dans `ansible.cfg`, juste à côté du playbook.

*[Deuxième case.]*

J'ai éliminé les hypothèses dans l'ordre. L'inventaire est mal écrit ? Non, il fonctionne quand je le
passe à la main. Mauvais répertoire de travail ? Non. Et puis j'ai posé la vraie question : **est-ce
que ce fichier est seulement lu ?** `ansible --version` répond : `config file = None`. Ansible
ignorait silencieusement ma configuration — donc l'inventaire qu'elle déclare.

*[Troisième case.]*

La documentation officielle donne la réponse, et c'est un comportement de sécurité : **Ansible refuse
un `ansible.cfg` situé dans un répertoire inscriptible par tous**, pour empêcher qu'on lui injecte
une configuration dans un répertoire partagé. Or un dépôt Windows monté par bind-mount dans Docker
apparaît world-writable côté Linux. Le comportement d'Ansible était correct — c'était mon
environnement qui le déclenchait.

*[Quatrième case.]*

J'ai pesé trois options et retenu celle que l'outil prévoit : fixer `ANSIBLE_CONFIG` dans l'image.

*[Encadré du bas — ralentir, c'est la chute.]*

Mais le plus important est venu après. En corrigeant, j'ai découvert pire que le bug : mes
validations avaient été faites avec des commandes que j'avais ajustées à la main pendant le
débogage. Et le script que je documentais, lui, ne portait pas ces réglages.

Autrement dit : **si vous aviez lancé mon script tel qu'il était documenté, vous auriez reproduit
l'échec initial.**

J'ai aligné le script, tout re-testé en ne passant que par lui, épinglé les versions validées, et
retiré de ma documentation une affirmation que je ne pouvais pas prouver.

Ce que j'en retiens : **l'artefact documenté doit être exactement celui qui a été validé.** »

---

## SLIDES 17 et 18 — Limites et bilan · 1:00 · cumul 30:00

*[Enchaîner les deux, ne pas lire les tableaux.]*

« Mes limites, en une slide : pas de cloud, pas de déploiement continu distant, pas de stockage
réseau, pas d'authentification, une alerte non routée, un scan advisory. **Ce sont des choix de
périmètre, écrits dans le dépôt avant cette soutenance — pas des oublis que j'aurais découverts en
la préparant.**

*[Slide 18.]*

Ce que je retiens. Côté satisfactions : la méthode. Six phases finies, validées et datées une à une —
c'est ce qui a permis au projet de survivre sans dégât à un changement de poste de travail en cours
de route. Et la correction de trajectoire de la fin : constater qu'un déploiement documenté mais
manuel ne prouvait rien, et fermer l'écart avant l'examen plutôt que d'espérer que ça passe.

Côté difficultés : le débogage du control node, le plus formateur. La revue visuelle, impossible à
automatiser, qui a trouvé deux défauts réels. Et, en continu, tenir le périmètre — dire non à tout
ce qui aurait grossi le projet sans le rendre plus défendable.

*[Bandeau sombre.]*

Le projet est gelé au commit `a9ec694`. Le dépôt est public, et chaque preuve de ce dossier est
rejouable — les commandes sont dans le dossier.

*[Marquer un vrai silence, deux secondes.]*

Je vous remercie. Je suis à votre disposition pour vos questions. »

---

# ⚠️ Ce que cette simulation a révélé sur le minutage

Écrit intégralement, ce script fait **environ 2 300 mots réellement prononcés**.

| Débit | Durée |
|---|---|
| Lecture rapide (160 mots/min) | 14 min |
| Débit de présentation courant (145) | 16 min |
| Débit posé (130) | 18 min |
| Débit posé **avec les pauses, les silences et les moments où tu pointes l'écran** | 21 à 25 min |

**Tu risques donc de finir bien avant 30 minutes.** Finir à 27 est normal ; finir à 18 donnerait
l'impression d'un projet mince — ce qu'il n'est pas.

**La première chose à faire aujourd'hui : un passage chronométré, à voix haute, debout.** C'est le
seul moyen de connaître ton débit réel. Puis :

- si tu es **entre 25 et 29 minutes** → ne change rien ;
- si tu es **en dessous de 24 minutes** → intègre la démonstration ci-dessous *dans* la présentation,
  après la slide 7. Elle vaut 3 minutes de contenu réel, et c'est le meilleur usage possible du temps
  qui te reste ;
- si tu es **encore court** → ralentis, et développe la slide 10 (structure des rôles Ansible, la
  condition qui rend la création du cluster idempotente) et la slide 16 (le raisonnement du
  diagnostic, hypothèse par hypothèse). Ce sont les deux endroits où de la profondeur est légitime.

Ne comble jamais en ajoutant des slides. Comble en respirant et en développant ce qui est déjà là.

---

# La démonstration

**Ce que je déconseille formellement : dérouler la chaîne complète en direct** (créer le cluster,
lancer Ansible, attendre les pods). Trois raisons :

1. Le référentiel ne la demande pas — il demande une présentation « à l'aide d'un support de type
   diaporama ». Tes captures sont des preuves recevables.
2. Le déploiement complet prend plusieurs minutes (cluster k3d, images, attente des pods). Impossible
   à caser sans casser ton minutage.
3. Une démo qui échoue devant un jury coûte infiniment plus que ce qu'une démo réussie rapporte.

**Mais la console, elle, ne présente aucun de ces risques** : c'est un onglet de navigateur déjà
ouvert sur une application qui tourne déjà. Rien à lancer, rien à attendre, rien qui puisse échouer
autrement qu'un clic.

Donc, selon ton chronomètre : soit tu l'intègres après la slide 7 comme un temps prévu, soit tu la
gardes en réserve si le jury demande « vous pouvez nous le montrer ? ». Dans les deux cas, elle se
prépare de la même façon.

### Avant d'entrer dans la salle

Pendant les 15 minutes où le jury lit ton dossier, tu es dans une autre pièce. C'est là que tu
prépares :

```
docker compose up -d
```

Vérifie `http://localhost:8000/overview` dans un onglet **déjà ouvert**, et laisse-le en arrière-plan.
Pas besoin du cluster k3d : la console suffit largement.

### Le déroulé — 3 minutes montre en main, pas plus

*[Alt-Tab vers le navigateur.]*

1. **La file d'alertes.** « Voici les signaux à qualifier. Celle-ci est critique, elle n'est pas
   encore prise en charge. » → *Acquitter*.
2. **Ouvrir l'incident.** « Le formulaire est pré-rempli avec le service et l'alerte source, et le
   champ service est verrouillé — l'incident hérite du service de son alerte. »
3. **Le Command Center.** « Contexte, responsable, transitions possibles — vous remarquerez qu'on ne
   me propose pas de revenir en arrière ni de sauter directement à résolu. »
4. **Un runbook.** Coche une partie des étapes seulement, tente de conclure en succès. « Refusé. Et
   l'échec est quand même audité. »
5. **L'activité.** « Et voilà la chaîne complète de ce que je viens de faire, horodatée. »

*[Retour aux slides.]*

**Ne montre rien d'autre.** Pas de terminal, pas de `kubectl`, pas de Grafana. Si on insiste sur le
cluster, réponds : « il tourne sur ce poste, mais le déployer prendrait quelques minutes — les
preuves d'exécution sont dans le dossier, avec les commandes pour les rejouer. »

---

# Repères de contrôle pendant la présentation

| Si à ce moment tu es… | …tu dois être sur |
|---|---|
| **8 minutes** | Slide 6 (la console) |
| **14 minutes** | Slide 9 (topologie) — dernière slide de contexte |
| **16 minutes** | Slide 10 (Ansible) ← **le repère critique** |
| **26 minutes** | Slide 15 (compétences) |

**Si tu as plus de deux minutes de retard à la slide 10 :** raccourcis les slides 13 et 15 (une
phrase chacune) et garde intégralement 14, 16 et 18. Ne sacrifie jamais Ansible, la supervision, ni
la situation de recherche : ce sont les deux compétences les plus démonstratives et le créneau
obligatoire.

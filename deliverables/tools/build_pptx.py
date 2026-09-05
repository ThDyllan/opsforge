# -*- coding: utf-8 -*-
"""Support de soutenance OpsForge (.pptx) + notes orateur."""
import os

from PIL import Image
from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import MSO_ANCHOR, PP_ALIGN
from pptx.util import Emu, Inches, Pt

ROOT = r"C:\Users\DyllanTHOUVIGNON\Desktop\Work\opsforge"
DELIV = os.path.join(ROOT, "deliverables")
SHOTS = os.path.join(DELIV, "assets", "screenshots")
FIGS = os.path.join(DELIV, "assets", "figures")
DIAG = os.path.join(DELIV, "assets", "diagrams")
OUT = os.path.join(DELIV, "Soutenance_OpsForge_Dyllan_Thouvignon.pptx")

TEAL = RGBColor(0x0F, 0x76, 0x6E)
TEAL_D = RGBColor(0x11, 0x5E, 0x59)
INK = RGBColor(0x1E, 0x29, 0x3B)
MUTE = RGBColor(0x64, 0x74, 0x8B)
LIGHT = RGBColor(0xF1, 0xF5, 0xF9)
TINT = RGBColor(0xEC, 0xFD, 0xF5)
TINT_B = RGBColor(0x5E, 0xEA, 0xD4)
AMB = RGBColor(0xB4, 0x53, 0x09)
AMB_BG = RGBColor(0xFF, 0xFB, 0xEB)
AMB_BD = RGBColor(0xFC, 0xD3, 0x4D)
BLU = RGBColor(0x1D, 0x4E, 0xD8)
BLU_BG = RGBColor(0xEF, 0xF6, 0xFF)
BLU_BD = RGBColor(0x93, 0xC5, 0xFD)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
DARK = RGBColor(0x0F, 0x17, 0x2A)
BORD = RGBColor(0xCB, 0xD5, 0xE1)

HEAD = "Segoe UI Semibold"
BODY = "Segoe UI"
MONO = "Consolas"

W, H = 13.333, 7.5
ML, MR = 0.72, 0.72
CW = W - ML - MR

prs = Presentation()
prs.slide_width = Inches(W)
prs.slide_height = Inches(H)
BLANK = prs.slide_layouts[6]

_n = [0]


def S(footer=True):
    s = prs.slides.add_slide(BLANK)
    _n[0] += 1
    if footer:
        t = box(s, W - 1.5, H - 0.46, 1.0, 0.3, str(_n[0]), 10, MUTE, align=PP_ALIGN.RIGHT)
        box(s, ML, H - 0.46, 6.0, 0.3, "OpsForge  ·  Dyllan Thouvignon", 10, MUTE)
    return s


def box(slide, x, y, w, h, text="", size=16, color=INK, font=BODY, bold=False,
        align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, italic=False, spacing=1.0):
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    p = tf.paragraphs[0]
    p.alignment = align
    p.line_spacing = spacing
    r = p.add_run()
    r.text = text
    r.font.size = Pt(size)
    r.font.color.rgb = color
    r.font.name = font
    r.font.bold = bold
    r.font.italic = italic
    return tb


def rich(slide, x, y, w, h, lines, align=PP_ALIGN.LEFT, anchor=MSO_ANCHOR.TOP, spacing=1.0):
    """lines : liste de (texte, taille, couleur, gras, font, espace_avant)."""
    tb = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h))
    tf = tb.text_frame
    tf.word_wrap = True
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    tf.vertical_anchor = anchor
    for i, spec in enumerate(lines):
        txt, sz, col, bold, fnt, before = spec
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.alignment = align
        p.line_spacing = spacing
        p.space_before = Pt(before)
        r = p.add_run()
        r.text = txt
        r.font.size = Pt(sz)
        r.font.color.rgb = col
        r.font.bold = bold
        r.font.name = fnt
    return tb


def rect(slide, x, y, w, h, fill=None, line=None, rounded=True, lw=1.25):
    shp = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE if rounded else MSO_SHAPE.RECTANGLE,
        Inches(x), Inches(y), Inches(w), Inches(h))
    if rounded:
        shp.adjustments[0] = 0.06
    if fill is None:
        shp.fill.background()
    else:
        shp.fill.solid()
        shp.fill.fore_color.rgb = fill
    if line is None:
        shp.line.fill.background()
    else:
        shp.line.color.rgb = line
        shp.line.width = Pt(lw)
    shp.shadow.inherit = False
    return shp


def title(slide, kicker, ttl, sub=None):
    two = len(ttl) > 56
    if kicker:
        box(slide, ML, 0.42, CW, 0.28, kicker.upper(), 12, TEAL, HEAD, bold=True)
    box(slide, ML, 0.72, CW, 1.05 if two else 0.62, ttl, 27 if two else 30, INK, HEAD,
        bold=True, spacing=0.95)
    ry = 1.78 if two else 1.42
    rect(slide, ML, ry, 1.5, 0.045, TEAL, None, rounded=False)
    if sub:
        box(slide, ML, ry + 0.18, CW, 0.4, sub, 15, MUTE, BODY)
        return ry + 0.68
    return ry + 0.30


def bullets(slide, x, y, w, items, size=16, gap=0.42, dash_col=TEAL, col=INK):
    for i, it in enumerate(items):
        box(slide, x, y + i * gap, 0.22, gap, "—", size, dash_col, BODY, bold=True)
        box(slide, x + 0.28, y + i * gap, w - 0.28, gap, it, size, col, BODY, spacing=0.95)
    return y + len(items) * gap


def pic(slide, path, x, y, w, h, border=True):
    iw, ih = Image.open(path).size
    r = min(w / iw, h / ih)
    nw, nh = iw * r, ih * r
    px, py = x + (w - nw) / 2, y + (h - nh) / 2
    if border:
        rect(slide, px - 0.04, py - 0.04, nw + 0.08, nh + 0.08, WHITE, BORD, rounded=False, lw=0.75)
    return slide.shapes.add_picture(path, Inches(px), Inches(py), Inches(nw), Inches(nh))


def code(slide, x, y, w, h, text, size=12.5, dark=True):
    rect(slide, x, y, w, h, DARK if dark else LIGHT, None)
    tb = slide.shapes.add_textbox(Inches(x + 0.18), Inches(y + 0.12), Inches(w - 0.36), Inches(h - 0.24))
    tf = tb.text_frame
    tf.word_wrap = False
    tf.margin_left = tf.margin_right = tf.margin_top = tf.margin_bottom = 0
    for i, ln in enumerate(text.strip("\n").split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.line_spacing = 1.15
        r = p.add_run()
        r.text = ln if ln else " "
        r.font.size = Pt(size)
        r.font.name = MONO
        r.font.color.rgb = RGBColor(0xE2, 0xE8, 0xF0) if dark else INK
    return tb


def card(slide, x, y, w, h, head, lines, accent=TEAL, bg=WHITE, bd=BORD, hsize=15, lsize=13.5):
    """h est une hauteur MINIMALE : la carte s'agrandit si les lignes le demandent."""
    h = max(h, 0.62 + len(lines) * 0.30 + 0.18)
    rect(slide, x, y, w, h, bg, bd)
    rect(slide, x, y, 0.055, h, accent, None, rounded=False)
    box(slide, x + 0.28, y + 0.18, w - 0.5, 0.3, head, hsize, accent, HEAD, bold=True)
    yy = y + 0.60
    for ln in lines:
        box(slide, x + 0.28, yy, w - 0.5, 0.3, ln, lsize, INK, BODY, spacing=0.95)
        yy += 0.30
    return y + h


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text.strip()


# =====================================================================  1
s = S(footer=False)
rect(s, 0, 0, W, H, WHITE, None, rounded=False)
rect(s, 0, 0, W, 0.28, TEAL, None, rounded=False)
s.shapes.add_picture(os.path.join(DIAG, "logo_opsforge.png"), Inches(ML), Inches(1.55), Inches(0.95), Inches(0.95))
box(s, ML, 2.72, CW, 0.32, "SOUTENANCE — TITRE PROFESSIONNEL ADMINISTRATEUR SYSTÈME DEVOPS", 13, TEAL, HEAD, bold=True)
box(s, ML, 3.05, CW, 1.1, "OpsForge", 60, INK, HEAD, bold=True)
box(s, ML, 4.22, CW, 0.5, "Console locale de gestion d'incidents et chaîne DevOps de bout en bout",
    20, MUTE, BODY)
rect(s, ML, 4.95, 2.0, 0.05, TEAL, None, rounded=False)
rich(s, ML, 5.25, CW, 1.3, [
    ("Dyllan Thouvignon", 17, INK, True, BODY, 0),
    ("Titre professionnel niveau 6  ·  TP-01414  ·  RNCP 36061", 14, MUTE, False, BODY, 4),
    ("Session du 7 septembre 2026  ·  Liora (ex DataScientest)", 14, MUTE, False, BODY, 2),
])
notes(s, """
OUVERTURE (30 s) — ne pas lire la slide.

« Bonjour, je m'appelle Dyllan Thouvignon. Je vais vous présenter OpsForge, mon projet fil rouge :
une console locale de gestion d'incidents, et surtout la chaîne DevOps complète que j'ai construite
et validée autour d'elle. »

Posture : calme, ne pas s'excuser du périmètre local. Le fil rouge de toute la présentation :
tout ce que je montre a été exécuté et vérifié, pas seulement écrit.
""")

# =====================================================================  2
s = S()
y = title(s, "Le cadre", "Un projet fil rouge indépendant, assumé comme tel")
b1 = card(s, ML, y + 0.05, 3.9, 2.2, "MON PARCOURS", [
    "BTS SIO option SLAM,", "puis formation DevOps", "en alternance.", "",
    "Activité orientée", "support technique."], TEAL)
card(s, ML + 4.15, y + 0.05, 3.9, 2.2, "POURQUOI CE PROJET", [
    "Elle ne m'a pas fourni un", "projet DevOps couvrant les",
    "attendus certificatifs.", "", "J'ai donc conçu OpsForge,", "de juin à août 2026."], AMB, AMB_BG, AMB_BD)
card(s, ML + 8.30, y + 0.05, 3.9, 2.2, "CE QUE ÇA IMPLIQUE", [
    "Cahier des charges conçu", "par moi, à partir du référentiel.", "",
    "Aucune donnée ni", "infrastructure professionnelle."], TEAL_D, TINT, TINT_B)
rect(s, ML, b1 + 0.35, CW, 0.72, LIGHT, None)
box(s, ML + 0.3, b1 + 0.52, CW - 0.6, 0.5,
    "Conséquence directe : je tiens tous les rôles — cadrage, réalisation, revue, validation. "
    "C'est une limite, et je l'assume explicitement dans le dossier.", 15, INK, BODY)
notes(s, """
1 min 30. C'est le créneau « présentation de l'entreprise et/ou du service » du canevas officiel.
Ne pas le sauter : le jury attend un cadrage.

À dire :
- Parcours dev à l'origine (BTS SIO SLAM), puis DevOps en alternance.
- Mon activité en entreprise est restée orientée support : elle ne m'a pas donné un projet DevOps
  assez complet pour couvrir les attendus. J'ai donc construit le mien.
- Point important à énoncer clairement : ce n'est PAS un projet de mon entreprise. Aucune donnée,
  aucune infrastructure professionnelle. J'ai écrit le cahier des charges moi-même à partir du
  référentiel — ce que les modalités autorisent explicitement pour un projet hors entreprise.

Ne pas s'excuser. C'est un choix, pas un défaut. Enchaîner vite.
""")

# =====================================================================  3
s = S()
y = title(s, "Déroulé", "Le fil de la présentation")
steps = [("1", "Le besoin", "Le problème métier\net le cahier des charges"),
         ("2", "La solution", "L'application\net ses règles"),
         ("3", "L'architecture", "Ce qui tourne,\net où"),
         ("4", "Les preuves", "Trois compétences,\ntrois démonstrations"),
         ("5", "La recherche", "Un blocage réel\net son diagnostic"),
         ("6", "Le bilan", "Limites assumées\net conclusion")]
bw, gap = 1.86, 0.16
for i, (num, t, d) in enumerate(steps):
    x = ML + i * (bw + gap)
    rect(s, x, y + 0.25, bw, 2.35, WHITE, BORD)
    rect(s, x, y + 0.25, bw, 0.06, TEAL, None, rounded=False)
    box(s, x, y + 0.5, bw, 0.5, num, 30, TINT_B, HEAD, bold=True, align=PP_ALIGN.CENTER)
    box(s, x + 0.12, y + 1.05, bw - 0.24, 0.4, t, 15, INK, HEAD, bold=True, align=PP_ALIGN.CENTER)
    box(s, x + 0.12, y + 1.45, bw - 0.24, 1.0, d, 12, MUTE, BODY, align=PP_ALIGN.CENTER, spacing=0.95)
box(s, ML, y + 2.95, CW, 0.4,
    "Une règle tout au long : chaque brique présentée a été exécutée et vérifiée — pas seulement écrite.",
    16, TEAL_D, BODY, bold=True, align=PP_ALIGN.CENTER)
notes(s, """
30 s. Donner la carte, ne pas commenter chaque case.

« Six temps. Je passerai le plus de temps sur le quatrième : les preuves. »

La phrase du bas est ma promesse au jury — je la tiendrai slide après slide.
Elle prépare aussi la question « qu'est-ce qui est réellement démontré ? ».
""")

# =====================================================================  4
s = S()
y = title(s, "1 — Le besoin", "Un incident, c'est une chaîne de décisions à tracer")
cyc = [("Signal", "une alerte arrive\nsur un service"),
       ("Qualification", "l'opérateur\nacquitte"),
       ("Prise en charge", "il ouvre\nun incident"),
       ("Procédure", "il applique\nun runbook"),
       ("Traçabilité", "tout est\naudité")]
bw2, g2 = 2.18, 0.29
for i, (t, d) in enumerate(cyc):
    x = ML + i * (bw2 + g2)
    last = (i == len(cyc) - 1)
    rect(s, x, y + 0.15, bw2, 1.5, TINT if last else WHITE, TINT_B if last else BORD)
    box(s, x + 0.1, y + 0.36, bw2 - 0.2, 0.35, t, 15.5, TEAL_D if last else INK, HEAD, bold=True,
        align=PP_ALIGN.CENTER)
    box(s, x + 0.1, y + 0.76, bw2 - 0.2, 0.8, d, 12.5, MUTE, BODY, align=PP_ALIGN.CENTER, spacing=0.95)
    if not last:
        box(s, x + bw2, y + 0.62, g2, 0.4, "›", 24, TEAL, BODY, bold=True, align=PP_ALIGN.CENTER)
box(s, ML, y + 1.95, CW, 0.35, "Sans outil, trois choses se perdent :", 16, INK, BODY, bold=True)
bullets(s, ML, y + 2.35, CW, [
    "l'ordre des décisions — qui a fait quoi, dans quel ordre, et pourquoi ;",
    "la sûreté de la procédure — rien n'empêche de sauter une étape ou de conclure trop vite ;",
    "la preuve — au moment du bilan, il ne reste que des souvenirs.",
], 15.5)
notes(s, """
2 min.

Le domaine vient de mon expérience de support : j'ai vécu ce cycle au quotidien. C'est ce qui m'a
permis de définir un métier crédible sans copier un outil existant ni utiliser la moindre donnée réelle.

Insister sur le troisième point : la preuve. C'est ce qui relie le domaine choisi à ma démarche
d'ensemble — un projet dont chaque décision est tracée, une application dont chaque action est auditée.

Si on me demande « pourquoi pas GLPI / ServiceNow ? » : l'objectif n'était pas de refaire un ITSM,
mais de construire une application dont je maîtrise le cycle de vie pour démontrer la chaîne DevOps
autour. Le métier devait être crédible, pas exhaustif.
""")

# =====================================================================  5
s = S()
y = title(s, "1 — Le besoin", "Le cahier des charges, écrit à partir du référentiel")
card(s, ML, y + 0.1, 3.9, 3.0, "OBJECTIFS", [
    "Une application métier", "démontrable, au cycle de vie", "strict et audité.", "",
    "Une chaîne DevOps couvrant", "les trois compétences", "obligatoires.", "",
    "Une preuve d'exécution pour", "chaque brique."], TEAL)
card(s, ML + 4.15, y + 0.1, 3.9, 3.0, "CONTRAINTES", [
    "Windows 11 + Docker Desktop", "— d'où k3d, PowerShell,",
    "control node conteneurisé.", "", "Projet individuel, mené en",
    "parallèle du travail.", "", "Zéro cloud, zéro donnée réelle,", "aucune commande arbitraire."], AMB, AMB_BG, AMB_BD)
card(s, ML + 8.30, y + 0.1, 3.9, 3.0, "LIVRABLES", [
    "Le dépôt Git complet :", "application, tests, Docker,",
    "k8s/, ansible/, scripts, CI.", "", "La documentation par phase et", "29 décisions d'architecture.",
    "", "Le dossier de projet", "et ce support."], TEAL_D, TINT, TINT_B)
notes(s, """
2 min. Ne pas lire les colonnes : les survoler et appuyer sur deux points.

1) Les contraintes ont dicté l'outillage, pas l'inverse. Poste Windows + Docker Desktop
   → k3d plutôt qu'une VM, PowerShell pour les sauvegardes, et un control node Ansible conteneurisé
   (Ansible ne tourne pas nativement sous Windows). C'est un raisonnement d'ingénieur, pas un défaut.

2) « Aucune commande arbitraire » est une contrainte de conception que j'ai tenue et vérifiée :
   pas de subprocess, pas d'eval dans l'application. Les automatisations sont une liste fermée
   de cinq clés approuvées dans le code.

Si on me demande le volume : six phases, de juin à août 2026, chacune finie et validée avant la suivante.
""")

# =====================================================================  6
s = S()
y = title(s, "2 — La solution", "Une console d'exploitation, utilisable sans outil externe")
pic(s, os.path.join(SHOTS, "01_overview.png"), ML, y, 8.15, 4.45)
xr = ML + 8.45
b = card(s, xr, y + 0.05, CW - 8.45, 0, "CE QUE L'OPÉRATEUR VOIT", [
    "Les incidents à traiter,", "les alertes récentes, et l'état", "réel de la plateforme."], TEAL)
card(s, xr, b + 0.25, CW - 8.45, 0, "HUIT SECTIONS", [
    "Vue d'ensemble, Alertes,", "Incidents, Services, Runbooks,", "Activité, Monitoring, Aide."], TEAL_D, TINT, TINT_B)
box(s, ML, y + 4.55, 8.15, 0.4,
    "Tout le parcours se fait dans l'interface — pas de Swagger, pas de ligne de commande.",
    14.5, TEAL_D, BODY, bold=True, align=PP_ALIGN.CENTER)
notes(s, """
2 min. Laisser la capture parler ; pointer trois zones à l'écran.

Le parcours type, à raconter en une phrase fluide :
« Un signal arrive sur un service → il devient une alerte → l'opérateur l'acquitte → il décide
d'ouvrir un incident → il s'attribue l'incident, le passe en investigation, applique un runbook →
chaque action alimente le journal d'audit → il résout l'incident, puis l'alerte séparément. »

Point à souligner : à droite de la capture, « État réel d'OpsForge » — ce sont les contrôles de la
plateforme elle-même (health, readiness), à distinguer des états métier des services, qui sont
des données de démonstration. J'y reviens sur la slide supervision.

Piège possible : « c'est un projet de dev, pas de DevOps ». Réponse : l'application est le support ;
ce que je certifie, c'est la chaîne autour — conteneurs, déploiement automatisé, supervision.
""")

# =====================================================================  7
s = S()
y = title(s, "2 — La solution", "Des règles appliquées côté serveur, pas des écrans")
bullets(s, ML, y + 0.1, 7.5, [
    "Transitions strictement en avant : une alerte va de « nouvelle » à « acquittée » puis « résolue », "
    "jamais en arrière. Un incident ne se rouvre pas.",
    "Une alerte n'a qu'un seul incident actif : le doublon est refusé, avec l'identifiant de "
    "l'incident existant.",
    "Aucune exécution arbitraire : cinq automatisations approuvées dans le code. Une clé inconnue "
    "est rejetée.",
    "Un runbook manuel ne peut pas être déclaré réussi avec une checklist incomplète.",
    "Toute mutation — y compris les échecs contrôlés — produit une entrée d'audit.",
], 15, gap=0.72)
rect(s, ML, y + 3.75, 7.5, 0.62, TINT, TINT_B)
box(s, ML + 0.25, y + 3.92, 7.0, 0.4,
    "Chaque règle est testée négativement : le refus est vérifié, pas seulement le cas nominal.",
    15, TEAL_D, BODY, bold=True)
pic(s, os.path.join(SHOTS, "03_incident_command_center.png"), ML + 8.0, y, CW - 8.0, 4.4)
notes(s, """
2 min. C'est la slide qui montre que ce n'est pas une maquette.

Vocabulaire précis à utiliser : les règles sont appliquées CÔTÉ SERVEUR. L'interface ne fait
que refléter ce que l'API autorise. Une transition invalide renvoie un 409, une clé
d'automatisation inconnue un 422.

Les 38 tests couvrent ces refus : c'est ce que j'appelle tester négativement.
Exemples concrets à citer si on me pousse :
- deuxième incident actif sur la même alerte → 409 avec l'id de l'incident existant ;
- runbook managé modifié par l'API → 409 (il est resynchronisé au démarrage) ;
- checklist incomplète déclarée en succès → refus, et l'échec est quand même audité.

La capture à droite : le Command Center d'un incident — contexte, alerte source, runbooks
compatibles, chronologie issue du journal d'audit.
""")

# =====================================================================  8
s = S()
y = title(s, "3 — L'architecture", "Une application, et deux chaînes d'outillage indépendantes")
pic(s, os.path.join(DIAG, "schema_architecture.png"), ML, y - 0.05, CW, 4.15, border=False)
box(s, ML, y + 4.25, CW, 0.4,
    "La CI valide le code et l'image sans rien publier.  Ansible reconstruit l'image localement "
    "et déploie l'infrastructure.  Aucun registre, aucun déploiement distant.",
    15, TEAL_D, BODY, bold=True, align=PP_ALIGN.CENTER)
notes(s, """
2 min. Slide de repère : ne pas tout décrire, montrer la structure.

À dire dans l'ordre :
1) En haut à gauche, l'application : opérateur → console → API → domaine → PostgreSQL,
   avec le journal d'audit et l'endpoint /metrics.
2) En haut à droite, la supervision réelle : Prometheus scrape /metrics toutes les 15 secondes,
   une règle d'alerte, un dashboard Grafana.
3) En bas, DEUX chaînes indépendantes — et c'est le point que je veux qu'on retienne :
   la chaîne 1 est l'intégration continue ; elle ne publie ni ne déploie rien.
   la chaîne 2 est l'automatisation du déploiement par Ansible.

Dire explicitement : il n'y a PAS de déploiement continu distant, et pas de registre d'images.
C'est un choix de périmètre, documenté. Le dire avant qu'on me le demande.
""")

# =====================================================================  9
s = S()
y = title(s, "3 — L'architecture", "Tout tient sur un poste, et c'est reproductible")
pic(s, os.path.join(DIAG, "schema_topologie.png"), ML, y - 0.05, CW - 3.55, 4.5, border=False)
xr = ML + CW - 3.4
b = card(s, xr, y + 0.15, 3.4, 0, "LE CLUSTER", [
    "k3d : un Kubernetes k3s", "dans des conteneurs Docker.", "Un seul nœud."], BLU, BLU_BG, BLU_BD)
b = card(s, xr, b + 0.25, 3.4, 0, "L'ACCÈS", [
    "API sur 127.0.0.1:8080", "via un NodePort.", "Supervision par port-forward."], TEAL)
card(s, xr, b + 0.25, 3.4, 0, "LA LIMITE", [
    "Mono-nœud, local.", "Pas de haute disponibilité,", "et je ne la revendique pas."], AMB, AMB_BG, AMB_BD)
notes(s, """
2 min.

Le control node Ansible (en jaune, à gauche du schéma) est un conteneur éphémère qui pilote k3d.
C'est né d'une contrainte réelle — Ansible ne tourne pas nativement sous Windows — et d'une
situation de recherche que je détaillerai.

À l'intérieur du cluster : le namespace opsforge (Service NodePort → Deployment API → Service
PostgreSQL → StatefulSet → PVC) et le namespace monitoring (Prometheus, Grafana).

Anticiper la question « pourquoi pas du cloud ? » :
budget zéro cloud assumé, et surtout le référentiel n'exige pas le cloud pour les trois compétences
obligatoires. La compétence « mise en production dans le cloud » n'est pas revendiquée — elle
relèvera de l'entretien technique, et je sais quoi en dire.
""")

# ===================================================================== 10
s = S()
y = title(s, "4 — Les preuves  ·  CP n° 2", "D'une séquence manuelle à une seule commande")
bA = card(s, ML, y + 0.05, 5.9, 2.35, "AVANT", [
    "Une séquence manuelle documentée :", "créer le cluster k3d, construire et",
    "importer l'image, appliquer les", "manifests un par un, attendre,",
    "vérifier à la main que ça répond.", "", "Documenté — mais pas automatisé."], AMB, AMB_BG, AMB_BD)
bB = card(s, ML + 6.2, y + 0.05, 6.0, 2.35, "APRÈS", [
    "Une seule commande, idempotente :", "", "cluster créé seulement s'il n'existe pas ;",
    "image construite et importée ;", "manifests appliqués dans l'ordre, chaque",
    "étage attendu prêt ;", "puis /health et /ready vérifiés en HTTP."], TEAL, TINT, TINT_B)
code(s, ML, max(bA, bB) + 0.28, CW, 1.62, """
$ ./ansible/run.sh deploy.yml -e cluster_name=opsforge-ansible-test ...

  PLAY RECAP   ok=22  changed=9  failed=0      "/health -> 200"   "/ready -> 200"
  second run   ok=21  changed=2  failed=0      (idempotence)
  teardown     ok=3   changed=1  failed=0
""", 13)
notes(s, """
3 min — C'EST L'EXEMPLE SIGNIFICATIF EXIGÉ PAR LE CANEVAS. Ma meilleure slide, prendre le temps.

L'histoire, à raconter honnêtement :
« En confrontant mon projet aux critères exacts du référentiel, j'ai constaté que mon déploiement
Kubernetes était documenté, mais manuel. Il ne prouvait donc pas la compétence d'automatisation.
J'ai fermé cet écart en fin de projet, avec un périmètre ciblé : automatiser le déploiement
existant, sans rien redéfinir. »

C'est une correction de trajectoire, et c'est un point fort — pas un aveu.

Les trois arguments techniques à avoir en bouche :
1) Idempotence : le cluster n'est créé que s'il n'existe pas. Le second run donne changed=2 au lieu
   de 9 — c'est la preuve, pas une affirmation.
2) Chaque étage est appliqué avec wait: true — PostgreSQL prêt, puis l'API, puis la supervision.
   Ce n'est pas un « kubectl apply » aveugle.
3) Le run ne réussit QUE si l'application répond : /ready exécute un SELECT 1 sur PostgreSQL.
   Le déploiement se prouve lui-même.

Si on demande « pourquoi Ansible et pas Terraform ? » :
les deux sont cités par le référentiel. Terraform est déclaratif et à état — on décrit une cible
qu'il réconcilie. Ma tâche est une orchestration procédurale multi-outils : préparer le control node,
créer le cluster, construire l'image, appliquer dans un ordre imposé, attendre, vérifier en HTTP.
C'est ce qu'Ansible exprime naturellement. Terraform deviendrait pertinent pour du provisioning cloud.
""")

# ===================================================================== 11
s = S()
y = title(s, "4 — Les preuves  ·  CP n° 7", "Gérer des containers : durcis, et une persistance prouvée")
box(s, ML, y + 0.05, 6.0, 0.32, "LE DURCISSEMENT, VÉRIFIÉ SUR CLUSTER RÉEL", 13, TEAL, HEAD, bold=True)
code(s, ML, y + 0.45, 6.0, 2.35, """
securityContext:
  runAsNonRoot: true
  runAsUser: 10001
  readOnlyRootFilesystem: true
  capabilities: {drop: ["ALL"]}
  seccompProfile: {type: RuntimeDefault}

readinessProbe: /ready    livenessProbe: /health
""", 12.5)
box(s, ML, y + 2.95, 6.0, 0.9,
    "Les deux sondes sont différentes, et c'est le point clé : /ready retire l'API du service quand "
    "la base est injoignable ; /health ne redémarre que si le processus est mort.", 14, INK, BODY)
box(s, ML + 6.5, y + 0.05, CW - 6.5, 0.32, "LA PERSISTANCE, PROUVÉE — PAS SUPPOSÉE", 13, TEAL, HEAD, bold=True)
code(s, ML + 6.5, y + 0.45, CW - 6.5, 2.35, """
pod UID avant : 554c3801-0b0e-42b7-...
  INSERT INTO persistence_check VALUES ('...');

$ kubectl delete pod postgres-0
  le StatefulSet recree le pod

pod UID apres : e035ce38-526f-4b3b-...   (pod neuf)
SELECT marker : dossier-v2-persisted     (donnee la)
""", 12.5)
rect(s, ML + 6.5, y + 2.95, CW - 6.5, 0.9, AMB_BG, AMB_BD)
box(s, ML + 6.75, y + 3.12, CW - 7.0, 0.6,
    "Limite : la StorageClass local-path reste locale au nœud. Ce n'est pas du stockage réseau — "
    "et je le dis avant qu'on me le demande.", 14, AMB, BODY, bold=True)
notes(s, """
2 min 30.

Sur le durcissement : l'image tourne en non-root (UID 10001) avec un système de fichiers racine en
lecture seule ; seul /tmp est inscriptible. Vérifié en conditions réelles : les pages répondent 200
sous rootfs read-only, et une écriture dans /app est refusée.

Sur les probes — l'argument qui montre que je comprends ce que je fais :
utiliser /ready en liveness provoquerait des redémarrages en boucle pendant une panne de base.
C'est pour ça qu'elles sont séparées.

Sur la persistance : l'UID du pod change, donc c'est un pod réellement neuf, et la donnée est
toujours là. C'est une preuve, pas une capture d'écran d'un manifest.

LE PIÈGE DE CETTE COMPÉTENCE : le critère du référentiel dit « les containers sont connectés au
stockage distant ». Ma réponse, préparée :
« Le conteneur est connecté à un stockage externalisé de son cycle de vie et porté par l'hôte —
un volume nommé en Compose, un PVC monté par le StatefulSet en Kubernetes. Dans mon environnement
k3d, la StorageClass local-path reste locale au nœud : ce n'est pas un stockage réseau. Une
StorageClass NFS ou CSI la remplacerait sans modifier le manifest — c'est justement l'intérêt de
l'abstraction PVC. »
Ne pas gonfler. Montrer que je connais exactement la limite.
""")

# ===================================================================== 12
s = S()
y = title(s, "4 — Les preuves  ·  CP n° 10", "Exploiter une supervision : l'alerte s'est déclenchée")
pic(s, os.path.join(FIGS, "06_prometheus_targets_up_fig.png"), ML, y + 0.05, 6.0, 1.5)
pic(s, os.path.join(FIGS, "07_prometheus_alert_firing_fig.png"), ML, y + 1.70, 6.0, 1.05)
code(s, ML, y + 2.95, 6.0, 1.72, """
$ kubectl scale deploy/opsforge-api --replicas=0
  t+20s  up=0   inactive
  t+40s  up=0   pending
  t+70s  up=0   FIRING        <<<
$ kubectl scale deploy/opsforge-api --replicas=1
  t+40s  up=1   inactive      (resolu)
""", 12.5)
xr = ML + 6.5
box(s, xr, y + 0.02, CW - 6.5, 0.32, "LE POINT D'HONNÊTETÉ DU PROJET", 13, TEAL, HEAD, bold=True)
rect(s, xr, y + 0.42, CW - 6.5, 1.55, TINT, TINT_B)
box(s, xr + 0.25, y + 0.62, CW - 7.0, 1.2,
    "Prometheus supervise OpsForge lui-même — l'API déployée dans le cluster.\n\n"
    "Les états métier des services du catalogue sont des données de démonstration, "
    "et la console l'affiche explicitement.", 14.5, TEAL_D, BODY, spacing=0.95)
pic(s, os.path.join(SHOTS, "05_monitoring.png"), xr, y + 2.25, CW - 6.5, 2.4)
notes(s, """
2 min 30. Compétence obligatoire — et la slide où je gagne ma crédibilité.

Ce que je montre, de haut en bas :
1) La cible Prometheus « opsforge-api (1/1 up) » — le scrape est réel, toutes les 15 secondes.
2) La règle OpsForgeApiDown en état FIRING.
3) Le cycle complet : j'ai provoqué la panne en passant le déploiement à zéro réplique.
   inactive → pending → firing en 70 secondes, puis restauration et retour à inactive.

Les indicateurs : métriques applicatives réelles produites par un middleware FastAPI — nombre de
requêtes et latence, avec des labels méthode / route / code. Le label « route » utilise le template
et pas l'URL réelle, sinon chaque identifiant créerait une série distincte : explosion de cardinalité.

La règle s'appuie sur la métrique « up » du scrape, pas sur une métrique applicative — parce qu'une
métrique applicative disparaît avec l'application. for: 30s est calibré sur le scrape de 15 s pour
qu'un raté isolé ne déclenche pas.

À DIRE SPONTANÉMENT (encadré de droite) : Prometheus supervise OpsForge, pas les services métier
du catalogue. Ces états-là sont simulés, et la console le dit. Ne jamais laisser croire l'inverse.

LE PIÈGE : le critère « les échanges avec les développeurs sont réguliers ». Réponse préparée :
« Projet individuel, je tiens les deux rôles — je ne peux pas revendiquer ce critère au sens strict.
Ce que je peux montrer, c'est que la boucle supervision → développement existe et qu'elle est tracée
dans mes décisions d'architecture : c'est la supervision qui m'a fait ajouter /ready, qui m'a fait
passer les labels de route en template. En équipe, ces constats seraient le contenu des échanges. »
""")

# ===================================================================== 13
s = S()
y = title(s, "4 — Les preuves", "Autour : intégration continue et sauvegardes restaurables")
box(s, ML, y, 7.4, 0.32, "À CHAQUE PUSH — ET UN SIGNAL QU'ON NE MASQUE PAS", 13, TEAL, HEAD, bold=True)
pic(s, os.path.join(FIGS, "11_github_actions_run_fig.png"), ML, y + 0.4, 7.4, 3.05)
box(s, ML, y + 3.55, 7.4, 0.62,
    "Job vert — et pourtant une annotation d'erreur : le scan Trivy signale ses vulnérabilités, "
    "sans bloquer la livraison. Politique advisory, assumée.", 14, INK, BODY)
xr = ML + 7.8
b = card(s, xr, y + 0.05, CW - 7.8, 0, "LA CHAÎNE CI", [
    "Ruff  →  38 tests SQLite  →", "1 test d'intégration PostgreSQL",
    "→  build de l'image  →  scan.", "Base de test éphémère, supprimée."], BLU, BLU_BG, BLU_BD)
card(s, xr, b + 0.30, CW - 7.8, 0, "SAUVEGARDE", [
    "pg_dump scripté, archive vérifiée.", "Restauration PAR DÉFAUT dans une",
    "base temporaire — la principale exige", "un drapeau et la saisie de RESTORE."], TEAL, TINT, TINT_B)
notes(s, """
2 min. Deux preuves rapides, ne pas s'attarder.

Sur la CI — la subtilité que je veux qu'on remarque :
l'étape Trivy est configurée avec exit-code 1, donc elle SIGNALE quand il y a des vulnérabilités
HIGH ou CRITICAL ; et continue-on-error garde le job vert. Résultat : le signal reste visible
(l'annotation d'erreur sur la capture) sans bloquer. C'est une politique advisory explicite,
transformable en portail bloquant par une décision documentée.

Le dernier scan de l'image épinglée rapportait 19 HIGH et 3 CRITICAL d'origine Debian, sans
correctif disponible. Je le dis franchement : une CI verte ne veut pas dire « image sans
vulnérabilité ». C'est de la dette de sécurité visible, pas cachée.

Sur la sauvegarde : le comportement par défaut est le comportement SÛR. Restaurer dans la base
principale demande un drapeau explicite ET de taper RESTORE en respectant la casse — une touche
Entrée pressée trop vite annule. Preuve rejouée : archive de 24 543 octets, restauration vérifiée
sur 6 tables.

Limite à énoncer : sauvegarde locale, non planifiée, non chiffrée, sans rotation. C'est un mécanisme
démontrable, pas une stratégie d'entreprise.
""")

# ===================================================================== 14
s = S()
y = title(s, "4 — Les preuves", "Ce que 35 tests automatisés ne voyaient pas")
box(s, ML, y, CW, 0.4,
    "Le produit passait les 35 tests et la CI était verte. Une revue manuelle, guidée par un runbook "
    "dédié, a trouvé deux défauts réels : une erreur 422 sur les filtres, et cette table illisible.",
    15.5, INK, BODY)
pic(s, os.path.join(FIGS, "12_incidents_mobile_avant_fig.png"), ML, y + 0.55, 5.6, 2.3)
box(s, ML, y + 2.95, 5.6, 0.32, "AVANT", 14, AMB, HEAD, bold=True, align=PP_ALIGN.CENTER)
pic(s, os.path.join(FIGS, "10_incidents_mobile_fig.png"), ML + 6.3, y + 0.55, 5.6, 2.3)
box(s, ML + 6.3, y + 2.95, 5.6, 0.32, "APRÈS CORRECTION", 14, TEAL, HEAD, bold=True, align=PP_ALIGN.CENTER)
rect(s, ML, y + 3.45, CW, 1.15, TINT, TINT_B)
box(s, ML + 0.35, y + 3.65, CW - 0.7, 0.8,
    "Les tests vérifiaient des réponses HTTP et des structures de page — ils ne simulaient ni la "
    "soumission réelle d'un formulaire, ni un rendu à 390 pixels.\n"
    "Corrigés en branches dédiées, couverts par trois tests de non-régression : la suite est passée "
    "de 35 à 38 tests.", 15, TEAL_D, BODY, spacing=1.0)
notes(s, """
2 min. Slide qui me distingue — elle montre une démarche qualité, pas une confession.

L'histoire : le produit passait tous les tests automatisés et la CI était verte. J'ai quand même
déroulé une revue manuelle, guidée par un runbook que j'avais écrit : parcours desktop, workflow
opérateur complet, comportement responsive.

Elle a trouvé deux défauts réels :
- un HTTP 422 dès qu'on cliquait sur « Filtrer » sans choisir de service — le formulaire envoyait
  une valeur vide que l'API refusait ;
- la table Incidents illisible sur mobile, avec les en-têtes qui se chevauchent (à gauche).

Pourquoi les tests ne les voyaient pas : ils vérifient des codes de retour et des structures de
page. Ils ne cliquent pas sur un bouton, et ils ne rendent pas une page à 390 pixels.

Ce que j'en tire, et c'est le message : une procédure de test manuelle documentée n'est pas le
reliquat d'un projet mal automatisé. C'est la couche qui attrape ce que l'automatisation ne voit pas.
J'ai corrigé en branches dédiées depuis le candidat gelé, ajouté trois tests de non-régression
(35 → 38), revalidé, puis seulement validé la phase.

ATTENTION : ne pas dire « 38 tests ne voyaient pas les défauts » — au moment de la découverte la
suite comptait 35 tests ; les 3 tests ajoutés sont précisément ceux qui couvrent ces défauts.
""")

# ===================================================================== 15
s = S()
y = title(s, "5 — Le référentiel", "Les trois compétences obligatoires, et ce que je n'affirme pas")
rows = [("CP n° 2", "Automatiser le déploiement\nd'une infrastructure",
         "Playbook Ansible : toute l'infrastructure locale déployée\net vérifiée en une commande idempotente.", TEAL),
        ("CP n° 7", "Gérer des containers",
         "Image durcie non-root, orchestration Compose puis Kubernetes,\npersistance prouvée après destruction du pod.", TEAL),
        ("CP n° 10", "Exploiter une solution\nde supervision",
         "Application instrumentée, scrape réel, dashboard, et une alerte\nobservée de « inactive » à « firing » puis résolue.", TEAL)]
yy = y + 0.05
for cp, lab, proof, col in rows:
    rect(s, ML, yy, CW, 1.02, WHITE, BORD)
    rect(s, ML, yy, 0.055, 1.02, col, None, rounded=False)
    box(s, ML + 0.3, yy + 0.14, 1.2, 0.3, cp, 15, col, HEAD, bold=True)
    box(s, ML + 1.55, yy + 0.12, 3.2, 0.8, lab, 14, INK, BODY, bold=True, spacing=0.95)
    box(s, ML + 5.0, yy + 0.14, CW - 5.3, 0.8, proof, 13.5, MUTE, BODY, spacing=0.95)
    yy += 1.12
rect(s, ML, yy + 0.1, CW, 0.95, LIGHT, None)
box(s, ML + 0.3, yy + 0.28, CW - 0.6, 0.65,
    "Deux nuances que j'assume plutôt que de les contourner : le stockage reste local au nœud, "
    "et « les échanges avec les développeurs » n'ont pas de sens dans un projet individuel — "
    "la boucle existe, elle est tracée dans mes décisions.\n"
    "Non revendiquées : la mise en production dans le cloud, et l'épreuve d'anglais, évaluées ailleurs.",
    14, INK, BODY, spacing=1.0)
notes(s, """
1 min 30. Slide de synthèse : la survoler, elle sert surtout de repère au jury.

Les trois compétences obligatoires sont couvertes, chacune avec une preuve distincte — c'est le
vocabulaire des modalités elles-mêmes.

Le message de l'encadré du bas est important : je ne contourne pas les deux points faibles,
je les nomme AVANT qu'on me les oppose. Ça change complètement la dynamique de l'entretien.

Rappel de ce qui relève d'ailleurs :
- « Mettre l'infrastructure en production dans le cloud » : aucun cloud déployé, donc non couverte
  par le projet — elle fera l'objet du questionnement de l'entretien technique, et je sais en parler
  (Kubernetes managé, Terraform, ce que je ferais).
- « Échanger sur des réseaux professionnels en anglais » : évaluée par le questionnaire professionnel.
  Je note simplement que la documentation du dépôt et mes messages de commit sont en anglais.
""")

# ===================================================================== 16
s = S()
y = title(s, "6 — La recherche", "Le fichier de configuration silencieusement ignoré")
steps2 = [("LE SYMPTÔME", "« skipping: no hosts matched »\n\nAucun hôte trouvé — alors que\nl'inventaire existait, déclaré\ndans ansible.cfg.", AMB, AMB_BG, AMB_BD),
          ("LE DIAGNOSTIC", "Inventaire mal écrit ? Non.\nMauvais répertoire ? Non.\n\nansible --version affichait\n« config file = None ».", BLU, BLU_BG, BLU_BD),
          ("LA CAUSE", "Ansible refuse un ansible.cfg\nsitué dans un répertoire\ninscriptible par tous.\n\nUn dépôt Windows monté dans\nDocker est world-writable.", TEAL_D, TINT, TINT_B),
          ("LA CORRECTION", "ANSIBLE_CONFIG fixé dans\nl'image — la solution prévue\npar l'outil.\n\nPlus un inventaire explicite,\npar ceinture et bretelles.", TEAL, WHITE, BORD)]
cw2, g3 = 2.95, 0.22
for i, (t, d, col, bg, bd) in enumerate(steps2):
    x = ML + i * (cw2 + g3)
    rect(s, x, y + 0.05, cw2, 2.5, bg, bd)
    rect(s, x, y + 0.05, cw2, 0.055, col, None, rounded=False)
    box(s, x + 0.22, y + 0.28, cw2 - 0.44, 0.3, t, 13.5, col, HEAD, bold=True)
    box(s, x + 0.22, y + 0.68, cw2 - 0.44, 1.7, d, 12.5, INK, BODY, spacing=0.98)
    if i < 3:
        box(s, x + cw2, y + 1.15, g3, 0.4, "›", 20, MUTE, BODY, bold=True, align=PP_ALIGN.CENTER)
rect(s, ML, y + 2.78, CW, 1.35, TINT, TINT_B)
box(s, ML + 0.35, y + 2.98, CW - 0.7, 1.0,
    "Le second enseignement, le plus important : en corrigeant, j'ai découvert que mes validations "
    "initiales avaient été faites avec des commandes ajustées à la main — le script documenté, lui, "
    "ne les portait pas. Quiconque l'aurait lancé aurait reproduit l'échec.\n"
    "J'ai aligné le script, tout re-testé en ne passant que par lui, et épinglé les versions validées.",
    14.5, TEAL_D, BODY, spacing=1.0)
notes(s, """
3 min. CRÉNEAU OBLIGATOIRE DU CANEVAS : « présentation d'un exemple de recherche effectuée ».
Slide à raconter, pas à lire. C'est une histoire, elle a un début et une chute.

Le déroulé :
- Ansible ne tourne pas nativement sous Windows, j'ai donc un control node conteneurisé.
- Première exécution : « skipping: no hosts matched ». Aucun hôte, alors que l'inventaire existe.
- Méthode : éliminer les hypothèses dans l'ordre. Inventaire mal écrit ? Non, il marche passé à la
  main. Mauvais répertoire de travail ? Non. Le fichier est-il seulement LU ? Et là,
  « ansible --version » affiche « config file = None » : Ansible ignore silencieusement ma config.
- Recherche dans la documentation officielle : Ansible REFUSE un ansible.cfg situé dans un
  répertoire inscriptible par tous — c'est une protection contre l'injection de configuration.
  Or un dépôt Windows monté par bind-mount dans Docker apparaît world-writable côté Linux.
  Le comportement d'Ansible était correct ; c'est mon environnement qui le déclenchait.
- Trois options pesées ; j'ai retenu celle prévue par l'outil : fixer ANSIBLE_CONFIG dans l'image.

LA CHUTE — c'est ce que je veux qu'on retienne de moi :
en corrigeant, j'ai découvert pire que le bug. Mes validations avaient été faites avec des commandes
que j'avais ajustées à la main pendant le débogage, et le script documenté ne portait pas ces
réglages. Si vous aviez lancé mon script tel que documenté, vous auriez reproduit l'échec initial.
Le message de mon commit de correction le dit sans détour.
J'ai aligné le script, re-testé tout le parcours en ne passant QUE par lui, épinglé les versions,
et retiré de ma documentation une affirmation que je ne pouvais pas prouver.

La leçon : l'artefact documenté doit être exactement celui qui a été validé.
""")

# ===================================================================== 17
s = S()
y = title(s, "7 — Le bilan", "Les limites, nommées — et ce qu'elles appellent ensuite")
lim = [("Infrastructure", "k3d mono-nœud, local. Pas de cloud.", "Kubernetes managé + Terraform"),
       ("Livraison", "Intégration continue, mais pas de déploiement continu distant.", "Registre d'images + déclenchement par la CI"),
       ("Stockage", "PVC local au nœud, pas de stockage réseau.", "StorageClass NFS ou CSI"),
       ("Application", "Pas d'authentification : les acteurs sont déclaratifs.", "Authentification et rôles"),
       ("Supervision", "Alerte visible dans Prometheus, non routée. Métriques techniques.", "Alertmanager, métriques métier"),
       ("Sécurité", "Trivy advisory : 19 HIGH / 3 CRITICAL visibles, sans correctif.", "Seuil de blocage explicite, TLS")]
rect(s, ML, y, CW, 0.42, TEAL, None, rounded=False)
box(s, ML + 0.25, y + 0.09, 2.2, 0.3, "DOMAINE", 12.5, WHITE, HEAD, bold=True)
box(s, ML + 2.6, y + 0.09, 5.6, 0.3, "CE QUE JE NE REVENDIQUE PAS", 12.5, WHITE, HEAD, bold=True)
box(s, ML + 8.5, y + 0.09, 3.5, 0.3, "L'ÉVOLUTION NATURELLE", 12.5, WHITE, HEAD, bold=True)
yy = y + 0.42
for i, (a, b, c) in enumerate(lim):
    rect(s, ML, yy, CW, 0.55, LIGHT if i % 2 else WHITE, None, rounded=False)
    box(s, ML + 0.25, yy + 0.15, 2.3, 0.3, a, 13.5, INK, BODY, bold=True)
    box(s, ML + 2.6, yy + 0.15, 5.8, 0.3, b, 13.5, INK, BODY)
    box(s, ML + 8.5, yy + 0.15, 3.6, 0.3, c, 13.5, TEAL_D, BODY)
    yy += 0.55
box(s, ML, yy + 0.25, CW, 0.45,
    "Ce sont des choix de périmètre, écrits dans le dépôt avant cette soutenance — pas des oublis "
    "découverts en la préparant.", 15.5, TEAL_D, BODY, bold=True, align=PP_ALIGN.CENTER)
notes(s, """
1 min 30. Slide courte à l'oral : la parcourir, pas la lire ligne à ligne.

La phrase du bas est la plus importante de la slide. Toutes ces limites sont documentées dans le
dépôt — fichier de risques et dette technique, décisions d'architecture — depuis les phases
concernées. Je ne les ai pas découvertes en préparant la soutenance.

Formulation à garder : « ce que je ne revendique pas ». Ce n'est pas une liste d'échecs, c'est
la frontière de ce que je peux prouver. Un jury sanctionne beaucoup plus une revendication
non prouvée qu'une limite assumée.

Si on me pousse sur une limite, la structure de réponse est toujours la même :
pourquoi ce choix était bon pour la phase → quelle limite il crée → ce que je ferais ensuite →
pourquoi je ne l'ai pas fait prématurément.
""")

# ===================================================================== 18
s = S()
y = title(s, "7 — Le bilan", "Ce que je retiens, et où en est le projet")
bA = card(s, ML, y + 0.05, 5.9, 2.9, "MES SATISFACTIONS", [
    "La méthode : six phases finies,", "validées et datées une à une.",
    "Le projet a survécu sans dégât à un", "changement de poste de travail.", "",
    "La correction de trajectoire : constater", "qu'un déploiement documenté mais",
    "manuel ne prouvait rien, et fermer", "l'écart avant l'examen."], TEAL, TINT, TINT_B)
bB = card(s, ML + 6.2, y + 0.05, 6.0, 2.9, "MES DIFFICULTÉS", [
    "Le débogage du control node Ansible —", "le plus formateur, avec sa leçon sur",
    "l'artefact documenté.", "", "La revue visuelle, impossible à",
    "automatiser, qui a révélé deux défauts", "réels.", "",
    "Et en continu : tenir le périmètre."], AMB, AMB_BG, AMB_BD)
_yb = max(bA, bB) + 0.30
rect(s, ML, _yb, CW, 1.0, DARK, None)
box(s, ML + 0.4, _yb + 0.20, CW - 0.8, 0.65,
    "Le projet est gelé au commit a9ec694 : c'est cet état, reproductible et documenté, "
    "que je vous présente.\nLe dépôt est public — chaque preuve de ce dossier est rejouable.",
    16, WHITE, BODY, spacing=1.05)
notes(s, """
1 min 30 — puis « je suis à votre disposition pour vos questions ».

Le canevas officiel demande explicitement satisfactions ET difficultés : les deux colonnes
sont là pour ça, ne pas en sauter une.

Ce que je veux laisser comme dernière impression :
« Ce projet n'est pas grand. Il est petit, local, et entièrement vérifiable. J'ai préféré
un périmètre que je peux prouver de bout en bout à un périmètre impressionnant que je ne
pourrais pas défendre devant vous. »

Ne pas enchaîner sur des excuses. Marquer un silence, puis passer aux questions.

Si le temps le permet, ouvrir : la suite naturelle serait un registre d'images et un
déploiement déclenché par la CI, puis un Kubernetes managé — dans cet ordre, parce que
chaque étape rend la suivante démontrable.
""")

# ===================================================== BACKUP ==========
s = S()
rect(s, 0, 0, W, H, DARK, None, rounded=False)
box(s, ML, 3.0, CW, 0.5, "ANNEXES", 14, TINT_B, HEAD, bold=True, align=PP_ALIGN.CENTER)
box(s, ML, 3.35, CW, 0.8, "Slides de secours", 40, WHITE, HEAD, bold=True, align=PP_ALIGN.CENTER)
box(s, ML, 4.3, CW, 0.5, "Questions probables, chiffres, détails techniques",
    17, RGBColor(0x94, 0xA3, 0xB8), BODY, align=PP_ALIGN.CENTER)
notes(s, "Séparateur. Ne pas projeter pendant l'exposé — n'y aller que si une question l'appelle.")

qa1 = [("« Pourquoi pas de cloud ? »",
        "Budget zéro cloud assumé, et le référentiel n'exige pas le cloud pour les trois compétences "
        "obligatoires. La mise en production cloud n'est pas revendiquée."),
       ("« Votre stockage n'est pas distant. »",
        "Exact. Le conteneur est connecté à un stockage externalisé de son cycle de vie, porté par "
        "l'hôte. En k3d, local-path reste local au nœud. Une StorageClass NFS ou CSI la remplacerait "
        "sans toucher au manifest."),
       ("« Où est le déploiement continu ? »",
        "Il n'y en a pas. La CI valide le code et l'image, elle ne publie rien. Le déploiement est "
        "automatisé mais déclenché à la main. La suite serait un registre puis un déclenchement par la CI."),
       ("« Une seule réplique, pas de HA ? »",
        "Non. Une réplique de chaque workload. La haute disponibilité n'était pas l'objectif : "
        "je préférais prouver la persistance et le durcissement.")]
s = S()
y = title(s, "Annexe", "Questions probables — le périmètre")
yy = y + 0.05
for q, a in qa1:
    rect(s, ML, yy, CW, 0.98, WHITE, BORD)
    rect(s, ML, yy, 0.055, 0.98, AMB, None, rounded=False)
    box(s, ML + 0.28, yy + 0.13, CW - 0.6, 0.3, q, 14.5, AMB, HEAD, bold=True)
    box(s, ML + 0.28, yy + 0.45, CW - 0.6, 0.5, a, 13.5, INK, BODY, spacing=0.95)
    yy += 1.08
notes(s, """
Réponses à connaître par cœur dans l'esprit, pas mot à mot.

Règle d'or : reconnaître d'abord, expliquer ensuite, proposer la suite enfin.
Ne jamais défendre l'indéfendable — chaque limite a été choisie et documentée.
""")

qa2 = [("« Vos tests couvrent quoi exactement ? »",
        "38 tests SQLite en mémoire pour le domaine, plus un test d'intégration contre un vrai "
        "PostgreSQL en CI. Ils testent surtout les refus : transitions invalides, doublons, "
        "clés d'automatisation inconnues, checklist incomplète."),
       ("« Pourquoi SQLite si vous tournez sur PostgreSQL ? »",
        "Pour la vitesse de retour. Le risque — un comportement propre à PostgreSQL — est couvert "
        "par le test d'intégration qui rejoue le flux complet sur postgres:16-alpine dans la CI."),
       ("« Comment gérez-vous les secrets ? »",
        "Aucun secret versionné. Le fichier .env et le Secret Kubernetes local sont ignorés par Git ; "
        "Ansible génère le Secret au déploiement depuis des variables, surchargeables par "
        "ansible-vault."),
       ("« Votre image est-elle sûre ? »",
        "Elle est reproductible — base épinglée par digest, non-root, rootfs en lecture seule. "
        "Elle n'est pas exempte de vulnérabilités : 19 HIGH et 3 CRITICAL Debian sans correctif "
        "disponible, visibles dans la CI.")]
s = S()
y = title(s, "Annexe", "Questions probables — la technique")
yy = y + 0.05
for q, a in qa2:
    rect(s, ML, yy, CW, 0.98, WHITE, BORD)
    rect(s, ML, yy, 0.055, 0.98, BLU, None, rounded=False)
    box(s, ML + 0.28, yy + 0.13, CW - 0.6, 0.3, q, 14.5, BLU, HEAD, bold=True)
    box(s, ML + 0.28, yy + 0.45, CW - 0.6, 0.5, a, 13.5, INK, BODY, spacing=0.95)
    yy += 1.08
notes(s, """
Deux autres à préparer, qui n'ont pas tenu sur la slide :

« Quelle est la part de l'IA dans ce projet ? »
J'ai utilisé des assistants comme outils d'aide à la conception, à l'implémentation et à la revue,
selon des règles que j'ai écrites dans le dépôt. Je suis resté responsable du cadrage, des choix
techniques, des arbitrages et de la validation : chaque changement important a été vérifié et testé
avant intégration. C'est d'ailleurs ce processus qui donne au dépôt son cycle
proposition → implémentation → revue → correction → validation. Répondre calmement, sans gêne :
c'est un outil, la responsabilité reste la mienne.

« Combien de temps le projet a-t-il pris ? »
Trois mois, de juin à août 2026, en parallèle de mon activité professionnelle, en six phases
validées une à une.
""")

s = S()
y = title(s, "Annexe", "Les chiffres et les versions")
cols = [("LE PROJET", ["45 commits sur la branche du candidat",
                       "6 commits de merge, 6 pull requests",
                       "29 décisions d'architecture",
                       "6 phases validées et datées",
                       "Candidat gelé : a9ec694"]),
        ("LES TESTS", ["38 tests unitaires SQLite",
                       "1 test d'intégration PostgreSQL",
                       "Base éphémère au nom unique",
                       "Lint Ruff en amont",
                       "CI verte sur le candidat final"]),
        ("LA PLATEFORME", ["Python 3.12, FastAPI, SQLAlchemy 2",
                           "PostgreSQL 16 partout",
                           "k3d 5.9 / k3s 1.35, kubectl 1.34",
                           "Prometheus 2.55, Grafana 11.3",
                           "ansible-core 2.17, kubernetes.core 6.5"])]
for i, (t, items) in enumerate(cols):
    x = ML + i * 4.15
    rect(s, x, y + 0.05, 3.9, 3.1, WHITE, BORD)
    rect(s, x, y + 0.05, 3.9, 0.055, TEAL, None, rounded=False)
    box(s, x + 0.28, y + 0.28, 3.4, 0.3, t, 14, TEAL, HEAD, bold=True)
    yy = y + 0.72
    for it in items:
        box(s, x + 0.28, yy, 3.4, 0.45, it, 13, INK, BODY, spacing=0.95)
        yy += 0.48
notes(s, """
À dégainer si on me demande un chiffre précis. Ne pas apprendre par cœur : savoir où regarder.

Le seul chiffre que je dois donner sans hésiter : 38 tests, et 45 commits sur la branche du candidat.
Et la date de validation de la phase 6 : le 19 août 2026.
""")

s = S()
y = title(s, "Annexe", "Le domaine en détail")
code(s, ML, y + 0.1, 6.1, 2.3, """
ALERTE
  new  ->  acknowledged  ->  resolved
  new  ->  resolved            (direct)
  transition arriere      ->  409

INCIDENT
  open ->  investigating  ->  resolved
  pas de reouverture      ->  409
""", 13)
code(s, ML + 6.6, y + 0.1, CW - 6.6, 2.3, """
REFUS TESTES
  2e incident actif sur l'alerte  ->  409
  runbook manage modifie par API  ->  409
  cle d'automatisation inconnue   ->  422
  checklist incomplete en succes  ->  refus
  incident resolu modifie         ->  409

  ... et l'echec controle est audite
""", 13)
box(s, ML, y + 2.65, CW, 0.35, "Six objets : Service · Alert · Incident · Runbook · RunbookExecution · AuditLog",
    15, INK, BODY, bold=True, align=PP_ALIGN.CENTER)
box(s, ML, y + 3.1, CW, 0.9,
    "L'incident hérite du service de son alerte source. Résoudre l'incident ne résout pas l'alerte : "
    "le cycle du signal et celui de la prise en charge sont indépendants — c'est un choix de "
    "modélisation, pas un oubli.", 14.5, MUTE, BODY, align=PP_ALIGN.CENTER, spacing=1.0)
notes(s, """
Si le jury creuse le domaine métier ou veut vérifier que je maîtrise mon modèle.

Le point qu'on me contestera peut-être : « pourquoi résoudre l'incident ne résout-il pas l'alerte ? »
Parce que ce sont deux cycles différents : l'alerte est un signal, l'incident est une prise en charge.
Un signal peut persister après la clôture d'une intervention, et deux alertes peuvent concerner
le même incident. Les lier automatiquement ferait perdre de l'information.

Autre point : l'unicité de l'incident actif est garantie par l'application (409), pas par une
contrainte en base. En production multi-workers, il faudrait une contrainte partielle PostgreSQL —
c'est écrit dans ma dette technique.
""")

s = S()
y = title(s, "Annexe", "La traçabilité, vue de l'application")
pic(s, os.path.join(FIGS, "04_activity_fig.png"), ML, y + 0.1, CW, 3.5)
box(s, ML, y + 3.75, CW, 0.5,
    "Chaque entrée porte l'acteur, l'action, l'objet lié et l'horodatage. "
    "Les exécutions de runbook sont auditées qu'elles réussissent ou non.",
    15, TEAL_D, BODY, bold=True, align=PP_ALIGN.CENTER)
notes(s, """
À montrer si on me demande « comment prouvez-vous ce qui a été fait ? » ou si on doute
de la traçabilité.

On y lit la chaîne complète d'une prise en charge : alerte créée, incident déclaré, statut modifié,
runbook exécuté — avec l'acteur et l'horodatage UTC à chaque fois.

Limite honnête si on insiste : l'acteur est une valeur déclarative, il n'y a pas d'authentification.
Ça prouve la traçabilité des actions, pas l'identité de celui qui les a faites. C'est écrit
dans mes limites.
""")

prs.save(OUT)
print("PPTX ecrit :", OUT)
print("slides :", len(prs.slides.__iter__.__self__._sldIdLst))

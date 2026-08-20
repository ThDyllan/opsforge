# -*- coding: utf-8 -*-
"""Schemas du dossier OpsForge.

Structure identique a la version initiale ; seules les tailles de libelle et la
geometrie ont ete revues pour rester lisibles une fois le schema reduit a la
largeur de page (les libelles passent d'environ 5 pt a environ 7 pt effectifs).
"""
import io, os
OUT = r"C:\Users\DyllanTHOUVIGNON\Desktop\Work\opsforge\deliverables\assets\diagrams"
os.makedirs(OUT, exist_ok=True)

TEAL = "#0f766e"; TEAL_D = "#115e59"; INK = "#1e293b"; MUTE = "#64748b"
BORD = "#cbd5e1"; FILL = "#f8fafc"; TINT = "#ecfdf5"; TINT_B = "#5eead4"
AMB = "#b45309"; AMB_BG = "#fffbeb"; AMB_BD = "#fcd34d"
BLU = "#1d4ed8"; BLU_BG = "#eff6ff"; BLU_BD = "#93c5fd"
FONT = "Segoe UI, Calibri, sans-serif"; MONO = "Consolas, monospace"

FS = 19        # libelle principal
FS2 = 16       # libelle secondaire
FS_PANEL = 17.5
FS_NOTE = 15
FS_ARROW = 14.5


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, lines, fill=FILL, stroke=BORD, r=9, fs=FS, color=INK, sw=1.6):
    o = ['<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"/>'
         % (x, y, w, h, r, fill, stroke, sw)]
    n = len(lines); lh = fs + 6
    y0 = y + h / 2 - (n - 1) * lh / 2 + fs * 0.35
    for i, t in enumerate(lines):
        fw = "600" if i == 0 else "400"
        cc = color if i == 0 else MUTE
        sz = fs if i == 0 else FS2
        o.append('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="middle">%s</text>'
                 % (x + w / 2, y0 + i * lh, FONT, sz, fw, cc, esc(t)))
    return "".join(o)


def panel(x, y, w, h, title, fill="#ffffff", stroke=BORD, tcol=TEAL, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="14" fill="%s" stroke="%s" stroke-width="1.8"%s/>'
            % (x, y, w, h, fill, stroke, d) +
            '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="700" fill="%s" letter-spacing="0.4">%s</text>'
            % (x + 20, y + 30, FONT, FS_PANEL, tcol, esc(title)))


def arrow(x1, y1, x2, y2, label=None, color="#94a3b8", lx=None, ly=None, dash=None, lcol=MUTE, curve=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    if curve:
        o = ['<path d="M %s %s Q %s %s %s %s" fill="none" stroke="%s" stroke-width="2.4"%s marker-end="url(#ah)"/>'
             % (x1, y1, curve[0], curve[1], x2, y2, color, d)]
    else:
        o = ['<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2.4"%s marker-end="url(#ah)"/>'
             % (x1, y1, x2, y2, color, d)]
    if label:
        mx = lx if lx is not None else (x1 + x2) / 2
        my = ly if ly is not None else (y1 + y2) / 2 - 8
        tw = len(label) * 7.6 + 16
        o.append('<rect x="%s" y="%s" width="%s" height="22" rx="5" fill="#ffffff" opacity="0.94"/>' % (mx - tw / 2, my - 16, tw))
        o.append('<text x="%s" y="%s" font-family="%s" font-size="%s" fill="%s" text-anchor="middle">%s</text>'
                 % (mx, my, FONT, FS_ARROW, lcol, esc(label)))
    return "".join(o)


def cylinder(x, y, w, h, lines, fill=TINT, stroke=TINT_B):
    ry = 13
    o = ['<path d="M %s %s a %s %s 0 0 1 %s 0 v %s a %s %s 0 0 1 %s 0 z" fill="%s" stroke="%s" stroke-width="1.8"/>'
         % (x, y + ry, w / 2, ry, w, h - 2 * ry, w / 2, ry, -w, fill, stroke),
         '<path d="M %s %s a %s %s 0 0 0 %s 0" fill="none" stroke="%s" stroke-width="1.8"/>'
         % (x, y + ry, w / 2, ry, w, stroke)]
    n = len(lines); lh = FS + 6; y0 = y + h / 2 - (n - 1) * lh / 2 + 7
    for i, t in enumerate(lines):
        o.append('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="middle">%s</text>'
                 % (x + w / 2, y0 + i * lh, FONT, FS if i == 0 else FS2, 600 if i == 0 else 400,
                    INK if i == 0 else MUTE, esc(t)))
    return "".join(o)


def txt(x, y, s, size=FS_NOTE, fill=MUTE, weight="400"):
    return '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s">%s</text>' % (x, y, FONT, size, weight, fill, esc(s))


DEFS = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6.5" markerHeight="6.5" '
        'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/></marker></defs>')

# ------------------------------------------------------------------ SCHEMA 1
W, H = 1450, 880
s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">' % (W, H, W, H),
     '<rect width="%s" height="%s" fill="#ffffff"/>' % (W, H), DEFS]

s.append(panel(40, 40, 1024, 340, "APPLICATION OPSFORGE"))
bw, bh = 176, 70
xs = [60, 262, 464, 666, 868]
ry = 96
s.append(box(xs[0], ry, bw, bh, ["Opérateur"], fill="#ffffff"))
s.append(box(xs[1], ry, bw, bh, ["Console web", "Jinja2"]))
s.append(box(xs[2], ry, bw, bh, ["API FastAPI", "22 routes JSON"]))
s.append(box(xs[3], ry, bw, bh, ["Domaine", "transitions strictes"]))
s.append(cylinder(xs[4], ry - 5, bw, bh + 10, ["PostgreSQL"]))
for i in range(4):
    s.append(arrow(xs[i] + bw, ry + bh / 2, xs[i + 1] - 7, ry + bh / 2))
s.append(box(400, 246, 226, 72, ["Journal d'audit", "+ timeline d'incident"]))
s.append(box(686, 246, 170, 72, ["/metrics"], fill=TINT, stroke=TINT_B))
s.append(arrow(530, ry + bh, 490, 242, color="#cbd5e1"))
s.append(arrow(596, ry + bh, 740, 242, color="#cbd5e1"))
s.append(txt(60, 356, "Runbooks : checklists manuelles et 5 automatisations approuvées dans le code — aucune commande arbitraire"))

s.append(panel(1094, 40, 316, 340, "SUPERVISION RÉELLE (k3d)", fill=TINT, stroke=TINT_B, tcol=TEAL_D))
s.append(box(1124, 96, 256, 70, ["Prometheus"], fill="#ffffff", stroke=TINT_B))
s.append(box(1124, 194, 256, 70, ["Règle OpsForgeApiDown"], fill="#ffffff", stroke=TINT_B))
s.append(box(1124, 292, 256, 70, ["Dashboard Grafana"], fill="#ffffff", stroke=TINT_B))
s.append(arrow(1252, 166, 1252, 190, color=TEAL_D))
s.append(arrow(1252, 264, 1252, 288, color=TEAL_D))
s.append(arrow(858, 274, 1120, 138, label="scrape 15 s", color=TEAL_D, lx=960, ly=262, lcol=TEAL_D, curve=(1000, 268)))

s.append(panel(40, 416, 1370, 176, "CHAÎNE 1 — INTÉGRATION CONTINUE (GitHub Actions, à chaque push)", fill=BLU_BG, stroke=BLU_BD, tcol=BLU))
cw, cg, cx = 240, 32, 62
items = [["Ruff", "lint"], ["38 tests", "SQLite en mémoire"], ["1 test", "intégration PostgreSQL"],
         ["Build image", "Docker"], ["Scan Trivy", "advisory"]]
for i, it in enumerate(items):
    x = cx + i * (cw + cg)
    s.append(box(x, 470, cw, 76, it, fill="#ffffff", stroke=BLU_BD))
    if i:
        s.append(arrow(x - cg - 1, 508, x - 6, 508, color=BLU_BD))
s.append(txt(62, 574, "Ne publie ni ne déploie rien : pas de registre d'images, pas de déploiement continu distant."))

s.append(panel(40, 622, 1370, 176, "CHAÎNE 2 — AUTOMATISATION DU DÉPLOIEMENT D'INFRASTRUCTURE (Ansible, une commande)", fill=AMB_BG, stroke=AMB_BD, tcol=AMB))
items2 = [["./ansible/run.sh", "control node conteneurisé"], ["Cluster k3d", "créé seulement si absent"],
          ["Image API", "build + import"], ["Manifests k8s/", "appliqués avec wait"], ["Vérification", "/health + /ready = 200"]]
for i, it in enumerate(items2):
    x = cx + i * (cw + cg)
    s.append(box(x, 676, cw, 76, it, fill="#ffffff", stroke=AMB_BD))
    if i:
        s.append(arrow(x - cg - 1, 714, x - 6, 714, color=AMB_BD))
s.append(txt(62, 780, "Idempotent : rejouable sans rien recréer. Le run échoue si l'application ne répond pas."))
s.append(txt(40, 846, "Les deux chaînes sont indépendantes : la CI valide le code et l'image sans rien publier ; Ansible reconstruit l'image localement et déploie l'infrastructure locale.", 15.5, INK))
s.append('</svg>')
io.open(os.path.join(OUT, "schema_architecture.svg"), "w", encoding="utf-8").write("".join(s))

# ------------------------------------------------------------------ SCHEMA 2
W2, H2 = 1340, 848
t = ['<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">' % (W2, H2, W2, H2),
     '<rect width="%s" height="%s" fill="#ffffff"/>' % (W2, H2), DEFS]
t.append(panel(30, 30, 1280, 778, "POSTE WINDOWS 11 — DOCKER DESKTOP"))
t.append(box(65, 100, 240, 96, ["Control node Ansible", "conteneur éphémère", "versions épinglées"], fill=AMB_BG, stroke=AMB_BD))
t.append(box(65, 252, 240, 72, ["Navigateur / kubectl"], fill="#ffffff"))
t.append(panel(370, 80, 910, 698, "CLUSTER k3d « opsforge » — 1 nœud", fill="#fbfdff", stroke="#bfdbfe", tcol=BLU, dash="7 6"))
t.append(arrow(307, 148, 366, 148, label="pilote", color=AMB, lx=336, ly=137, lcol=AMB))
t.append(panel(400, 132, 470, 616, "namespace  opsforge", fill="#ffffff", stroke=BORD, tcol=MUTE))
t.append(box(425, 176, 420, 66, ["Service NodePort 30080"]))
t.append(box(425, 268, 420, 126, ["Deployment  opsforge-api", "non-root UID 10001 · rootfs en lecture seule",
                                  "probes distinctes :", "/health (liveness) · /ready (readiness)"],
             fill=TINT, stroke=TINT_B))
t.append(box(425, 420, 420, 82, ["Service postgres — ClusterIP 5432", "interne au cluster, non exposé"]))
t.append(box(425, 528, 420, 66, ["StatefulSet  postgres-0"]))
t.append(cylinder(425, 620, 420, 106, ["PVC postgres-data", "1 Gi · StorageClass local-path",
                                       "persistance prouvée après recréation du pod"]))
t.append(arrow(635, 242, 635, 264, color="#94a3b8"))
t.append(arrow(635, 394, 635, 416, color="#94a3b8"))
t.append(arrow(635, 502, 635, 524, color="#94a3b8"))
t.append(arrow(635, 594, 635, 616, color="#94a3b8"))
t.append(arrow(307, 288, 421, 206, label="127.0.0.1:8080  →  NodePort 30080", color=BLU, lx=240, ly=372, lcol=BLU, curve=(370, 300)))
t.append(panel(905, 132, 350, 400, "namespace  monitoring", fill="#ffffff", stroke=BORD, tcol=MUTE))
t.append(box(930, 176, 300, 66, ["Prometheus"], fill=TINT, stroke=TINT_B))
t.append(box(930, 290, 300, 66, ["Grafana"], fill=TINT, stroke=TINT_B))
t.append(arrow(1080, 286, 1080, 248, color=TEAL_D))
t.append(arrow(926, 220, 851, 300, label="scrape 15 s", color=TEAL_D, lx=888, ly=246, lcol=TEAL_D, curve=(880, 236)))
t.append(txt(930, 404, "Cible statique : job opsforge-api"))
t.append(txt(930, 428, "sur :8000/metrics."))
t.append(txt(930, 462, "Accès local par kubectl port-forward"))
t.append(txt(930, 486, "(Prometheus 9090, Grafana 3000)."))
t.append(txt(905, 606, "Aucun registre d'images : l'image", 15.5, INK))
t.append(txt(905, 632, "est construite puis importée dans", 15.5, INK))
t.append(txt(905, 658, "le nœud (imagePullPolicy: Never).", 15.5, INK))
t.append('</svg>')
io.open(os.path.join(OUT, "schema_topologie.svg"), "w", encoding="utf-8").write("".join(t))
print("SVG ecrits dans", OUT)

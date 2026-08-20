# -*- coding: utf-8 -*-
import io, os
OUT = r"C:\Users\DyllanTHOUVIGNON\Desktop\Work\opsforge\deliverables\assets\diagrams"
os.makedirs(OUT, exist_ok=True)

TEAL = "#0f766e"; TEAL_D = "#115e59"; INK = "#1e293b"; MUTE = "#64748b"
BORD = "#cbd5e1"; FILL = "#f8fafc"; TINT = "#ecfdf5"; TINT_B = "#5eead4"
AMB = "#b45309"; AMB_BG = "#fffbeb"; AMB_BD = "#fcd34d"
BLU = "#1d4ed8"; BLU_BG = "#eff6ff"; BLU_BD = "#93c5fd"
FONT = "Segoe UI, Calibri, sans-serif"; MONO = "Consolas, monospace"


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def box(x, y, w, h, lines, fill=FILL, stroke=BORD, r=8, fs=15, color=INK, sw=1.4):
    o = ['<rect x="%s" y="%s" width="%s" height="%s" rx="%s" fill="%s" stroke="%s" stroke-width="%s"/>'
         % (x, y, w, h, r, fill, stroke, sw)]
    n = len(lines); lh = fs + 5
    y0 = y + h / 2 - (n - 1) * lh / 2 + fs * 0.35
    for i, t in enumerate(lines):
        fw = "600" if i == 0 else "400"
        cc = color if i == 0 else MUTE
        sz = fs if i == 0 else fs - 2
        o.append('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="middle">%s</text>'
                 % (x + w / 2, y0 + i * lh, FONT, sz, fw, cc, esc(t)))
    return "".join(o)


def panel(x, y, w, h, title, fill="#ffffff", stroke=BORD, tcol=TEAL, dash=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    return ('<rect x="%s" y="%s" width="%s" height="%s" rx="12" fill="%s" stroke="%s" stroke-width="1.6"%s/>'
            % (x, y, w, h, fill, stroke, d) +
            '<text x="%s" y="%s" font-family="%s" font-size="15" font-weight="700" fill="%s" letter-spacing="0.4">%s</text>'
            % (x + 18, y + 26, FONT, tcol, esc(title)))


def arrow(x1, y1, x2, y2, label=None, color="#94a3b8", lx=None, ly=None, dash=None, lcol=MUTE, curve=None):
    d = ' stroke-dasharray="%s"' % dash if dash else ''
    if curve:
        o = ['<path d="M %s %s Q %s %s %s %s" fill="none" stroke="%s" stroke-width="2"%s marker-end="url(#ah)"/>'
             % (x1, y1, curve[0], curve[1], x2, y2, color, d)]
    else:
        o = ['<line x1="%s" y1="%s" x2="%s" y2="%s" stroke="%s" stroke-width="2"%s marker-end="url(#ah)"/>'
             % (x1, y1, x2, y2, color, d)]
    if label:
        mx = lx if lx is not None else (x1 + x2) / 2
        my = ly if ly is not None else (y1 + y2) / 2 - 8
        tw = len(label) * 6.5 + 14
        o.append('<rect x="%s" y="%s" width="%s" height="19" rx="4" fill="#ffffff" opacity="0.94"/>' % (mx - tw / 2, my - 13, tw))
        o.append('<text x="%s" y="%s" font-family="%s" font-size="12.5" fill="%s" text-anchor="middle">%s</text>'
                 % (mx, my, FONT, lcol, esc(label)))
    return "".join(o)


def cylinder(x, y, w, h, lines, fill=TINT, stroke=TINT_B):
    ry = 11
    o = ['<path d="M %s %s a %s %s 0 0 1 %s 0 v %s a %s %s 0 0 1 %s 0 z" fill="%s" stroke="%s" stroke-width="1.6"/>'
         % (x, y + ry, w / 2, ry, w, h - 2 * ry, w / 2, ry, -w, fill, stroke),
         '<path d="M %s %s a %s %s 0 0 0 %s 0" fill="none" stroke="%s" stroke-width="1.6"/>'
         % (x, y + ry, w / 2, ry, w, stroke)]
    n = len(lines); lh = 19; y0 = y + h / 2 - (n - 1) * lh / 2 + 6
    for i, t in enumerate(lines):
        o.append('<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s" text-anchor="middle">%s</text>'
                 % (x + w / 2, y0 + i * lh, FONT, 15 if i == 0 else 13, 600 if i == 0 else 400, INK if i == 0 else MUTE, esc(t)))
    return "".join(o)


def txt(x, y, s, size=13, fill=MUTE, weight="400"):
    return '<text x="%s" y="%s" font-family="%s" font-size="%s" font-weight="%s" fill="%s">%s</text>' % (x, y, FONT, size, weight, fill, esc(s))


DEFS = ('<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
        'orient="auto-start-reverse"><path d="M 0 0 L 10 5 L 0 10 z" fill="#94a3b8"/></marker></defs>')

# ------------------------------------------------------------------ SCHEMA 1
W, H = 1520, 830
s = ['<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">' % (W, H, W, H),
     '<rect width="%s" height="%s" fill="#ffffff"/>' % (W, H), DEFS]

s.append(panel(40, 40, 1046, 320, "APPLICATION OPSFORGE"))
bw, bh = 150, 58
xs = [70, 275, 480, 685, 890]
ry = 100
s.append(box(xs[0], ry, bw, bh, ["Operateur".replace("Operateur", "Opérateur")], fill="#ffffff"))
s.append(box(xs[1], ry, bw, bh, ["Console web", "Jinja2"]))
s.append(box(xs[2], ry, bw, bh, ["API FastAPI", "22 routes JSON"]))
s.append(box(xs[3], ry, bw, bh, ["Domaine", "transitions strictes"]))
s.append(cylinder(xs[4], ry - 4, bw, bh + 8, ["PostgreSQL"]))
for i in range(4):
    s.append(arrow(xs[i] + bw, ry + bh / 2, xs[i + 1] - 6, ry + bh / 2))
s.append(box(400, 238, 210, 60, ["Journal d'audit", "+ timeline d'incident"]))
s.append(box(660, 238, 150, 60, ["/metrics"], fill=TINT, stroke=TINT_B))
s.append(arrow(530, ry + bh, 480, 234, color="#cbd5e1"))
s.append(arrow(580, ry + bh, 700, 234, color="#cbd5e1"))
s.append(txt(70, 335, "Runbooks : checklists manuelles et 5 automatisations approuvées dans le code — aucune commande arbitraire"))

s.append(panel(1120, 40, 360, 320, "SUPERVISION RÉELLE (k3d)", fill=TINT, stroke=TINT_B, tcol=TEAL_D))
s.append(box(1160, 100, 280, 58, ["Prometheus"], fill="#ffffff", stroke=TINT_B))
s.append(box(1160, 186, 280, 58, ["Règle OpsForgeApiDown"], fill="#ffffff", stroke=TINT_B))
s.append(box(1160, 272, 280, 58, ["Dashboard Grafana"], fill="#ffffff", stroke=TINT_B))
s.append(arrow(1300, 158, 1300, 182, color=TEAL_D))
s.append(arrow(1300, 244, 1300, 268, color=TEAL_D))
s.append(arrow(812, 262, 1156, 140, label="scrape 15 s", color=TEAL_D, lx=985, ly=252, lcol=TEAL_D, curve=(980, 258)))

s.append(panel(40, 396, 1440, 156, "CHAÎNE 1 — INTÉGRATION CONTINUE (GitHub Actions, à chaque push)", fill=BLU_BG, stroke=BLU_BD, tcol=BLU))
cw, cg, cx = 232, 22, 70
items = [["Ruff", "lint"], ["38 tests", "SQLite en mémoire"], ["1 test", "intégration PostgreSQL"],
         ["Build image", "Docker"], ["Scan Trivy", "advisory"]]
for i, it in enumerate(items):
    x = cx + i * (cw + cg)
    s.append(box(x, 446, cw, 64, it, fill="#ffffff", stroke=BLU_BD))
    if i:
        s.append(arrow(x - cg - 1, 478, x - 5, 478, color=BLU_BD))
s.append(txt(70, 536, "Ne publie ni ne déploie rien : pas de registre d'images, pas de déploiement continu distant."))

s.append(panel(40, 586, 1440, 156, "CHAÎNE 2 — AUTOMATISATION DU DÉPLOIEMENT D'INFRASTRUCTURE (Ansible, une commande)", fill=AMB_BG, stroke=AMB_BD, tcol=AMB))
items2 = [["./ansible/run.sh", "control node conteneurisé"], ["Cluster k3d", "créé seulement si absent"],
          ["Image API", "build + import"], ["Manifests k8s/", "appliqués avec wait"], ["Vérification", "/health + /ready = 200"]]
for i, it in enumerate(items2):
    x = cx + i * (cw + cg)
    s.append(box(x, 636, cw, 64, it, fill="#ffffff", stroke=AMB_BD))
    if i:
        s.append(arrow(x - cg - 1, 668, x - 5, 668, color=AMB_BD))
s.append(txt(70, 726, "Idempotent : rejouable sans rien recréer. Le run échoue si l'application ne répond pas."))
s.append(txt(40, 786, "Les deux chaînes sont indépendantes : la CI valide le code et l'image sans rien publier ; Ansible reconstruit l'image localement et déploie l'infrastructure locale.", 13.5, INK))
s.append('</svg>')
io.open(os.path.join(OUT, "schema_architecture.svg"), "w", encoding="utf-8").write("".join(s))

# ------------------------------------------------------------------ SCHEMA 2
W2, H2 = 1340, 790
t = ['<svg xmlns="http://www.w3.org/2000/svg" width="%s" height="%s" viewBox="0 0 %s %s">' % (W2, H2, W2, H2),
     '<rect width="%s" height="%s" fill="#ffffff"/>' % (W2, H2), DEFS]
t.append(panel(30, 30, 1280, 720, "POSTE WINDOWS 11 — DOCKER DESKTOP"))
t.append(box(65, 96, 250, 76, ["Control node Ansible", "conteneur éphémère", "versions épinglées"], fill=AMB_BG, stroke=AMB_BD))
t.append(box(65, 236, 250, 66, ["Navigateur / kubectl"], fill="#ffffff"))
t.append(panel(360, 80, 910, 630, "CLUSTER k3d « opsforge » — 1 nœud", fill="#fbfdff", stroke="#bfdbfe", tcol=BLU, dash="6 5"))
t.append(arrow(317, 134, 356, 134, label="pilote", color=AMB, lx=336, ly=126, lcol=AMB))
t.append(panel(395, 128, 470, 560, "namespace  opsforge", fill="#ffffff", stroke=BORD, tcol=MUTE))
t.append(box(425, 164, 410, 56, ["Service NodePort 30080"]))
t.append(box(425, 256, 410, 82, ["Deployment  opsforge-api", "non-root UID 10001 · rootfs en lecture seule",
                                 "probes distinctes : /health (liveness) · /ready (readiness)"], fill=TINT, stroke=TINT_B))
t.append(box(425, 374, 410, 60, ["Service postgres — ClusterIP 5432", "interne au cluster, non exposé"]))
t.append(box(425, 470, 410, 56, ["StatefulSet  postgres-0"]))
t.append(cylinder(425, 562, 410, 92, ["PVC postgres-data", "1 Gi · StorageClass local-path",
                                      "persistance prouvée après recréation du pod"]))
t.append(arrow(630, 220, 630, 252, color="#94a3b8"))
t.append(arrow(630, 338, 630, 370, color="#94a3b8"))
t.append(arrow(630, 434, 630, 466, color="#94a3b8"))
t.append(arrow(630, 526, 630, 558, color="#94a3b8"))
t.append(arrow(317, 269, 421, 192, label="127.0.0.1:8080  →  NodePort 30080", color=BLU, lx=250, ly=340, lcol=BLU, curve=(380, 284)))
t.append(panel(900, 128, 340, 350, "namespace  monitoring", fill="#ffffff", stroke=BORD, tcol=MUTE))
t.append(box(930, 166, 280, 56, ["Prometheus"], fill=TINT, stroke=TINT_B))
t.append(box(930, 272, 280, 56, ["Grafana"], fill=TINT, stroke=TINT_B))
t.append(arrow(1070, 268, 1070, 230, color=TEAL_D))
t.append(arrow(926, 208, 841, 284, label="scrape 15 s", color=TEAL_D, lx=882, ly=228, lcol=TEAL_D, curve=(880, 222)))
t.append(txt(930, 380, "Cible statique : job opsforge-api"))
t.append(txt(930, 400, "sur :8000/metrics."))
t.append(txt(930, 428, "Accès local par kubectl port-forward"))
t.append(txt(930, 448, "(Prometheus 9090, Grafana 3000)."))
t.append(txt(900, 552, "Aucun registre d'images : l'image", 13.5, INK))
t.append(txt(900, 574, "est construite puis importée dans", 13.5, INK))
t.append(txt(900, 596, "le nœud (imagePullPolicy: Never).", 13.5, INK))
t.append('</svg>')
io.open(os.path.join(OUT, "schema_topologie.svg"), "w", encoding="utf-8").write("".join(t))
print("SVG ecrits dans", OUT)

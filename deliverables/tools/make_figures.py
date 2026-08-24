# -*- coding: utf-8 -*-
"""Recadre les captures sur leur zone utile pour le dossier.

Meme principe que les figures Prometheus : la capture complete reste au depot,
seule la version recadree est placee dans le document.
"""
import os
import shutil

from PIL import Image

ROOT = r"C:\Users\DyllanTHOUVIGNON\Desktop\Work\opsforge\deliverables\assets"
SHOTS = os.path.join(ROOT, "screenshots")
FIGS = os.path.join(ROOT, "figures")
SCRATCH = os.path.dirname(os.path.abspath(__file__))
os.makedirs(FIGS, exist_ok=True)


def last_content_row(im, x_from, x_to, bg_tol=8, sample=3):
    """Derniere ligne dont le contenu differe du fond (couleur du coin bas-gauche)."""
    px = im.convert("RGB").load()
    w, h = im.size
    bg = px[x_from + 5, h - 5]
    last = 0
    for y in range(h):
        for x in range(x_from, min(x_to, w), sample):
            p = px[x, y]
            if abs(p[0] - bg[0]) > bg_tol or abs(p[1] - bg[1]) > bg_tol or abs(p[2] - bg[2]) > bg_tol:
                last = y
                break
    return last


# --- 1. capture GitHub Actions : depuis le scratchpad vers le depot -----------
src = os.path.join(SCRATCH, "gh_job.png")
dst_full = os.path.join(SHOTS, "11_github_actions_run.png")
shutil.copy(src, dst_full)
im = Image.open(dst_full)
w, h = im.size
bottom = last_content_row(im, 600, w - 40) + 40
# on retire la barre marketing de GitHub (haut) et le vide sous la derniere etape
top = int(h * 0.055)
im.crop((0, top, w, min(bottom, h))).save(os.path.join(FIGS, "11_github_actions_run_fig.png"))
print("11_github_actions_run : %dx%d -> recadre %dx%d" % (w, h, w, min(bottom, h) - top))

# --- 2 et 3. file d'alertes et journal d'audit -------------------------------
for name, xfrom in (("02_alerts", 300), ("04_activity", 300)):
    p = os.path.join(SHOTS, name + ".png")
    im = Image.open(p)
    w, h = im.size
    bottom = min(h, last_content_row(im, xfrom, w - 20) + 30)
    im.crop((0, 0, w, bottom)).save(os.path.join(FIGS, name + "_fig.png"))
    print("%-14s : %dx%d -> recadre %dx%d (ratio %.2f)" % (name, w, h, w, bottom, w / bottom))

print()
for f in sorted(os.listdir(FIGS)):
    im = Image.open(os.path.join(FIGS, f))
    print("  %-38s %5dx%-5d  hauteur a 16,6 cm : %.1f cm" % (f, im.size[0], im.size[1],
                                                             16.6 * im.size[1] / im.size[0]))

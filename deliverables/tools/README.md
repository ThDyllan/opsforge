# Outillage de génération du dossier (interne)

Ces scripts ont produit la **première version** du livrable Word à partir du contenu rédigé.
Ils sont conservés pour que les schémas et la mise en page restent reproductibles.

> **Le fichier qui fait foi est `deliverables/Dossier_de_projet_OpsForge_Dyllan_Thouvignon.docx`.**
> Toute modification faite directement dans Word y reste ; **relancer `build_docx.py` écrase le
> `.docx` et perd ces modifications**. Après la première génération, éditer le `.docx` dans Word.

## Contenu

| Fichier | Rôle |
|---|---|
| `gen_diagrams.py` | Génère les deux schémas (`assets/diagrams/*.svg`), à rasteriser ensuite en PNG |
| `make_figures.py` | Recadre les captures sur leur zone utile (`assets/figures/`) : file d'alertes, journal d'audit, cibles Prometheus, alerte FIRING, run GitHub Actions |
| `build_docx.py` | Construit le `.docx` : styles, page de garde, champ de sommaire, tableaux, figures, blocs de code |
| `finalize.ps1` | Ouvre le `.docx` dans Word, compacte les styles du sommaire, met à jour les champs, repagine, enregistre et exporte le PDF |

## Prérequis

```bash
python -m pip install python-docx pillow
```

Microsoft Word est requis pour `finalize.ps1` (mise à jour du sommaire et export PDF).

## Chaîne complète

```bash
python deliverables/tools/gen_diagrams.py          # 1. schémas SVG
# 2. rasterisation SVG -> PNG (navigateur en mode headless, facteur d'échelle 2)
python deliverables/tools/build_docx.py            # 3. document Word
pwsh deliverables/tools/finalize.ps1               # 4. sommaire, pagination, PDF
```

Le contenu rédactionnel est porté par `build_docx.py` ; la version Markdown de travail
(`deliverables/DOSSIER_FIL_ROUGE_OPSFORGE.md`) sert de brouillon et de trace de relecture.

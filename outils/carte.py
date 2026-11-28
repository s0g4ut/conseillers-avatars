#!/usr/bin/env python3
"""Carte de portrait d'un acolyte en image PNG, pour les tâches planifiées
(où le widget Visualizer n'existe pas).

Usage :
  python3 -I carte.py --prenom maia --nom "Maïa" --role "IA et automatisation" \
      --expression reflechie --emoji "🤔" --out carte.png \
      [--badges perso-aimee-20261128.webp,or_mois.webp] [--commit 2b85b9a]

- prenom : minuscules, sans accent (nom du fichier d'image).
- expression : une des 16 expressions ; repli automatique sur « neutre ».
- badges : fichiers du dossier badges/ du dépôt, trois au plus, de gauche à droite.
- Sans l'emoji (ou sans police emoji), la pastille d'humeur est simplement omise.
"""
import argparse
import glob
import io
import urllib.request

from PIL import Image, ImageDraw, ImageFont

BASE = "https://cdn.jsdelivr.net/gh/s0g4ut/conseillers-avatars@{commit}/{chemin}"


def telecharger(url):
    with urllib.request.urlopen(url, timeout=30) as r:
        return Image.open(io.BytesIO(r.read()))


def police(taille):
    for chemin in (
        "/usr/share/fonts/truetype/google-fonts/ofl/roboto/Roboto[wdth,wght].ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ):
        try:
            return ImageFont.truetype(chemin, taille)
        except OSError:
            continue
    return ImageFont.load_default()


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--prenom", required=True)
    p.add_argument("--nom", required=True)
    p.add_argument("--role", required=True)
    p.add_argument("--expression", default="neutre")
    p.add_argument("--emoji", default="")
    p.add_argument("--badges", default="")
    p.add_argument("--commit", default="2b85b9a")
    p.add_argument("--out", default="carte.png")
    a = p.parse_args()

    W, H = 460, 580  # 2 x 230 x 290
    try:
        photo = telecharger(BASE.format(commit=a.commit, chemin=f"corps/{a.prenom}-{a.expression}.webp"))
    except Exception:
        photo = telecharger(BASE.format(commit=a.commit, chemin=f"corps/{a.prenom}-neutre.webp"))
    carte = photo.convert("RGBA").resize((W, H), Image.LANCZOS)

    degrade = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(degrade)
    for i in range(130):
        d.line([(0, H - 130 + i), (W, H - 130 + i)], fill=(0, 0, 0, int(165 * i / 130)))
    carte = Image.alpha_composite(carte, degrade)

    d = ImageDraw.Draw(carte)
    d.text((28, H - 92), a.nom, font=police(34), fill="white")
    d.text((28, H - 48), a.role, font=police(26), fill=(255, 255, 255, 205))

    if a.emoji:
        polices = glob.glob("/usr/share/fonts/**/NotoColorEmoji.ttf", recursive=True)
        if polices:
            try:
                d.ellipse((W - 98, 20, W - 10, 108), fill="white", outline=(0, 0, 0, 30), width=3)
                t = Image.new("RGBA", (136, 128), (0, 0, 0, 0))
                ImageDraw.Draw(t).text((0, 0), a.emoji, font=ImageFont.truetype(polices[0], 109), embedded_color=True)
                carte.alpha_composite(t.resize((52, 50)), (W - 98 + 18, 20 + 19))
            except Exception:
                pass

    x = 20
    for nom in [b for b in a.badges.split(",") if b][:3]:
        try:
            b = telecharger(BASE.format(commit=a.commit, chemin=f"badges/{nom}")).convert("RGBA").resize((76, 76), Image.LANCZOS)
            carte.alpha_composite(b, (x, 20))
            x += 76 + 8
        except Exception:
            pass

    masque = Image.new("L", (W, H), 0)
    ImageDraw.Draw(masque).rounded_rectangle((0, 0, W - 1, H - 1), 44, fill=255)
    sortie = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sortie.paste(carte, (0, 0), masque)
    sortie.save(a.out)
    print(a.out)


if __name__ == "__main__":
    main()

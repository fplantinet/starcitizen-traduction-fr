#!/usr/bin/env python3
"""Génère dist/global.ini : la traduction FR (Dymerz) enrichie des améliorations
des packs anglophones (BeltaKoda Remix prioritaire, puis ExoAE).

Règle centrale : le français gagne toujours. Quand un pack se contente d'ajouter
du texte autour de la valeur stock (préfixe/suffixe), l'ajout est greffé sur le
texte français ; sinon la valeur française est conservée telle quelle.

Usage : python3 scripts/build_fr_enriched.py   (exit 0 = OK ; 1 = échec, rien n'est écrit)
"""
import sys
import urllib.request
from collections import Counter
from pathlib import Path

RAW = 'https://raw.githubusercontent.com'
SOURCES = {
    # Stock = l'anglais vanilla de Dymerz : mis à jour à chaque patch par leur
    # automatisation, il sert d'ancre de greffe toujours alignée sur la version LIVE.
    'stock': f'{RAW}/Dymerz/StarCitizen-Localization/main/data/Localization/english/global.ini',
    'fr': f'{RAW}/Dymerz/StarCitizen-Localization/main/data/Localization/french_(france)/global.ini',
    'remix': f'{RAW}/BeltaKoda/ScCompLangPackRemix/main/LIVE/data/Localization/english/global.ini',
    'exoae': f'{RAW}/ExoAE/ScCompLangPack/main/ScCompLangPack/data/Localization/english/global.ini',
}
MIN_FR_KEYS = 50_000
OUTPUT = Path(__file__).resolve().parent.parent / 'dist' / 'global.ini'


def parse_ini(text):
    """dict clé → valeur ; dernière occurrence d'une clé dupliquée gagne."""
    entries = {}
    for line in text.lstrip('\ufeff').splitlines():
        if not line or '=' not in line:
            continue
        key, _, value = line.partition('=')
        entries[key] = value
    return entries


def modifies(stock_value, pack_value):
    """Vrai si le pack change réellement la valeur (espaces de bord ignorés)."""
    return stock_value.strip() != pack_value.strip()


def graft(stock_value, fr_value, pack_value):
    """Greffe l'ajout du pack (autour du texte stock) sur le texte FR.

    Retourne (valeur greffée, True) si la valeur pack contient le texte stock,
    sinon (valeur FR intacte, False)."""
    stock_text = stock_value.strip()
    if stock_text and stock_text in pack_value:
        prefix, _, suffix = pack_value.partition(stock_text)
        return prefix + fr_value.strip() + suffix, True
    return fr_value, False


def build(stock, fr, packs):
    """Fusionne clé par clé. packs : liste (nom, dict) par priorité décroissante.

    Retourne (dict ordonné comme le fichier FR — clés inédites en fin, Counter)."""
    stats = Counter()
    result = {}
    for key, fr_value in fr.items():
        if key not in stock:
            result[key] = fr_value
            stats['fr_hors_stock'] += 1
            continue
        stock_value = stock[key]
        pack_value = next((p[key] for _, p in packs
                           if key in p and modifies(stock_value, p[key])), None)
        if pack_value is None:
            result[key] = fr_value
            stats['fr'] += 1
        elif not modifies(stock_value, fr_value):
            result[key] = pack_value  # FR non traduite : l'amélioration passe telle quelle
            stats['pack'] += 1
        else:
            value, grafted = graft(stock_value, fr_value, pack_value)
            result[key] = value
            stats['greffee' if grafted else 'conflit_fr'] += 1
    for _, pack in packs:
        for key, value in pack.items():
            if key not in result and key not in stock:
                result[key] = value  # clés inédites (ex. missions ajoutées par ExoAE)
                stats['nouvelle'] += 1
    return result, stats


def sanity_error(fr_size, result_size):
    """Message d'erreur si les tailles sont suspectes, sinon None."""
    if fr_size < MIN_FR_KEYS:
        return f'fichier FR anormalement petit ({fr_size} clés < {MIN_FR_KEYS})'
    if result_size < fr_size:
        return f'résultat ({result_size} clés) plus petit que le FR source ({fr_size})'
    return None


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read().decode('utf-8')


def main():
    try:
        texts = {name: fetch(url) for name, url in SOURCES.items()}
    except OSError as err:
        print(f'ERREUR téléchargement : {err}', file=sys.stderr)
        return 1
    stock = parse_ini(texts['stock'])
    fr = parse_ini(texts['fr'])
    packs = [('remix', parse_ini(texts['remix'])),
             ('exoae', parse_ini(texts['exoae']))]
    result, stats = build(stock, fr, packs)
    error = sanity_error(len(fr), len(result))
    if error:
        print(f'ERREUR : {error}', file=sys.stderr)
        return 1
    eol = '\r\n' if '\r\n' in texts['fr'] else '\n'
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, 'w', encoding='utf-8-sig', newline='') as f:
        f.write(eol.join(f'{key}={value}' for key, value in result.items()) + eol)
    print(f'{OUTPUT} : {len(result):,} clés')
    for label, key in [('inchangées (FR)', 'fr'),
                       ('améliorations greffées sur le FR', 'greffee'),
                       ('améliorations prises telles quelles', 'pack'),
                       ('conflits résolus en FR pur', 'conflit_fr'),
                       ('clés FR hors stock', 'fr_hors_stock'),
                       ('clés inédites des packs', 'nouvelle')]:
        print(f'  {label} : {stats[key]:,}')
    return 0


if __name__ == '__main__':
    sys.exit(main())

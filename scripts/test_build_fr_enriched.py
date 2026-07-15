#!/usr/bin/env python3
"""Tests unitaires du générateur de pack FR enrichi (fixtures inline, zéro réseau)."""
import unittest

from build_fr_enriched import (MIN_FR_KEYS, build, graft, modifies,
                               parse_ini, sanity_error)


class TestParseIni(unittest.TestCase):
    def test_bom_et_lignes_invalides_ignorees(self):
        d = parse_ini('\ufeffa=1\n\nligne sans egal\nb=x=y\n')
        self.assertEqual(d, {'a': '1', 'b': 'x=y'})

    def test_cle_dupliquee_derniere_occurrence_gagne(self):
        self.assertEqual(parse_ini('k=un\nk=deux\n')['k'], 'deux')

    def test_crlf(self):
        self.assertEqual(parse_ini('a=1\r\nb=2\r\n'), {'a': '1', 'b': '2'})


class TestModifies(unittest.TestCase):
    def test_espaces_de_bord_ignores(self):
        self.assertFalse(modifies('TEXT ', 'TEXT'))

    def test_changement_reel_detecte(self):
        self.assertTrue(modifies('TEXT', 'AUTRE'))


class TestGraft(unittest.TestCase):
    def test_prefixe_seul(self):
        value, grafted = graft('REP-8 Generator', 'Générateur REP-8', 'C4A REP-8 Generator')
        self.assertTrue(grafted)
        self.assertEqual(value, 'C4A Générateur REP-8')

    def test_suffixe_seul(self):
        value, grafted = graft('Fix VOLT', 'Réparer VOLT', 'Fix VOLT <EM4>[10 Rep]</EM4>')
        self.assertTrue(grafted)
        self.assertEqual(value, 'Réparer VOLT <EM4>[10 Rep]</EM4>')

    def test_prefixe_et_suffixe(self):
        value, grafted = graft('Core', 'Noyau', '[A] Core (v2)')
        self.assertTrue(grafted)
        self.assertEqual(value, '[A] Noyau (v2)')

    def test_reformulation_non_greffable_garde_fr(self):
        value, grafted = graft('Old text', 'Vieux texte', 'Completely rewritten')
        self.assertFalse(grafted)
        self.assertEqual(value, 'Vieux texte')

    def test_stock_vide_garde_fr(self):
        value, grafted = graft('   ', 'Texte FR', 'nimporte quoi')
        self.assertFalse(grafted)
        self.assertEqual(value, 'Texte FR')


class TestBuild(unittest.TestCase):
    def setUp(self):
        self.stock = {'intacte': 'Alpha', 'nontrad': 'Beta', 'greffable': 'Gamma',
                      'reformulee': 'Delta', 'partagee': 'Epsilon'}
        self.fr = {'intacte': 'Alpha FR', 'nontrad': 'Beta', 'greffable': 'Gamma FR',
                   'reformulee': 'Delta FR', 'partagee': 'Epsilon FR',
                   'orpheline_fr': 'Texte FR hors stock'}
        self.remix = {'partagee': 'R- Epsilon'}
        self.exoae = {'nontrad': 'Beta+', 'greffable': 'Gamma <EM4>[10 Rep]</EM4>',
                      'reformulee': 'Nouveau texte anglais', 'partagee': 'X- Epsilon',
                      'inedite': 'Clé inédite ExoAE'}

    def _build(self):
        return build(self.stock, self.fr,
                     [('remix', self.remix), ('exoae', self.exoae)])

    def test_regles_de_fusion(self):
        result, stats = self._build()
        self.assertEqual(result['intacte'], 'Alpha FR')            # aucun pack → FR
        self.assertEqual(result['nontrad'], 'Beta+')               # FR non traduite → pack
        self.assertEqual(result['greffable'], 'Gamma FR <EM4>[10 Rep]</EM4>')  # greffe
        self.assertEqual(result['reformulee'], 'Delta FR')         # non greffable → FR
        self.assertEqual(result['orpheline_fr'], 'Texte FR hors stock')
        self.assertEqual(result['inedite'], 'Clé inédite ExoAE')   # nouvelle clé
        self.assertEqual(stats['fr'], 1)
        self.assertEqual(stats['pack'], 1)
        self.assertEqual(stats['greffee'], 2)   # 'greffable' + 'partagee'
        self.assertEqual(stats['conflit_fr'], 1)
        self.assertEqual(stats['fr_hors_stock'], 1)
        self.assertEqual(stats['nouvelle'], 1)

    def test_priorite_remix_sur_exoae(self):
        result, _ = self._build()
        # Les deux packs modifient 'partagee' ; Remix gagne et sa greffe s'applique.
        self.assertEqual(result['partagee'], 'R- Epsilon FR')

    def test_ordre_cles_fr_preserve_nouvelles_en_fin(self):
        result, _ = self._build()
        self.assertEqual(list(result), list(self.fr) + ['inedite'])


class TestSanityError(unittest.TestCase):
    def test_fr_trop_petit(self):
        self.assertIn('anormalement petit', sanity_error(MIN_FR_KEYS - 1, MIN_FR_KEYS))

    def test_resultat_plus_petit_que_fr(self):
        self.assertIn('plus petit', sanity_error(60_000, 59_999))

    def test_ok(self):
        self.assertIsNone(sanity_error(60_000, 60_000))


if __name__ == '__main__':
    unittest.main()

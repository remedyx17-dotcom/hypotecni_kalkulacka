import os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from calculator import Vstup, max_uver, mesicni_splatka, validuj, vypocitej


class TestVypocty(unittest.TestCase):
    def test_splatka(self):
        self.assertAlmostEqual(mesicni_splatka(1_000_000, 5, 30), 5368.22, places=2)

    def test_max_uver_je_inverzni_k_splatce(self):
        s = mesicni_splatka(3_000_000, 4.9, 25)
        self.assertAlmostEqual(max_uver(s, 4.9, 25), 3_000_000, places=2)

    def test_validace(self):
        self.assertTrue(validuj(Vstup(50000, 20000, 0, 5_000_000, 6_000_000, 5, 30)))

    def test_vypocet(self):
        r = vypocitej(Vstup(55000, 20000, 0, 5_000_000, 1_000_000, 4.9, 30))
        self.assertAlmostEqual(r["ltv"], 80.0)
        self.assertEqual(r["verdikt"][0], "ok")


if __name__ == "__main__":
    unittest.main()

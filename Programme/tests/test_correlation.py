"""
Tests unitaires pour le module de corrélation
"""
import sys
from pathlib import Path

# Ajout du dossier src au path pour les imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import unittest
import numpy as np
import pandas as pd
from correlation import (
    calculer_correlation_pearson,
    interpreter_correlation,
    matrice_correlation
)


class TestCorrelationPearson(unittest.TestCase):
    """Tests pour le calcul de corrélation de Pearson."""

    def test_correlation_parfaite_positive(self):
        """Test avec une corrélation parfaite positive."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([2, 4, 6, 8, 10])

        coef, p_value = calculer_correlation_pearson(x, y)

        self.assertAlmostEqual(coef, 1.0, places=5)

    def test_correlation_parfaite_negative(self):
        """Test avec une corrélation parfaite négative."""
        x = np.array([1, 2, 3, 4, 5])
        y = np.array([10, 8, 6, 4, 2])

        coef, p_value = calculer_correlation_pearson(x, y)

        self.assertAlmostEqual(coef, -1.0, places=5)

    def test_pas_de_correlation(self):
        """Test avec des données non corrélées."""
        np.random.seed(42)
        x = np.random.randn(100)
        y = np.random.randn(100)

        coef, p_value = calculer_correlation_pearson(x, y)

        # La corrélation devrait être proche de 0
        self.assertTrue(abs(coef) < 0.3)

    def test_donnees_insuffisantes(self):
        """Test avec moins de 3 points."""
        x = np.array([1, 2])
        y = np.array([3, 4])

        coef, p_value = calculer_correlation_pearson(x, y)

        self.assertTrue(np.isnan(coef))

    def test_valeurs_manquantes(self):
        """Test avec des valeurs NaN."""
        x = np.array([1, 2, np.nan, 4, 5])
        y = np.array([2, 4, 6, np.nan, 10])

        coef, p_value = calculer_correlation_pearson(x, y)

        # Devrait fonctionner avec les valeurs restantes
        self.assertFalse(np.isnan(coef))


class TestInterpretation(unittest.TestCase):
    """Tests pour l'interprétation des corrélations."""

    def test_correlation_tres_forte_positive(self):
        """Test interprétation corrélation très forte positive."""
        result = interpreter_correlation(0.95)
        self.assertIn("très forte", result)
        self.assertIn("positive", result)

    def test_correlation_forte_negative(self):
        """Test interprétation corrélation forte négative."""
        result = interpreter_correlation(-0.75)
        self.assertIn("forte", result)
        self.assertIn("négative", result)

    def test_correlation_moderee(self):
        """Test interprétation corrélation modérée."""
        result = interpreter_correlation(0.55)
        self.assertIn("modérée", result)

    def test_correlation_faible(self):
        """Test interprétation corrélation faible."""
        result = interpreter_correlation(0.35)
        self.assertIn("faible", result)

    def test_correlation_nulle(self):
        """Test interprétation absence de corrélation."""
        result = interpreter_correlation(0.1)
        self.assertIn("très faible", result)

    def test_valeur_nan(self):
        """Test avec valeur NaN."""
        result = interpreter_correlation(np.nan)
        self.assertIn("Indéterminé", result)


class TestMatriceCorrelation(unittest.TestCase):
    """Tests pour la matrice de corrélation."""

    def setUp(self):
        """Création de données de test."""
        np.random.seed(42)
        n = 50

        # Données avec corrélation connue
        self.df = pd.DataFrame({
            "var_demo_1": np.random.randn(n),
            "var_demo_2": np.arange(n),
            "prix_1": np.arange(n) * 2 + np.random.randn(n) * 5,  # Corrélé avec var_demo_2
            "prix_2": np.random.randn(n)
        })

    def test_matrice_structure(self):
        """Test de la structure de la matrice retournée."""
        result = matrice_correlation(
            self.df,
            ["var_demo_1", "var_demo_2"],
            ["prix_1", "prix_2"]
        )

        # Vérification des colonnes
        colonnes_attendues = ["variable_demo", "variable_prix", "correlation",
                             "p_value", "interpretation", "significatif"]
        for col in colonnes_attendues:
            self.assertIn(col, result.columns)

        # Vérification du nombre de lignes (2 demo * 2 prix = 4)
        self.assertEqual(len(result), 4)

    def test_detection_correlation_forte(self):
        """Test que les corrélations fortes sont détectées."""
        result = matrice_correlation(
            self.df,
            ["var_demo_2"],
            ["prix_1"]
        )

        # var_demo_2 et prix_1 sont corrélés par construction
        self.assertTrue(result.iloc[0]["correlation"] > 0.8)


if __name__ == "__main__":
    unittest.main()

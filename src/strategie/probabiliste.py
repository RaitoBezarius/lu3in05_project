from strategie.memoire import StrategieAvecMemoire
from typing import Tuple, Iterable
from grille import TypeBateau, Point2D, Direction, Grille
from bataille import Bataille
import numpy as np

class StrategieProbabilisteSimple(StrategieAvecMemoire):
    def agir_selon_probabilites(
        self, grille_proba: np.array
    ) -> Point2D:
        """
        Joue la case de probabilité maximale.
        """
        return np.unravel_index(np.argmax(grille_proba), grille_proba.shape)

    def agir(self, bataille: Bataille) -> Point2D:
        """
        Évalue la grille connue et joue la case de probabilité maximale.
        """
        pass

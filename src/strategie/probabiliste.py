from strategie.base import StrategieBase
from typing import Tuple, Iterable
from grille import TypeBateau, Point2D, Direction, Grille
from bataille import Bataille
import numpy as np

Placement = Tuple[TypeBateau, Point2D, Direction]
def generer_placement_admissibles(bataille: Bataille, bateau: Point2D) -> Iterable[Placement]:
    # idée: faire un DFS sur la case bateau
    # cela nous donne la composante connexe de bateau
    # ensuite pour toute case de la composante connexe, on a un certain nombre de types de bâteaux qu'on peut poser en horizontal ou vertical.
    pass

class StrategieProbabilisteSimple(StrategieBase):
    def __init__(self):
        pass

    def evaluer(self, bataille: Bataille, grille_candidate: Grille) -> np.array:
        """
        Compte tenu des contraintes du champ de bataille actuel, nous faisons l'hypothèse que le champ de bataille est la grille passée en paramètre.
        Alors, on évalue les probabilités p_ij de présence d'un bâteau en chaque point et on le retourne.
        """
        # idée: itérer sur les bateaux non coulés.
        # générer leur placement admissible
        pass

    def agir_selon_probabilites(self, bataille: Bataille, grille_proba: np.array) -> Point2D:
        """
        Joue la case de probabilité maximale.
        """
        pass

    def agir(self, bataille: Bataille) -> Point2D:
        """
        Évalue la grille connue et joue la case de probabilité maximale.
        """
        pass

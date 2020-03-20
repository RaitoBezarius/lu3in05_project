from strategie.memoire import StrategieAvecMemoire
from typing import Tuple, Iterable
from grille import TypeBateau, Point2D, Direction, Grille, LONGUEUR_BATEAUX
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

    def positions_bateau(self, bateau: TypeBateau, position: Point2D, direction:Direction) -> list[tuple]:
        i, j = position
        if direction == Direction.Horizontal:
            return [(i + k, j) for k in range(LONGUEUR_BATEAUX[bateau])]
        else:
            return [(i, j + k) for k in range(LONGUEUR_BATEAUX[bateau])]

    def peut_placer(seld, bataille: Bataille, position: Point2D, direction: Direction, bateau: TypeBateau) -> bool:
        case = bataille.case(pos)

        return np.all(
            bataille.est_dans_la_grille(pos)
            and not (
                case != TypeBateau.Vide
                and
                case != -1
                and
                (case != bateau
                or
                bataille.case_coulee(pos))
            )
            for pos in self.positions_bateau(bateau, position, direction)
        )

    def agir(self, bataille: Bataille) -> Point2D:
        """
        Évalue la grille connue et joue la case de probabilité maximale.
        """
        proba = []
        w, h = bataille.tailles()
        for b in range(1, 6):
            prob_curr = np.zeros((w,h))
            sum_curr = 0

            proba.append(prob_curr)
            for i in range(w):
                for j in range(h):
                    if bataille.case() == i and bataille.case_touchee():
                        #Horizontalement
                        longueur = LONGUEUR_BATEAUX[b]
                        for k in range(-longueur, longueur + 1):
                            if peut_placer(bataille, (i, j + k), Direction.Horizontal, b):
                                proba[i, j+k : j+k+longueur] += np.ones((1, longueur))
                                sum_curr += longueur
                        for k in range(-longueur, longueur + 1):
                            if peut_placer(bataille, (i + k, j), Direction.Vertical, b):
                                proba[i+k : i+k+longueur, j] += np.ones((1, longueur))
                                sum_curr += longueur
            
            if sum_curr == 0:
                #TODO: traiter le cas où il n'y a pas de cases touchée de ce type

        return self.agir_selon_probabilites(grille_proba)
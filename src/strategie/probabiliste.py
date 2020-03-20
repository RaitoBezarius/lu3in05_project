from strategie.memoire import StrategieAvecMemoire
from typing import Tuple, Iterable
from grille import TypeBateau, Point2D, Direction, Grille, LONGUEUR_BATEAUX
from bataille import Bataille
import numpy as np

class GameFinishedException(Exception):
    pass

class StrategieProbabilisteSimple(StrategieAvecMemoire):
    def agir_selon_probabilites(
        self, grille_proba: np.array
    ) -> Point2D:
        """
        Joue la case de probabilité maximale.
        """
        w, h = grille_proba.shape
        max_curr = - np.inf
        list_argmax = []

        for i in range(w):
            for j in range(h):
                if grille_proba[i,j] > max_curr :
                    max_curr = grille_proba[i,j]
                    list_argmax = [(i,j)]
                elif grille_proba[i,j] == max_curr :
                    list_argmax.append((i,j))

        index = np.random.randint(len(list_argmax))

        return list_argmax[index]

    def positions_bateau(self, bateau: TypeBateau, position: Point2D, direction:Direction) -> list(tuple):
        i, j = position
        if direction == Direction.Horizontal:
            return [(i + k, j) for k in range(LONGUEUR_BATEAUX[bateau])]
        else:
            return [(i, j + k) for k in range(LONGUEUR_BATEAUX[bateau])]

    def peut_placer(self, bataille: Bataille, position: Point2D, direction: Direction, bateau: TypeBateau) -> bool:

        return np.all(
            bataille.est_dans_la_grille(position)
            and not (
                bataille.case(pos) != TypeBateau.Vide
                and
                bataille.case(pos) != -1
                and
                (bataille.case(pos) != bateau
                or
                bataille.case_coulee(pos))
            )
            for pos in self.positions_bateau(bateau, position, direction)
        )

    def placement_proba_bateau(self, bataille: Bataille, position: Point2D, b: TypeBateau, prob_curr: np.Array, sum_curr: int) -> int:
        longueur = LONGUEUR_BATEAUX[b]

        #Horizontalement
        for k in range(-longueur, longueur + 1):
            if self.peut_placer(bataille, (i, j + k), Direction.Horizontal, b):
                prob_curr[i, j+k : j+k+longueur] += np.ones(longueur)
                sum_curr += longueur

        #Verticalement
        for k in range(-longueur, longueur + 1):
            if self.peut_placer(bataille, (i + k, j), Direction.Vertical, b):
                prob_curr[i+k : i+k+longueur, j] += np.ones(longueur)
                sum_curr += longueur

        return sum_curr

    def calcul_proba(self, bataille: Bataille, b: TypeBateau, prob_curr: np.Array, touche : bool) -> tuple(np.Array, Point2D):
        sum_curr = 0
        w, h = prob_curr.shape
        if touche:
            for i in range(w):
                for j in range(h):
                    if (bataille.case((i,j)) == i and bataille.case_touchee((i,j))):
                        sum_curr = self.placement_proba_bateau(bataille, (i,j), b, prob_curr, sum_curr)
        else:
            for i in range(w):
                for j in range(h):
                    sum_curr = self.placement_proba_bateau(bataille, (i,j), b, prob_curr, sum_curr)
        return (prob_curr, sum_curr)

    def agir(self, bataille: Bataille) -> Point2D:
        """
        Évalue la grille connue et joue la case de probabilité maximale.
        """

        w, h = bataille.tailles()
        proba = np.zeros((w,h))
        nb_type_bateau = 0

        for b in list(TypeBateau):

            prob_curr = np.zeros((w,h))
            sum_curr = 0
            
            prob_curr, sum_curr = self.calcul_proba(bataille, b, prob_curr, True)

            if sum_curr == 0:
                prob_curr, sum_curr = self.calcul_proba(bataille, b, prob_curr, False)

            if sum_curr == 0:
                nb_type_bateau -= 1
            else:
                prob_curr /= sum_curr
                proba += prob_curr
        
        if nb_type_bateau != 0:
            proba /= nb_type_bateau
        else:
            raise GameFinishedException
        

        return self.agir_selon_probabilites(proba)
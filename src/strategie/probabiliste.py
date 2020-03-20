from strategie.memoire import StrategieAvecMemoire
from typing import Tuple, Iterable
from grille import TypeBateau, Point2D, Direction, Grille, LONGUEUR_BATEAUX
from bataille import Bataille, RetourDeTir
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

    def positions_bateau(self, bateau: TypeBateau, position: Point2D, direction:Direction):
        i, j = position
        if direction == Direction.Vertical:
            return [(i + k, j) for k in range(LONGUEUR_BATEAUX[bateau])]
        else:
            return [(i, j + k) for k in range(LONGUEUR_BATEAUX[bateau])]

    def peut_placer(self, bataille: Bataille, position: Point2D, direction: Direction, bateau: TypeBateau) -> bool:
        return  np.all([
            (bataille.est_dans_la_grille(pos)
            and
            (bataille.etat_de_case(pos) == RetourDeTir.Inconnu
            or
            (bataille.case(pos) == bateau
                and
                not bataille.case_coulee(pos))
            ))
            for pos in self.positions_bateau(bateau, position, direction)
        ])

    def placement_proba_bateau(self, bataille: Bataille, position: Point2D, b: TypeBateau, prob_curr, sum_curr: int) -> int:
        longueur = LONGUEUR_BATEAUX[b]
        i,j = position

        #Horizontalement
        for k in range(-longueur + 1, 0):
            if self.peut_placer(bataille, (i, j + k), Direction.Horizontal, b):
                prob_curr[i, j+k : j+k+longueur] += np.ones(longueur)
                sum_curr += longueur - 1

        #Verticalement
        for k in range(-longueur + 1, 0):
            if self.peut_placer(bataille, (i + k, j), Direction.Vertical, b):
                prob_curr[i+k : i+k+longueur, j] += np.ones(longueur)
                sum_curr += longueur - 1

        prob_curr[i, j] = 0

        return sum_curr

    def calcul_proba(self, bataille: Bataille, b: TypeBateau, prob_curr, touche : bool):
        sum_curr = 0
        w, h = prob_curr.shape
        if touche:
            for i in range(w):
                for j in range(h):
                    if bataille.case((i,j)) == b:
                        sum_curr = self.placement_proba_bateau(bataille, (i,j), b, prob_curr, sum_curr)
        else:
            longueur = LONGUEUR_BATEAUX[b]
            bateau_ones = np.ones(longueur)
            for i in range(w):
                for j in range(h):
                    if self.peut_placer(bataille, (i, j), Direction.Horizontal, b):
                        prob_curr[i, j : j + longueur] += bateau_ones
                        sum_curr += longueur
                    if self.peut_placer(bataille, (i, j), Direction.Vertical, b):
                        prob_curr[i : i + longueur, j] += bateau_ones
                        sum_curr += longueur
        return (prob_curr, sum_curr)

    def agir(self, bataille: Bataille) -> Point2D:
        """
        Évalue la grille connue et joue la case de probabilité maximale.
        """
        
        w, h = bataille.tailles
        proba = np.zeros((w,h))
        liste_bateau = list(TypeBateau)
        liste_bateau.remove(TypeBateau.Vide)
        nb_type_bateau = len(liste_bateau)


        for b in liste_bateau:
            prob_curr = np.zeros((w,h))
            
            prob_curr, sum_curr = self.calcul_proba(bataille, b, prob_curr, True)

            if sum_curr == 0:
                prob_curr, sum_curr = self.calcul_proba(bataille, b, prob_curr, False)

            if sum_curr == 0:
                assert(sum_curr == np.sum(prob_curr))
                nb_type_bateau -= 1
            else:
                prob_curr /= sum_curr
                proba += prob_curr
        
        if nb_type_bateau != 0:
            proba /= nb_type_bateau
        

        return self.agir_selon_probabilites(proba)
from strategie.base import StrategieBase
from strategie.probabiliste import StrategieProbabilisteSimple, generer_placement_admissibles
from bataille import InvalidGameState, Bataille
from grille import Point2D, Grille
from typing import Set, Iterable, Tuple
import random
import numpy as np

def generer_choix(bateaux_non_coules: Set[Point2D]) -> Tuple[Set[Point2D], Point2D]:
    bateau, = random.sample(bateaux_non_coules, 1)
    return (bateaux_non_coules - {bateau}, bateau)

def generer_grille(bataille: Bataille, bateaux_non_coules: Set[Point2D]) -> Iterable[Grille]:
    if not bataille.cases_touchees_non_coulees:
        raise ValueError("Le champ de bataille ne contient pas de cases touchées non coulées, aucun placement admissible ne sera calculable")

    stack = [(generer_choix(bateaux_non_coules), bataille.creer_grille_connue())]
    while stack:
        (bateau_non_coule, bateaux_restants), grille = stack.pop()
        placements_admissibles = generer_placement_admissibles(bataille, bateau_non_coule)

        if not placements_admissibles:
            raise InvalidGameState("Aucun placement admissible n'était disponible pour un bâteau non coulé, absurdité")

        for placement in placements_admissibles:
            grille.place(*placement)
            if bateaux_restants:
                stack.append((generer_choix(bateaux_restants), grille))
            elif not bateaux_restants and bataille.compatible_avec_les_contraintes(grille): # i.e. toutes les cases touchées sont occupées par un bâteau.
                yield grille
                break # on pourrait enlever ce break et générer plus de grilles.


class StrategieMonteCarlo(StrategieProbabilisteSimple):
    def agir(self, bataille: Bataille) -> Point2D:
        p_grille = np.zeros(bataille.tailles)
        n = 0
        for grille in generer_grille(bataille, bataille.cases_touchees_non_coules):
            p_grille += self.evaluer(bataille, grille)
            n += 1

        p_grille /= n

        # p_grille contient les probabilités moyennées, on peut désormais jouer un coup.
        return self.agir_selon_probabilites(bataille, p_grille)

from strategie.base import StrategieBase
from strategie.probabiliste import (
    StrategieProbabilisteSimple,
)
from bataille import InvalidGameState, Bataille, RetourDeTir
from grille import Point2D, Grille, Direction, TypeBateau, tirer_point_uniformement, engendre_position_pour_un_bateau, LONGUEUR_BATEAUX
from typing import Set, Iterable, Tuple
from itertools import product
from collections import deque
import random
import numpy as np
import math

Placement = Tuple[TypeBateau, Point2D, Direction]

def difficulte(nb_tirs):
    A = 5_000
    B = 100
    c = (1/50)*math.log(3/2)
    return int(A*math.exp(nb_tirs*c) + B)

def generer_choix(bateaux_non_coules: Set[Point2D]) -> Tuple[Set[Point2D], Point2D]:
    (bateau,) = random.sample(bateaux_non_coules, 1)
    return (bateaux_non_coules - {bateau}, bateau)

def est_admissible(
        grille: Grille,
        bataille: Bataille,
        placement: Placement) -> bool:
    if grille[placement[1]] != TypeBateau.Vide:
        # print('la grille ne le permet pas', placement)
        return False

    if not grille.peut_placer(*placement):
        return False

    for q in engendre_position_pour_un_bateau(*placement):
        if bataille.etat_de_case(q) == RetourDeTir.Vide:
            # print('le cdb montre qu\'une des cases est vide: {}'.format(q))
            return False

    return True

def generer_placement_admissibles(
        grille: Grille, bataille: Bataille, bateau: Point2D
) -> Iterable[Placement]:
    y, x = bateau
    for type_ in TypeBateau:
        if type_ == TypeBateau.Vide:
            continue

        l = LONGUEUR_BATEAUX[type_]
        for dir_ in Direction:
            # we look at the inverse direction.
            dx = dir_.value % 2
            dy = 1 - dx

            cur = x*dx + y*dy
            for k in range(max(0, cur - l + 1), cur + 1):
                # FIXME: it's a bit ugly, but that would require to change the Point2D type into something better.
                # like a proper vector class with basis (e_1, e_2).
                p = (y, k) if dir_ == Direction.Horizontal else (k, x)
                tentative = (type_, p, dir_)
                if est_admissible(grille, bataille, tentative):
                    # print('placement: {} pour {}'.format(tentative, bateau))
                    yield tentative


def generer_grille(
    bataille: Bataille, bateaux_non_coules: Set[Point2D],
    noeuds: int = 5_000
) -> Iterable[Grille]:
    if not bateaux_non_coules:
        raise ValueError(
            "Le champ de bataille ne contient pas de cases touchées non coulées, aucun placement admissible ne sera calculable"
        )

    noeud = (generer_choix(frozenset(bateaux_non_coules)), bataille.creer_grille_connue())
    stack = deque([noeud])
    deja_visite = set([noeud[1]])
    while stack:
        # print(len(stack), len(deja_visite))
        if len(deja_visite) >= noeuds:
            return

        (bateaux_restants, bateau_non_coule), grille = stack.pop()
        assert bataille.etat_de_case(bateau_non_coule) not in (RetourDeTir.Coulee, RetourDeTir.Vide), "Un bâteau non coulé ne peut pas être coulé ou vide: {}".format(bateau_non_coule)
        if next(generer_placement_admissibles(grille, bataille, bateau_non_coule), None) is None:
            continue
        placements_admissibles = generer_placement_admissibles(
            grille, bataille, bateau_non_coule
        )

        for placement in sorted(placements_admissibles, key=lambda placement: LONGUEUR_BATEAUX[placement[0]]):
            nouvelle_grille = grille.place(*placement, en_place=False)
            assert (nouvelle_grille[bateau_non_coule] != TypeBateau.Vide), "Bâteau non coulé, non placé dans la nouvelle grille!"
            nouveau_restants = bateaux_restants.copy()
            nouveau_restants -= frozenset(engendre_position_pour_un_bateau(*placement)) # on enlève les bâteaux éventuellement placés
            if not nouveau_restants and bataille.compatible_avec_les_contraintes(nouvelle_grille):
                yield nouvelle_grille
                break

            if not nouveau_restants:
                try:
                    assert all(nouvelle_grille[b] != TypeBateau.Vide for b in bateaux_non_coules), "Tous les bâteaux n'ont pas été placé!"
                except AssertionError:
                    import pdb; pdb.set_trace()
                continue

            nouveau_noeud = (generer_choix(nouveau_restants), nouvelle_grille)
            try:
                if nouvelle_grille not in deja_visite:
                    deja_visite.add(nouvelle_grille)
                    stack.append(nouveau_noeud)
            except ValueError as e:
                print(e)
                import pdb; pdb.set_trace()

class StrategieMonteCarlo(StrategieProbabilisteSimple):
    def __init__(self):
        super().__init__()
        self.prev_mcmc = None
    def evaluer(self, bataille: Bataille, grille_candidate: Grille) -> np.array:
        """
        Compte tenu des contraintes du champ de bataille actuel, nous faisons l'hypothèse que le champ de bataille est la grille passée en paramètre.
        Alors, on évalue les probabilités p_ij de présence d'un bâteau en chaque point et on le retourne.

        Complexité: O(nm)
        """
        proba = np.zeros(bataille.tailles)
        for i, j in product(range(bataille.tailles[0]), range(bataille.tailles[1])):
            if bataille.etat_de_case((i, j)) != RetourDeTir.Inconnu:
                continue

            if grille_candidate[i, j] != TypeBateau.Vide:
                proba[i, j] += 1

        nnz = np.count_nonzero(proba)
        return proba / np.count_nonzero(proba) if nnz > 0 else proba

    def tirer_quelque_part(self, bataille: Bataille) -> Point2D:
        """
        Cette fonction essaye de tirer au niveau du centre si elle ne l'a pas déjà fait.
        Ou alors, essaye d'exploiter la matrice de probabilités précédente.
        """
        if self.prev_mcmc is not None:
            print('Tir par réutilisation de la MCMC précédente')
            pos = self.agir_selon_probabilites(self.prev_mcmc)
            prev_pos = pos
            while pos in self.positions_deja_tirees:
                self.prev_mcmc[pos] = 0
                pos = self.agir_selon_probabilites(self.prev_mcmc)
                if pos == prev_pos: # do a random fire
                    print('Annulation, car la MCMC donne des positions répétés')
                    break
                prev_pos = pos

            if pos not in self.positions_deja_tirees:
                return pos

        pos = tirer_point_uniformement(bataille.tailles)
        while pos in self.positions_deja_tirees:
            pos = tirer_point_uniformement(bataille.tailles)

        print('Tir aléatoire')
        return pos

    def agir(self, bataille: Bataille) -> Point2D:
        if not self.cases_touchees_non_coulees:
            return self.tirer_quelque_part(bataille)

        nb_tirs = bataille.score
        p_grille = np.zeros(bataille.tailles)
        n = 0
        max_nodes = difficulte(nb_tirs)
        print('#Noeuds: {}'.format(max_nodes))
        for grille in generer_grille(bataille, self.cases_touchees_non_coulees, noeuds=max_nodes):
            p_grille += self.evaluer(bataille, grille)
            n += 1

        if n == 0:
            return self.tirer_quelque_part(bataille)

        p_grille /= n

        if not p_grille.any():
            return self.tirer_quelque_part(bataille)

        print('MCMC:', p_grille)
        self.prev_mcmc = p_grille

        # p_grille contient les probabilités moyennées, on peut désormais jouer un coup.
        pos = self.agir_selon_probabilites(p_grille)
        self.prev_mcmc[pos] = 0 # on supprime cette case.
        nnz = np.count_nonzero(self.prev_mcmc)
        self.prev_mcmc = self.prev_mcmc*(1+1/nnz) if nnz > 0 else None # re-multiplier les probabilités.

        return pos

    def analyser(self, bataille: Bataille, cible: Point2D, retour: RetourDeTir) -> Point2D:
        super().analyser(bataille, cible, retour)
        # FIXME: si on a eu un coulé, on supprime les bâteaux qu'on a dans prev_mcmc

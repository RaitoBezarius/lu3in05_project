from grille import (
    Grille,
    Point2D,
    tirer_point_uniformement,
    TypeBateau,
    Direction,
    LONGUEUR_BATEAUX
)
from matplotlib import pyplot
from matplotlib.colors import ListedColormap, BoundaryNorm
import numpy as np
from typing import Tuple, Iterable, Optional, Set
from enum import Enum
from collections import defaultdict

CMAP_BATAILLE_ARRAY = [
    'xkcd:azure', # inconnu
    'xkcd:white', # vide
    'xkcd:violet', # touché
    'xkcd:crimson', # coulé
]


BATAILLE_CMAP = ListedColormap(CMAP_BATAILLE_ARRAY)
BATAILLE_BOUNDS = [0, 1, 2, 3, 4]
BATAILLE_NORM = BoundaryNorm(BATAILLE_BOUNDS, BATAILLE_CMAP.N)


class InvalidGameState(Exception):
    pass


class InvalidAction(Exception):
    pass


class RetourDeTir(Enum):
    Vide = 1
    Touchee = 2
    Coulee = 3
    Inconnu = 0


class Bataille:
    def __init__(self, grille: Grille):
        # On récupère la grille mais on ne la modifiera jamais
        self._grille = grille

        # On enregistre dans un np.array si les cases ont été touchées ou non
        self._cases_touchees = np.zeros(self.tailles, np.uint8)

        # On récupère en tant que constante le nombre de cases occupées
        self._nb_cases_occupees = grille.nb_cases_occupees

        # On compte au fur et à mesure le nombre de cases occupées touchées
        # La condition de victoire de la bataille est:
        #   sum(self._nb_cases_touchees) == self.NB_CASES_OCCUPEES
        self._nb_cases_touchees = defaultdict(lambda: 0)

        self.bateaux_coules: List[Tuple[TypeBateau, Direction, Set[Point2D]]] = []

        # On compte au fur et à mesure le score (i.e. le nombre de tirs effectués au cours de la bataille)
        self.score = 0

    def fog_of_war(self):
        """ La représentation souhaitée est la suivante:
                repr[x, 0] = -1
                repr[x, 1] = x
            On propose donc la fonction suivante:
                f(x,y) =(x + 1) * y - 1
            On vérifie que c'est bien ce qu'on souhaite"""
        # FIXME: le fog of war doit afficher les cases coulées entièrement.
        return self._cases_touchees

    def __repr__(self):
        return repr(self.fog_of_war())

    def __str__(self):
        n, m = self.tailles
        return "<Bataille {} {}×{}, score: {}>".format(
            "gagnée" if self.victoire else "en cours", n, m, self.score
        )

    @property
    def tailles(self) -> Point2D:
        return self._grille.tailles

    def est_dans_la_grille(self, pos: Point2D) -> bool:
        return self._grille.est_dans_la_grille(pos)

    def etat_de_case(self, case: Point2D) -> RetourDeTir:
        return RetourDeTir(self._cases_touchees[case])

    def case_touchee(self, case: Point2D) -> bool:
        return self.etat_de_case(case) == RetourDeTir.Touchee

    def case_coulee(self, case: Point2D) -> bool:
        return self.etat_de_case(case) == RetourDeTir.Coulee

    def case(self, pos: Point2D) -> int:
        if self.case_touchee(pos):
            return self._grille.case(pos)
        else:
            return -1

    @property
    def victoire(self) -> bool:
        return sum(self._nb_cases_touchees.values()) == self._nb_cases_occupees

    def affiche(self, **kwargs):
        return pyplot.matshow(self.fog_of_war(), cmap=BATAILLE_CMAP, norm=BATAILLE_NORM, interpolation='nearest', **kwargs)

    def obtenir_bateau(self, case: Point2D) -> Tuple[TypeBateau, Direction, Set[Point2D]]:
        """
        Si la case a été coulée, donc le bâteau est devenu visible, il faut retourner les points du bâteau.
        """
        if not self.case_coulee(case):
            raise InvalidAction(
                "Le bâteau n'a pas encore été coulé! Il est donc impossible de récupérer ses coordonnées"
            )

        return self._grille.obtenir_bateau(case)

    def creer_grille_connue(self) -> Grille:
        """
        À partir de l'ensemble des cases coulées, on peut calculer une grille partielle.
        """
        g = Grille(self.tailles)

        for type_, dir_, positions in self.bateaux_coules:
            c_pos = self._grille.registre_des_positions[next(iter(positions))]
            g.place(type_, c_pos, dir_)

        return g

    def compatible_avec_les_contraintes(self, grille: Grille) -> bool:
        """
        Détermine si la grille fournie est compatible avec les cases déjà coulées:
        — il faut vérifier que les cases coulées soient là avec le bon type ;
        — il faut vérifier que les cases non coulées mais proposées sur des cases touchées (de bâteaux) soient là avec le bon type ;
        — il faut vérifier que les cases non coulées non touchées soient là avec le bon type
        """
        for type_, _, positions in self.bateaux_coules:
            for pos in positions:
                if grille[pos] != type_:
                    return False

        for pos_index in np.flatnonzero(self._cases_touchees):
            pos = np.unravel_index(pos_index, self._cases_touchees.shape)
            if grille[pos] == TypeBateau.Vide and self.etat_de_case(pos) != RetourDeTir.Vide:
                return False

        # TODO: étape 3: vérification des tailles des cases.
        return True

    def tirer(self, case: Point2D) -> RetourDeTir:
        """
        Cette fonction assume que le point case est inclus dans la grille et qu'il n'a jamais été touché par un tir
        """
        if self.victoire:
            raise InvalidGameState("Bataille déjà gagnée")

        if not self.est_dans_la_grille(case):
            raise InvalidAction("Case hors de la grille!")

        self.score += 1
        if (
            self._grille.case(case) != TypeBateau.Vide.value
            and self.etat_de_case(case) == RetourDeTir.Inconnu
        ):
            # on récupère une référence canonique au bâteau, peu importe sa case.
            type_, dir_, c_pos = self._grille.reference_bateau(case)
            # on augmente le nombre de cases touchées.
            self._nb_cases_touchees[c_pos] += 1
            # on détermine si on a coulé ou touchée seulement le bâteau.
            retour = (
                RetourDeTir.Coulee
                if self._nb_cases_touchees[c_pos] == LONGUEUR_BATEAUX[type_]
                else RetourDeTir.Touchee
            )
            # on note la valeur de retour.
            self._cases_touchees[case] = retour.value

            if retour == RetourDeTir.Coulee:
                placement = self.obtenir_bateau(case)
                for c in placement[2]:
                    self._cases_touchees[c] = RetourDeTir.Coulee.value

                self.bateaux_coules.append(self.obtenir_bateau(case))
            # on redonne le retour.
            return retour
        else:
            self._cases_touchees[case] = RetourDeTir.Vide.value
            return self.etat_de_case(case)

    def reset(self) -> None:
        self._cases_touchees = np.zeros(self.tailles)
        self._nb_cases_touchees = 0
        self.score = 0

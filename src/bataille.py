from grille import Grille, Point2D, CMAP_GRILLE_ARRAY, tirer_point_uniformement,\
                   TypeBateau, Direction
from matplotlib import pyplot
from matplotlib.colors import ListedColormap
import numpy as np
from typing import Tuple, Iterable

CMAP_BATAILLE_ARRAY = np.vstack(([0,0,0], CMAP_GRILLE_ARRAY))

CMAP_BATAILLE = ListedColormap(CMAP_BATAILLE_ARRAY)

class UnexpectedGameState(Exception):
    pass

class RetourDeTir(Enum):
    Vide = 1
    Touchee = 2
    Coulee = 3

class Bataille:
    def __init__(self, grille: Grille):
        #On récupère la grille mais on ne la modifiera jamais
        self._grille = grille

        #On enregistre dans un np.array si les cases ont été touchées ou non
        self._cases_touchees = np.zeros(self.tailles)

        #On récupère en tant que constante le nombre de cases occupées
        self._nb_cases_occupees = grille.nb_cases_occupees

        #On compte au fur et à mesure le nombre de cases occupées touchées
        #La condition de victoire de la bataille est:
        #   self._nb_cases_touchees == self.NB_CASES_OCCUPEES
        self._nb_cases_touchees = 0

        #On compte au fur et à mesure le score (i.e. le nombre de tirs effectués au cours de la bataille)
        self.score = 0

    def fog_of_war(self):
        """ La représentation souhaitée est la suivante:
                repr[x, 0] = -1
                repr[x, 1] = x
            On propose donc la fonction suivante:
                f(x,y) =(x + 1) * y - 1
            On vérifie que c'est bien ce qu'on souhaite"""
        return ((self._grille.inner + 1) * self._cases_touchees) - 1

    def __repr__(self):
        return repr(self.fog_of_war())

    def __str__(self):
        n, m = self.tailles
        return "<Bataille {} {}X{} Score = {}>".format("gagnée" if self._victoire else "en cours", n, m, self.score)

    @property
    def tailles(self) -> Point2D:
        return self._grille.tailles

    def est_dans_la_grille(self, pos: Point2D) -> bool:
        return self._grille.est_dans_la_grille(pos)

    def case_touchee(self, case:Point2D) -> bool:
        return self._cases_touchees[case[0], case[1]] == 1

    def case(self, pos: Point2D) -> int:
        if self.case_touchee(pos):
            return self._grille.case(pos)
        else:
            return -1

    @property
    def victoire(self) -> bool:
        return self._nb_cases_touchees == self._nb_cases_occupees

    def affiche(self, **kwargs):
        pyplot.matshow(self.fog_of_war(), cmap=CMAP_BATAILLE, **kwargs)

    def tirer(self, case: Point2D) -> RetourDeTir:
        """
        Cette fonction assume que le point case est inclus dans la grille et qu'il n'a jamais été touché par un tir
        """
        if self.victoire:
            raise UnexpectedGameState("Bataille déjà gagnée")
        else:
            self._cases_touchees[case[0], case[1]] = 1
            self.score = self.score + 1
            if self._grille.case(case) != TypeBateau.Vide.value:
                self._nb_cases_touchees = self._nb_cases_touchees + 1
                # FIXME: retourner touchée ou coulée
                return self._grille.case(case)
            else:
                return RetourDeTir.Vide

    def reset(self) -> None:
        self._cases_touchees = np.zeros(self.tailles)
        self._nb_cases_touchees = 0
        self.score = 0


grille = Grille(20,6)
grille.place(TypeBateau.PorteAvions, (0,0), Direction.Horizontal, en_place = True)
grille.place(TypeBateau.Croiseur, (0,1), Direction.Horizontal, en_place = True)
grille.place(TypeBateau.ContreTorpilleurs,(0,2), Direction.Horizontal, en_place = True)
grille.place(TypeBateau.SousMarin, (0,3), Direction.Horizontal, en_place = True)
grille.affiche()

bat = Bataille(grille)
while not bat.victoire:
    case = tirer_point_uniformement(bat.tailles)
    if not bat.case_touchee(case):
        bat.tirer(case)
bat.reset()
bat.affiche()
pyplot.show()

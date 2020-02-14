import numpy as np
from typing import Tuple

class TypeBateau(IntEnum):
    Vide = 0
    PorteAvions = 1
    Croiseur = 2
    ContreTorpilleurs = 3
    SousMarin = 4
    Torpilleur = 5

class Direction(IntEnum):
    Horizontal = 1
    Vertical = 2

LONGUEUR_BATEAUX = {
    TypeBateau.Vide: 0,
    TypeBateau.PorteAvions: 5,
    TypeBateau.Croiseur: 4,
    TypeBateau.ContreTorpilleurs: 3,
    TypeBateau.SousMarin: 3,
    TypeBateau.Torpilleur: 2
}

Point2D = Tuple[int, int]

class Grille:
    def __init__(self, n=10, m=10):
        self.inner = np.zeros(n, m)

    def peut_placer(self, type_: TypeBateau, pos: Point2D, dir_: Direction) -> bool:
        pass

    def place(self, type_: TypeBateau, pos: Point2D, dir_: Direction, inplace: bool = False) -> Grille:
        pass

    def place_alea(self, type_: TypeBateau) -> Grille:
        pass

    def affiche(self) -> None:
        pass

    def __eq__(self, other: Grille) -> bool:
        assert isinstance(other, Grille), 'Equality cannot be tested only between `Grille`'
        return self.inner == other.inner

    @classmethod
    def generer_grille(cls) -> Grille:
        g = cls()
        pass

import numpy as np
from typing import Tuple, Iterable, Set, Dict
import random
from enum import IntEnum
from collections import defaultdict
from matplotlib import pyplot
from matplotlib.colors import ListedColormap


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
    TypeBateau.Torpilleur: 2,
}

DIRECTION_GENERATOR = {Direction.Horizontal: (1, 0), Direction.Vertical: (0, 1)}

Point2D = Tuple[int, int]

CMAP_GRILLE_ARRAY = (
    np.array(
        [
            [0, 0, 255],
            [30, 40, 23],
            [100, 0, 20],
            [20, 200, 10],
            [200, 100, 100],
            [255, 255, 0],
        ]
    )
    / 255
)

CMAP_GRILLE = ListedColormap(CMAP_GRILLE_ARRAY)


def engendre_position_pour_un_bateau(
    courant: Point2D, type_: TypeBateau, dir_: Direction
) -> Iterable[Point2D]:
    length = LONGUEUR_BATEAUX.get(type_)
    if length is None:
        raise ValueError("`type_` n'est pas un type de bâteau connu")

    delta = DIRECTION_GENERATOR.get(dir_)
    if delta is None:
        raise ValueError("`dir_` n'est pas une direction")

    x, y = courant
    delta_x, delta_y = delta
    for k in range(length + 1):
        yield (x + k * delta_x, y + k * delta_y)


def tirer_point_uniformement(tailles: Tuple[int, int]) -> Point2D:
    n, m = tailles
    total = n * m
    k = random.randint(0, total - 1)
    # interprétation phi : [[0, nb_cases_totales - 1]] → [[0, n - 1]] × [[0, m - 1]]
    #                             k                →     (k   mod  n,   k intdiv n)
    # où intdiv est la division entière.
    # justifié par unicité (et existence) de la division euclidienne.
    # il faut voir que k = ny + x.

    return (k % n, k // n)


def tirer_direction_uniformement() -> Direction:
    i = random.randint(1, 2)
    return Direction(i)


class Grille:
    def __init__(self, n=10, m=10):
        self.inner: np.array = np.zeros((n, m), np.uint8)
        self.registre_des_bateaux: Dict[Point2D, Tuple[TypeBateau, Direction, Set[Point2D]]] = dict()
        self.registre_des_positions: Dict[Point2D, Point2D] = dict()

    def __repr__(self):
        return repr(self.inner)

    def __str__(self):
        return "<Grille {} × {}>".format(*self.inner.shape)

    @property
    def nb_cases_totales(self) -> int:
        return self.inner.size

    @property
    def nb_cases_occupees(self) -> int:
        return np.count_nonzero(self.inner)

    @property
    def nb_cases_vides(self) -> int:
        return self.nb_cases_totales - self.nb_cases_occupees

    @property
    def tailles(self) -> Tuple[int, int]:
        return self.inner.shape

    def est_dans_la_grille(self, pos: Point2D) -> bool:
        x, y = pos
        n, m = self.tailles

        return 0 <= x < n and 0 <= y < m

    @property
    def est_vide(self):
        return self.nb_cases_occupees == 0

    def case(self, pos: Point2D) -> int:
        if not self.est_dans_la_grille(pos):
            raise ValueError("`pos` est hors de la grille!")

        return self.inner[pos[0]][pos[1]]

    def reference_bateau(self, case: Point2D) -> Tuple[TypeBateau, Direction, Point2D]:
        """
        Retourne les données canoniques d'un bâteau dans cette grille.
        """
        c_pos = self.registre_des_positions.get(case)
        if c_pos is None:
            raise ValueError("Aucun bâteau ne se trouve à cette case!")

        type_, dir_, _ = self.registre_des_bateaux.get(c_pos)

        return type_, dir_, c_pos

    def peut_placer(self, type_: TypeBateau, pos: Point2D, dir_: Direction) -> bool:
        return all(
            self.est_dans_la_grille(pos) and self.case(pos) == TypeBateau.Vide
            for pos in engendre_position_pour_un_bateau(pos, type_, dir_)
        )

    def peut_placer_quelque_part(self, type_: TypeBateau) -> bool:
        length = LONGUEUR_BATEAUX.get(type_)
        if length is None:
            raise ValueError("`type_` n'est pas un bâteau de type connu!")

        n, m = self.tailles
        for dir_ in Direction:
            dx = dir_.value % 2  # vaut 1 si dir_ = Horizontal, 0 sinon.
            dy = 1 - dx  # vaut 1 si dir_ = Vertical, 0 sinon.
            courant = [0, 0]

            for z in range(
                dx * n + dy * m - length
            ):  # dx*n + dy*m = n ou m ; par construction.
                if self.peut_placer(type_, tuple(courant), dir_):
                    return True

                # lorsque dy = 0, i.e. dir_ = Horizontal, on fait varier x, donc la première composante.
                # lorsque dy = 1, l'inverse.
                courant[dy] = z

        return False

    def place(
        self, type_: TypeBateau, pos: Point2D, dir_: Direction, en_place: bool = True
    ) -> "Grille":
        inner = self.inner
        reg_bateaux = self.registre_des_bateaux
        reg_positions = self.registre_des_positions
        if not en_place:
            inner = self.inner.copy()
            reg_bateaux = self.registre_des_bateaux.copy()
            reg_positions = self.registre_des_positions.copy()

        reg_bateaux[pos] = (type_, dir_, set())

        for pos_ in engendre_position_pour_un_bateau(pos, type_, dir_):
            inner[pos_[0], pos[1]] = type_.value
            reg_bateaux[pos][2].add(pos_)
            reg_positions[pos_] = pos

        if en_place:
            return self
        else:
            return Grille.depuis_tableau(inner, reg_bateaux, reg_positions)

    def place_alea(self, type_: TypeBateau, en_place: bool = True) -> "Grille":
        """
        Cette fonction fait l'hypothèse qu'il existe un emplacement admissible, sinon elle bouclera infiniement.
        """
        courant = tirer_point_uniformement(self.tailles)
        dir_ = tirer_direction_uniformement()
        while not self.peut_placer(type_, courant, dir_):
            courant = tirer_point_uniformement(self.tailles)
            dir_ = tirer_direction_uniformement()

        return self.place(type_, courant, dir_, en_place=en_place)

    def affiche(self, **kwargs) -> None:
        # FIXME: légender les couleurs automatiquement.
        # Utiliser une cmap custom?
        return pyplot.matshow(self.inner, cmap=CMAP_GRILLE, **kwargs)

    def obtenir_bateau(self, case: Point2D) -> Tuple[TypeBateau, Direction, Set[Point2D]]:
        if case not in self.registre_des_positions:
            raise ValueError("Cette position n'est pas enregistré pour un bâteau")
        c_pos = self.registre_des_positions.get(case)
        return self.registre_des_bateaux[c_pos]

    def __eq__(self, other: "Grille") -> bool:
        assert isinstance(
            other, Grille
        ), "L'égalité de grilles ne peut être fait qu'entre instances de `Grille`"
        return self.inner == other.inner

    @classmethod
    def generer_grille(
        cls, *, n: int = 10, m: int = 10, facteur_vide: float = 0.3
    ) -> "Grille":
        """
        Analyse probabiliste:

        On note n, m les tailles respectives de la grille.
        On tire uniformément A dans [[0, nm - 1]].
        Puis, on construit une suite (X_k)_k de variables aléatoires où k est dans [[0, 5]], tel que X_i donne le nombre de bâteau de type i.
        Avec la convention: X_0 donne le nombre de cases.

        Alors, à chaque type de bâteau, on tire uniformément B_k dans [[0, (nm - S_k) / longueur_k - 1]] où S_k = somme_(j=1)^(k - 1) longueur_j*X_j où k est le k-ème type de bâteau qu'on regarde.
        On peut interpréter S_k comme le nombre de cases prises par tous les bâteaux tirés jusque là.

        Tant que cela est possible (i.e. il existe une couple (p, d) de point et de direction tel qu'on puisse poser le bâteau à la position p et selon la direction d),
        On pose un bâteau, au plus B_k.

        Donc: X_k <= B_k < (nm - S_k)/longueur_k

        Aussi, on sait que S_5 = nm.

        FIXME: cette fonction génère trop de grilles vides.
        """
        g = cls(n, m)
        maxNbBateau = random.randint(
            0, g.nb_cases_totales // 2
        )  # TODO: remplacer 2 par nonzero_min(LONGUEUR_BATEAUX.values())
        nbBateau = random.randint(
            0, facteur_vide * g.nb_cases_totales
        )  # nombre de cases vides.
        for bateau in TypeBateau:
            if nbBateau >= maxNbBateau:
                break

            if bateau == TypeBateau.Vide:
                continue

            maxNbBateauDeCeType = random.randint(
                0, g.nb_cases_vides // int(bateau)
            )  # c'est une majoration grossière qui ne tient pas compte de la contrainte de direction.
            nbBateauDeCeType = 0
            while (
                g.peut_placer_quelque_part(bateau)
                and nbBateau < maxNbBateau
                and nbBateauDeCeType < maxNbBateauDeCeType
            ):
                g.place_alea(bateau)
                nbBateau += 1
                nbBateauDeCeType += 1
        return g

    @classmethod
    def depuis_tableau(
        cls,
        inner: np.array,
        reg_bateaux: Dict[Point2D, Set[Point2D]],
        reg_positions: Dict[Point2D, Point2D],
    ) -> "Grille":
        n, m = inner.shape
        g = cls(n, m)
        g.inner = inner
        g.reg_bateaux = reg_bateaux
        g.reg_positions = reg_positions
        return g

from strategie.memoire import StrategieAvecMemoire
from enum import IntEnum
from bataille import Bataille, RetourDeTir
from grille import Point2D
import numpy as np
from typing import Tuple, Iterable, Set, Dict

ALEATOIRE = 1
CONNEXE = 2

class Direction(IntEnum):
    STOP = 0
    NORD = 1
    OUEST = 2
    SUD = 3
    EST = 4

dir_to_vect = {
    Direction.NORD: (-1, 0),
    Direction.OUEST: (0, -1),
    Direction.SUD: (1, 0),
    Direction.EST: (0, 1)
}

class UnexpectedState(Exception):
    pass

class StrategieHeuristique(StrategieAvecMemoire):
    def __init__(self):
        super().__init__()
        self.mode = ALEATOIRE
        self.dir = Direction.STOP
        self.pt_de_depart = (-1, -1)
        self.tir = (-1, - 1)
        self.tailles = (-1, -1)
        self.positions_bataille = set()

    def mode_aleatoire(self, bataille: Bataille) -> Point2D:
        # Calcul de l'ensemble des positions dans la bataille
        if bataille.tailles != self.tailles:
            h, w = bataille.tailles
            self.tailles = (h, w)
            self.positions_bataille = {(i,j) for i in range(h) for j in range(w)}

        # Calcul des positions non tirees precedemment
        positions_a_tirer = list(self.positions_bataille - self.positions_deja_tirees)

        # Selection d'une position au hasard
        if len(positions_a_tirer) == 0:
            print("Aucune position disponible")
            exit(1)
        index = np.random.randint(len(positions_a_tirer))
        return positions_a_tirer[index]

    def agir(self, bataille: Bataille) -> Point2D :
        if self.mode == ALEATOIRE:
            self.tir = self.mode_aleatoire(bataille)
        return self.tir

    def add_dir(self, pos: Point2D, direc: Direction) -> Point2D:
        # On considere que les directions correspondent à ces vecteurs:
        #   NORD -> (-1, 0)
        #   OUEST -> (0, -1)
        #   SUD -> (1, 0)
        #   EST -> (0, 1)

        vect = dir_to_vect[direc]
        return (pos[0] + vect[0], pos[1] + vect[1])

    def recuperer_dir_pos(self, bataille: Bataille, direction_suivante: Direction) -> Tuple[Direction, Point2D]:
        # (-1, -1) est un peu comme un None, on veut juste respecter les types
        tir = (-1, -1)
        direc = direction_suivante

        # On avance dans chaque direction, tant que ce n'est pas une chaine du bateau du type du point de depart
        while tir == (-1, -1) and direc != Direction.STOP:
            # On démarre à partir de la case a cote au point de depart
            tir = self.add_dir(self.pt_de_depart, direc)

            # On avance dans la direction direc tant que a des bateaux touches du meme type que celui du point de depart
            while bataille.est_dans_la_grille(tir) and bataille.case(tir) == bataille.case(self.pt_de_depart):
                tir = self.add_dir(tir, direc)
            
            #Si on est sorti de la grille ou qu'on s'est arrete sur case qui n'est pas inconnu, on test la direction suivante
            if not(bataille.est_dans_la_grille(tir)) or bataille.etat_de_case(tir) != RetourDeTir.Inconnu:
                tir = (-1, -1)
                direc = (direc + 1) % 5

        # Ce test est là temporairement, le temps de voir si tout marche
        if tir == (-1, -1):
            print(repr(bataille))
            print(tir, direc)
            raise UnexpectedState

        return (direc, tir)
    
    def direc_suiv(self, direc: Direction) -> Direction:
        return (direc + 1) % 5
    
    def analyser(self, bataille: Bataille, cible: Point2D, retour: RetourDeTir):
        super().analyser(bataille, cible, retour)
        if self.mode == ALEATOIRE:
            if retour == RetourDeTir.Touchee:
                self.mode = CONNEXE
                self.pt_de_depart = cible
                self.dir, self.tir = self.recuperer_dir_pos(bataille, Direction.NORD)
        else:
            # Si la case est coulee
            # Alors si la case coulee correspond au bateau du point de depart
            #       alors choisir une case touchee non coulee restante au hasard  
            #       sinon changer de direction
            if retour == RetourDeTir.Coulee:
                if bataille.case_coulee(self.pt_de_depart):
                    if self.cases_touchees_non_coulees == set():
                        self.mode = ALEATOIRE
                    else:
                        self.pt_de_depart = self.cases_touchees_non_coulees.pop()
                        self.cases_touchees_non_coulees.add(self.pt_de_depart)
                        self.dir, self.tir = self.recuperer_dir_pos(bataille, Direction.NORD)
            # Si la case tiree est differente du type de bateau du point de depart
            # Alors changer de direction
            elif retour == RetourDeTir.Vide or bataille.case(self.tir) != bataille.case(self.pt_de_depart):
                self.dir, self.tir = self.recuperer_dir_pos(bataille, self.direc_suiv((self.dir)))
            # Si la case touchee n'est ni coulee ni d'un type different du type du bateau
            # Alors avancer dans la direction courante
            #       Si on sort de la grille
            #       Alors changer de position
            else:
                self.dir, self.tir = self.recuperer_dir_pos(bataille, self.dir)

    def reset(self):
        super().reset()
        self.mode = ALEATOIRE
        self.dir = Direction.STOP
        self.pt_de_depart = (-1, -1)
        self.tir = (-1, - 1)
        self.tailles = (-1, -1)
        self.positions_bataille = set() 

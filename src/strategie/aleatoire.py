from strategie.base import StrategieBase
from bataille import Bataille, RetourDeTir
from grille import Grille, Point2D

class StrategieAleatoire(StrategieBase):
    def __init__(self):
        super().__init__()
        self.positions_deja_jouees = set()

    def agir(self, bataille: Bataille) -> Point2D:
        while True:
            g = Grille.generer_grille(tailles=bataille.tailles)
            for p in g.registre_des_positions.keys():
                if p not in self.positions_deja_jouees:
                    return p

    def analyser(self, bataille: Bataille, cible: Point2D, retour: RetourDeTir):
        self.positions_deja_jouees.add(cible)

    def reset(self):
        super().reset()
        self.positions_deja_jouees = set()
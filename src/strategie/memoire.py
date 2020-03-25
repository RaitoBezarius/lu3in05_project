from strategie.base import StrategieBase
from grille import Point2D
from bataille import Bataille, RetourDeTir


class StrategieAvecMemoire(StrategieBase):
    def __init__(self):
        super().__init__()
        self.cases_touchees_non_coulees = set()
        self.positions_deja_tirees = set()

    def analyser(self, bataille: Bataille, cible: Point2D, retour: RetourDeTir):
        self.positions_deja_tirees.add(cible)
        if retour == RetourDeTir.Touchee:
            self.cases_touchees_non_coulees.add(cible)

        if retour == RetourDeTir.Coulee:
            _, _, pos = bataille.obtenir_bateau(cible)
            self.cases_touchees_non_coulees -= pos

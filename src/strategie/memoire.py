from strategie.base import StrategieBase
from grille import Point2D
from bataille import Bataille, RetourDeTir


class StrategieAvecMemoire(StrategieBase):
    def __init__(self):
        super().__init__()
        self.cases_touchees_non_coulees = set()

    def analyser(self, bataille: Bataille, cible: Point2D, retour: RetourDeTir):
        if retour == RetourDeTir.Touchee:
            self.cases_touchees_non_coulees.add(cible)

        if retour == RetourDeTir.Coulee:
            self.cases_touchees_non_coulees -= bataille.obtenir_bateau(cible)

from bataille import Bataille
from grille import Point2D
from bataille import RetourDeTir

class StrategieBase:
    def __init__(self):
        pass

    def agir(self, bataille: Bataille) -> Point2D:
        raise NotImplementedError

    def analyser(self, bataille: Bataille, cible: Point2D, retour: RetourDeTir):
        raise NotImplementedError

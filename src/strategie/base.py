from bataille import Bataille, RetourDeTir
from grille import Point2D


class StrategieBase:
    def __init__(self):
        pass

    def agir(self, bataille: Bataille) -> Point2D:
        raise NotImplementedError

    def analyser(self, bataille: Bataille, cible: Point2D, retour: RetourDeTir):
        raise NotImplementedError
    
    def reset(self):
        pass
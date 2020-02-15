from grille import *

class Bataille:
    def __init__(self, grille: "Grille"):
        #On récupère la grille mais on ne la modifiera jamais
        self.GRILLE = grille

        #On enregistre dans un np.array si les cases ont été touchées ou non
        self._cases_touchees = np.zeros(grille.tailles)

        #On récupère en tant que constante le nombre de cases occupées
        self.NB_CASES_OCCUPEES = grille.nb_cases_occupees

        #On compte au fur et à mesure le nombre de cases occupées touchées
        #La condition de victoire de la bataille est:
        #   self._nb_cases_touchees == self.NB_CASES_OCCUPEES
        self._nb_cases_touchees = 0

        #On compte au fur et à mesure le score (i.e. le nombre de tirs effectués au cours de la bataille)
        self._score = 0

        #Un booleen indique si la victoire a été obtenue ou non
        #Si la grille fournie est vide, on considère qu'on a gagné d'office (ne faites pas cela svp)
        if self.NB_CASES_OCCUPEES != 0:
            self._victoire = False
        else:
            self._victoire = True

    def __repr__(self):
        """ La représentation souhaitée est la suivante:
                repr[x, 0] = -1
                repr[x, 1] = x
            On propose donc la fonction suivante:
                f(x,y) =(x + 1) * y - 1
            On vérifie que c'est bien ce qu'on souhaite"""
        return repr(((self.GRILLE.inner + 1) * self._cases_touchees) - 1)

    def __str__(self):
        n, m = grille.tailles
        string =  "<Bataille " + ("gagnée" if self._victoire else "en cours")
        return string + " {}X{} Score = {}>".format(n, m, self._score)

    @property
    def tailles(self) -> Point2D:
        return grille.tailles
    
    def est_dans_la_grille(self, pos: Point2D) -> bool:
        return grille.est_dans_la_grille(pos)

    def case_touchee(self, case:Point2D) -> bool:
        return self._cases_touchees[case[0], case[1]] == 1
    
    @property
    def victoire(self) -> bool:
        return self._victoire
    
    def affiche(self, **kwargs):
        cmap = ListedColormap(np.array([[0,0,0], \
                            [50,0,200], \
                            [30, 40, 23], \
                            [100, 0, 20], \
                            [20,200,10], \
                            [200,100, 100],\
                            [255,255,0]]) / 255)
        pyplot.matshow(((self.GRILLE.inner + 1) * self._cases_touchees), cmap = cmap, **kwargs)
    
    @property
    def nb_cases_touchees(self) -> int:
        return self._nb_cases_touchees

    def tirer(self, case: Point2D) -> int:
        """Cette fonction assume que le point case est inclus dans la grille et qu'il n'a jamais été touché par un tir
        Retourne 1 ssi il y a victoire 0 sinon"""
        if self._victoire:
            print("Vous avez déjà gagné!")
            return 1
        else:
            self._cases_touchees[case[0], case[1]] = 1
            self._score = self._score + 1
            if self.GRILLE.case(case) != TypeBateau.Vide:
                self._nb_cases_touchees = self._nb_cases_touchees + 1
                if self._nb_cases_touchees == self.NB_CASES_OCCUPEES:
                    self._victoire = True
                    print("Victoire! Score: {1}".format(self._score))
                    return 1
            else:
                return 0
    

grille = Grille.generer_grille(n = 100, m = 100)
while(grille.est_vide):
    grille = Grille.generer_grille(n = 100, m = 100)

b = Bataille(grille)
print(b)

for i in range(1000):
    case = tirer_point_uniformement(b.tailles)
    if not b.case_touchee(case):
        b.tirer(case)

print(repr(b))
grille.affiche()
b.affiche()
pyplot.show()
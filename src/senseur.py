import logging
from grille import Grille, TypeBateau, Point2D, tirer_point_uniformement
from typing import Optional
from itertools import product
import numpy as np
import random

logger = logging.getLogger()

# (Z_i | Y_i = 1) ~ B(p_s)
# (Z_i | Y_i = 0) = 0

# P(Z_i = 0) = 1 - pi_i p_s
# P(Z_i = 1) = pi_i p_s

# On a donc: P(Y_i = 1 | Z_i = 0) = 1 - (1 - pi_i)/(1 - pi_i p_s) <= pi_i
# on appelle ça pi_i^(nouveau).
# Puis, P(Y_k = 1 | Z_i = 0) = pi_k/(1 - pi_i p_s) >= pi_k
# on appelle ça pi_k^(nouveau).

# puis on prend argmax comme d'hab.

def generer_grille_objet_perdu(n: int = 10, m: int = 10):
    perdu = tirer_point_uniformement((n, m))
    inner = np.zeros((n, m), np.uint8)

    inner[perdu[0], perdu[1]] = TypeBateau.ObjetPerdu.value

    return Grille.depuis_tableau(inner)

class RechercheBayesienne:
    def __init__(self,
            grille: Grille,
            p_s: float = 0.5,
            distribution: Optional[np.array] = None):
        self.grille = grille
        self.prob_senseur = p_s
        self.pi = distribution or (np.ones(grille.tailles)/grille.nb_cases_totales)

    def detecter(self, p: Point2D) -> bool:
        if self.grille.case(p) == TypeBateau.ObjetPerdu:
            q = random.random()
            return random.random() <= self.prob_senseur
        else:
            return False

    def mettre_a_jour_pi(self, p: Point2D):
        pi_i = self.pi[p[0], p[1]]
        self.pi[p[0], p[1]] = 1 - (1 - pi_i) / (1 - pi_i * self.prob_senseur)
        n, m = self.grille.tailles
        for k, j in product(range(n), range(m)):
            pi_k = self.pi[k, j]
            self.pi[k, j] = pi_k / (1 - pi_i * self.prob_senseur)

    def chercher(self) -> int:
        logger.info('Début de la recherche bayésienne')
        detecte = False
        score = 0

        while not detecte:
            target = np.argmax(self.pi, axis=None)
            target_point = np.unravel_index(target, self.pi.shape)
            logger.info('Tentative de détection en {} (probabilité: {})'.format(target_point, self.pi[target_point[0], target_point[1]]))
            detecte = self.detecter(target_point)
            score += 1
            if not detecte:
                self.mettre_a_jour_pi(target_point)
                print(self.pi)

        logger.info('Détection réussite en {} coups.'.format(score))
        return score

# FIXME: créer des distributions usuelles.
# genre considérer que plus on va vers le centre, plus la probabilité augmente (i.e. une gaussienne 2D?)

def evaluer_performance(N, grille_kwargs=None, bayesian_kwargs=None) -> np.array:
    scores = np.zeros(N)

    if grille_kwargs is None:
        grille_kwargs = {}

    if bayesian_kwargs is None:
        bayesian_kwargs = {}

    for i in range(N):
        g = generer_grille_objet_perdu(**grille_kwargs)
        senseur = RechercheBayesienne(g, **bayesian_kwargs)
        scores[i] = senseur.chercher()
    return scores

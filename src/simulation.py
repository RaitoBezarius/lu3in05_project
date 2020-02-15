#!/usr/bin/env python3
from bataille import Bataille
from grille import Grille
import strategie
import argparse
import matplotlib.pyplot as plt
from matplotlib import animation


def charge_strategie(name):
    return getattr(strategie, name)


def cree_animation(fig, trames):
    return animation.ArtistAnimation(
        fig, trames, interval=250, blit=True, repeat_delay=1000
    )


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "strategie",
        help="Sélectionne une stratégie nommée qui se trouve dans strategie/__init__.py (exemple: monte_carlo)",
    )
    parser.add_argument(
        "-t",
        "--tailles",
        help="Taille du champ de bataille au format NxM (par défaut: 10x10)",
        default="10x10",
    )
    parser.add_argument(
        "-fv",
        "--facteur-vide",
        help="Détermine le facteur vide de la grille générée aléatoirement (defaut: environ 30 %% des cases sont vides)",
        default=0.3,
    )
    parser.add_argument(
        "-ag",
        "--animation-grille",
        help="Affiche à la fin du jeu la grille en temps réel",
        action="store_true",
    )
    parser.add_argument(
        "-ab",
        "--animation-bataille",
        help="Affiche à la fin du jeu la bataille en temps réel",
        action="store_true",
    )

    args = parser.parse_args()
    tailles = tuple(map(int, args.tailles.split("x")))
    grille = Grille.generer_grille(
        n=tailles[0], m=tailles[1], facteur_vide=args.facteur_vide
    )
    if args.animation_bataille and args.animation_grille:
        raise NotImplementedError("Race condition is occurring when those two options are enabled, try only one")
    print(repr(grille))
    bataille = Bataille(grille)
    strategie = charge_strategie(args.strategie)

    trames_bataille = []
    trames_grille = []
    fig = plt.figure()


    while not bataille.victoire:
        if args.animation_bataille:
            trames_bataille.append([bataille.affiche(fignum=0, animated=True)])
        if args.animation_grille:
            trames_grille.append([grille.affiche(fignum=0, animated=True)])
        cible = strategie.agir(bataille)
        strategie.analyser(bataille, cible, bataille.tirer(cible))

    if args.animation_bataille:
        ani_bataille = cree_animation(fig, trames_bataille + [trames_bataille[-1]] * 5)
        ani_bataille.save('bataille.mp4')

    if args.animation_grille:
        ani_grille = cree_animation(fig, trames_grille)
        ani_grille.save('grille.mp4')

    print(bataille.score)


if __name__ == "__main__":
    main()

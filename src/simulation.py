#!/usr/bin/env python3
from bataille import Bataille, BATAILLE_BOUNDS, BATAILLE_NORM, BATAILLE_CMAP
from grille import Grille
import strategie
import argparse
import matplotlib.pyplot as plt
from matplotlib import animation
import numpy as np


def charge_strategie(name):
    return getattr(strategie, name)

def animate_wrapper(ax, fig, cmap, norm, bounds, frames):
    cv0 = frames[0]
    im = ax.imshow(cv0, interpolation='nearest', norm=norm, cmap=cmap, origin='lower')
    cb = fig.colorbar(im, cmap=cmap, norm=norm,
        spacing='proportional',
        ticks=bounds,
        boundaries=bounds,
        format='%1i')

    tx = ax.set_title('Frame 0')
    vmax = np.max(bounds)
    vmin = np.min(bounds)

    im.set_clim(vmin, vmax)

    def animate(i):
        arr = frames[i]

        im.set_data(arr)
        tx.set_text('Frame {}'.format(i))

    return animate

def cree_animation(ax, fig, trames, cmap, norm, bounds):
    return animation.FuncAnimation(
        fig, animate_wrapper(ax, fig, cmap, norm, bounds, trames), interval=250, repeat_delay=1000,
        frames=len(trames)
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
        type=float,
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
    parser.add_argument(
        "-d",
        "--distribution",
        type=int,
        nargs='?',
        help="Genere la distribution, prends en argument le nombre de batailles a jouer",
        const=1000,
        default=1,
    )
    parser.add_argument(
        "-n",
        "--nom-courbe",
        nargs=1,
        help="Nom de la courbe de distribution, si demandee",
        default="",
    )

    args = parser.parse_args()
    tailles = tuple(map(int, args.tailles.split("x")))
    grille = Grille.generer_grille(
        tailles=tailles, facteur_vide=args.facteur_vide
    )
    if args.animation_bataille and args.animation_grille:
        raise NotImplementedError("Race condition is occurring when those two options are enabled, try only one")
    bataille = Bataille(grille)
    strategie = charge_strategie(args.strategie)

    if args.distribution > 0:
        nb_bat = args.distribution
    else:
        raise ValueError("The number of games have to be strictly positive")
    
    is_building_curve = args.distribution > 1

    if is_building_curve and (args.animation_bataille or args.animation_grille):
        raise NotImplementedError("It is not possible to produce animation while building a distribution curve.")

    if is_building_curve:
        X = np.arange(tailles[0] * tailles[1] + 1)
        pX = np.zeros(tailles[0] * tailles[1] + 1)

    trames_bataille = []
    trames_grille = []
    fig = plt.figure()
    ax = fig.add_subplot(111)

    if not is_building_curve:
        print(repr(grille))

    for i in range(args.distribution):
        while not bataille.victoire:
            if args.animation_bataille:
                trames_bataille.append(bataille.fog_of_war().copy())
            if args.animation_grille:
                trames_grille.append(grille.inner.copy())

            cible = strategie.agir(bataille)
            retour = bataille.tirer(cible)

            if not is_building_curve:
                print('Tir à {}, retour: {}'.format(cible, retour))

            strategie.analyser(bataille, cible, retour)

            if not is_building_curve:
                print(bataille._nb_cases_occupees, sum(bataille._nb_cases_touchees.values()))
        
        if is_building_curve:
            try:
                pX[bataille.score] += 1
            except:
                print("La strategie tire plusieurs fois sur une meme case")
                print(bataille.score)
                exit(1)

            grille = Grille.generer_grille(
                tailles=tailles, facteur_vide=args.facteur_vide
            )
            bataille = Bataille(grille)
            strategie.reset()

    if args.animation_bataille:
        trames_bataille.extend([bataille.fog_of_war().copy()] * 10)

    if args.animation_bataille:
        ani_bataille = cree_animation(ax, fig, trames_bataille, BATAILLE_CMAP, BATAILLE_NORM, BATAILLE_BOUNDS)
        ani_bataille.save('bataille.mp4')

    if args.animation_grille:
        ani_grille = cree_animation(ax, fig, trames_grille, None, None, None)
        ani_grille.save('grille.mp4')
    
    if is_building_curve:
        plt.plot(X, pX/np.sum(pX))
        plt.xlabel("Score")
        plt.ylabel("Fréquence")
        plt.title("Distribution du score pour la strategie " + args.strategie + " sur des batailles " + args.tailles)
        if args.nom_courbe == "":
            plt.savefig("_".join([args.strategie, str(args.distribution), args.tailles]) + ".png")
        else:
            plt.savefig(args.nom_courbe)
        plt.show()

    if not is_building_curve:
        print(bataille.score)


if __name__ == "__main__":
    main()

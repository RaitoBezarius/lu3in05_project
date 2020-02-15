from grille import TypeBateau, LONGUEUR_BATEAUX, Grille
from typing import List
from collections import Counter

def nb_facons_de_placer_un_bateau(type_: TypeBateau, n: int = 10, m: int = 10) -> int:
    length = LONGUEUR_BATEAUX[type_]

    if n < 0 or m < 0:
        return 0

    if n < length and m < length:
        return 0

    print('{},{},{}'.format(n,m,length))
    if length <= n < 2*length and m < length:
        r = n % length
        return (r + 1)*m

    if length <= m < 2*length and n < length:
        r = m % length
        return (r + 1)*n

    if n == m == length:
        return n*m

    # on le place en horizontal ou en vertical
    # u_(n + k, m + k) = (n + k) u_(n + k, m) + (m + k)u_(n, m + k)
    # u_(n,m) = n u_(n,m - l + 1) + m u_(n - l + 1, m)
    # u_(i,j) = 0 si i < l et j < l
    # u_(l + r, j) = (r + 1)j si r < l et j < l
    # u_(j,l + r) = (r + 1)j si r < l et j < l
    return n*nb_facons_de_placer_un_bateau(type_, n, m - length) + m*nb_facons_de_placer_un_bateau(type_, n - length, m)

def nb_facons_de_placer_un_bateau2(type_: TypeBateau, n: int = 10, m: int = 10) -> int:
    length = LONGUEUR_BATEAUX[type_]

    if n < length and m < length:
        return 0

    acc = 0

    if n > length:
        acc += 1

    if m > length:
        acc += 1

    return acc + nb_facons_de_placer_un_bateau2(type_, n - 1, m - 1)

def nb_facons_de_placer_des_bateaux(bateaux: Counter[TypeBateau], n: int = 10, m: int = 10) -> int:
    acc = 0

    for bateau, occ in bateaux:
        if occ == 0:
            continue

        length = LONGUEUR_BATEAUX[bateau]

        # horizontal
        if n > length:
            acc += 1

        # vertical
        if m > length:
            acc += 1

        c_bateaux = bateaux.copy()
        c_bateaux[bateau] -= 1
        # on place le reste
        acc += nb_facons_de_placer_des_bateaux(c_bateaux, n - 1, m -1)

    return acc

def genere_la_bonne_grille(cible: Grille):
    pass


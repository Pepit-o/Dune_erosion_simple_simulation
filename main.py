import random as rd
from typing import Union
import numpy as np
from matplotlib import pyplot as plt
from scipy.interpolate import make_interp_spline
import time

Matrice = list[list[str]]


def printmat(M: Matrice) -> None:  # Permet d'afficher une matrice comme un none-type au lieu d'un tableau de tableau
    for i in range(len(M)):
        for j in range(len(M[i])):
            print(str(M[i][j]), end=' ')
        print()


def pyramide(n: int) -> Matrice:  # Création de la dune
    M = [[' ' for _ in range(n)] for _ in range(n)]
    for i in range(-1, -len(M), -1):
        j = -(1 + i)
        while j != len(M):
            for k in range(j, len(M) - j):
                M[i][k] = '■'
            j += 1
    return M


def pyramide_racines(n: int, x: int) -> Matrice:
    M = [[' ' for _ in range(n)] for _ in range(n)]
    for i in range(-1, -len(M), -1):
        j = -(1 + i)
        while j != len(M):
            for k in range(j, len(M) - j):
                if k == len(M[0]) // 2 and abs(i) <= (len(M) // 2) - (x + 1):
                    # La racine primaire est au centre de
                    # la dune, le paramètre x limite sa hauteur
                    M[i][k] = '│'
                elif i % 4 == 0 and x - i <= k <= len(M) - (x + 1) + i:
                    # Les racines secondaires sont espacées de
                    # trois cases et limités en longueur par x
                    M[i][k] = '─'
                else:
                    M[i][k] = '■'
            j += 1
    return M


def check_zeros(M: Matrice, i: int, j: int) -> tuple:  # Calcul le degré d'exposition d'un grain de sable (nombre de
    # grain de sable autour de lui) et indique s'il est sur la face gauche de la dune (là d'où le vent arrive) ou non.
    compteur, left = 0, False
    if j != 0 and M[i][j - 1] == ' ':
        compteur += 1
        left = True
    if j != len(M[0]) and M[i][j + 1] == ' ':
        compteur += 1
    if M[i - 1][j] == ' ':
        compteur += 1
    return compteur, left


def check_zeros_2(M: Matrice, i: int, j: int) -> tuple:  # Prend en compte en plus les racines environnantes
    compteur, left, racines = 0, False, False
    if 3 < i < len(M) - 3 and j < len(M[0]) - 3:
        for k in range(i - 4, i + 4, 1):
            for l in range(j - 4, j + 4, 1):
                if M[k][l] == '─' or M[k][l] == '│':
                    racines = True
    if j != 0 and M[i][j - 1] == ' ':
        compteur += 1
        left = True
    if j != len(M[0]) and M[i][j + 1] == ' ':
        compteur += 1
    if M[i - 1][j] == ' ':
        compteur += 1
    return racines, compteur, left


def proba(M: Matrice, i: int, j: int, racines: int, compteur: int, left: bool) -> Union[float, int]:  # Calcul la
    # probabilité qu'un grain se déplace en fonction de sa position (i,j), de son degré d'exposition et des
    # potentielles racines proches
    h = (len(M) // 2) + 1
    a = (70 * len(M[0]) + 29 * h) / (100 * h * len(M[0]))
    b = 29 / (100 * len(M[0]))
    if compteur == 0:
        p = 0
    elif compteur == 1:
        if left:
            p = 0.3
        else:
            p = 0.01
    elif compteur == 2:
        if left:
            if racines:
                p = ((0.3 + a * i - b * j) / 99)
            else:
                p = ((0.3 + a * i - b * j) / 9)
        else:
            if racines:
                p = ((0.3 + a * i - b * j) / 33)
            else:
                p = ((0.3 + a * i - b * j) / 3)
    else:
        p = 1
    return p


def gravity(M: Matrice) -> Matrice:  # Comme son nom l'indique cette fonction fait redescendre les grains de sables
    # flottants dans les airs
    for i in range(-2, -len(M) + 1, -1):
        for j in range(len(M[0])):
            x = i
            while i < len(M) + 1 and M[i][j] == '■' and M[i + 1][j] == ' ':
                M[i][j] = ' '
                M[i + 1][j] = '■'
                i += 1
            i = x
    return M


def nombre_grain_de_sable(M: Matrice) -> int:
    nb_grains = 0
    for i in range(-1, (-len(M) // 2) - 1, -1):
        for j in range(len(M[0])):
            if M[i][j] == '■':
                nb_grains += 1
    print(str(nb_grains) + ' grains de sable')
    return nb_grains


def dune_simulation(n: int, tour: int, temps: float) -> Matrice:
    if tour < 0:
        raise Exception('Le nombre de tour doit être strictement positif')
    else:
        M = pyramide(n)
        printmat(M)
        n1, racines = nombre_grain_de_sable(M), False
        time.sleep(temps)
        compteur_de_tour = 1
        while tour > 0:
            Copy = [[' ' for _ in range(n)] for _ in range(n)]
            for i in range(len(M)):
                for j in range(len(M[0])):
                    Copy[i][j] = M[i][j]
            # On effectue les calculs de probabilité à partir de Copy et on réalise ensuite les
            # changements sur la matrice M. Lorsque l'on défini Copy = M on attribue la même adresse en mémoire à M et
            # Copy ce qui implique que chaque changement sur Copy sera répercuté sur M, on dit que Copy pointe vers M.
            # Pour éviter cela et avoir deux matrices indépendantes on construit Copy élément par élément.
            for i in range(len(M) - 1):
                for j in range(len(M[0]) - 1):
                    if M[i][j] != ' ':
                        compteur, left = check_zeros(Copy, i, j)
                        p = proba(Copy, i, j, racines, compteur, left)
                        if p >= rd.random():
                            if j != len(M[0]) and M[i][j + 1] == ' ' and M[i + 1][j + 1] == ' ':
                                M[i][j] = ' '
                                M[i + 1][j + 1] = '■'
                            elif j != len(M[0]) and M[i][j + 1] == ' ' and M[i + 1][j + 1] == '■':
                                M[i][j] = ' '
                                M[i][j + 1] = '■'
                            elif i != 0 and M[i - 1][j + 1] == ' ':
                                M[i][j] = ' '
                                M[i - 1][j + 1] = '■'
                            else:
                                M[i][j] = ' '
            gravity(M)
            printmat(M)
            print('Tour: ' + str(compteur_de_tour))
            nombre_grain_de_sable(M)
            time.sleep(temps)
            compteur_de_tour += 1
            tour -= 1
        printmat(M)
        Δn = n1 - nombre_grain_de_sable(M)
        print(str(Δn) + ' grains de sable de différence')
        return M


def image(n: int, tour: int):  # Affiche les profils de la simulation témoin
    A = pyramide(n)
    B = dune_simulation(n, tour, 0)
    M = [[[0, 0, 0] for _ in range(n)] for _ in range(n)]
    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j] == B[i][j] == ' ':
                M[i][j] = [255, 255, 255]
            elif A[i][j] == B[i][j] == '■' or A[i][j] == ' ' and B[i][j] == '■':
                M[i][j] = [0, 255, 255]
            elif A[i][j] == '■' and B[i][j] == ' ':
                M[i][j] = [0, 0, 0]
    img = np.array(M, dtype=np.uint32)[..., ::-1]
    plt.ylabel('Hauteur en cm')
    plt.xlabel('Distance en cm')
    plt.title('Noir: Avant soufflage │ Jaune: après soufflage')
    plt.imshow(img, interpolation='none')


def dune_simulation_racines(n: int, x: int, tour: int, temps: float) -> Matrice:
    if tour < 0:
        raise Exception('Le nombre de tour doit être strictement positif')
    else:
        M = pyramide_racines(n, x)
        printmat(M)
        n1 = nombre_grain_de_sable(M)
        time.sleep(temps)
        compteur_de_tour = 1
        while tour > 0:
            Copy = [[' ' for _ in range(n)] for _ in range(n)]
            for i in range(len(M)):
                for j in range(len(M[0])):
                    Copy[i][j] = M[i][j]
            for i in range(len(M) - 1):
                for j in range(len(M[0]) - 1):
                    if M[i][j] != ' ' and M[i][j] != '│' and M[i][j] != '─':
                        racines, compteur, left = check_zeros_2(Copy, i, j)
                        p = proba(Copy, i, j, racines, compteur, left)
                        if p >= rd.random():
                            if j != len(M[0]) and M[i][j + 1] == ' ' and M[i + 1][j + 1] == ' ':
                                M[i][j] = ' '
                                M[i + 1][j + 1] = '■'
                            elif j != len(M[0]) and M[i][j + 1] == ' ' and M[i + 1][j + 1] == '■':
                                M[i][j] = ' '
                                M[i][j + 1] = '■'
                            elif i != 0 and M[i - 1][j + 1] == ' ':
                                M[i][j] = ' '
                                M[i - 1][j + 1] = '■'
                            else:
                                M[i][j] = ' '
            gravity(M)
            printmat(M)
            print('Tour: ' + str(compteur_de_tour))
            nombre_grain_de_sable(M)
            time.sleep(temps)
            compteur_de_tour += 1
            tour -= 1
        printmat(M)
        Δn = n1 - nombre_grain_de_sable(M)
        print(str(Δn) + ' grains de sable de différence')
        return M


def image_bis(n: int, x: int, tour: int):  # Affiche les profils de la simulation test
    A = pyramide_racines(n, x)
    B = dune_simulation_racines(n, x, tour, 0)
    M = [[[0, 0, 0] for _ in range(n)] for _ in range(n)]
    for i in range(len(A)):
        for j in range(len(A[i])):
            if A[i][j] == B[i][j] == ' ':
                M[i][j] = [255, 255, 255]
            elif A[i][j] == B[i][j] == '■' or A[i][j] == ' ' and B[i][j] == '■':
                M[i][j] = [0, 255, 255]
            elif A[i][j] == '■' and B[i][j] == ' ':
                M[i][j] = [0, 0, 0]
            elif A[i][j] == '│' or A[i][j] == '─':
                M[i][j] = [40, 182, 9]
    img = np.array(M, dtype=np.uint32)[..., ::-1]
    plt.ylabel('Hauteur en cm')
    plt.xlabel('Distance en cm')
    plt.title('Noir: Avant soufflage │ Jaune: après soufflage')
    plt.imshow(img, interpolation='none')


h1_témoin = [0, 4.7, 8, 12, 8, 3.5, 0]
h2_témoin = [0, 3, 4.5, 6, 5, 2.5, 0]

h1_test_1 = [0, 4.3, 8, 10, 9.5, 4.3, 0]
h2_test_1 = [0, 3.2, 6, 7.5, 6.5, 4, 0]

h1_test_2 = [0, 3, 7, 12, 8, 3.5, 0]
h2_test_2 = [0, 3.2, 6.5, 7.4, 5.5, 3.5, 0]


def profil_lissé(hauteurs_à_vide: list, hauteurs_après_soufflage: list, d1: float, d2: float,
                 nom_expérience: str) -> None:
    x1 = np.linspace(0, d1, 7)  # Création de la liste des abscisses avec np.linspace pour avoir des points
    # équidistants comme dans l'expérience
    x1s = np.linspace(0, d1, 700)  # Le lissage requiert beaucoup de points pour être efficient d'où le découpage en 700
    x2 = np.linspace(0, d2, 7)
    x2s = np.linspace(0, d2, 700)
    model_1 = make_interp_spline(x1, hauteurs_à_vide)  # Fonction de lissage des points
    model_2 = make_interp_spline(x2, hauteurs_après_soufflage)
    y1 = model_1(x1s)
    y2 = model_2(x2s)
    plt.plot(x1s, y1, label='Dune avant soufflage')
    plt.plot(x2s, y2, label='Dune après soufflage (2 min)')
    plt.legend()
    plt.ylabel('Hauteur en cm')
    plt.xlabel('Distance en cm')
    plt.title('Profils des dunes ' + nom_expérience)
    plt.grid(True)
    plt.show()


start_time = time.time()  # A placer avant une fonction pour calculer son temps d'exécution

#dune_simulation(51, 10, 0.8)

print("--- %s seconds ---" % (time.time() - start_time))  # Calcul l'écart de temps avec start_time

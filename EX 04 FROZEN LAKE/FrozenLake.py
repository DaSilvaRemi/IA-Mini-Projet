import tkinter as tk
import random

import numpy as np
import copy

# voici les 4 touches utilisees pour les deplacements  gauche/haut/droite/bas

Keys = ['q', 'z', 'd', 's']

#################################################################################
#
#   Donnees de partie
#
#################################################################################


Data = [[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0],
        [0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0],
        [0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 8]]

GInit = np.array(Data, dtype=np.int8)
GInit = np.flip(GInit, 0).transpose()

tab_possible_action = (0, 2, 4, 6)

nb_de_fois_action_a_depuis_A = []
nb_de_fois_action_a_depuis_A_vers_B = []
somme_recompense_action_a_depuis_A_vers_B = []
proba_deplacement_action_a_depuis_A_vers_B = []
moyenne_recompense_action_a_depuis_A_vers_B = []

LARGEUR = 13
HAUTEUR = 17

#################################################################################
#
#   creation de la fenetre principale  - NE PAS TOUCHER
#
#################################################################################


L = 20  # largeur d'une case du jeu en pixel
largeurPix = LARGEUR * L
hauteurPix = (HAUTEUR + 1) * L

Window = tk.Tk()
# taille de la fenetre
Window.geometry(str(largeurPix) + "x" + str(hauteurPix + 3))
Window.title("Frozen Lake")

# gestion du clavier

LastKey = '0'


def keydown(e):
    global LastKey
    if hasattr(e, 'char') and e.char in Keys:
        LastKey = e.char


# creation de la frame principale stockant toutes les pages

F = tk.Frame(Window)
F.bind("<KeyPress>", keydown)
F.pack(side="top", fill="both", expand=True)
F.grid_rowconfigure(0, weight=1)
F.grid_columnconfigure(0, weight=1)
F.focus_set()

# gestion des pages

ListePages = {}
PageActive = 0


def CreerUnePage(id):
    Frame = tk.Frame(F)
    ListePages[id] = Frame
    Frame.grid(row=0, column=0, sticky="nsew")
    return Frame


def AfficherPage(id):
    global PageActive
    PageActive = id
    ListePages[id].tkraise()


Frame0 = CreerUnePage(0)

canvas = tk.Canvas(Frame0, width=largeurPix, height=hauteurPix, bg="black")
canvas.place(x=0, y=0)


#   Dessine la grille de jeu - ne pas toucher


def Affiche(Game):
    canvas.delete("all")
    H = canvas.winfo_height() - 2

    def MSG(coul, txt):

        canvas.create_rectangle(0, 0, largeurPix, 20, fill="black")
        canvas.create_text(largeurPix // 2, 10,
                           font='Helvetica 12 bold', fill=coul, text=txt)

    def DrawCase(x, y, coul):
        x *= L
        y *= L
        canvas.create_rectangle(x, H - y, x + L, H - y - L, fill=coul)

    # dessin du decors

    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            if Game.Grille[x, y] == 0:
                DrawCase(x, y, "cyan")
            if Game.Grille[x, y] == 1:
                DrawCase(x, y, "blue")
            if Game.Grille[x, y] == 8:
                DrawCase(x, y, "pink")

    DrawCase(Game.PlayerPos[0], Game.PlayerPos[1], "yellow")

    MSG("yellow", str(Game.Score))


################################################################################
#
#                          Gestionnaire de partie
#
################################################################################


class Game:

    def __init__(self):
        self.Grille = GInit
        self.Score = 0
        self.ResetPlayerPos()

    def ResetPlayerPos(self):
        self.PlayerPos = [0, HAUTEUR - 1]

    def Doo(self, action):
        #  annulation des deplacements vers un mur
        if self.PlayerPos[0] == 0 and action == 0:
            return 0
        if self.PlayerPos[0] == LARGEUR - 1 and action == 2:
            return 0

        if self.PlayerPos[1] == 0 and action == 3:
            return 0
        if self.PlayerPos[1] == HAUTEUR - 1 and action == 1:
            return 0

        # 0 ; left, 2: up, 4: right, 6: down
        P = [0] * 8
        v = 100
        P[(action * 2 - 1) % 8] = v
        P[action * 2] = v
        P[(action * 2 + 1) % 8] = v

        # plus on se rapproche de l'objectif, plus ca glisse
        for i in range(8):
            P[i] += LARGEUR - self.PlayerPos[0] + (HAUTEUR - self.PlayerPos[1])

        # gestion des murs
        if self.PlayerPos[0] == 0:
            P[7] = P[0] = P[1] = 0  # mur gauche
        if self.PlayerPos[0] == LARGEUR - 1:
            P[3] = P[4] = P[5] = 0  # mur droit

        if self.PlayerPos[1] == 0:
            P[5] = P[6] = P[7] = 0  # mur bas
        if self.PlayerPos[1] == HAUTEUR - 1:
            P[1] = P[2] = P[3] = 0  # mur haut

        # tirage alea
        totProb = sum(P)
        rd = random.randrange(0, totProb) + 1
        choix = 0
        while P[choix] < rd:
            rd -= P[choix]
            choix += 1

        # traduction 0-7 => deplacement
        if choix in [7, 0, 1]:
            self.PlayerPos[0] -= 1
        if choix in [3, 4, 5]:
            self.PlayerPos[0] += 1
        if choix in [1, 2, 3]:
            self.PlayerPos[1] += 1
        if choix in [5, 6, 7]:
            self.PlayerPos[1] -= 1

        # gestion des collisions

        xP, yP = self.PlayerPos
        if self.Grille[xP][yP] == 1:  # DEAD
            self.ResetPlayerPos()
            return -100

        if self.Grille[xP][yP] == 8:  # WIN
            self.ResetPlayerPos()
            return 100

        return 0

    def Do(self, action):
        reward = self.Doo(action)
        self.Score += reward
        return reward


###########################################################
#
#   decouvrez le jeu en jouant au clavier
#
###########################################################

G = Game()


def JeuClavier():
    F.focus_force()
    global LastKey

    """
    r = 0  # reward
    if LastKey != '0':
        if LastKey == Keys[0]: G.Do(0)
        if LastKey == Keys[1]: G.Do(1)
        if LastKey == Keys[2]: G.Do(2)
        if LastKey == Keys[3]: G.Do(3)
    """

    JeuIA()

    Affiche(G)
    """LastKey = '0'"""
    Window.after(500, JeuClavier)


def JeuIA():
    SimulateGame()
    G.Do(random.randrange(0, 4))


###########################################################
#
#  simulateur de partie aleatoire
#
###########################################################

def ListeIsEqual(l1: list, l2: list) -> bool:
    if len(l1) != len(l2):
        return False

    for i in range(0, len(l1)):
        if l1[i] != l2[i]:
            return False
    return True


def Update_nb_de_fois_action_a_depuis_A(pos_player_A: list, action: int) -> None:
    global nb_de_fois_action_a_depuis_A
    # Liste vide donc on lui ajoute directement la valeur

    # checker dans la liste si on n'a pas déjà cette enchaînement position + action
    for i in range(0, len(nb_de_fois_action_a_depuis_A)):
        if nb_de_fois_action_a_depuis_A[i][0] == pos_player_A and nb_de_fois_action_a_depuis_A[i][1] == action:
            # On a ici trouvé une sous-liste contenant la position et l'action.
            # On ajoute donc 1 au compteur !
            nb_de_fois_action_a_depuis_A[i][2] += 1
            return None

    # Arriver ici signifie ne pas avoir trouvé d'occurence de sous-liste contenant position + action
    # On crée alors une nouvelle liste, que l'on append à la principale
    nb_de_fois_action_a_depuis_A.append([pos_player_A.copy(), action, 1])
    return None


def Update_nb_de_fois_action_a_depuis_A_vers_B(pos_player_A: list, action: int, pos_player_B: list) -> None:
    global nb_de_fois_action_a_depuis_A_vers_B

    # Pour chaque Action stockée dans la liste d'action
    for an_action_a_depuis_a_vers_b in nb_de_fois_action_a_depuis_A_vers_B:
        # Dissociation de la liste en plusieurs variables
        pos_player_A_actuel, pos_player_B_actuel, action_actuel, nb_action_depuis_A_vers_B = an_action_a_depuis_a_vers_b

        # Test des positions A et B avec l'action réalisé afin d'atteindre la position B à partir de  la position A
        if ListeIsEqual(pos_player_A, pos_player_A_actuel) and action == action_actuel and ListeIsEqual(pos_player_B,
                                                                                                        pos_player_B_actuel):
            nb_action_depuis_A_vers_B += 1
            return None

    nb_de_fois_action_a_depuis_A_vers_B.append([pos_player_A.copy(), pos_player_B.copy(), action, 1])


def Update_somme_recompense_action_a_depuis_A_vers_B(pos_player_A: list, action: int, pos_player_B: list,
                                                     recompense: int) -> None:
    global somme_recompense_action_a_depuis_A_vers_B
    # Pour chaque Somme stockée dans la liste de somme
    for an_somme_recompense_action_a_depuis_A_vers_B in somme_recompense_action_a_depuis_A_vers_B:

        # Dissociation de la liste en plusieurs variables
        pos_player_A_actuel, pos_player_B_actuel, action_actuel, somme_recompense = an_somme_recompense_action_a_depuis_A_vers_B

        # Test des positions A et B avec l'action réalisé afin d'atteindre la position B à partir de  la position A
        if ListeIsEqual(pos_player_A, pos_player_A_actuel) and ListeIsEqual(pos_player_B,
                                                                            pos_player_B_actuel) and action == action_actuel:
            somme_recompense += recompense
            return None

    somme_recompense_action_a_depuis_A_vers_B.append([pos_player_A.copy(), pos_player_B.copy(), action, recompense])


def Set_proba_deplacement_action_a_depuis_A_vers_B() -> None:
    global nb_de_fois_action_a_depuis_A, nb_de_fois_action_a_depuis_A_vers_B, proba_deplacement_action_a_depuis_A_vers_B
    """
    proba_deplacement_action_a_depuis_A_vers_B
        =
    nb_de_fois_action_a_depuis_A_vers_B
        /
    nb_de_fois_action_a_depuis_A
    """

    for i in range(0, len(nb_de_fois_action_a_depuis_A_vers_B)):
        ptA, ptB, action, nb_occ = nb_de_fois_action_a_depuis_A_vers_B[i]
        ptA_x = ptA[0]
        ptA_y = ptA[1]

        somme_valeur_autour_case = 0

        # Sommes des transitions depuis une case C vers les cases voisines

        for j in range(0, len(nb_de_fois_action_a_depuis_A)):
            ptA_bis, action_bis, nb_occ_bis = nb_de_fois_action_a_depuis_A[j]

            if ListeIsEqual(ptA_bis, ptA):
                somme_valeur_autour_case += nb_occ_bis

        # Pourcentage p_barre d'aller de A vers B
        pourcentage = nb_occ / somme_valeur_autour_case if somme_valeur_autour_case != 0 else 0

        proba_deplacement_action_a_depuis_A_vers_B.append([ptA, ptB, action, pourcentage])

    """
        # for j in range(0, len(nb_de_fois_action_a_depuis_A)):
        #     ptA_bis = nb_de_fois_action_a_depuis_A[j][0]
        #     ptA_bis_x = ptA_bis[0]
        #     ptA_bis_y = ptA_bis[1]
        #     if (abs(ptA_bis_x - ptA_x) <= 1) and (abs(ptA_bis_y - ptA_y) <= 1):
        #         # Ici on a trouvé une case qui est dans l'étoile autour de la case actuelle
    """

    return


def Set_moyenne_recompense_action_a_depuis_A_vers_B() -> None:
    global moyenne_recompense_action_a_depuis_A_vers_B, somme_recompense_action_a_depuis_A_vers_B, nb_de_fois_action_a_depuis_A_vers_B

    # Pour chaque action on récupère depuis A vers B on récupère les différentes variables
    for an_action_a_depuis_a_vers_b in nb_de_fois_action_a_depuis_A_vers_B:
        pos_player_A_actuel, pos_player_B_actuel, action_actuel, nb_action_depuis_A_vers_B = an_action_a_depuis_a_vers_b

        # Pour chaque somme de récompense pour une action on récupère depuis A vers B on récupère les différentes variables
        for an_somme_recompense_action_a_depuis_A_vers_B in somme_recompense_action_a_depuis_A_vers_B:
            pos_player_A_actuel_bis, pos_player_B_actuel_bis, action_actuel_bis, somme_recompense = an_somme_recompense_action_a_depuis_A_vers_B

            # Si les positions sont les mêmes et l'action est la même dans ce cas on ajoute la moyenne de la somme / nb actions à la liste
            if ListeIsEqual(pos_player_A_actuel, pos_player_A_actuel_bis) and ListeIsEqual(pos_player_B_actuel,
                                                                                           pos_player_B_actuel_bis) and action_actuel == action_actuel_bis:
                moyenne_recompense = somme_recompense / nb_action_depuis_A_vers_B if nb_action_depuis_A_vers_B else 0
                moyenne_recompense_action_a_depuis_A_vers_B.append(
                    [pos_player_A_actuel, pos_player_B_actuel, action_actuel, moyenne_recompense])
                break


def SimulateGame():  # il n'y a pas de notion de "fin de partie"
    Q = np.array([0, -1, 0, 1, 0], dtype=np.int32)

    G = Game()
    reward = 0
    for i in range(100):
        # Randomisation des actions à faire
        action = random.randrange(0, 4)
        real_action = tab_possible_action[action]

        # Position avant mouvement
        pos_player_A = G.PlayerPos

        # On fait faire une action au joueur
        r = G.Do(action)

        # Position après mouvement
        pos_player_B = G.PlayerPos

        # Ajout du reward actuel à celui global
        reward += r

        # Update des listes
        Update_nb_de_fois_action_a_depuis_A(pos_player_A, real_action)
        Update_nb_de_fois_action_a_depuis_A_vers_B(pos_player_A, real_action, pos_player_B)
        Update_somme_recompense_action_a_depuis_A_vers_B(pos_player_A, real_action, pos_player_B, r)

    # breakpoint()
    Set_proba_deplacement_action_a_depuis_A_vers_B()
    Set_moyenne_recompense_action_a_depuis_A_vers_B()
    return reward


#####################################################################################
#
#  Mise en place de l'interface - ne pas toucher


AfficherPage(0)
Window.after(500, JeuClavier)
Window.mainloop()

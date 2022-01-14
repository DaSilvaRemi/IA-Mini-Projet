from math import gamma
import tkinter as tk
import random
import numpy as np
import copy

# voici les 4 touches utilisées pour les déplacements  gauche/haut/droite/bas

Keys = ['q', 'z', 'd', 's']

#################################################################################
#
#   Données de partie
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

LARGEUR = 13
HAUTEUR = 17
ACTIONS = 4
GAMMA = 0.9

nb_de_fois_action_a_depuis_A = np.zeros(
    (LARGEUR, HAUTEUR, ACTIONS), dtype=float)
nb_de_fois_action_a_depuis_A_vers_B = np.zeros(
    (LARGEUR, HAUTEUR, ACTIONS, LARGEUR, HAUTEUR), dtype=float)
somme_recompense_action_a_depuis_A_vers_B = np.zeros(
    (LARGEUR, HAUTEUR, ACTIONS, LARGEUR, HAUTEUR), dtype=float)


#################################################################################
#
#   création de la fenetre principale  - NE PAS TOUCHER
#
#################################################################################


L = 20  # largeur d'une case du jeu en pixel
largeurPix = LARGEUR * L
hauteurPix = (HAUTEUR+1) * L


Window = tk.Tk()
Window.geometry(str(largeurPix)+"x"+str(hauteurPix+3))   # taille de la fenetre
Window.title("Frozen Lake")

# gestion du clavier

LastKey = '0'


def keydown(e):
    global LastKey
    if hasattr(e, 'char') and e.char in Keys:
        LastKey = e.char


# création de la frame principale stockant toutes les pages

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
    H = canvas.winfo_height()-2

    def MSG(coul, txt):

        canvas.create_rectangle(0, 0, largeurPix, 20, fill="black")
        canvas.create_text(largeurPix//2, 10,
                           font='Helvetica 12 bold', fill=coul, text=txt)

    def DrawCase(x, y, coul):
        x *= L
        y *= L
        canvas.create_rectangle(x, H-y, x+L, H-y-L, fill=coul)

    # dessin du décors

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
        self.PlayerPos = [0, HAUTEUR-1]

    def Doo(self, action):
        #  annulation des déplacements vers un mur
        if self.PlayerPos[0] == 0 and action == 0:
            return -1
        if self.PlayerPos[0] == LARGEUR-1 and action == 2:
            return -1

        if self.PlayerPos[1] == 0 and action == 3:
            return -1
        if self.PlayerPos[1] == HAUTEUR-1 and action == 1:
            return -1

        # 0 ; left, 2: up, 4: right, 6: down
        P = [0] * 8
        v = 100
        P[(action * 2 - 1) % 8] = v
        P[action * 2] = v
        P[(action * 2 + 1) % 8] = v

        # plus on se rapproche de l'objectif, plus ca glisse
        for i in range(8):
            P[i] += LARGEUR-self.PlayerPos[0] + (HAUTEUR-self.PlayerPos[1])

        # gestion des murs
        if self.PlayerPos[0] == 0:
            P[7] = P[0] = P[1] = 0  # mur gauche
        if self.PlayerPos[0] == LARGEUR-1:
            P[3] = P[4] = P[5] = 0  # mur droit

        if self.PlayerPos[1] == 0:
            P[5] = P[6] = P[7] = 0  # mur bas
        if self.PlayerPos[1] == HAUTEUR-1:
            P[1] = P[2] = P[3] = 0  # mur haut

        # tirage aléa
        totProb = sum(P)
        rd = random.randrange(0, totProb)+1
        choix = 0
        while P[choix] < rd:
            rd -= P[choix]
            choix += 1

        # traduction 0-7 => déplacement
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
        if self.Grille[xP][yP] == 1:   # DEAD
            self.ResetPlayerPos()
            return -100

        if self.Grille[xP][yP] == 8:   # WIN
            self.ResetPlayerPos()
            return 100

        return -1

    def Do(self, action):
        reward = self.Doo(action)
        self.Score += reward
        return reward


###########################################################
#
#   découvrez le jeu en jouant au clavier
#
###########################################################

G = Game()


def JeuClavier():
    F.focus_force()

    global LastKey

    r = 0  # reward
    if LastKey != '0':
        if LastKey == Keys[0]:
            G.Do(0)
        if LastKey == Keys[1]:
            G.Do(1)
        if LastKey == Keys[2]:
            G.Do(2)
        if LastKey == Keys[3]:
            G.Do(3)

    Affiche(G)
    LastKey = '0'
    Window.after(500, JeuClavier)


def JeuIA():
    pos_x_player, pos_y_player = G.PlayerPos

    action = np.argmax([QEA[pos_x_player, pos_y_player, index_action]
                       for index_action in range(0, ACTIONS)])

    G.Do(action)
    Affiche(G)
    if abs(G.Score < 300):
        Window.after(500, JeuIA)

###########################################################
#
#  simulateur de partie aléatoire
#
###########################################################


def SimulGame(nb_simulations):   # il n y a pas de notion de "fin de partie"
    global nb_de_fois_action_a_depuis_A, nb_de_fois_action_a_depuis_A_vers_B, somme_recompense_action_a_depuis_A_vers_B

    G = Game()
    for i in range(nb_simulations):
        # Etat initial
        pos_x_player_A, pos_y_player_A = G.PlayerPos

        # Action choisi
        action = random.randrange(0, 4)

        # Récompense
        r = G.Do(action)

        # Etat Prime e'
        pos_x_player_B, pos_y_player_B = G.PlayerPos

        # Nb de fois qu'une action à été réalisé depuis un état E
        nb_de_fois_action_a_depuis_A[
            pos_x_player_A,
            pos_y_player_A,
            action
        ] += 1

        # Nb de fois qu'une transition à été réalisé entre un état E et un état E prime
        nb_de_fois_action_a_depuis_A_vers_B[
            pos_x_player_A,
            pos_y_player_A,
            action,
            pos_x_player_B,
            pos_y_player_B
        ] += 1

        # Somme des récompenses qu'une action à été réalisé depuis un état E vers un état E prime
        somme_recompense_action_a_depuis_A_vers_B[
            pos_x_player_A,
            pos_y_player_A,
            action,
            pos_x_player_B,
            pos_y_player_B
        ] += r

    # Application du broadcasting numpy afin de pouvoir additionner les matrices
    nb_de_fois_action_a_depuis_A_broadcast = nb_de_fois_action_a_depuis_A[:, :, :, np.newaxis, np.newaxis]

    # Probabilité de déplacement d'un état E vers un état Eprime en réalisant une action
    proba_deplacement_action_a_depuis_A_vers_B = np.divide(
        nb_de_fois_action_a_depuis_A_vers_B,
        nb_de_fois_action_a_depuis_A_broadcast,
        out=np.zeros_like
        (
            nb_de_fois_action_a_depuis_A_vers_B,
            dtype=float
        ),
        where=nb_de_fois_action_a_depuis_A_broadcast != 0)

    moy_recompense_action_a_depuis_A_vers_B = np.divide(
        somme_recompense_action_a_depuis_A_vers_B,
        nb_de_fois_action_a_depuis_A_vers_B,
        out=np.zeros_like
        (
            somme_recompense_action_a_depuis_A_vers_B,
            dtype=float
        ),
        where=nb_de_fois_action_a_depuis_A_vers_B != 0)

    Q = Q_OLD = np.zeros((LARGEUR, HAUTEUR, ACTIONS), dtype=float)

    variationinstable = True
    while(variationinstable):
        Q = np.zeros((LARGEUR, HAUTEUR, ACTIONS), dtype=float)

        # PosX, PosY for E, E' for a
        for pos_x_A in range(0, LARGEUR):
            for pos_y_A in range(0, HAUTEUR):
                for a in range(0, ACTIONS):
                    for pos_x_B in range(0, LARGEUR):
                        for pos_y_B in range(0, HAUTEUR):
                            MAX_Q_OLD = max(
                                [Q_OLD[pos_x_B, pos_y_B, a_prime] for a_prime in range(0, ACTIONS)]
                            )

                            SOMME_MOY = (
                                moy_recompense_action_a_depuis_A_vers_B[pos_x_A, pos_y_A, a, pos_x_B, pos_y_B] + GAMMA * MAX_Q_OLD
                            )

                            Q[pos_x_A, pos_y_A, a] += proba_deplacement_action_a_depuis_A_vers_B[pos_x_A,pos_y_A, a, pos_x_B, pos_y_B] * SOMME_MOY

        variationinstable = np.any(np.abs(Q - Q_OLD) > 0.01)
        Q_OLD = Q.copy()

    return Q


#####################################################################################
#
#  Mise en place de l'interface - ne pas toucher

QEA = SimulGame(100000)
AfficherPage(0)
Window.after(500, JeuIA)
Window.mainloop()

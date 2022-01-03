import tkinter as tk
import random
import numpy as np
import copy
import random
import time

#################################################################################
#
#   Données de partie

Data = [[1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]]

GInit = np.array(Data, dtype=np.int8)
GInit = np.flip(GInit, 0).transpose()

LARGEUR = 13
HAUTEUR = 17


# container pour passer efficacement toutes les données de la partie

class Game:
    def __init__(self, Grille, PlayerX, PlayerY, Score=0):
        self.PlayerX = PlayerX
        self.PlayerY = PlayerY
        self.Score = Score
        self.Grille = Grille

    def copy(self):
        return copy.deepcopy(self)


GameInit = Game(GInit, 3, 5)

##############################################################
#
#   création de la fenetre principale  - NE PAS TOUCHER

L = 20  # largeur d'une case du jeu en pixel
largeurPix = LARGEUR * L
hauteurPix = HAUTEUR * L

Window = tk.Tk()
Window.geometry(str(largeurPix) + "x" + str(hauteurPix))  # taille de la fenetre
Window.title("TRON")

# création de la frame principale stockant toutes les pages

F = tk.Frame(Window)
F.pack(side="top", fill="both", expand=True)
F.grid_rowconfigure(0, weight=1)
F.grid_columnconfigure(0, weight=1)

# gestion des différentes pages

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
    H = canvas.winfo_height()

    def DrawCase(x, y, coul):
        x *= L
        y *= L
        canvas.create_rectangle(x, H - y, x + L, H - y - L, fill=coul)

    # dessin des murs

    for x in range(LARGEUR):
        for y in range(HAUTEUR):
            if Game.Grille[x, y] == 1: DrawCase(x, y, "gray")
            if Game.Grille[x, y] == 2: DrawCase(x, y, "cyan")

    # dessin de la moto
    DrawCase(Game.PlayerX, Game.PlayerY, "red")


def AfficheScore(Game):
    info = "SCORE : " + str(Game.Score)
    canvas.create_text(80, 13, font='Helvetica 12 bold', fill="yellow", text=info)


###########################################################
#
# gestion du joueur IA

# VOTRE CODE ICI

def DirectionsPossibles(Game) -> list:
    L = []
    x, y = Game.PlayerX, Game.PlayerY

    val1 = Game.Grille[x - 1][y]
    val2 = Game.Grille[x + 1][y]
    val3 = Game.Grille[x][y - 1]
    val4 = Game.Grille[x][y + 1]

    if (val1 == 0):
        L.append((-1, 0))

    if (val2 == 0):
        L.append((1, 0))

    if (val3 == 0):
        L.append((0, -1))

    if (val4 == 0):
        L.append((0, 1))
    return L


def SimulationPartie(Game: Game) -> int:
    while (True):
        L = DirectionsPossibles(Game)
        if len(L) == 0:
            return Game.Score

        choix = random.randrange(len(L))

        x, y = Game.PlayerX, Game.PlayerY
        Game.Grille[x, y] = 2  # laisse la trace de la moto

        x += L[choix][0]
        y += L[choix][1]

        Game.PlayerX = x  # valide le déplacement
        Game.PlayerY = y  # valide le déplacement
        Game.Score += 1


###########################################################
#
# simulation en parallèle des parties


# Liste des directions :
# 0 : sur place   1: à gauche  2 : en haut   3: à droite    4: en bas

dx = np.array([0, -1, 0,  1,  0],dtype=np.int32)
dy = np.array([0,  0, 1,  0, -1],dtype=np.int32)

# scores associés à chaque déplacement
ds = np.array([0,  1,  1,  1,  1],dtype=np.int32)

def Simulate(Game, nb):

    # on copie les datas de départ pour créer plusieurs parties en //
    G      = np.tile(Game.Grille,(nb,1,1))
    X      = np.tile(Game.PlayerX,nb)
    Y      = np.tile(Game.PlayerY,nb)
    S      = np.tile(Game.Score,nb)
    I      = np.arange(nb)  # 0,1,2,3,4,5...
    boucle = True

    # VOTRE CODE ICI

    while(boucle) :
        LPossibles = np.zeros((nb, 4), dtype=np.int32)
        Indices = np.zeros(nb, dtype=np.int32)

        VGauche = (G[I, X - 1, Y] == 0) * 1
        VDroite = (G[I, X + 1, Y] == 0) * 1
        VHaut = (G[I, X, Y + 1] == 0) * 1
        VBas = (G[I, X, Y - 1] == 0) * 1

        LPossibles[I, Indices] = VGauche * 1
        Indices += VGauche
        LPossibles[I, Indices] = VHaut * 2
        Indices += VHaut
        LPossibles[I, Indices] = VDroite * 3
        Indices += VDroite
        LPossibles[I, Indices] = VBas * 4
        Indices += VBas

        Indices[Indices == 0] = 1
        R = np.random.randint(Indices)

        # marque le passage de la moto
        G[I, X, Y] = 2

        # Direction : 2 = vers le haut
        Choix = LPossibles[I, R]

        # DEPLACEMENT
        DX = dx[Choix]
        DY = dy[Choix]
        X += DX
        Y += DY

        if np.mean(ds[Choix]) == 0:
            break

        S += ds[Choix]

    return S.sum()


def MonteCarlo(Game: Game, nombreParties) -> int:
    Total = 0
    for i in range(0, nombreParties):
        Game2 = Game.copy()
        Total += SimulationPartie(Game2)
    return Total


def DeterminerCoupPlusPrometteur(Game, L) -> tuple:
    Tstart = time.time()
    ScorePlusPrometteur = 0
    CoupPlusPrometteur = ()

    for offset in L:
        Game2 = Game.copy()
        Game2.PlayerX += offset[0]
        Game2.PlayerY += offset[1]
        tmpScorePlusPrometteur = Simulate(Game2, 30000)

        if (tmpScorePlusPrometteur > ScorePlusPrometteur):
            CoupPlusPrometteur = offset
            ScorePlusPrometteur = tmpScorePlusPrometteur
    print(time.time() - Tstart)
    return CoupPlusPrometteur


def Play(Game):
    x, y = Game.PlayerX, Game.PlayerY
    print(x, y)

    Game.Grille[x, y] = 2  # laisse la trace de la moto

    LPlacementsPossible = DirectionsPossibles(Game)
    if len(LPlacementsPossible) == 0:
        # aucun déplacement possible
        return True  # partie terminée
    CoupsPlusPrometteur = DeterminerCoupPlusPrometteur(Game, LPlacementsPossible)

    x += CoupsPlusPrometteur[0]
    y += CoupsPlusPrometteur[1]

    v = Game.Grille[x, y]

    if v > 0:
        # collision détectée
        return True  # partie terminée
    else:
        Game.PlayerX = x  # valide le déplacement
        Game.PlayerY = y  # valide le déplacement
        Game.Score += 1
        return False  # la partie continue


################################################################################

CurrentGame = GameInit.copy()


def Partie():
    PartieTermine = Play(CurrentGame)

    if not PartieTermine:
        Affiche(CurrentGame)
        # rappelle la fonction Partie() dans 30ms
        # entre temps laisse l'OS réafficher l'interface
        Window.after(100, Partie)
    else:
        AfficheScore(CurrentGame)


#####################################################################################
#
#  Mise en place de l'interface - ne pas toucher

AfficherPage(0)
Window.after(100, Partie)
Window.mainloop()

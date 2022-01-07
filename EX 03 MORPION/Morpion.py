import tkinter as tk
from tkinter import messagebox
import random
import numpy as np

###############################################################################
# création de la fenetre principale  - ne pas toucher

LARG = 300
HAUT = 300

Window = tk.Tk()
Window.geometry(str(LARG) + "x" + str(HAUT))  # taille de la fenetre
Window.title("ESIEE - Morpion")

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

canvas = tk.Canvas(Frame0, width=LARG, height=HAUT, bg="black")
canvas.place(x=0, y=0)

#################################################################################
#
#  Parametres du jeu

Grille = [[0, 0, 0],
          [0, 0, 0],
          [0, 0, 0]]  # attention les lignes représentent les colonnes de la grille

Grille = np.array(Grille)
Grille = Grille.transpose()  # pour avoir x,y

ScoreIA = 0
ScorePlayer = 0
DebutPartie = True
turn = "IA"


###############################################################################
#
# gestion du joueur humain et de l'IA
# VOTRE CODE ICI
def EndGame(gagnant: int) -> None:
    global ScorePlayer, ScoreIA

    if gagnant == 1:
        ScorePlayer += 1
    elif gagnant == 2:
        ScoreIA += 1

    Dessine(True, gagnant)


def CaseIsEmpty(x: int, y: int) -> bool:
    return Grille[x, y] == 0


def GetCaseDisponible() -> list:
    CaseDisponible = []

    for x in range(0, len(Grille)):
        for y in range(0, len(Grille)):
            if CaseIsEmpty(x, y):
                CaseDisponible.append((x, y))
    return CaseDisponible


def ConfigIsGagnante(L: list, v: int) -> int:
    return L.count(v) == 3


def HaveWin(valCasePlayer: int = 1) -> bool:
    """
    :param valCasePlayer:
    :return:
    """
    col = []
    diagonaleLeft = []
    diagonaleRight = []

    haveWin = False

    for y in range(0, len(Grille)):
        for x in range(0, len(Grille)):
            ligne = Grille[x].tolist()
            diagonaleLeft.append(Grille[x][x])
            xEnd = len(Grille) - 1 - x
            diagonaleRight.append(Grille[x][xEnd])
            col.append(Grille[x][y])

            if ConfigIsGagnante(ligne, valCasePlayer):
                haveWin = True
                break

        if ConfigIsGagnante(diagonaleLeft, valCasePlayer) or ConfigIsGagnante(col, valCasePlayer) or ConfigIsGagnante(
                diagonaleRight, valCasePlayer):
            haveWin = True
            break

        diagonaleLeft.clear()
        diagonaleRight.clear()
        col.clear()

    if not haveWin and len(GetCaseDisponible()) == 0:
        haveWin = valCasePlayer == 3

    return haveWin


def GetGagnant() -> str:
    gagnant = "N"
    if HaveWin(1):
        gagnant = "H"
    elif HaveWin(2):
        gagnant = "IA"

    return gagnant


def ConvertTypePlayerToValuePlayer(typePlayer):
    value = 1

    if typePlayer == "IA":
        value = 2
    elif typePlayer == "N":
        value = 3

    return value


def PartieIsEnd() -> bool:
    return HaveWin() or HaveWin(2) or HaveWin(3)


def GetBestCoups(Resultats: list, R: str) -> tuple:
    coupsPlayer = []

    for i in range(0, len(Resultats)):
        typePlayer = Resultats[i][0]
        if typePlayer == R:
            coupsPlayer.append(Resultats[i])

    if len(coupsPlayer) > 0:
        choix = random.randrange(len(coupsPlayer))
        return coupsPlayer[choix]

    if R == "N":
        for i in range(0, len(Resultats)):
            typePlayer = Resultats[i][0]
            posX, posY = Resultats[i][1]
            valuePlayer = ConvertTypePlayerToValuePlayer(typePlayer)
            Grille[posX][posY] = valuePlayer

            if HaveWin(valuePlayer):
                Grille[posX][posY] = 0
                return Resultats[i]
            Grille[posX, posY] = 0
        choix = random.randrange(len(Resultats))
        return Resultats[choix]

    return GetBestCoups(Resultats, "N")


def PlayerSimIA() -> tuple[str, tuple[int, int]] or str:
    if PartieIsEnd():
        return GetGagnant()
    L = GetCaseDisponible()
    Resultats = []

    for K in L:
        x, y = K
        Grille[x][y] = 2
        R = PlayerSimHuman()
        Resultats.append((R, K))
        Grille[x][y] = 0

    return GetBestCoups(Resultats, "IA")


def PlayerSimHuman() -> tuple[str, tuple[int, int]] or str:
    if PartieIsEnd():
        return GetGagnant()
    L = GetCaseDisponible()
    Resultats = []

    for K in L:
        x, y = K
        Grille[x][y] = 1
        R = PlayerSimIA()
        Resultats.append((R, K))
        Grille[x][y] = 0

    return GetBestCoups(Resultats, "H")


def Play(x: int, y: int) -> None:
    valCasePlayer = 1

    if turn == "IA":
        valCasePlayer = 2

    Grille[x][y] = valCasePlayer
    HaveWin(valCasePlayer)


def PlayerPlay(x: int, y: int) -> None:
    global turn
    turn = "PLAYER"
    Play(x, y)


def IAPlay() -> None:
    global turn

    turn = "IA"
    posX, posY = [0, 0]
    try:
        caseDisponibles = GetCaseDisponible()
        if 8 > len(caseDisponibles) > 1:
            bestCoupIA = PlayerSimIA()
            posX = bestCoupIA[1][0]
            posY = bestCoupIA[1][1]
        else:
            choix = random.randrange(len(caseDisponibles))
            bestCoupIA = caseDisponibles[choix]
            posX, posY = bestCoupIA
    except IndexError:
        breakpoint()
    Play(posX, posY)


################################################################################
#
# Dessine la grille de jeu

def Dessine(PartieGagnee=False, gagnant=-1):
    global canvas
    ## DOC canvas : http://tkinter.fdex.eu/doc/caw.html
    canvas.delete("all")

    if PartieGagnee:
        color = "red" if gagnant == 1 else "yellow" if gagnant == 2 else "white" if gagnant == 3 else "dark"
        canvas.configure(bg=color)

    for i in range(4):
        canvas.create_line(i * 100, 0, i * 100, 300, fill="blue", width="4")
        canvas.create_line(0, i * 100, 300, i * 100, fill="blue", width="4")

    for x in range(3):
        for y in range(3):
            xc = x * 100
            yc = y * 100
            if (Grille[x][y] == 1):
                canvas.create_line(xc + 10, yc + 10, xc + 90, yc + 90, fill="red", width="4")
                canvas.create_line(xc + 90, yc + 10, xc + 10, yc + 90, fill="red", width="4")
            if (Grille[x][y] == 2):
                canvas.create_oval(xc + 10, yc + 10, xc + 90, yc + 90, outline="yellow", width="4")

    canvas.create_text(30, 15, text=f"J1: {ScorePlayer}", fill="yellow", font="Helvetica 12 bold")
    canvas.create_text(LARG - 30, 15, text=f"IA: {ScoreIA}", fill="yellow", font="Helvetica 12 bold")


####################################################################################
#
#  fnt appelée par un clic souris sur la zone de dessin

def MouseClick(event):
    global canvas, Grille, DebutPartie

    if DebutPartie:
        Grille.fill(0)
        canvas.configure(bg="black")

    Window.focus_set()
    x = event.x // 100  # convertit une coordonée pixel écran en coord grille de jeu
    y = event.y // 100
    if ((x < 0) or (x > 2) or (y < 0) or (y > 2)): return
    print("clicked at", x, y)

    if not CaseIsEmpty(x, y):
        return

    PlayerPlay(x, y)  # gestion du joueur humain et de l'IA

    if PartieIsEnd():
        DebutPartie = True
        EndGame(ConvertTypePlayerToValuePlayer(GetGagnant()))
    else:
        IAPlay()
        if PartieIsEnd():
            DebutPartie = True
            EndGame(ConvertTypePlayerToValuePlayer(GetGagnant()))
        else:
            DebutPartie = False

    Dessine()


canvas.bind('<ButtonPress-1>', MouseClick)
#####################################################################################
#
#  Mise en place de l'interface - ne pas toucher

AfficherPage(0)
Dessine()
Window.mainloop()

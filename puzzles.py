# -*- coding: iso-8859-15 -*-

# Code réalisé par Emmanuel Beffara et Damien Allonsius
import math
import random
import sys

import cairo

# Une palette de 6 couleurs pour les pièces

palette = [
    (1,  0,  0),  # rouge
    (0,  .8, 0),  # vert
    (0,  0,  1),  # bleu
    (.8, .8, 0),  # jaune
    (.8, 0,  1),  # violet 
    (1, .5,  0)   # orange
]

class Tile:
    """
    Représentation d'une pièce de puzzle.
    
    La pièce est décrite par le champ 'border' qui décrit le bord de la pièce
    dans l'ordre haut, droite, bas, gauche. Chaque élément de la liste est 1
    pour une bosse et -1 pour un creux. On ne considère pas de bords droits.
    """
    def __init__ (self, border):
        """
        Crée une pièce avec le bord spécifié.
        """
        self.border = border

    def value (self):
        """
        Calcule la somme des valeurs des bords, le résultat est un entier pair
        entre -4 et 4.
        """
        return sum(self.border)

    def number (self):
        """
        Calcule le numéro de la pièce, entre 0 et 5.
        
        Les pièces sont numérotées par valeurs (somme des bords) croissantes
        et sont identifiées à rotation près. Chaque valeur correspond à une
        seule pièce, sauf 0 qui a deux instances: [1,-1,1,-1] et [1,1,-1,-1].
        On distingue ces valeurs par le fait que la première est symétrique et
        la deuxième ne l'est pas; dans l'ordre on met la symétrique en
        premier.
        """
        v = self.value()
        if v < 0:
            return (v + 4) // 2
        elif v > 0:
            return (v + 4) // 2 + 1
        elif self.border[0] == self.border[2]:
            # cas symétrique
            return 2
        else:
            # cas asymétrique
            return 3

    def draw (self, ctx):
        """
        Dessine la pièce. Le carré de la pièce est de côte 1, le centre est
        placé à la position courante et les bords sont orientés selon les
        axes. La pièce est remplie avec la couleur de palette qui correspond à
        son numéro.
        """
        # Dans l'opération de tracé, on utilise les transformations du plan
        # fourni par Cairo pour procéder par des mouvements relatifs. On se
        # place sur le coin en haut à gauche et on parcourt le bord dans le
        # sens horaire en alternant le tracé d'un bord et une rotation d'un
        # quart de tour.
        # 
        # La routine de tracé d'un bord n'a qu'à tracer un segment horizontal
        # de longueur 1 en partant de la position courante avec la bosse à
        # gauche. L'utilisation des rotations permet de répétér le schéma pour
        # chaque bord avec le même code. Pour tracer un creux plutôt qu'une
        # bosse, on se contente d'appliquer une réflexion par rapport à l'axe
        # des abscisses, le temps de faire le tracé.

        ctx.save()
        # Placement au coin supérieur gauche.
        ctx.rel_move_to(-0.5, -0.5)
        for b in self.border:
            # Si le bord est un creux, on applique une réflexion.
            if b < 0:
                ctx.save()
                ctx.scale(1, -1)
            # On trace le bord avec une courbe du côté gauche.
            ctx.rel_line_to(0.35, 0)
            ctx.rel_curve_to(-0.15, -0.3, 0.45, -0.3, 0.3, 0)
            ctx.rel_line_to(0.35, 0)
            # Si le bord était un creux, on annule la réflexion.
            if b < 0:
                ctx.restore()
            # On applique une rotation pour le bord suivant.
            ctx.rotate(math.pi/2)
        # On remplit la pièce avec la couleur associée à son numéro.
        ctx.set_source_rgb(*palette[self.number()])
        ctx.fill_preserve()
        # On trace la bordure en noir.
        ctx.set_source_rgb(0, 0, 0)
        ctx.stroke()
        ctx.restore()

class Matrix:
    """
    Représentation d'une matrice de pièces.

    L'objet contient simplement un tableau à deux dimensions (liste de listes)
    contenant un objet Tile par case, ou éventuellement None pour une case
    vide.
    """
    def __init__ (self, width, height):
        """
        Création d'une matrice vide d'une taille donnée.
        """
        self.width = width
        self.height = height
        self.data = [[None] * width for y in range(height)]

    @classmethod
    def from_random_graph (cls, width, height):
        """
        Création d'une matrice d'une taille donnée en choisissant les bords de
        façon aléatoire.
        """
        # Création d'une matrice vide.
        self = cls(width, height)
        # dh indique le sens des connexions horizontales (donc des bords
        # verticaux), 1 pour la bosse vers la droite, -1 pour la bosse vers la
        # gauche.
        dh = [[random.choice([-1,1]) for x in range(width + 1)]
                for y in range(height + 1)]
        # dv indique de même les connexions verticales (donc les bords
        # horizontaux), 1 pour la bosse vers la bas, -1 pour la bosse vers le
        # haut.
        dv = [[random.choice([-1,1]) for x in range(width + 1)]
                for y in range(height + 1)]
        # Remplissage de la matrice avec les pièces voulues.
        for x in range(width):
            for y in range(height):
                self.data[y][x] = Tile([-dv[y][x], dh[y][x+1], dv[y+1][x], -dh[y][x]])
        return self

    @classmethod
    def from_periodic_graph (cls, width, height):
        """
        Création d'une matrice d'une taille donnée en choisissant les bords de
        façon à obtenir un pavage périodique. On commence par créer une matrice avec
        des bords aléatoires et on modifie la ligne du bas pour qu'elle puisse s'emboiter
        avec la ligne du haut et la colonne de droite avec celle de gauche.
        """
        # Création d'une matrice aléatoire comme dans from_random_graph
        
        # Création d'une matrice vide.
        self = cls(width, height)
        # dh indique le sens des connexions horizontales (donc des bords
        # verticaux), 1 pour la bosse vers la droite, -1 pour la bosse vers la
        # gauche.
        dh = [[random.choice([-1,1]) for x in range(width + 1)]
                for y in range(height + 1)]
        # dv indique de même les connexions verticales (donc les bords
        # horizontaux), 1 pour la bosse vers la bas, -1 pour la bosse vers le
        # haut.
        dv = [[random.choice([-1,1]) for x in range(width + 1)]
                for y in range(height + 1)]
        # Remplissage de la matrice avec les pièces voulues.
        for x in range(width):
            for y in range(height):
                self.data[y][x] = Tile([-dv[y][x], dh[y][x+1], dv[y+1][x], -dh[y][x]])

        # On ajoute le côté périodique en bas du puzzle
        for x in range(width):
        # Définition des pièces de puzzle sur la première et la dernière ligne de la colonne x
            tile_first_row=self.data[0][x]
            tile_last_row=self.data[height-1][x]
        # Modification de la bosse du bas de façon à compléter la bosse du haut
            tile_last_row.border[2]=-tile_first_row.border[0]
            self.data[height-1][x]=tile_last_row

        # On ajoute le côté périodique à droite du puzzle
        for y in range(height):
        # Définition des pièces de puzzle sur la première et la dernière colonne de la ligne y
            tile_first_col=self.data[y][0]
            tile_last_col=self.data[y][width-1]
        # Modification de la bosse de droite de façon à compléter la bosse de gauche
            tile_last_col.border[1]=-tile_first_col.border[3]
            self.data[y][width-1]=tile_last_col
        return self

    def draw (self, ctx):
        """
        Tracé de la matrice avec le coin en haut à gauche à la position (0,0).
        """
        for x in range(self.width):
            for y in range(self.height):
                ctx.move_to(x + 0.5, y + 0.5)
                self.data[y][x].draw(ctx)

class UI:
    """
    Interface (graphique ou ligne de commande).
    """
    def main (self):
        """
        Programme principal: le programme reçoit la largeur et la hauteur de la
        matrice en arguments puis éventuellement le nom d'un fichier PDF à produire.
        Si le nom de fichier est fourni, produit le fichier PDF et quitte, sinon
        affiche le dessin à l'écran.
        """
        if len(sys.argv) < 3:
            print("arguments attendus: largeur hauteur [fichier.pdf]")
            return
        self.width = int(sys.argv[1])
        self.height = int(sys.argv[2])

        #self.M = Matrix.from_random_graph(self.width, self.height)
        self.M = Matrix.from_periodic_graph(self.width, self.height)

        if len(sys.argv) == 3:
            import gi
            gi.require_version('Gtk', '3.0')
            global Gtk
            from gi.repository import Gtk
            win = Gtk.Window()
            win.connect('delete-event', Gtk.main_quit)
            area = Gtk.DrawingArea()
            area.connect('draw', self.on_draw)
            area.set_property('can-focus', True)
            area.connect('key-press-event', self.on_key_press)
            win.add(area)
            win.set_default_size((self.width+1)*40, (self.height+1)*40)
            win.show_all()
            Gtk.main()

        else:
            surface = cairo.PDFSurface(sys.argv[3], (self.width+1)*72, (self.height+1)*72)
            ctx = cairo.Context(surface)
            ctx.scale(72, 72)
            self.draw(ctx)

    def draw (self, ctx):
        """
        Rendu du dessin dans un contexte donné.
        """
        ctx.translate(0.5, 0.5)
        ctx.set_line_width(0.05)
        self.M.draw(ctx)

    def on_draw (self, area, ctx):
        """
        Rendu du dessin dans une fenêtre (avec mise à l'échelle).
        """
        ctx.scale(40, 40)
        self.draw(ctx)

    def on_key_press (self, area, event):
        """
        Réaction à une frappe au clavier.
        """
        if event.string == ' ':
            # espace: recréer un puzzle
            self.M = Matrix.from_random_graph(self.width, self.height)
            area.queue_draw()
        elif event.string == 'q':
            # Q: quitter
            Gtk.main_quit()

if __name__ == '__main__':
    UI().main()

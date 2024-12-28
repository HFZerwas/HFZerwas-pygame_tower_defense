import pygame as pg
import config as c


class Button():
    def __init__(self, x, y, image, single_click):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.clicked = False
        self.single_click = single_click

    def draw(self, Surface):
        action = False
        pos = pg.mouse.get_pos()
        if self.rect.collidepoint(pos):
            if pg.mouse.get_pressed()[0] == 1 and self.clicked == False:
                action = True
                self.clicked = True
        if pg.mouse.get_pressed()[0] == 0:
            self.clicked = False

        Surface.blit(self.image, self.rect)
        return action


class Main_Menu_Button:
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input

        # Initialisiere die Schriftart
        if isinstance(font, str):
            # Erstelle ein SysFont-Objekt
            self.font = pg.font.SysFont(font, 40)
        elif isinstance(font, pg.font.Font):
            self.font = font
        else:
            raise TypeError(
                "Font muss ein String oder ein pg.font.Font-Objekt sein.")

        # Erstelle den Text
        self.text = self.font.render(self.text_input, True, self.base_color)

        # Falls kein Bild übergeben wurde, verwende nur den Text
        if self.image is None:
            self.image = self.text

        # Definiere `self.rect` unabhängig von `self.image`
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        # Prüfe, ob die Position innerhalb der Button-Rechtecke liegt
        return self.rect.collidepoint(position)

    def changeColor(self, position):
        if self.checkForInput(position):
            self.text = self.font.render(
                self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(
                self.text_input, True, self.base_color)

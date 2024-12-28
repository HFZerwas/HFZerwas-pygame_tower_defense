import pygame as pg
import config as c
import math

#######################################################################################
#                                                                                     #
# Bilder:                                                                             #
# https://github.com/russs123/tower_defence_tut/tree/main/Part%2013/assets            #
#                                                                                     #
#######################################################################################

# Funktionen zum prüfen ob die Plazierung auf dem Weg ist oder nicht


def is_point_within_radius(mouse_pos, forbidden_point, kind_of_test):
    """Berechnet, ob der Punkt innerhalb eines bestimmten Radius vom Zentrum koordinate liegt."""
    px, py = mouse_pos
    cx, cy = forbidden_point
    # Berechne den Abstand zwischen den beiden Punkten
    distance = math.hypot(px - cx, py - cy)

    if px > 800:  # außerhalb des Spielfeldes
        return True
    # Überprüfe, ob der Abstand kleiner oder gleich dem erlaubten Radius ist
    if kind_of_test == 1:
        return distance <= c.forbidden_radius_street
    if kind_of_test == 2:
        return distance <= c.forbidden_radius_tower


def is_point_near_path(mouse_pos):
    """Überprüft, ob der Punkt (mouse_pos) zu nah an einem der verbotenen Punkte liegt."""
    for point in c.tower_forbidden_zone:  # überprüft die Straße
        if is_point_within_radius(mouse_pos, point, 1):
            # print(f"Punkt {mouse_pos} ist zu nah an einem verbotenen Punkt {point}.")
            return True
    if c.tower_places:
        for point in c.tower_places:  # überprüft ob da schon ein Tower steht
            if is_point_within_radius(mouse_pos, point, 2):
                # print(f"Punkt {mouse_pos} ist zu nah an einem verbotenen Punkt {point}.")
                return True
    c.tower_places.append(mouse_pos)  # keine 2 tower auf der selben Position
    return False


def create_tower(mouse_pos, corsor_turret, tower_version):
    """ Überprüfen, ob die Position innerhalb des Spielfelds liegt
        erstellt Tower wenn dieser nicht in der verbotenen Zone (schwarzer Spielfeldrand)
        liegt oder dort schon ein Tower ist """
    mouse_tile_x = mouse_pos[0] // c.tile_size
    mouse_tile_y = mouse_pos[1] // c.tile_size

    #
    if mouse_pos[0] < c.screen_width and mouse_pos[1] < c.screen_height:
        # Überprüfen, ob die aktuelle Position nicht in der verbotenen Zone liegt
        if not is_point_near_path(mouse_pos):
            print(mouse_pos)
            print("Turm wird platziert.")
            tower = Tower(corsor_turret, mouse_tile_x,
                          mouse_tile_y, tower_version)
            return tower
        else:
            print("Turm kann nicht auf der Straße oder zu nah daran platziert werden.")
    return None


class Tower(pg.sprite.Sprite):
    def __init__(self, sprite_sheet, mouse_tile_x, mouse_tile_y, tower_version=1):
        pg.sprite.Sprite.__init__(self)
        self.monster = None
        self.last_shot = pg.time.get_ticks()
        self.is_selected = False
        # Positionen
        self.tile_x = mouse_tile_x
        self.tile_y = mouse_tile_y
        self.tower_version = tower_version
        # Zentrum der Kacheln ermitteln
        self.x = (self.tile_x + 0.5) * c.tile_size
        # Zentrum der Kacheln ermittln
        self.y = (self.tile_y + 0.5) * c.tile_size
        self.enemy_dist = 1000000
        # animationsvariablen
        self.sprite_sheet = sprite_sheet
        self.animation_list = self.load_images()
        self.frame_index = 0
        self.update_time = pg.time.get_ticks()
        self.angle = 90
        self.first_shot_angle = 90
        # update
        self._origin_image = self.animation_list[self.frame_index]
        self.image = pg.transform.rotate(self._origin_image, self.angle)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        self.reset_after_last_shot = True
        # range - transparenter Bereich
        self.range_image = pg.Surface((c.tower_range * 2, c.tower_range * 2))
        self.range_image.fill((0, 0, 0))
        self.range_image.set_colorkey((0, 0, 0))
        pg.draw.circle(self.range_image, "grey100",
                       (c.tower_range, c.tower_range), c.tower_range)
        self.range_image.set_alpha(60)
        self.range_rect = self.range_image.get_rect()
        self.range_rect.center = (self.x, self.y)

    def load_images(self):
        """ laden der Türme- Bilder """
        size = self.sprite_sheet.get_height()
        animation_list = []
        for x in range(c.anzahl_animationen):
            temp_img = self.sprite_sheet.subsurface(x * size, 0, size, size)
            original_width, original_height = temp_img.get_size()
            new_size = (int(original_width * c.scale_factor),
                        int(original_height * c.scale_factor))
            temp_img = pg.transform.scale(
                temp_img, new_size)  # Skaliere das Bild
            animation_list.append(temp_img)
        return animation_list

    def tower_animation(self):
        """ Schussanimation """
        if not self.reset_after_last_shot:
            self._origin_image = self.animation_list[self.frame_index % 8]
        else:
            self._origin_image = self.animation_list[0]

    def draw(self, surface):
        """ zeichnet die Oberfläche neu """
        self.image = pg.transform.rotate(self._origin_image, self.angle - 90)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)
        surface.blit(self.image, self.rect)
        if self.is_selected:
            surface.blit(self.range_image, self.range_rect)
        if (pg.time.get_ticks() - self.update_time) > c.verzoegrung_animation:
            self.update_time = pg.time.get_ticks()
            self.frame_index += 1

    def update(self):
        """ Update des gesammten Spiels """
        rotation_speed = 2  # Maximale Drehgeschwindigkeit in Grad pro Frame

        if self.monster is None:
            # Setze den Turm auf den Standardzustand zurück
            self.frame_index = 0
            self.image = self.animation_list[0]  # Standard-Sprite setzen
            self.angle = self.first_shot_angle
            self.reset_after_last_shot = True  # Animation zurücksetzen
            self.find_target()  # Suche nach einem neuen Ziel
        else:
            # Berechne den Zielwinkel
            x_distanz = self.monster.pos[0] - self.x
            y_distanz = self.monster.pos[1] - self.y
            target_angle = math.degrees(math.atan2(-y_distanz, x_distanz)) - 10

            # Berechne die Differenz zwischen dem aktuellen und dem Zielwinkel
            angle_difference = (target_angle - self.angle + 360) % 360
            if angle_difference > 180:
                angle_difference -= 360

            # Begrenze die Drehgeschwindigkeit
            if abs(angle_difference) <= rotation_speed:
                self.angle = target_angle  # Zielwinkel erreicht
            else:
                self.angle += rotation_speed if angle_difference > 0 else -rotation_speed

            self.reset_after_last_shot = False
            self.tower_animation()  # Schussanimation

            if (pg.time.get_ticks() - self.last_shot) >= c.cool_down_time:
                self.last_shot = pg.time.get_ticks()
                self.attack_monster()

        # Prüfe, ob das Monster noch HP hat oder außer Reichweite ist
        if self.monster:
            if self.monster.health <= 0:
                c.enemy_group.remove(self.monster)
                self.monster.destroy()
                self.monster = None
                self.reset_after_last_shot = True  # Animation zurücksetzen
                self.image = self.animation_list[0]  # Standard-Sprite setzen
            elif self._is_monster_out_of_range():
                self.monster = None
                self.reset_after_last_shot = True  # Animation zurücksetzen
                self.image = self.animation_list[0]  # Standard-Sprite setzen
        # Prüfe, ob alle Gegner entfernt wurden, um c.last_enemy_of_round_killed zu setzen
        if not c.enemy_group and self.monster is None:
            self.image = self.animation_list[0]
            c.last_enemy_of_round_killed = True

    def _is_monster_out_of_range(self):
        """ prüft ob zugewiesenes Monster noch in Reichweite ist """
        return self.enemy_dist > c.tower_range

    def find_target(self):
        ''' findet den nächsten Gegner'''
        x_distanz = 0
        y_distanz = 0
        for monster in c.enemy_group:
            # print(c.enemy_group)
            x_distanz = monster.pos[0] - self.x
            y_distanz = monster.pos[1] - self.y
            self.enemy_dist = math.sqrt(x_distanz ** 2 + y_distanz ** 2)
            if self.enemy_dist < c.tower_range:
                self.monster = monster
                self.first_shot_angle = math.degrees(
                    math.atan2(-y_distanz, x_distanz)) - 25
                break
            else:
                self.monster = None

    def attack_monster(self):
        """ greift Gegner an, wenn noch vorhanden """
        if self.monster is not None:
            if self.monster.health <= 0:
                # Entferne das Monster und aktualisiere Punkte
                c.enemy_group.remove(self.monster)
                self.monster.destroy()
                self.monster = None
                self.frame_index = 0  # Animation stoppen
                # Setze c.last_enemy_of_round_killed, wenn keine Monster mehr existieren
                if not c.enemy_group:
                    c.last_enemy_of_round_killed = True
                    c.next_spawn_time = pg.time.get_ticks() + c.spawn_timer
                    print("Alle Gegner besiegt, warte auf neuen Spawn.")
            elif self.enemy_dist > c.tower_range:
                # Entferne das Ziel, wenn es außer Reichweite ist
                self.monster = None
            else:
                # Greife das Monster an
                self.monster.take_damage(20)

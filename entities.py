import pygame as pg
import config as c
from pygame.math import Vector2
import math
######################################################################################
#                                                                                    #
# Bilder:                                                                            #
# https://github.com/russs123/tower_defence_tut/tree/main/Part%2013/assets           #
#                                                                                    #
# Klasse der Gegner mit entsprechenden Objektmethoden                                #
#                                                                                    #
# ####################################################################################


class Enemy2(pg.sprite.Sprite):
    def __init__(self, path, image, tile_size=32, monsterspeed=1):
        super().__init__()
        self.waypoints = path
        self.pos = Vector2(self.waypoints[0])  # Starting position
        self.target_waypoint = 1
        self.path = path
        self.current_index = 0
        self.speed = monsterspeed  # Speed in pixels per frame
        self.health = c.enemy_health
        self.tile_size = tile_size

        # Bild und Rechteck für Positionierung
        self.original_image = image  # Speichere das Originalbild
        self.image = image
        self.rect = self.image.get_rect(center=self.pos)
        self.angle = 0  # Winkel für Animation

        # Flag zum prüfen ob enemy besiegt wurde
        self.alive = True

    def move(self):
        """Bewegt den enemy zum nächsten waypoint"""
        if self.alive and self.target_waypoint < len(self.waypoints):  # prüft ob es schon am Ziel ist
            target_pos = Vector2(self.waypoints[self.target_waypoint])
            movement_vector = target_pos - self.pos
            distance = movement_vector.length()

            if distance >= self.speed:  # Bewegung zur Zielposition
                # Anpassung, damit es nicht ruckellig aussieht
                self.pos += movement_vector.normalize() * self.speed
            else:
                self.pos = target_pos
                self.target_waypoint += 1  # Move to the next waypoint

            self.rect.center = self.pos  # Update rect position zur neuen pos

        else:  # Ziel ist erreicht
            if self.alive:
                self.destroy()
                c.lost = True

    def rotate(self):
        """Rotiert das Enemy-Objekt in Richtung des nächsten Wegpunkts."""
        if self.target_waypoint < len(self.waypoints):
            target_pos = Vector2(self.waypoints[self.target_waypoint])
            dist = target_pos - self.pos
            self.angle = math.degrees(math.atan2(-dist.y, dist.x))

            # Bild neu berechnen und transformieren
            self.image = pg.transform.rotate(self.original_image, self.angle)
            self.rect = self.image.get_rect(center=self.rect.center)

    def update(self):
        """Update enemy position und rotation in jedem frame."""
        self.move()
        self.rotate()

    def draw(self, screen):
        """Zeichnet enemy auf das Feld an derzeitiger Position."""
        if self.alive:
            screen.blit(self.image, self.rect.topleft)

    def take_damage(self, amount):
        """Reduzierung der HP, und zerstörung falls HP<=0"""
        print(f"def take_damage(self, amount): amount = {amount}", flush=True)
        print(f"self.health  : {self.health}", flush=True)
        self.health -= amount
        if self.health <= 0:
            self.destroy()
            c.tower_points += 5
            print(f" Gegner besiegt. Guthaben +5: {c.tower_points}")
        if not c.enemy_group:
            c.last_enemy_of_round_killed = True
            c.next_spawn_time = pg.time.get_ticks() + c.spawn_timer

    def destroy(self):
        """zerstörung des enemy-Objekts"""
        self.alive = False

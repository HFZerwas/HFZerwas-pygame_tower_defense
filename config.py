import pygame as pg

#######################################################################################
#                                                                                     #
# Konfigurationsscript                                                                #
#                                                                                     #
#######################################################################################

# Spielfeldgröße und Kachelgröße festlegen
screen_width = 1000
screen_height = 600
tile_size = 32  # Größe jeder Kachel

# allgemeine Einstellungen
start_game = False
lost = False
level = 1  # Startlevel

# Hintergrundbild laden und skalieren
background_image = pg.image.load("assets/stone_bg_512x512.png")
background_image = pg.transform.scale(background_image, (800, screen_height))

# Farben definieren
path_color = (0, 0, 0)      # Black for path
start_color = (0, 255, 0)   # Green for start point
end_color = (255, 0, 0)     # Red for endpoint

# Pfad Einstellungen
path_width = 25
tower_forbidden_zone = []
forbidden_radius_street = 35
forbidden_radius_tower = 25

# Tower Einstellungen
tower_points = 100
tower_kosten = [10, 25, 50]
tower_places = []
scale_factor = 0.75
anzahl_animationen = 8
verzoegrung_animation = 35
cool_down_time = 500
tower_range = 140

# Monster einstellungen
enemy_health = 100
spawn_interval = 400
next_spawn_time = 0
monsters_to_spawn = 1
monsters_to_spawn_next_round = 1
monsters = []
enemy_group = pg.sprite.Group()
spawn_timer = 5000  # Zeit in MS vom Ende der letzten Welle bis zur neuen
last_enemy_of_round_killed = False  # end of round flag
no_enemy = False


def reload():
    ''' setzt die Einstellungen zurück, wenn man das Spiel neu starten möchte (noch nicht implementiert)'''
    global start_game, lost, level, tower_points, tower_places, enemy_group, \
        monsters, next_spawn_time, monsters_to_spawn, monsters_to_spawn_next_round, \
        spawn_timer, last_enemy_of_round_killed, no_enemy

    # Allgemeine Einstellungen zurücksetzen

    lost = False
    level = 1

    # Tower-Einstellungen zurücksetzen
    tower_points = 100
    tower_places = []

    # Monster-Einstellungen zurücksetzen
    next_spawn_time = 0
    monsters_to_spawn = 1
    monsters_to_spawn_next_round = 1
    monsters = []
    enemy_group = pg.sprite.Group()
    spawn_timer = 2000
    last_enemy_of_round_killed = False
    no_enemy = False

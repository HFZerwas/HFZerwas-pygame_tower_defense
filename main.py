import pygame as pg
import math
import config as c
from entities import Enemy2  
from board_builder import create_board
from towers import create_tower
from buttons import Button, Main_Menu_Button


#######################################################################################
# Funktonsbereich
#######################################################################################

def draw_board():
    global board_first_time_drawn
    """Malt die Straße auf das Spielfeld"""
    # Zeichne den Start- und Endpunkt als Kreise
    start_pos = (enemy_path[0][0] * c.tile_size + c.tile_size //
                 2, enemy_path[0][1] * c.tile_size + c.tile_size // 2)
    end_pos = (enemy_path[-1][0] * c.tile_size + c.tile_size //
               2, enemy_path[-1][1] * c.tile_size + c.tile_size // 2)

    pg.draw.circle(screen, c.start_color, start_pos, c.tile_size // 2)
    pg.draw.circle(screen, c.end_color, end_pos, c.tile_size // 2)

    # Zeichne Linien, die die Punkte im Pfad verbinden und speichere die Koordinaten
    for i in range(len(enemy_path) - 1):
        start = (enemy_path[i][0] * c.tile_size + c.tile_size //
                 2, enemy_path[i][1] * c.tile_size + c.tile_size // 2)
        end = (enemy_path[i + 1][0] * c.tile_size + c.tile_size //
               2, enemy_path[i + 1][1] * c.tile_size + c.tile_size // 2)

        # Zeichne die Linie
        pg.draw.line(screen, c.path_color, start, end, width=25)

        # Füge die Koordinatenpunkte entlang des Liniensegments der verbotenen Zone hinzu
        # Dies sollte nur einmal passieren, wenn `first_time` wahr ist
        if board_first_time_drawn:
            step_size = 2  # Kann angepasst werden, je nach gewünschter Präzision
            dx = (end[0] - start[0])
            dy = (end[1] - start[1])
            distance = int(math.hypot(dx, dy))

            # Generiere Punkte entlang des Liniensegments
            for step in range(0, distance, step_size):
                ratio = step / distance
                point_x = int(start[0] + ratio * dx)
                point_y = int(start[1] + ratio * dy)
                c.tower_forbidden_zone.append((point_x, point_y))

    # first time
    if board_first_time_drawn:
        board_first_time_drawn = False
        # Debug-print(optional)
        # print(f"Verbotene Zonen: {c.tower_forbidden_zone}")


def set_tower(mouse_pos, tower_version):
    """setzt die Tower, abhängig von der Mausposition"""
    global placing_towers
    created = False
    tower = None
    if placing_towers:
        # prüft Guthaben
        if c.tower_points - c.tower_kosten[tower_version] >= 0:
            c.tower_points -= c.tower_kosten[tower_version]
            print(f"Restguthaben : {c.tower_points}", flush=True)
            tower = create_tower(mouse_pos, corsor_turret_sheet, tower_version)
        else:
            print(f"nicht genug Guthaben.")
        if tower is not None:
            created = True
            turret_group.add(tower)
        if not created:
            # erstattet Guthaben falls Tower nicht platziert werden kann
            c.tower_points += c.tower_kosten[tower_version]


def select_tower(mouse_pos):
    """macht Tower anklickbar"""
    mouse_tile_x = mouse_pos[0] // c.tile_size
    mouse_tile_y = mouse_pos[1] // c.tile_size
    if c.tower_places:
        print(c.tower_places)
        for tower in turret_group:
            if (mouse_tile_x, mouse_tile_y) == (tower.tile_x, tower.tile_y):
                return tower


def clear_tower_selection():
    """ Tower nicht mehr markiert """
    for tower in turret_group:
        tower.is_selected = False


def get_screen_path(enemy_path, tile_size):
    """Konvertiert den logischen Pfad in Bildschirmkoordinaten."""
    screen_path = []
    print(enemy_path)
    for point in enemy_path:
        x = point[0] * tile_size + tile_size // 2
        y = point[1] * tile_size + tile_size // 2
        screen_path.append((x, y))
    return screen_path


def spawn_new_monsters():
    """ neues Monster """
    new_monsters = Enemy2(path=screen_path, image=enemy_image,
                          tile_size=c.tile_size, monsterspeed=0.5)
    c.monsters.append(new_monsters)
    c.enemy_group.add(new_monsters)


#######################################################################################
# Variablen und Objekte
#######################################################################################

####### pg initialisieren#######
pg.init()

####### Display Fenster#######
screen = pg.display.set_mode((c.screen_width, c.screen_height))
pg.display.set_caption("Tower Defense")

####### CLOCK für FRAMES#######
clock = pg.time.Clock()

######## Flags #######
placing_towers = False
tower_selected = None
board_first_time_drawn = True
####### BILDER #######
# Tower
corsor_turret = pg.image.load(
    "assets\\images\\turrets\\cursor_turret.png").convert_alpha()
# Tower_sheet
corsor_turret_sheet = pg.image.load(
    "assets\\images\\turrets\\turret_1.png").convert_alpha()
# Main Menu
menu_background = pg.image.load("assets\\stone_bg_512x512.png").convert_alpha()
menu_background = pg.transform.scale(
    menu_background, (c.screen_width, c.screen_height))
# Gegner
enemy_image = pg.image.load(
    "assets\\images\\enemies\\enemy_1.png").convert_alpha()
# Buttons
buy_tower_button_image = pg.image.load(
    "assets\\images\\buttons\\buy_turret.png").convert_alpha()
cancel_image = pg.image.load(
    "assets\\images\\buttons\\cancel.png").convert_alpha()

# Guthaben
account = pg.font.SysFont("Arial", 20, True, False)
account.render(str(c.tower_points), True, (250, 250, 250))

# Level
level = pg.font.SysFont("Arial", 20, True, False)
level.render("Level: " + str(c.level), True, (250, 250, 250))

####### UPDATE #######
# größe der Tower anpassen
original_width, original_height = corsor_turret.get_size()
new_size = (int(original_width * c.scale_factor),
            int(original_height * c.scale_factor))
corsor_turret = pg.transform.scale(
    corsor_turret, new_size)  # Skaliere das Bild

# Erstelle das Spielfeld und den Gegnerpfad
enemy_path = create_board()  # holt die Tupel aus denen der Weg erstellt wird
screen_path = get_screen_path(enemy_path, c.tile_size)  # weg der Monster

# Tower group
turret_group = pg.sprite.Group()

# Button
tower_button = (Button((c.screen_width - 175),
                120, buy_tower_button_image, True))
cancel_button = (Button(c.screen_width - 175, 180, cancel_image, True))

#######################################################################################
# Spielbereich
#######################################################################################

running = True


def play(screen):
    """ Funktion zur Steuerung des Spiels """
    global running
    global tower_selected
    global placing_towers
    global enemy_image
    clock.tick(45)
    current_time = pg.time.get_ticks()
    # Draw the background
    screen.fill((0, 0, 0))
    screen.blit(c.background_image, (0, 0))
    draw_board()
    screen.blit(account.render("Guthabeln: "+str(c.tower_points),
                True, (250, 250, 250)), [(c.screen_width - 175), 60,])
    screen.blit(level.render("Level: " + str(c.level), True,
                (250, 250, 250)), [(c.screen_width - 175), 40,])

    if tower_selected:
        tower_selected.is_selected = True
    if tower_button.draw(screen):
        placing_towers = True

    # eventhandler
    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pg.mouse.get_pos()
            set_tower(mouse_pos, 0)
        if event.type == pg.MOUSEBUTTONDOWN and not placing_towers:
            clear_tower_selection()
            mouse_pos = pg.mouse.get_pos()
            tower_selected = select_tower(mouse_pos)

    # spawn monsters
    if c.last_enemy_of_round_killed and c.monsters_to_spawn > 0:
        enemy_image = pg.image.load(
            f"assets\\images\\enemies\\enemy_{int((c.level/4)+1)%4}.png").convert_alpha()
        c.enemy_health = (int((c.level/3)+1))*100
        if current_time >= c.next_spawn_time:
            spawn_new_monsters()
            c.monsters_to_spawn -= 1
            c.next_spawn_time = current_time + c.spawn_interval
        if c.monsters_to_spawn == 0:
            c.level += 1
            c.last_enemy_of_round_killed = False
            c.monsters_to_spawn_next_round += 1
            c.monsters_to_spawn = c.monsters_to_spawn_next_round
            c.next_spawn_time = current_time + c.spawn_timer

    # Move and draw c.monsters
    for monster in c.monsters[:]:
        monster.move()
        monster.rotate()
        monster.draw(screen)

    # Draw towers
    for tower in turret_group:
        tower.update()
        tower.draw(screen)
    # If placing_towers, wird der Tower als Bild zur Platzierung angezeigt
    if placing_towers == True:
        cursor_rect = corsor_turret.get_rect()
        cursor_pos = pg.mouse.get_pos()
        cursor_rect.center = cursor_pos
        screen.blit(corsor_turret, cursor_rect)
        if cancel_button.draw(screen):
            placing_towers = False

    pg.display.flip()


def main_menu(SCREEN):
    """ Hauptmenü """
    def render_multiline_text(screen, text, font, color, pos):
        lines = text.split('\n')  # Teile den Text in Zeilen
        x, y = pos  # Startposition
        for line in lines:
            rendered_text = font.render(line, True, color)
            screen.blit(rendered_text, (x, y))
            y += font.get_height()  # Nächste Zeile unterhalb der vorherigen

    global running
    global menu_background
    pg.display.set_caption("PYGAME TOWER DEFENSE")
    SCREEN.blit(menu_background, (0, 0))

    MENU_MOUSE_POS = pg.mouse.get_pos()
    MENU_FONT = pg.font.SysFont("Arial", 60)
    MENU_TEXT = MENU_FONT.render(
        "Welcome", True, "#00FF00")
    MENU_RECT = MENU_TEXT.get_rect(center=(500, 100))

    PLAY_BUTTON = Main_Menu_Button(image=pg.image.load("assets/Play.png"), pos=(500, 250),
                                   text_input="PLAY", font="ARIAL", base_color="#d7fcd4", hovering_color="White")

    SCREEN.blit(MENU_TEXT, MENU_RECT)
    MENU_FONT = pg.font.SysFont("Arial", 30)
    MENU_TEXT = "Special features: \nA new map is generated at the start of each game\nEvery 5 levels, the difficulty increases and the “monster” changes its appearance\nTowers can be clicked to display their radius"
    MENU_POS = (200, 350)  # Startposition für den Absatz
    MENU_COLOR = "#00FF00"
    render_multiline_text(SCREEN, MENU_TEXT, MENU_FONT, MENU_COLOR, MENU_POS)

    for button in [PLAY_BUTTON]:
        button.changeColor(MENU_MOUSE_POS)
        button.update(SCREEN)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False
        if event.type == pg.MOUSEBUTTONDOWN:
            if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                c.start_game = True
                play(screen)

    pg.display.flip()


def game_over(SCREEN):
    """ Spiel verloren Anzeige """
    global running
    global menu_background
    pg.display.set_caption("PYGAME TOWER DEFENSE")
    SCREEN.blit(menu_background, (0, 0))

    MENU_MOUSE_POS = pg.mouse.get_pos()
    MENU_FONT = pg.font.SysFont("Arial", 100)
    MENU_TEXT = MENU_FONT.render("GAME OVER", True, "#FFFFFF")
    MENU_RECT = MENU_TEXT.get_rect(center=(500, 200))

    SCREEN.blit(MENU_TEXT, MENU_RECT)

    for event in pg.event.get():
        if event.type == pg.QUIT:
            running = False

    pg.display.flip()


#######################################################################################
# Main loop
#######################################################################################
while running:
    if not c.start_game:
        main_menu(screen)
    elif not c.lost:
        play(screen)
    elif c.lost:
        game_over(screen)

pg.quit()

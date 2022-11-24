import pygame
from pygame.math import Vector2
import random
import sys

# Initialise
pygame.init()
pygame.mixer.init()
pygame.mixer.pre_init(44100, -16, 2, 2048)
clock = pygame.time.Clock()
current_fps = 30

#  ========================================================================== set screen size
SCREEN_WIDTH = 800  # 1000
SCREEN_HEIGHT = 600  # 800
display_size = (SCREEN_WIDTH, SCREEN_HEIGHT)
SCREEN = pygame.display.set_mode(display_size)

#  ========================================================================== add caption
pygame.display.set_caption('***Mars Invasion***')

#  ========================================================================== add icon
programIcon = pygame.image.load('./src/icons/planets/mars.png')
pygame.display.set_icon(programIcon)

# =========================================================================== hide mouse
pygame.mouse.set_visible(False)


# ========================================================================= global methods
def fps():
    global current_fps
    font = pygame.font.Font(None, 22)
    text = font.render(f'FPS: {int(clock.get_fps())}', True, pygame.Color('orange'))
    text.get_rect()
    SCREEN.blit(text, (SCREEN_WIDTH - 220, 10))
    # pygame.draw.rect(SCREEN, 'orange', (SCREEN_WIDTH - 250, 8, 100, 30), 2, 2)

    if pygame.key.get_pressed()[pygame.K_1] and current_fps > 30:
        current_fps -= 1
    elif pygame.key.get_pressed()[pygame.K_2] and current_fps < 70:
        current_fps += 1


# show little explosion when collide on laser and ship
def explosion_after_hit(who, kill=True, message=True):
    if kill:
        who.kill()  # remove killed element from screen
    if message:
        Message.target_eliminated()  # show message target eliminated

    explosion_img_one = pygame.image.load('./src/icons/explosion/exp_1.png').convert_alpha()
    explosion_rect = pygame.Rect((who.rect.x, who.rect.y), (0, 0))
    SCREEN.blit(explosion_img_one, explosion_rect)  # show explosion
    play_sound.alien_ship_explosion()


# draw background
def background_image(image='./src/backgrounds/bg_Mars_1000_700.jpeg', fix_pic=70):
    bg_image = pygame.image.load(image)
    scale_img = pygame.transform.scale(bg_image, (800, 600))
    block_rect = scale_img.get_rect()
    SCREEN.blit(scale_img, (block_rect.x, block_rect.y + fix_pic))


# ========================================================================  CLASSES
class Ship(pygame.sprite.Sprite):
    # SHIP_SIZE = (60, 60)
    energy_power = 120
    ship_destroyed = False
    counter = 0

    def __init__(self, pos=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.transform.rotate(pygame.image.load('./src/icons/ship/my_ship.png'), 180)
        # self.image = pygame.transform.scale(pygame.image.load('./src/icons/ship/ship1.png'), self.SHIP_SIZE)
        self.orig_image = self.image  # copy image
        self.rect = self.orig_image.get_bounding_rect(min_alpha=1)
        # self.rect.center = pos
        self.position = Vector2(pos)  # ship start position
        # The vector points upwards.
        self.direction = Vector2(0, -1)
        self.speed = 0  # ship speed
        self.current_speed = 3  # current ship speed
        self.rotation_speed = 0  # ship rotation speed
        self.angle = 0  # ship current angle rotation

    def update(self):
        pygame.mask.from_surface(self.image)  # create mask image
        # chek collide ship and alien
        ship_crash = pygame.sprite.groupcollide(ship_group, aliens_group, True, True, pygame.sprite.collide_mask)
        # collide ship and alien_two
        ship_crash2 = pygame.sprite.groupcollide(ship_group, aliens_two_group, True, True, pygame.sprite.collide_mask)
        # collide ship and boss
        ship_collide_boss = pygame.sprite.groupcollide(ship_group, boss_group, True, True, pygame.sprite.collide_mask)

        if ship_crash != {} or ship_crash2 != {} or ship_collide_boss != {}:  # remove crashed ships
            if ship_collide_boss:
                SCREEN.fill(pygame.Color('Black'))
                background_image()
                SCREEN.blit(boss.image, (boss.rect.x, boss.rect.y))

            table.energy_power = 0  # energy = 0 if ship be killed
            self.ship_explosion()  # animation explosion
            self.ship_destroyed = True
            game_state.game_over()  # go to state game over

    def ship_movie_update(self):
        if self.rotation_speed != 0:
            # Rotate the direction vector and then the image
            self.direction.rotate_ip(self.rotation_speed)
            self.angle += self.rotation_speed
            self.image = pygame.transform.rotate(self.orig_image, -self.angle)
            self.rect = self.image.get_rect(top=self.rect.top)  # top=self.rect.top
        # Update the position vector and the rect.
        self.position += self.direction * self.speed
        self.rect.center = self.position

    def ship_explosion(self):
        Message.ship_destroyed()
        pygame.mixer.stop()  # stop all music
        play_sound.sound_bomb()  # play sound explosion
        for i in range(1, 5):
            explosion = pygame.image.load(f'./src/icons/explosion/exp_{i}.png')
            rect = pygame.Rect(self.position.x - 35, self.position.y - 30, SCREEN_WIDTH, SCREEN_HEIGHT)
            SCREEN.blit(explosion, rect)
            pygame.display.update()
            pygame.time.delay(300)

    def check_ship_in_border_screen(self):
        ship_block_rect = pygame.Rect(self.rect.x, self.rect.y, 10, 10)  # ship position
        screen_rect = pygame.Rect(5, 120, SCREEN_WIDTH - 60, SCREEN_HEIGHT - 170)  # collision border alarm
        if not pygame.Rect.colliderect(ship_block_rect, screen_rect):
            table.energy_power -= table.decrease_power_out_of_gravity  # decrease power
            if table.energy_power > 0:
                play_sound.sound_warning()
                if game_state.boos_battle:
                    Message.out_of_gravity(30)
                else:
                    Message.out_of_gravity()
            else:
                self.ship_destroyed = True
                game_state.game_over()

    def ship_key_control_movement(self):  # ----------------------- key control movement
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:  # UP--------------------
            ship.speed = ship.current_speed

        if keys[pygame.K_DOWN]:  # DOWN ------------
            # ship.speed = -2    # automatic movement ship
            ship.speed = ship.rotation_speed = 0  # manual movement

        if keys[pygame.K_LEFT]:  # LEFT ------------------
            ship.rotation_speed = -ship.current_speed

        if keys[pygame.K_RIGHT]:  # RIGHT ------------
            ship.rotation_speed = ship.current_speed

        if keys[pygame.K_UP] or keys[pygame.K_DOWN] or keys[pygame.K_LEFT] or keys[pygame.K_RIGHT]:  # Sound movie ship
            play_sound.sound_ship_movie()

        get_laser_time_now = pygame.time.get_ticks()  # get current time
        # shot_per_mill_sec = 700  # time before new shot
        if len(aliens_group) == 1:  # fix  bug shot_per_mill_sec = 2500
            Laser.shot_per_mill_sec = 2500
            Message.manual_fire()
            reload_energy_bar = pygame.Rect(SCREEN_WIDTH // 2 - 50, 40, 100, 10)  # draw reload energy barr
            pygame.draw.rect(SCREEN, (255, 0, 0), reload_energy_bar)
            if Ship.counter < 100:
                Ship.counter += 1.3
                reload_energy_bar = pygame.Rect(SCREEN_WIDTH // 2 - 50, 40, Ship.counter, 10)
                pygame.draw.rect(SCREEN, (0, 255, 0), reload_energy_bar)
            if Ship.counter >= 100:
                reload_energy_bar = pygame.Rect(SCREEN_WIDTH // 2 - 50, 40, Ship.counter, 10)
                pygame.draw.rect(SCREEN, (0, 255, 0), reload_energy_bar)

        else:
            Laser.shot_per_mill_sec = 700
        if keys[pygame.K_SPACE] and get_laser_time_now - Laser.time_last_shot > Laser.shot_per_mill_sec:  # create laser
            Laser.time_last_shot = get_laser_time_now  # reset time last shot
            # Just pass the rect.center, direction vector and angle.
            laser = Laser(self.rect.center, ship.direction)
            laser_ship_group.add(laser)  # add laser to group
            play_sound.laser_gun_sound()  # play sound
            Ship.counter = 0  # reset counter

    def ship_restore_begin_position(self):
        self.image = pygame.transform.rotate(pygame.image.load('./src/icons/ship/my_ship.png'), 180)
        self.orig_image = self.image  # copy image
        self.rect = self.orig_image.get_bounding_rect(min_alpha=1)
        self.position = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)  # ship start position
        self.direction = Vector2(0, -1)
        self.rotation_speed = 0  # ship rotation speed
        self.speed = 0  # ship speed
        self.angle = 0  # ship current angle rotation
        aliens_two_group.empty()   # remove aliens two from screen
        aliens_laser_group.empty()  # remove aliens laser form screen
        laser_ship_group.empty()
        boss_group.empty()


class Laser(pygame.sprite.Sprite):
    laser_speed = 5
    time_last_shot = pygame.time.get_ticks()  # save time last shot
    shot_per_mill_sec = 700  # time before new shot

    def __init__(self, pos, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('./src/icons/laser/laser_one.png')
        # self.image = pygame.Surface([4, 9], pygame.SRCALPHA)
        # self.image.fill((38, 130, 242))
        self.rect = self.image.get_rect(center=pos)
        # self.image = pygame.transform.rotozoom(self.image, -angle, 1)
        self.position = Vector2(pos)  # The position vector.
        self.velocity = direction * 11  # Multiply by  bullets speed

    def update(self):
        """Move the bullet."""
        self.position += self.velocity  # Update the position vector.
        self.rect.center = self.position  # Update the position rect.

        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 70 or self.rect.y > SCREEN_HEIGHT:
            self.kill()  # remove old shot from laser_group
        # check laser in aliens dish
        collide_aliens = pygame.sprite.spritecollide(self, aliens_group, True, pygame.sprite.collide_mask)
        # check laser in alien dish two
        collide_aliens_two = pygame.sprite.spritecollide(self, aliens_two_group, True, pygame.sprite.collide_mask)
        if collide_aliens:  # kill aliens dish
            Message.target_eliminated()

            if table.level <= 5:  # add point to score
                table.score += table.points_aliens_group_one
            elif table.level <= 10:
                table.score += table.points_aliens_group_two
            elif table.level <= 15:
                table.score += table.points_aliens_group_three
            else:
                table.score += table.points_aliens_group_four

            explosion_img_one = pygame.image.load('./src/icons/explosion/exp_1.png').convert_alpha()
            explosion_rect = pygame.Rect((self.rect.x - 35, self.rect.y - 60), (0, 0))
            SCREEN.blit(explosion_img_one, explosion_rect)  # show explosion
            play_sound.alien_ship_explosion()
            self.kill()  # remove laser shot

        if collide_aliens_two:  # kill aliens dish two
            table.score += table.points_aliens_group_five
            explosion_after_hit(aliens_two)
            self.kill()  # remove laser shot

        if len(aliens_group) == 0 and not game_state.boos_battle:  # if all aliens groups killed
            ship_group.empty()  # remove ship group from moment position

            if not game_state.boos_battle:
                table.level += 1  # increase level +1
                if table.level > 1:
                    pygame.mixer.stop()
                    play_sound.level_complete()
                    play_sound.game_music()

                if table.energy_power + table.add_energy <= Ship.energy_power:  # add power if level complete
                    table.energy_power += table.add_energy
                else:
                    table.energy_power = Ship.energy_power

                if table.level % boss.level_for_battle != 0 and table.level != 0:
                    ship.ship_restore_begin_position()  # go ship to start position
                    Aliens.create_aliens()  # Add new aliens group
                else:
                    SCREEN.fill(pygame.Color('black'))  # clear screen
                    game_state.get_ready()  # go to state get_ready to switch for BOSS BATTLE

        if game_state.boos_battle:
            # check laser in aliens BOSS SHIP
            laser_collide_boss = pygame.sprite.spritecollide(self, boss_group, False, pygame.sprite.collide_mask)
            if laser_collide_boss:
                table.energy_power_boss -= 3  # decrease energy boss ship
                self.kill()  # remove laser
                Message.boss_damage()
                play_sound.sound_bomb()  # play sound explosion
                for i in range(1, 5):
                    explosion = pygame.image.load(f'./src/icons/explosion/exp_{i}.png')
                    position = boss.rect.center
                    SCREEN.blit(explosion, position)
                    pygame.time.delay(10)


class Aliens(pygame.sprite.Sprite):
    num_row_enemy = 3  # numbers of row dishes 3
    num_col_enemy = 9  # numbers of coll dishes 9

    def __init__(self, pos=(10, SCREEN_HEIGHT - 100)):
        pygame.sprite.Sprite.__init__(self)
        self.image = self.load_aliens_ship_image_type()
        self.rect = self.image.get_bounding_rect(min_alpha=1)
        self.rect.center = pos
        self.direction = Vector2(1, 0)
        self.speed_movie_dish = 3

    def update(self):
        if self.rect.x >= 20 and self.direction.x == 1:
            self.rect.x -= self.speed_movie_dish
        else:
            self.direction.x = -1

        if self.direction.x == -1 and self.rect.x < SCREEN_WIDTH - 100:
            self.rect.x += self.speed_movie_dish
        else:
            self.direction.x = 1

    @staticmethod
    def load_aliens_ship_image_type(ship_num=1):
        global table
        if 6 <= table.level <= 10:
            ship_num = 2  # load alien ship 2
        elif 10 <= table.level <= 15:
            ship_num = 6  # load alien ship 6
        elif table.level >= 16:
            ship_num = 8  # load alien ship 8

        img = pygame.image.load(f'src/icons/enemy_ships/ufo_{ship_num}.png')
        scaled_img = pygame.transform.scale(img, (50, 50))
        return scaled_img

    @staticmethod
    def create_aliens():
        create_aliens_flot()


class AliensLaser(pygame.sprite.Sprite):
    laser_speed = 3
    num_of_shot_per_second = 5
    last_time = pygame.time.get_ticks()
    delay_time = 0

    def __init__(self, x, y, direction):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.Surface([3, 6], pygame.SRCALPHA)
        # self.image.fill((38, 130, 242))
        self.image.fill((self.laser_color()))  # set type color laser
        self.rect = self.image.get_rect()  # (center=pos)
        self.rect.midbottom = (x, y)
        self.position = Vector2(x, y)  # The position vector.
        self.velocity = direction * self.laser_speed  # Multiply by  bullets speed

    def update(self):
        """Move the bullet."""
        self.position += self.velocity  # Update the position vector.
        self.rect.center = self.position  # Update the position rect.
        if self.rect.x < 0 or self.rect.x > SCREEN_WIDTH or self.rect.y < 100 or self.rect.y > SCREEN_HEIGHT:
            self.kill()  # remove old shot from laser_group
        # create mask image aliens_two_image
        pygame.mask.from_surface(aliens_two.image)
        # chek collide laser alien and alien two ship
        if pygame.sprite.groupcollide(aliens_laser_group, aliens_two_group, True, True):
            explosion_after_hit(aliens_two)

        if pygame.sprite.spritecollide(self, ship_group, False, pygame.sprite.collide_mask):  # alien shot target ship
            self.kill()  # remove laser if collide ship
            # decrease ship power energy
            if table.level <= 15:
                table.energy_power -= table.decrease_power_shot  # -3
            else:
                table.energy_power -= table.decrease_power_shot + 1  # -4

            if table.energy_power > 0:
                Message.ship_damage()  # show ship damage

            if table.energy_power > 0:
                explosion_after_hit(ship, False, False)
            else:
                ship.ship_explosion()  # draw ship explosion animation
                # table.ships -= 1  # decrease ships
                ship.kill()  # remove ship from screen
                table.energy_power = 0  # energy = 0 if ship be killed
                ship.ship_destroyed = True
                game_state.game_over()

    @staticmethod
    def laser_color():
        if table.level <= 5:
            return 78, 244, 108  # green laser
        elif 6 <= table.level <= 10:
            return 38, 130, 242  # blue laser
        elif 10 <= table.level <= 15:
            return 180, 5, 17  # red laser
        else:
            return 160, 148, 35  # yellow laser

    @staticmethod
    def aliens_laser_shot():
        random_alien = random.choice(aliens_group.sprites())  # generate random alien who shot
        alien_laser_shot = AliensLaser(random_alien.rect.centerx, random_alien.rect.bottom, Vector2(0, 1))
        aliens_laser_group.add(alien_laser_shot)
        play_sound.alien_laser_gun_sound()


class AliensTwo(pygame.sprite.Sprite):
    def __init__(self, pos=(-70, random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2 + 200))):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('src/icons/enemy_ships/comet_55.png')
        self.rect = self.image.convert_alpha().get_bounding_rect(min_alpha=1)
        self.rect.center = pos
        self.speed_movie_dish = 5

    def update(self):
        if table.level >= 7:  # show aliens ship two if level >= 7
            timer = pygame.time.get_ticks() // 1000
            if timer & 1 == 0:
                play_sound.alien_ship_two_movie()  # play sound every one second

            self.rect.x += self.speed_movie_dish
            if self.rect.x < -100 or self.rect.x > SCREEN_WIDTH + 100:  # remove alien_two form group
                self.kill()

    @staticmethod
    def create_second_aliens():
        create_second_aliens_ship()


class AlienBoss(pygame.sprite.Sprite):
    energy = 120
    boss_shot_per_seconds = 3000
    boss_old_time = pygame.time.get_ticks()
    count_show_laser = 0

    def __init__(self, pos=(SCREEN_WIDTH // 2 + 30, 100)):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('src/icons/boss/b1.png')
        self.image = pygame.transform.scale(self.image, (250, 250))
        self.rect = self.image.convert_alpha().get_bounding_rect(min_alpha=1)
        self.rect.center = pos
        self.direction = Vector2(-1, 0)
        self.speed_movie_boss_dish = 5
        self.change_direction = False
        self.alive = True
        self.level_for_battle = 15  # every 15-th level
        self.start_position = 160

    def update(self):
        # show boss ship
        if self.rect.y < self.start_position:
            self.rect.y += self.speed_movie_boss_dish
        else:
            boss.boss_fire()
            self.boss_movie()

    # move boss ship
    def boss_movie(self):
        if self.direction.x == -1 and self.rect.x >= -80:  # move to end of left position
            self.rect.x -= self.speed_movie_boss_dish

        if self.direction.x == 1 and self.rect.x <= SCREEN_WIDTH - 310:  # move to end of right position
            self.rect.x += self.speed_movie_boss_dish

        if self.rect.x <= -80:
            self.direction.x = 1  # change direction
            self.rect.y += 20  # boss ship movie step down
            if self.speed_movie_boss_dish < 13:
                self.speed_movie_boss_dish += 0.25  # increase speed

        if self.rect.x >= SCREEN_WIDTH - 310:  # change direction
            self.direction.x = -1
            self.rect.y += 20
            if self.speed_movie_boss_dish < 13:
                self.speed_movie_boss_dish += 0.25  # increase speed

        if self.rect.x >= SCREEN_WIDTH // 2 and self.rect.y >= SCREEN_HEIGHT - 160:  # go to begin position
            self.rect.y = SCREEN_WIDTH // 2 + 30
            self.rect.y = 100
            self.start_position = 0

    def boss_fire(self):
        get_time_now = pygame.time.get_ticks()
        if get_time_now - boss.boss_old_time >= boss.boss_shot_per_seconds:
            boss.boss_old_time = get_time_now
            self.count_show_laser += 1

            if 20 < table.energy_power_boss <= 60:
                self.image = pygame.image.load('src/icons/boss/b_fire_2.png')
            elif table.energy_power_boss <= 20:
                self.image = pygame.image.load('src/icons/boss/b_fire_3.png')
            else:
                self.image = pygame.image.load('src/icons/boss/b_fire_1.png')
        if get_time_now // 1000 % 2 == 0:
            if 20 < table.energy_power_boss <= 60:
                self.image = pygame.image.load('src/icons/boss/b2.png')
            elif table.energy_power_boss <= 20:
                self.image = pygame.image.load('src/icons/boss/b3.png')
            else:
                self.image = pygame.image.load('src/icons/boss/b1.png')

        self.image = pygame.transform.scale(self.image, (250, 250))


class Message:
    @staticmethod
    def fps_message():
        font = pygame.font.Font(None, 24)
        pygame.font.Font.set_underline(font, False)
        text = font.render(f'FPS [1] slow - [2] fast', True, 'orange')
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 12))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def get_ready():
        font = pygame.font.Font(None, 24)
        text = font.render('PRESS [P] TO PAUSE', True, 'white')
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 35))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def press_space_to_start():
        font = pygame.font.Font(None, 25)
        text = font.render('PRESS SPACE TO START', True, (0, 255, 255))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 55))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def out_of_gravity(height_pos=40):
        font = pygame.font.Font(None, 30)
        pygame.font.Font.set_underline(font, True)
        text = font.render('WARNING! OUT OF GRAVITY', True, (255, 0, 0))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, height_pos))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def target_eliminated():
        font = pygame.font.Font(None, 30)
        text = font.render('TARGET ELIMINATED', True, (255, 255, 255))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def ship_damage():
        font = pygame.font.Font(None, 30)
        pygame.font.Font.set_underline(font, True)
        text = font.render('SHIP DAMAGE', True, (255, 0, 0))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def boss_battle():
        font = pygame.font.Font(None, 30)
        pygame.font.Font.set_underline(font, True)
        text = font.render('BOSS BATTLE', True, (255, 0, 0))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def boss_damage():
        font = pygame.font.Font(None, 30)
        pygame.font.Font.set_underline(font, True)
        text = font.render('BOSS DAMAGE', True, (255, 0, 0))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def boss_destroyed():
        font = pygame.font.Font(None, 30)
        pygame.font.Font.set_underline(font, True)
        text = font.render('BOSS DESTROYED', True, (255, 255, 255))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def ship_destroyed():
        font = pygame.font.Font(None, 30)
        pygame.font.Font.set_underline(font, True)
        text = font.render('SHIP DESTROYED, YOU ARE DED!!!', True, (255, 0, 0))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 30))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def manual_fire():
        font = pygame.font.Font(None, 24)
        pygame.font.Font.set_underline(font, True)
        text = font.render('MANUAL FIRE', True, (255, 255, 255))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 15))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def pause():
        font = pygame.font.Font(None, 50)
        pygame.font.Font.set_underline(font, False)
        text = font.render(f'Stop the attack! PAUSE', True, 'yellowgreen')
        text_pos = text.get_rect(center=(SCREEN_WIDTH - 240, SCREEN_HEIGHT // 3))
        SCREEN.blit(text, text_pos)

    @staticmethod
    def press_return_to_continue():
        font = pygame.font.Font(None, 24)
        text = font.render('Press RETURN to continue...', True, (255, 255, 255))
        text_pos = text.get_rect(center=(SCREEN_WIDTH - 140, SCREEN_HEIGHT - 20))
        SCREEN.blit(text, text_pos)

    # @staticmethod
    # def reload():
    #     font = pygame.font.Font(None, 36)
    #     text = font.render('(recharge every second)', True, (255, 255, 255))
    #     text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, 70))
    #     SCREEN.blit(text, text_pos)


class Table:
    height_score = 60000
    score = 0
    level = 0
    points_aliens_group_one = 100
    points_aliens_group_two = 200
    points_aliens_group_three = 300
    points_aliens_group_four = 500
    points_aliens_group_five = 1000
    points_boss = 50000
    energy_power = Ship.energy_power
    energy_power_boss = AlienBoss.energy  # 122
    add_energy = 30
    decrease_power_out_of_gravity = 1
    decrease_power_shot = 20
    get_time_now = pygame.time.get_ticks()

    def get_height_score_from_file(self):
        with open('./src/score/save_height_score.txt', 'r') as file:
            self.height_score = int(file.readline())

    def write_new_height_score_in_file(self):  # write new score record in file
        if self.score >= self.height_score:
            with open('./src/score/save_height_score.txt', 'w') as file:
                file.write(str(self.height_score))

    def draw_height_score(self):
        if self.score >= self.height_score:
            self.height_score = self.score

        font = pygame.font.Font(None, 26)
        text = font.render(f'Height Score: {self.height_score}', True, pygame.Color('yellow'))
        text.get_rect()
        SCREEN.blit(text, (10, 10))

    def draw_current_score(self):
        font = pygame.font.Font(None, 26)
        text = font.render(f'Height Score: {self.score}', True, pygame.Color('white'))
        text.get_rect()
        SCREEN.blit(text, (10, 40))

    def draw_level(self):
        font = pygame.font.Font(None, 26)
        text = font.render(f'Level: {self.level}', True, pygame.Color('yellow'))
        text.get_rect()
        SCREEN.blit(text, (SCREEN_WIDTH - 100, 10))

    def energy_bar(self):
        font = pygame.font.Font(None, 26)
        text = font.render(f'Energy:', True, pygame.Color('white'))
        text.get_rect()
        SCREEN.blit(text, (SCREEN_WIDTH - 220, 40))
        # bottom red
        bar = pygame.Rect(SCREEN_WIDTH - 140, 40, 120, 20)
        pygame.draw.rect(SCREEN, (255, 0, 0), bar, border_radius=2)
        # up green
        bar = pygame.Rect(SCREEN_WIDTH - 140, 40, self.energy_power, 20)
        pygame.draw.rect(SCREEN, (0, 255, 0), bar, border_radius=2)

    def energy_bar_boss(self):
        font = pygame.font.Font(None, 26)
        text = font.render(f'Boss Energy:', True, pygame.Color('white'))
        text.get_rect()
        SCREEN.blit(text, (SCREEN_WIDTH // 2 - 144, 40))
        # bottom red
        bar = pygame.Rect(SCREEN_WIDTH // 2 - 20, 40, 120, 20)
        pygame.draw.rect(SCREEN, (255, 0, 0), bar, border_radius=2)
        # up green
        bar = pygame.Rect(SCREEN_WIDTH // 2 - 20, 40, self.energy_power_boss, 20)
        pygame.draw.rect(SCREEN, (0, 255, 0), bar, border_radius=2)

    def update_table(self):
        self.draw_height_score()
        self.draw_current_score()
        self.draw_level()
        self.energy_bar()
        if game_state.boos_battle:
            self.energy_bar_boss()


class Sound:
    @staticmethod
    def play_sound(sound_file, volume=0.2, loops=0):
        play = pygame.mixer.Sound(sound_file)
        play.set_volume(volume)
        play.play(loops)

    def intro_music(self):
        self.play_sound('./src/sounds/background_music/intro_music.wav')

    def final_music(self):
        self.play_sound('./src/sounds/background_music/bg_final_music.mp3', 0.2, -1)

    def game_music(self):
        self.play_sound('./src/sounds/background_music/game_music.mp3', 0.2, -1)

    def boss_music(self):
        self.play_sound('./src/sounds/background_music/boss_music.mp3', 0.2, -1)

    def get_ready(self):
        self.play_sound('./src/sounds/get_ready/getReady.wav')

    def sound_final_explosion(self):
        self.play_sound('./src/sounds/bomb/final_explosion.wav')

    def sound_bomb(self):
        self.play_sound('./src/sounds/bomb/bomb_3.wav')

    def sound_ship_movie(self):
        self.play_sound('./src/sounds/ship/movie_ship.wav')

    def sound_ship_crash(self):
        self.play_sound('./src/sounds/ship/crash_ship.wav')

    def laser_gun_sound(self):
        self.play_sound('./src/sounds/ship/blaster_shot/blaster_shot_2.wav')

    def alien_ship_two_movie(self):
        self.play_sound('./src/sounds/aliens/alien_ship_two_move.wav')

    def alien_laser_two_gun_sound(self):
        self.play_sound('./src/sounds/aliens/laser_3.wav')

    def alien_laser_gun_sound(self):
        self.play_sound('./src/sounds/aliens/laser_2.wav')

    def alien_ship_explosion(self):
        self.play_sound('./src/sounds/bomb/bomb_1.wav')

    def ship_little_explosion(self):
        self.play_sound('./src/sounds/bomb/bomb_2.wav')

    def ship_big_explosion(self):
        self.play_sound('./src/sounds/bomb/bomb_3.wav')

    def sound_warning(self):
        self.play_sound('./src/sounds/ship/alarm/warning_two.wav')

    def level_complete(self):
        self.play_sound('./src/sounds/level_complete/level_complete.wav', 1.0)

    def click_button(self):
        self.play_sound('./src/sounds/button_click/click.wav')


# =====================================
play_sound = Sound()
table = Table()
table.get_height_score_from_file()
ship = Ship()
aliens_two = AliensTwo()
boss = AlienBoss()

# ====================================

# ================ Sprite Groups
ship_group = pygame.sprite.GroupSingle(ship)
laser_ship_group = pygame.sprite.Group()
aliens_group = pygame.sprite.Group()
aliens_laser_group = pygame.sprite.Group()
aliens_two_group = pygame.sprite.GroupSingle(aliens_two)
boss_group = pygame.sprite.GroupSingle(boss)


# ================Create new Classes


# create aliens dish flot
def create_aliens_flot():
    for row in range(Aliens.num_row_enemy):
        for dish in range(Aliens.num_col_enemy):
            aliens = Aliens((100 + dish * 80, 100 + row * 70))
            aliens_group.add(aliens)


# create second aliens
def create_second_aliens_ship():
    aliens_two_group.add(aliens_two)


# ================ ADD to GROUP

# ========================================================================== game Stage process switch
class GameState:
    def __init__(self):
        self.state = 'intro'
        self.x_pos = 0  # start satellite pos x
        self.y_pos = 450  # start satellite pos y
        self.font_size = 10  # text begin size
        self.boos_battle = False
        self.is_music_play = False

    def intro(self):  # ========================== INTRO STATE
        # draw background
        background_image('./src/backgrounds/bg_intro_600_800.png', 0)
        #  draw satellite
        intro_satellite_image = pygame.image.load('./src/icons/intro_satellite/satellite_32.png')
        intro_satellite_block_rect = pygame.Rect(self.x_pos, self.y_pos, 10, 10)
        if self.y_pos > 0:
            SCREEN.blit(intro_satellite_image, intro_satellite_block_rect)
            self.x_pos += 1
            self.y_pos -= 1

        # text labels
        font = pygame.font.Font(None, 26)
        text_copyright = font.render("Copyright - 2021", True, (0, 160, 255))
        text_pos_two = text_copyright.get_rect(center=(80, SCREEN_HEIGHT - 20))
        SCREEN.blit(text_copyright, text_pos_two)

        text = font.render("By Abaddon", True, (0, 160, 255))
        text_pos = text.get_rect(center=(SCREEN_WIDTH - 60, SCREEN_HEIGHT - 20))
        SCREEN.blit(text, text_pos)

        # background music
        play_sound.intro_music()  # play intro music
        # pygame.mixer.music.set_volume(volume_music)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:  # START GAME
                    pygame.mixer.stop()
                    self.state = 'get_ready'

                    play_sound.game_music()  # background music level
                    play_sound.get_ready()
                    Message.get_ready()
                    pygame.display.update()  # update screen

    def get_ready(self):  # ========================== GET READY STATE
        self.state = 'get_ready'
        SCREEN.fill(pygame.Color('black'))  # clear screen
        background_image()  # draw background
        table.energy_power = 120
        table.energy_power_boss = AlienBoss.energy  # 122
        table.update_table()
        Message.press_space_to_start()
        Message.fps_message()

        # check is boss level fight
        if table.level % boss.level_for_battle == 0 and table.level != 0 and boss.alive:
            Message.boss_battle()
        elif not boss.alive:
            Message.boss_destroyed()
        else:
            Message.get_ready()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if table.level % boss.level_for_battle == 0 and table.level != 0 and boss.alive:
                        ship_group.add(ship)  # add new ship to boss level
                        ship.ship_restore_begin_position()  # go ship to start position
                        self.state = 'the_boss'
                    else:
                        boss.alive = True
                        self.state = 'levels'  # go to state and begin Game

        pygame.display.update()  # update screen

    # ========================== LEVELS STATE
    def levels(self):
        background_image()  # draw background

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)

        #  --------------------------------------  # Pause
        if pygame.key.get_pressed()[pygame.K_p]:
            self.state = 'pause'
            return

        if len(ship_group) == 0 and ship.rect.y > 300:  # check is ship on start position
            ship_group.add(ship)  # add new ship to new level

        # key control movement
        ship.ship_key_control_movement()
        # Update
        ship.update()
        ship.ship_movie_update()  # ship Update
        ship.check_ship_in_border_screen()  # check ship position

        # UPDATE SPRITE GROUPS
        laser_ship_group.update()
        aliens_laser_group.update()
        aliens_group.update()
        aliens_two_group.update()

        # DRAW SPRITE GROUPS
        ship_group.draw(SCREEN)
        laser_ship_group.draw(SCREEN)
        aliens_laser_group.draw(SCREEN)
        aliens_two_group.draw(SCREEN)
        aliens_group.draw(SCREEN)

        # ===============================  draw laser
        AliensLaser.num_of_shot_per_second = 5  # restore default number of shots

        if table.level >= 5:  # increase laser shot every new level by one
            AliensLaser.num_of_shot_per_second = table.level

        if len(aliens_group) and len(aliens_group) <= 5:  # decrease laser shot to number of aliens
            AliensLaser.num_of_shot_per_second = len(aliens_group)

        current_time = pygame.time.get_ticks()
        tick = int(str(current_time)[-4])  # get any seconds from time
        # shot per one second , number of shot , and check if some aliens is alive

        if tick & 1 and len(aliens_laser_group) < AliensLaser.num_of_shot_per_second and len(aliens_group) > 0:
            AliensLaser.aliens_laser_shot()

            if len(aliens_two_group) == 0 and tick > 5 and table.level >= 7:  # create nwe aliens two if not exist
                # aliens_two.direction.x = -1
                aliens_two.rect.x = -60
                aliens_two.rect.y = random.randint(SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2 + 250)
                aliens_two.create_second_aliens()

        #  update table
        table.update_table()
        fps()

    def the_boss(self):  # ========================== THE BOSS STATE
        if not game_state.boos_battle:
            # REMOVE ALL GROUPS from screen
            aliens_group.empty()
            aliens_laser_group.empty()
            aliens_two_group.empty()
            pygame.event.clear()  # clear all events in queue
            boss_group.add(boss)  # add boss to Screen
            pygame.mixer.stop()  # stop old music
            play_sound.boss_music()  # play new music for Boss level
            game_state.boos_battle = True  # battle begin
            # ship.position = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 60)
            boss.rect.center = (SCREEN_WIDTH // 2 + 30, 100)  # restore start position
            self.state = 'the_boss'  # switch to state the_boss loop infinity

        # draw background
        background_image()

        for event in pygame.event.get():  # EXIT
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)

        if table.energy_power_boss <= 0:
            boss.alive = False  # boss dead
            boss.speed_movie_boss_dish = 10  # restore default boss speed
            self.boos_battle = False  # restore battle to false
            boss_group.empty()
            pygame.mixer.stop()
            play_sound.sound_bomb()  # play sound explosion

            for i in range(1, 20):  # explosion animation
                increase_pic = 100 * i
                exp = pygame.image.load('./src/icons/explosion/boss_exp_1.jpeg')
                explosion = pygame.transform.scale(exp, (increase_pic, increase_pic))
                central_pos = explosion.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                SCREEN.blit(explosion, central_pos)
                pygame.display.update()
                pygame.time.delay(50)

            table.score += table.points_boss  # add point to score
            boss.speed_movie_boss_dish = 10  # reset speed to default
            self.state = 'get_ready'  # switch to levels to continue game

        # DRAW SPRITE GROUPS
        ship_group.draw(SCREEN)
        laser_ship_group.draw(SCREEN)
        boss_group.draw(SCREEN)

        # UPDATE SPRITE GROUPS
        laser_ship_group.update()
        boss_group.update()

        # Update
        ship.update()
        ship.ship_movie_update()  # ship Update
        ship.check_ship_in_border_screen()  # chek ship position
        ship.ship_key_control_movement()  # key control movement

        #  update table
        table.update_table()

    def game_over(self):  # ========================== GAME OVER STATE
        if ship.ship_destroyed:
            pygame.event.clear()  # clear all events in queue
            SCREEN.fill(pygame.Color('black'))
            pygame.mixer.stop()
            play_sound.sound_final_explosion()  # play sound bomb
            for i in range(17):
                increase_pic = 100 * i
                exp = pygame.image.load('./src/icons/explosion/big_exp_1.jpeg')
                explosion = pygame.transform.scale(exp, (increase_pic, increase_pic))
                central_pos = explosion.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
                SCREEN.blit(explosion, central_pos)
                pygame.display.update()
                pygame.time.delay(70)
                ship.ship_destroyed = False

        self.state = 'game_over'  # switch to state game over

        if table.energy_power == 0:
            self.font_size = 10  # restore text Game Over font_size
            pygame.mixer.stop()  # stop all other sounds
            play_sound.final_music()  # play final music
            table.write_new_height_score_in_file()  # write record to file
            table.energy_power = -1  # stop loop

        for event in pygame.event.get():  # EXIT
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)

            if event.type == pygame.KEYDOWN:  # EXIT
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit(1)

                if event.key == pygame.K_LEFT:
                    self.state = 'controls'
                    play_sound.click_button()
                if event.key == pygame.K_RIGHT:
                    self.state = 'legend'
                    play_sound.click_button()
                if event.key == pygame.K_SPACE:  # START NEW GAME
                    self.state = 'intro'  # switch to intro state
                    # RESET ALL / Table aliens and ship
                    pygame.mixer.stop()
                    table.energy_power = 110
                    table.score = 0
                    table.level = 0
                    laser_ship_group.empty()
                    aliens_laser_group.empty()
                    aliens_two_group.empty()
                    aliens_group.empty()
                    boss_group.empty()
                    game_state.boos_battle = False

                    ship.ship_restore_begin_position()

        bg_game_over = pygame.image.load('./src/backgrounds/bg_game_over_1000_700.jpeg')
        game_over_rect = pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)
        SCREEN.blit(bg_game_over, game_over_rect)  # show explosion

        font = pygame.font.Font(None, self.font_size)
        text = font.render('GAME OVER', True, (255, 80 + self.font_size, 255))
        text_pos = text.get_rect(center=(SCREEN_WIDTH // 2, self.font_size * 2))
        SCREEN.blit(text, text_pos)
        if self.font_size < 150:
            self.font_size += 2

        font = pygame.font.Font(None, 30)
        text = font.render('PRESS SPACE TO BEGIN', True, (0, 180, 255))
        text_pos_exit = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 20))
        SCREEN.blit(text, text_pos_exit)

        img_left_arrow = pygame.transform.rotate(pygame.image.load('./src/icons/arrows/blue.png'), 270)
        rect_pos = img_left_arrow.get_rect(center=(50, SCREEN_HEIGHT - 25))
        SCREEN.blit(img_left_arrow, rect_pos)

        font = pygame.font.Font(None, 30)
        text = font.render('Controls', True, (0, 180, 255))
        text_pos_exit = text.get_rect(center=(133, SCREEN_HEIGHT - 25))
        SCREEN.blit(text, text_pos_exit)

        img_left_arrow = pygame.transform.rotate(pygame.image.load('./src/icons/arrows/blue.png'), 90)
        rect_pos = img_left_arrow.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 25))
        SCREEN.blit(img_left_arrow, rect_pos)

        font = pygame.font.Font(None, 30)
        text = font.render('Legend', True, (0, 180, 255))
        text_pos_exit = text.get_rect(center=(SCREEN_WIDTH - 130, SCREEN_HEIGHT - 25))
        SCREEN.blit(text, text_pos_exit)

    def controls(self):
        background_image('./src/backgrounds/bg_controls_img_2.png', -20)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # EXIT
                pygame.quit()
                sys.exit(1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RIGHT:
                    play_sound.click_button()
                    self.state = 'game_over'

        img_left_arrow = pygame.transform.rotate(pygame.image.load('./src/icons/arrows/red.png'), 90)
        rect_pos = img_left_arrow.get_rect(center=(SCREEN_WIDTH - 50, SCREEN_HEIGHT - 25))
        SCREEN.blit(img_left_arrow, rect_pos)

        font = pygame.font.Font(None, 30)
        text = font.render('BACK', True, (255, 70, 90))
        text_pos_exit = text.get_rect(center=(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 25))
        SCREEN.blit(text, text_pos_exit)

    def legend(self):
        background_image('./src/backgrounds/bg_legend.png', -20)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    play_sound.click_button()
                    self.state = 'game_over'

        img_left_arrow = pygame.transform.rotate(pygame.image.load('./src/icons/arrows/red.png'), 270)
        rect_pos = img_left_arrow.get_rect(center=(50, SCREEN_HEIGHT - 25))
        SCREEN.blit(img_left_arrow, rect_pos)

        font = pygame.font.Font(None, 30)
        text = font.render('BACK', True, (255, 70, 90))
        text_pos_exit = text.get_rect(center=(120, SCREEN_HEIGHT - 25))
        SCREEN.blit(text, text_pos_exit)
    
    def pause(self):
        SCREEN.fill('black')
        img = pygame.image.load('src/icons/pause/extraterrestrial.png')
        SCREEN.blit(img, [20, 20])
        Message.pause()
        Message.press_return_to_continue()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit(1)
        if pygame.key.get_pressed()[pygame.K_RETURN]:
            pygame.time.delay(0)
            self.state = 'levels'
        
    def state_manager(self):
        # print(self.state)
        if self.state == 'intro':
            self.intro()
        if self.state == 'get_ready':
            self.get_ready()
        if self.state == 'levels':
            self.levels()
        if self.state == 'the_boss':
            self.the_boss()
        if self.state == 'game_over':
            self.game_over()
        if self.state == 'controls':
            self.controls()
        if self.state == 'legend':
            self.legend()
        if self.state == 'pause':
            self.pause()


#  ========================================================================== create new GameState
game_state = GameState()

#  ========================================================================== loop
while True:
    SCREEN.fill(pygame.Color('black'))
    game_state.state_manager()
    pygame.display.update()
    clock.tick(current_fps)
    time_counter = pygame.time.get_ticks()


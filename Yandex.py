import os
import pygame
import sys
import random


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    if colorkey is not None:
        image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


FPS = 50


def terminate():
    pygame.quit()
    sys.exit()


def start_screen():
    intro_text = ["SPACE RIDER", "",
                  "Правила игры:", "",
                  "Вам нужно уничтожать корабли",
                  "противников до того как они скроются.",
                  "При этом, избегая попаданий по вам.", "",
                  "Управление:", "",
                  "Перемещение - с помощью стрелок",
                  "Выстрел - пробел"]

    pygame.init()
    size = 500, 450
    screen = pygame.display.set_mode(size)

    fon = load_image('fon.jpg')
    fon = pygame.transform.scale(fon, size)
    clock = pygame.time.Clock()
    screen.blit(fon, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('yellow'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                start_the_game()
        pygame.display.flip()
        clock.tick(FPS)


def start_the_game():
    pygame.init()
    size = 800, 600
    screen = pygame.display.set_mode(size)

    fon = load_image('fon.jpg')
    fon = pygame.transform.scale(fon, size)

    ships = pygame.sprite.Group()
    ship = Ship(ships)
    ships.add(ship)

    cartridges = pygame.sprite.Group()

    enemys = pygame.sprite.Group()

    bullets = pygame.sprite.Group()

    clock = pygame.time.Clock()
    time = 0
    number = 5

    score = 0

    shot_sound = pygame.mixer.Sound('./data/shot.wav')
    enemy_shot_sound = pygame.mixer.Sound('./data/enemy_shot.wav')
    boom_sound = pygame.mixer.Sound('./data/boom.wav')

    pygame.mixer.music.load('./data/main.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(0.3)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    ships.sprites()[0].left()
                elif event.key == pygame.K_RIGHT:
                    ships.sprites()[0].right()
                elif event.key == pygame.K_UP:
                    ships.sprites()[0].up()
                elif event.key == pygame.K_DOWN:
                    ships.sprites()[0].down()
                elif event.key == pygame.K_SPACE:
                    cartridge = Cartridge(cartridges, (ships.sprites()[0].rect.x, ships.sprites()[0].rect.y), enemys, score)
                    cartridges.add(cartridge)
                    shot_sound.play()
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    ships.sprites()[0].stop_x()
                elif event.key == pygame.K_RIGHT:
                    ships.sprites()[0].stop_x()
                elif event.key == pygame.K_UP:
                    ships.sprites()[0].stop_y()
                elif event.key == pygame.K_DOWN:
                    ships.sprites()[0].stop_y()
        time += clock.tick() / 1000
        screen.blit(fon, (0, 0))
        ships.draw(screen)
        cartridges.draw(screen)
        enemys.draw(screen)
        bullets.draw(screen)
        if len(ships) > 0:
            for s in ships:
                s.move()
        if len(cartridges) > 0:
            for s in cartridges:
                if s.move():
                    boom_sound.play()
                    score += 1
        if len(bullets) > 0:
            for b in bullets:
                b.move()
        if len(enemys) > 0:
            for e in enemys:
                e.move()
                if e.rect.y == 600:
                    boom_sound.play()
                    end_game(score)
                    terminate()
        if time > number:
            time = 0
            enemy = Enemy(enemys, ships, score)
            enemys.add(enemy)
            number = random.randint(0, 5)
        for i in enemys:
            if random.randint(1, 2) == 2 and int(time) == 1 and i.x:
                bullet = Bullet(bullets, (i.rect.x, i.rect.y), ships, score)
                bullets.add(bullet)
                enemy_shot_sound.play()
                i.x = False
            if int(time) == 2:
                i.x = True

        f1 = pygame.font.Font(None, 36)
        text1 = f1.render(f'Счет: {score}', 1, pygame.Color('white'))

        screen.blit(text1, (700, 10))

        pygame.display.flip()


class Ship(pygame.sprite.Sprite):
    def __init__(self, group):
        super().__init__(group)
        self.group = group
        self.image = load_image("ship.jpg", -1)
        self.image = pygame.transform.scale(self.image, (100, 90))
        self.rect = self.image.get_rect()
        self.rect.x = 400 - 50
        self.rect.y = 600 - 90
        self.speed_x = 0
        self.speed_y = 0
        self.clock = pygame.time.Clock()
        self.y = self.rect.x
        self.x = self.rect.y

    def up(self):
        self.speed_y = -1

    def down(self):
        self.speed_y = 1

    def left(self):
        self.speed_x = -1

    def right(self):
        self.speed_x = 1

    def stop_x(self):
        self.speed_x = 0

    def stop_y(self):
        self.speed_y = 0

    def move(self):
        t = self.clock.tick()
        self.y += (100 * t / 1000) * self.speed_y
        if self.y > 600 - 100:
            self.y = 600 - 100
        if self.y < 0:
            self.y = 0
        self.rect.y = int(self.y)
        self.x += (100 * t / 1000) * self.speed_x
        if self.x > 800 - 100:
            self.x = 800 - 100
        if self.x < 0:
            self.x = 0
        self.rect.x = int(self.x)


class Cartridge(pygame.sprite.Sprite):
    def __init__(self, group, pos, enemys, score):
        self.enemys = enemys
        self.score = score
        super().__init__(group)
        self.group = group
        rec = pygame.Surface((10, 20))
        rec.fill(pygame.Color('green'))
        self.image = rec
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] + 50 - 5
        self.rect.y = pos[1] + 40 - 10
        self.clock = pygame.time.Clock()
        self.y = 0

    def move(self):
        self.y += 200 * self.clock.tick() / 1000
        self.rect.y -= int(self.y)
        self.y %= 1
        for i in self.enemys:
            if pygame.sprite.collide_rect(self, i):
                i.kill()
                self.kill()
                return True


class Enemy(pygame.sprite.Sprite):
    def __init__(self, group, ships, score):
        super().__init__(group)
        self.group = group
        self.score = score
        self.ships = ships
        self.image = load_image("enemy.jpg", -1)
        self.image = pygame.transform.scale(self.image, (100, 90))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint(0, 800 - 90)
        self.rect.y = 0
        self.clock = pygame.time.Clock()
        self.y = 0
        self.x = True

    def move(self):
        self.y += 25 * self.clock.tick() / 1000
        self.rect.y += int(self.y)
        self.y %= 1
        for i in self.ships:
            if pygame.sprite.collide_rect(self, i) and self != i:
                end_game(self.score)
                terminate()


class Bullet(pygame.sprite.Sprite):
    def __init__(self, group, pos, ships, score):
        self.ships = ships
        self.score = score
        super().__init__(group)
        self.group = group
        rec = pygame.Surface((10, 20))
        rec.fill(pygame.Color('red'))
        self.image = rec
        self.rect = self.image.get_rect()
        self.rect.x = pos[0] + 50 - 5
        self.rect.y = pos[1] + 40 - 10
        self.clock = pygame.time.Clock()
        self.y = 0

    def move(self):
        self.y += 100 * self.clock.tick() / 1000
        self.rect.y += int(self.y)
        self.y %= 1
        for i in self.ships:
            if pygame.sprite.collide_rect(self, i):
                end_game(self.score)
                self.kill()
                terminate()


class Gameover(pygame.sprite.Sprite):
    def __init__(self, group, gameover_image):
        super().__init__(group)
        self.group = group
        self.x = 0
        self.n = 1
        self.clock = pygame.time.Clock()
        self.clock.tick()
        super().__init__(group)
        self.group = group
        gameover_image = pygame.transform.scale(gameover_image, (800, 600))
        self.image = gameover_image
        self.rect = self.image.get_rect()
        self.rect.x = -600
        self.rect.y = 0

    def move(self):
        self.x += (200 * self.clock.tick() / 1000)
        self.rect.x += int(self.x) * self.n
        self.x %= 1
        if self.rect.x > 0:
            self.n = 0
            self.rect.x = 0
            return True


def end_game(score):
    pygame.init()
    size = 800, 600
    screen = pygame.display.set_mode(size)

    fon = load_image('fon.jpg')
    fon = pygame.transform.scale(fon, size)
    screen.blit(fon, (0, 0))

    running = True

    all_sprites = pygame.sprite.Group()
    gameover_image = load_image("gameover.png")
    Gameover(all_sprites, gameover_image)

    x = False

    pygame.mixer.music.load('./data/game_over.mp3')
    pygame.mixer.music.play()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        screen.blit(fon, (0, 0))
        all_sprites.draw(screen)
        if all_sprites.sprites()[0].move() or x:
            f1 = pygame.font.SysFont('arial', 40)
            text1 = f1.render(f'Ваш итоговый счет: {score}', 1, pygame.Color('yellow'))
            x = True

            screen.blit(text1, (220, 285))

        pygame.display.flip()


start_screen()

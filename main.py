import pygame
import random
import sys

pygame.init()

# Настройки экрана
WIDTH, HEIGHT = 800, 600
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Shooter")

FPS = 60

# Загрузка картинок
player_img = pygame.image.load("images/player.png")
player_img = pygame.transform.scale(player_img, (50, 40))

enemy_img = pygame.image.load("images/enemy.png")
enemy_img = pygame.transform.scale(enemy_img, (40, 30))

background_img = pygame.image.load("images/background.png")
background_img = pygame.transform.scale(background_img, (WIDTH, HEIGHT))

heart_img = pygame.image.load("images/heart.png")
heart_img = pygame.transform.scale(heart_img, (30, 30))

bullet_img = pygame.image.load("images/bullet.png")
bullet_img = pygame.transform.scale(bullet_img, (10, 20))

# Шрифт
font = pygame.font.SysFont("Arial", 36)

# Игрок
class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 60, 50, 40)
        self.speed = 5
        self.bullets = []
        self.max_shots = 4
        self.shots_left = self.max_shots
        self.reload_time = 1000  # 1 секунда
        self.last_shot_time = 0

    def move(self, keys):
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

    def shoot(self):
        now = pygame.time.get_ticks()
        if self.shots_left > 0:
            bullet = Bullet(self.rect.centerx - 5, self.rect.y)
            self.bullets.append(bullet)
            self.shots_left -= 1
            if self.shots_left == 0:
                self.last_shot_time = now
        else:
            if now - self.last_shot_time >= self.reload_time:
                self.shots_left = self.max_shots

    def update_bullets(self):
        for bullet in self.bullets[:]:
            bullet.move()
            if bullet.rect.y < 0:
                self.bullets.remove(bullet)

    def draw(self, surface):
        surface.blit(player_img, (self.rect.x, self.rect.y))
        for bullet in self.bullets:
            bullet.draw(surface)

class Bullet:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 10, 20)
        self.speed = 10

    def move(self):
        self.rect.y -= self.speed

    def draw(self, surface):
        surface.blit(bullet_img, (self.rect.x, self.rect.y))

class Enemy:
    def __init__(self):
        self.rect = pygame.Rect(random.randint(0, WIDTH - 40), -40, 40, 30)
        self.speed = random.randint(2, 4)

    def move(self):
        self.rect.y += self.speed

    def draw(self, surface):
        surface.blit(enemy_img, (self.rect.x, self.rect.y))

# Функция сброса игры
def reset_game():
    global player, enemies, lives, score, enemy_spawn_delay
    player = Player()
    enemies = []
    lives = 3
    score = 0
    enemy_spawn_delay = 30

# Переменные игры
player = Player()
enemies = []
lives = 3
score = 0
enemy_spawn_delay = 30
enemy_timer = 0

# Основной цикл игры
clock = pygame.time.Clock()
running = True
game_over = False

while running:
    clock.tick(FPS)
    win.blit(background_img, (0, 0))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    if not game_over:
        keys = pygame.key.get_pressed()
        player.move(keys)
        if keys[pygame.K_SPACE]:
            player.shoot()

        # Спавн врагов
        enemy_timer += 1
        if enemy_timer >= enemy_spawn_delay:
            enemies.append(Enemy())
            enemy_timer = 0

        # Обновление пуль
        player.update_bullets()

        # Обновление врагов
        for enemy in enemies[:]:
            enemy.move()
            if enemy.rect.y > HEIGHT:
                enemies.remove(enemy)

        # Проверка попаданий
        for bullet in player.bullets[:]:
            for enemy in enemies[:]:
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in player.bullets:
                        player.bullets.remove(bullet)
                    if enemy in enemies:
                        enemies.remove(enemy)
                    score += 1
                    break

        # Проверка столкновения игрока с врагами
        for enemy in enemies[:]:
            if player.rect.colliderect(enemy.rect):
                enemies.remove(enemy)
                lives -= 1
                if lives <= 0:
                    game_over = True

        # Повышение сложности
        if score % 10 == 0 and score != 0:
            enemy_spawn_delay = max(10, enemy_spawn_delay - 1)

        # Отрисовка объектов
        player.draw(win)
        for enemy in enemies:
            enemy.draw(win)

        # Отрисовка жизней
        for i in range(lives):
            win.blit(heart_img, (10 + i * 40, 10))

        # Отрисовка очков
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        win.blit(score_text, (WIDTH - 200, 10))

    else:
        game_over_text = font.render("GAME OVER", True, (255, 0, 0))
        restart_text = font.render("Press R to Restart", True, (255, 255, 255))
        win.blit(game_over_text, (WIDTH // 2 - game_over_text.get_width() // 2, HEIGHT // 2 - 50))
        win.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 10))

        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            reset_game()
            game_over = False

    pygame.display.update()

pygame.quit()
sys.exit()

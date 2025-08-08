import pygame
import random
import sys
import time

# Inicjalizacja
pygame.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Podbij piłkę!")

# Kolory
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)

# Parametry piłki
radius = 30
x = WIDTH // 2
y = HEIGHT // 2
velocity = 0
gravity = 0.05
mass = 1.0
kick_strength = -10

# Wynik
score = 0
font = pygame.font.SysFont(None, 50)

# Pieniążek
coin_radius = 20
coin_x, coin_y = 0, 0
coin_visible = False
coin_timer = 0
next_coin_time = random.uniform(5, 10)  # pierwsze pojawienie się
last_coin_check = time.time()

# Czerwony pieniążek (pułapka)
bad_coin_radius = 30
bad_coin_x, bad_coin_y = 0, 0
bad_coin_visible = False
bad_coin_timer = 0
next_bad_coin_time = random.uniform(8, 12)
last_bad_coin_check = time.time()

# Stan gry
clock = pygame.time.Clock()
running = True
game_started = False
game_over = False

def reset_ball_position():
    global x, y
    x = random.randint(radius, WIDTH - radius)
    y = random.randint(radius, HEIGHT // 2 - radius)

def spawn_coin():
    global coin_x, coin_y, coin_visible, coin_timer
    coin_x = random.randint(coin_radius, WIDTH - coin_radius)
    coin_y = random.randint(coin_radius, HEIGHT - coin_radius)
    coin_visible = True
    coin_timer = time.time() + 2  # 2 sekundy widoczny

reset_ball_position()

while running:
    screen.fill(WHITE)

    now = time.time()

    # Obsługa pieniążków tylko w trakcie aktywnej gry
    if not coin_visible and not game_over and game_started and now - last_coin_check > next_coin_time:
        spawn_coin()
        last_coin_check = now
        next_coin_time = random.uniform(5, 10)

    if coin_visible and now > coin_timer:
        coin_visible = False

    # Obsługa czerwonych pieniążków tylko w trakcie gry
    if not bad_coin_visible and not game_over and game_started and now - last_bad_coin_check > next_bad_coin_time:
        bad_coin_x = random.randint(bad_coin_radius, WIDTH - bad_coin_radius)
        bad_coin_y = random.randint(bad_coin_radius, HEIGHT - bad_coin_radius)
        bad_coin_visible = True
        bad_coin_timer = time.time() + 3  # widoczne przez 3 sekundy
        last_bad_coin_check = now
        next_bad_coin_time = random.uniform(8, 12)

    # Czas minął → znikają i odejmujemy punkty
    if bad_coin_visible and now > bad_coin_timer:
        score -= 3
        bad_coin_visible = False

    # Rysuj pieniążek jeśli jest widoczny
    if coin_visible:
        pygame.draw.circle(screen, GOLD, (coin_x, coin_y), coin_radius)
    
    if bad_coin_visible:
        pygame.draw.circle(screen, (255, 0, 0), (bad_coin_x, bad_coin_y), bad_coin_radius)

    # Kliknięcie w czerwony pieniążek – nic się nie dzieje, ale znika
    if bad_coin_visible:
        bad_coin_distance = ((mouse_x - bad_coin_x) ** 2 + (mouse_y - bad_coin_y) ** 2) ** 0.5
        if bad_coin_distance <= bad_coin_radius:
            bad_coin_visible = False  # znika, ale bez efektu    

    # Ekran startowy
    if not game_started:
        intro_text = font.render("Kliknij piłkę, aby rozpocząć!", True, BLACK)
        screen.blit(intro_text, (WIDTH // 2 - 250, HEIGHT // 2 - 30))
        pygame.draw.circle(screen, BLUE, (x, int(y)), radius)

    elif game_over:
        over_text = font.render(f"Koniec gry! Wynik: {score}", True, BLACK)
        screen.blit(over_text, (WIDTH // 2 - 250, HEIGHT // 2 - 30))
        pygame.draw.circle(screen, BLUE, (x, int(y)), radius)

    else:
        # Fizyka z masą
        velocity += gravity * mass
        y += velocity

        # Dolna granica (przegrana)
        if y - radius > HEIGHT:
            game_over = True

        # Górna granica
        if y - radius < 0:
            y = radius
            velocity = 0

        # Rysowanie
        pygame.draw.circle(screen, BLUE, (x, int(y)), radius)
        score_text = font.render(f"Wynik: {score}", True, BLACK)
        screen.blit(score_text, (20, 20))

    # Obsługa zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()

            # Kliknięcie w piłkę
            ball_distance = ((mouse_x - x) ** 2 + (mouse_y - y) ** 2) ** 0.5
            if ball_distance <= radius:
                if not game_started:
                    game_started = True
                    velocity = 0
                elif game_over:
                    # Restart
                    score = 0
                    gravity = 0.05
                    mass = 1.0
                    velocity = 0
                    reset_ball_position()
                    game_over = False
                    game_started = False
                else:
                    velocity = kick_strength / mass
                    reset_ball_position()
                    score += 1
                    gravity *= 1.05
                    mass *= 1.05

            # Kliknięcie w pieniążek
            if coin_visible:
                coin_distance = ((mouse_x - coin_x) ** 2 + (mouse_y - coin_y) ** 2) ** 0.5
                if coin_distance <= coin_radius:
                    score += 5
                    coin_visible = False  # znika od razu

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
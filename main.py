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
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)

# Parametry piłki
base_radius = 30
radius = base_radius * 3  # Początkowo 3x większa
x = WIDTH // 2
y = HEIGHT // 2
velocity = 0
gravity = 0.05
mass = 1.0
kick_strength = -10

# Licznik kliknięć dla zmiany rozmiaru
click_count = 0
clicks_for_size_reduction = 5

# Wynik
score = 0
font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 36)

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

# Platformy
class Platform:
    def __init__(self):
        self.width = int(WIDTH * 0.3)  # 30% szerokości ekranu
        self.height = 20
        self.y = HEIGHT - 100  # 100 pikseli od dołu
        self.speed = 2  # piksele na frame
        self.direction = random.choice([-1, 1])  # -1 = lewo, 1 = prawo
        
        if self.direction == 1:  # idzie w prawo
            self.x = -self.width
        else:  # idzie w lewo
            self.x = WIDTH
            
    def update(self):
        self.x += self.speed * self.direction
        
    def draw(self, screen):
        pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2)
        
    def check_collision(self, ball_x, ball_y, ball_radius):
        # Sprawdź czy piłka dotyka platformy
        if (ball_y + ball_radius >= self.y and 
            ball_y - ball_radius <= self.y + self.height and
            ball_x + ball_radius >= self.x and 
            ball_x - ball_radius <= self.x + self.width):
            return True
        return False

platforms = []
next_platform_time = random.uniform(10, 15)
last_platform_check = time.time()

# Stan gry
clock = pygame.time.Clock()
running = True
game_started = False
game_over = False

# Przycisk resetowania
reset_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)

def reset_game():
    global score, gravity, mass, velocity, game_over, game_started
    global coin_visible, bad_coin_visible, coin_timer, bad_coin_timer
    global last_coin_check, last_bad_coin_check, next_coin_time, next_bad_coin_time
    global platforms, next_platform_time, last_platform_check
    global radius, click_count
    
    score = 0
    gravity = 0.05
    mass = 1.0
    velocity = 0
    radius = base_radius * 3  # Resetuj rozmiar piłki
    click_count = 0
    reset_ball_position()
    game_over = False
    game_started = False
    
    # Resetuj pieniążki
    coin_visible = False
    bad_coin_visible = False
    coin_timer = 0
    bad_coin_timer = 0
    last_coin_check = time.time()
    last_bad_coin_check = time.time()
    next_coin_time = random.uniform(5, 10)
    next_bad_coin_time = random.uniform(8, 12)
    
    # Resetuj platformy
    platforms.clear()
    next_platform_time = random.uniform(10, 15)
    last_platform_check = time.time()

def reset_ball_position():
    global x, y
    x = random.randint(int(radius), WIDTH - int(radius))
    y = random.randint(int(radius), HEIGHT // 2 - int(radius))

def spawn_coin():
    global coin_x, coin_y, coin_visible, coin_timer
    coin_x = random.randint(coin_radius, WIDTH - coin_radius)
    coin_y = random.randint(coin_radius, HEIGHT - coin_radius)
    coin_visible = True
    coin_timer = time.time() + 2  # 2 sekundy widoczny

def handle_ball_click():
    global velocity, score, gravity, mass, click_count, radius, x, y
    
    velocity = kick_strength / mass
    reset_ball_position()
    score += 1
    gravity *= 1.05
    mass *= 1.05
    
    # Zwiększ licznik kliknięć
    click_count += 1
    
    # Sprawdź czy należy zmniejszyć piłkę
    if click_count % clicks_for_size_reduction == 0:
        radius *= 0.9  # Zmniejsz o 10%
        # Upewnij się, że piłka nie wyjdzie poza ekran po zmianie rozmiaru
        if x - radius < 0:
            x = radius
        if x + radius > WIDTH:
            x = WIDTH - radius
        if y - radius < 0:
            y = radius

reset_ball_position()

while running:
    screen.fill(WHITE)

    now = time.time()

    # Obsługa platform tylko w trakcie aktywnej gry
    if game_started and not game_over:
        # Spawn nowej platformy
        if now - last_platform_check > next_platform_time:
            platforms.append(Platform())
            last_platform_check = now
            next_platform_time = random.uniform(10, 15)
        
        # Aktualizuj i rysuj platformy
        for platform in platforms[:]:
            platform.update()
            platform.draw(screen)
            
            # Sprawdź kolizję z piłką
            if platform.check_collision(x, y, radius):
                handle_ball_click()
            
            # Usuń platformy, które wyszły poza ekran
            if (platform.direction == 1 and platform.x > WIDTH) or (platform.direction == -1 and platform.x < -platform.width):
                platforms.remove(platform)

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

    # Czas minął → znikają i odejmujemy punkty (tylko jeśli gra nie jest skończona)
    if bad_coin_visible and now > bad_coin_timer and not game_over:
        score -= 3
        bad_coin_visible = False

    # Rysuj pieniążek jeśli jest widoczny (tylko jeśli gra nie jest skończona)
    if coin_visible and not game_over:
        pygame.draw.circle(screen, GOLD, (coin_x, coin_y), coin_radius)
    
    if bad_coin_visible and not game_over:
        pygame.draw.circle(screen, (255, 0, 0), (bad_coin_x, bad_coin_y), bad_coin_radius)

    # Ekran startowy
    if not game_started:
        intro_text = font.render("Kliknij piłkę, aby rozpocząć!", True, BLACK)
        screen.blit(intro_text, (WIDTH // 2 - 250, HEIGHT // 2 - 30))
        pygame.draw.circle(screen, BLUE, (x, int(y)), radius)

    elif game_over:
        # Ekran końcowy z przyciskiem resetowania
        over_text = font.render(f"Koniec gry! Wynik: {score}", True, BLACK)
        screen.blit(over_text, (WIDTH // 2 - 200, HEIGHT // 2 - 80))
        
        # Rysuj przycisk resetowania
        pygame.draw.rect(screen, GREEN, reset_button_rect)
        pygame.draw.rect(screen, BLACK, reset_button_rect, 3)
        reset_text = small_font.render("Resetuj grę", True, BLACK)
        reset_text_rect = reset_text.get_rect(center=reset_button_rect.center)
        screen.blit(reset_text, reset_text_rect)
        
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
                elif not game_over:
                    handle_ball_click()

            # Kliknięcie w przycisk resetowania
            if game_over and reset_button_rect.collidepoint(mouse_x, mouse_y):
                reset_game()

            # Kliknięcie w pieniążek
            if coin_visible:
                coin_distance = ((mouse_x - coin_x) ** 2 + (mouse_y - coin_y) ** 2) ** 0.5
                if coin_distance <= coin_radius:
                    score += 5
                    coin_visible = False  # znika od razu

            # Kliknięcie w czerwony pieniążek – nic się nie dzieje, ale znika
            if bad_coin_visible:
                bad_coin_distance = ((mouse_x - bad_coin_x) ** 2 + (mouse_y - bad_coin_y) ** 2) ** 0.5
                if bad_coin_distance <= bad_coin_radius:
                    bad_coin_visible = False  # znika, ale bez efektu    

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
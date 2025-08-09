import pygame
import random
import sys
import time
import math  # sqrt, trig
from typing import List

# ================== INIT ==================
pygame.init()
pygame.mixer.init()
WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Podbij piłkę!")

# ================== AUDIO (opcjonalnie) ==================
try:
    pygame.mixer.music.load("music.mp3")
    music_loaded = True
except pygame.error:
    print("Nie można załadować music.mp3 (pomijam).")
    music_loaded = False

try:
    pop_sound = pygame.mixer.Sound("pop.wav")
except Exception:
    pop_sound = None

# ================== ASSETY ==================
bubble_img = None
bg_img = None
platform_img_raw = None
yellow_star_img = None
red_star_img = None

try:
    bubble_img = pygame.image.load("banka.png").convert_alpha()
except Exception as e:
    print("Nie mogę wczytać banka.png – użyję kółka. Powód:", e)

try:
    bg_img = pygame.image.load("background.png").convert()
except Exception as e:
    print("Nie mogę wczytać background.png – użyję białego tła. Powód:", e)

try:
    platform_img_raw = pygame.image.load("platform.png").convert_alpha()
except Exception as e:
    print("Nie mogę wczytać platform.png – użyję prostokąta. Powód:", e)

try:
    yellow_star_img = pygame.image.load("yellow-star.png").convert_alpha()
except Exception as e:
    print("Nie mogę wczytać yellow-star.png – żółta gwiazdka nie będzie wyświetlana. Powód:", e)

try:
    red_star_img = pygame.image.load("red-star.png").convert_alpha()
except Exception as e:
    print("Nie mogę wczytać red-star.png – czerwona gwiazdka nie będzie wyświetlana. Powód:", e)

# cache’owanie skalowanych assetów
_bubble_cache = {}
_platform_cache = {}
_coin_cache = {}

def get_bubble_surface(r):
    """Zwraca przeskalowaną bańkę (2r x 2r) lub None jeśli brak pliku."""
    r = int(max(1, r))
    if bubble_img is None:
        return None
    if r in _bubble_cache:
        return _bubble_cache[r]
    surf = pygame.transform.smoothscale(bubble_img, (r*2, r*2))
    _bubble_cache[r] = surf
    return surf

def get_platform_surface(width, height, direction):
    """Zwraca przeskalowany sprite platformy."""
    if platform_img_raw is None:
        return None
    key = (int(width), int(height), int(direction))
    if key in _platform_cache:
        return _platform_cache[key]
    surf = pygame.transform.smoothscale(platform_img_raw, (int(width), int(height)))
    if direction == -1:
        surf = pygame.transform.flip(surf, True, False)
    _platform_cache[key] = surf
    return surf

def get_coin_surface(img, radius):
    """Zwraca przeskalowaną grafikę monety/gwiazdy."""
    if img is None:
        return None
    key = (id(img), radius)
    if key in _coin_cache:
        return _coin_cache[key]
    size = radius * 2
    surf = pygame.transform.smoothscale(img, (size, size))
    _coin_cache[key] = surf
    return surf

# ================== TŁO ==================
def draw_background():
    """Fit background.png on screen (contain, centered)."""
    if bg_img is None:
        screen.fill((20, 22, 30))
        return
    bw, bh = bg_img.get_width(), bg_img.get_height()
    scale = min(WIDTH / bw, HEIGHT / bh)
    new_w, new_h = int(bw * scale), int(bh * scale)
    scaled = pygame.transform.smoothscale(bg_img, (new_w, new_h))
    screen.fill((20, 22, 30))
    screen.blit(scaled, ((WIDTH - new_w) // 2, (HEIGHT - new_h) // 2))

# ================== KOLORY + UI ==================
WHITE = (255, 255, 255)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
GOLD = (255, 215, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (128, 128, 128)
UI_GRAY = (60, 60, 60)

font = pygame.font.SysFont(None, 50)
small_font = pygame.font.SysFont(None, 36)

def draw_shadow_text(text, x, y, fnt, color, shadow=(0,0,0), off=2):
    sh = fnt.render(text, True, shadow)
    screen.blit(sh, (x+off, y+off))
    tx = fnt.render(text, True, color)
    screen.blit(tx, (x, y))

def draw_center_panel(lines, box_w=700, box_h=220, panel_alpha=70, text_alpha=230):
    if panel_alpha > 0:
        panel = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        panel.fill((255, 255, 255, panel_alpha))
        screen.blit(panel, (WIDTH//2 - box_w//2, HEIGHT//2 - box_h//2))
    top = HEIGHT//2 - box_h//2 + 20
    for i, (txt, fnt, col) in enumerate(lines):
        s = fnt.render(txt, True, col)
        s.set_alpha(text_alpha)
        r = s.get_rect(center=(WIDTH//2, top + i*48))
        screen.blit(s, r)

# ================== TOP 10 ==================
TOP10_PATH = "top10.txt"
top10: List[int] = []
def load_top10():
    global top10
    top10 = []
    try:
        with open(TOP10_PATH, "r", encoding="utf-8") as f:
            for line in f:
                parts = line.strip().split(".", 1)
                if len(parts) == 2:
                    try:
                        val = int(parts[1])
                        top10.append(val)
                    except:
                        pass
    except FileNotFoundError:
        pass
    top10 = sorted(top10, reverse=True)[:10]
def save_top10():
    with open(TOP10_PATH, "w", encoding="utf-8") as f:
        for i in range(10):
            val = top10[i] if i < len(top10) else None
            f.write(f"{i+1}. {val if val is not None else '-'}\n")
def update_top10(new_score: int):
    global top10
    if new_score > 0:
        top10.append(new_score)
        top10 = sorted(top10, reverse=True)[:10]
def draw_top10_list(x, y, lh=28, color=UI_GRAY):
    for i in range(10):
        val = top10[i] if i < len(top10) else None
        txt = f"{i+1}. {'-' if val is None else val}"
        surf = small_font.render(txt, True, color)
        surf.set_alpha(220)
        screen.blit(surf, (x, y + i*lh))
load_top10()

# ================== STAN PIŁKI ==================
base_radius = 30
radius = base_radius * 3
x = WIDTH // 2
y = HEIGHT // 2
velocity = 0.0
gravity = 0.05
mass = 1.0
kick_strength = -10.0
TARGET_BOUNCE_HEIGHT = 260
COLLISION_OFFSET = 75
click_count = 0
clicks_for_size_reduction = 5
score = 0
best_score = 0

# monety
coin_radius = 20
coin_x, coin_y = 0, 0
coin_visible = False
coin_timer = 0.0
next_coin_time = random.uniform(5, 10)
last_coin_check = time.time()

bad_coin_radius = 30
bad_coin_x, bad_coin_y = 0, 0
bad_coin_visible = False
bad_coin_timer = 0.0
next_bad_coin_time = random.uniform(8, 12)
last_bad_coin_check = time.time()

# ================== PRYSKANIE ==================
bubble_alive = True
bubble_respawn_at = 0.0
POP_DURATION = 0.20
POP_PARTICLES = 18
particles = []
def spawn_pop_particles(cx, cy, base_r):
    for _ in range(POP_PARTICLES):
        ang = random.uniform(0, 2*math.pi)
        spd = random.uniform(120, 360)
        vx = math.cos(ang) * spd / 60.0
        vy = math.sin(ang) * spd / 60.0
        life = random.uniform(0.25, 0.6)
        particles.append({
            "x": float(cx), "y": float(cy),
            "vx": vx, "vy": vy,
            "life": life, "ttl": time.time() + life,
            "r": random.randint(max(2, base_r//12), max(3, base_r//9)),
            "col": (200, 230, 255)
        })
def update_and_draw_particles(now):
    for p in particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["vy"] += 0.35
        remain = p["ttl"] - now
        if remain <= 0:
            particles.remove(p)
            continue
        alpha = max(0, min(255, int(255 * (remain / p["life"]))))
        r = max(1, int(p["r"] * (0.6 + 0.4 * (remain / p["life"]))))
        s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (*p["col"], alpha), (r, r), r)
        screen.blit(s, (int(p["x"] - r), int(p["y"] - r)))

# ================== PLATFORMY ==================
class Platform:
    def __init__(self):
        self.width = int(WIDTH * 0.3)
        if platform_img_raw:
            scale = self.width / platform_img_raw.get_width()
            self.height = max(10, int(platform_img_raw.get_height() * scale))
        else:
            self.height = 20
        self.y = HEIGHT - 100
        self.speed = 2
        self.direction = random.choice([-1, 1])
        self.x = -self.width if self.direction == 1 else WIDTH
    def update(self):
        self.x += self.speed * self.direction
    def draw(self, screen):
        sprite = get_platform_surface(self.width, self.height, self.direction)
        if sprite:
            screen.blit(sprite, (int(self.x), int(self.y - self.height)))
        else:
            pygame.draw.rect(screen, GRAY, (self.x, self.y, self.width, self.height), border_radius=8)
            pygame.draw.rect(screen, BLACK, (self.x, self.y, self.width, self.height), 2, border_radius=8)
    def check_collision(self, ball_x, ball_y, ball_radius):
        if (ball_y + ball_radius >= self.y - COLLISION_OFFSET and 
            ball_y - ball_radius <= self.y + self.height and
            ball_x + ball_radius >= self.x and 
            ball_x - ball_radius <= self.x + self.width):
            return True
        return False
platforms = []
next_platform_time = random.uniform(5, 10)
last_platform_check = time.time()

# ================== STAN GRY ==================
clock = pygame.time.Clock()
running = True
game_started = False
game_over = False
paused = False
reset_button_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2 + 50, 200, 50)
def reset_ball_position():
    global x, y
    x = random.randint(int(radius), WIDTH - int(radius))
    y = random.randint(int(radius), HEIGHT // 2 - int(radius))
def spawn_coin():
    global coin_x, coin_y, coin_visible, coin_timer
    coin_x = random.randint(coin_radius, WIDTH - coin_radius)
    coin_y = random.randint(coin_radius, HEIGHT - coin_radius)
    coin_visible = True
    coin_timer = time.time() + 2
def get_mass_multiplier():
    return 1.05 if click_count < 20 else 1.02
def handle_ball_click():
    global score, mass, click_count, radius, bubble_alive, bubble_respawn_at, velocity, x, y
    if not bubble_alive:
        return
    spawn_pop_particles(x, y, radius)
    if pop_sound:
        pop_sound.play()
    score += 1
    mass *= get_mass_multiplier()
    click_count += 1
    if click_count % clicks_for_size_reduction == 0:
        radius = int(radius * 0.9)
        x = max(radius, min(WIDTH - radius, x))
        y = max(radius, y)
    bubble_alive = False
    bubble_respawn_at = time.time() + POP_DURATION
    velocity = 0.0
def reset_game():
    global score, gravity, mass, velocity, game_over, game_started, paused
    global coin_visible, bad_coin_visible, coin_timer, bad_coin_timer
    global last_coin_check, last_bad_coin_check, next_coin_time, next_bad_coin_time
    global platforms, next_platform_time, last_platform_check
    global radius, click_count, x, y, _bubble_cache, _platform_cache, _coin_cache
    global bubble_alive, bubble_respawn_at, particles, best_score
    if score > best_score:
        best_score = score
    score = 0
    gravity = 0.05
    mass = 1.0
    velocity = 0.0
    radius = base_radius * 3
    _bubble_cache.clear()
    _platform_cache.clear()
    _coin_cache.clear()
    click_count = 0
    reset_ball_position()
    game_over = False
    game_started = False
    paused = False
    bubble_alive = True
    bubble_respawn_at = 0.0
    particles.clear()
    if music_loaded:
        pygame.mixer.music.stop()
    coin_visible = False
    bad_coin_visible = False
    coin_timer = 0.0
    bad_coin_timer = 0.0
    last_coin_check = time.time()
    last_bad_coin_check = time.time()
    next_coin_time = random.uniform(5, 10)
    next_bad_coin_time = random.uniform(8, 12)
    platforms.clear()
    next_platform_time = random.uniform(10, 15)
    last_platform_check = time.time()
reset_ball_position()

# ================== PĘTLA GŁÓWNA ==================
while running:
    draw_background()
    now = time.time()

    def draw_coin_timers():
        if coin_visible:
            total = 2.0
            remain = max(0.0, coin_timer - now)
            frac = max(0.0, min(1.0, remain / total))
            pygame.draw.rect(screen, BLACK, (20, 70, 220, 12), 2, border_radius=6)
            pygame.draw.rect(screen, GOLD,  (22, 72, int(216 * frac), 8), border_radius=6)
        if bad_coin_visible:
            total = 3.0
            remain = max(0.0, bad_coin_timer - now)
            frac = max(0.0, min(1.0, remain / total))
            pygame.draw.rect(screen, BLACK, (20, 90, 220, 12), 2, border_radius=6)
            pygame.draw.rect(screen, RED,   (22, 92, int(216 * frac), 8), border_radius=6)

    # respawn bubble
    if (not bubble_alive) and (now >= bubble_respawn_at) and game_started and (not paused) and (not game_over):
        reset_ball_position()
        velocity = kick_strength / max(1.0, mass)
        bubble_alive = True

    # platform spawn/update
    if game_started and not game_over and not paused:
        if now - last_platform_check > next_platform_time:
            platforms.append(Platform())
            last_platform_check = now
            next_platform_time = random.uniform(10, 15)
        for platform in platforms[:]:
            platform.update()
            platform.draw(screen)
            if bubble_alive and platform.check_collision(x, y, radius):
                if y + radius > platform.y:
                    y = platform.y - radius
                velocity = -math.sqrt(2.0 * gravity * mass * TARGET_BOUNCE_HEIGHT)
                score += 1
                mass *= get_mass_multiplier()
                click_count += 1
                if click_count % clicks_for_size_reduction == 0:
                    radius = int(radius * 0.9)
                    x = max(radius, min(WIDTH - radius, x))
                    y = max(radius, y)
            if (platform.direction == 1 and platform.x > WIDTH) or (platform.direction == -1 and platform.x < -platform.width):
                platforms.remove(platform)
    else:
        for platform in platforms:
            platform.draw(screen)

    # coin logic
    if not coin_visible and not game_over and game_started and not paused and now - last_coin_check > next_coin_time:
        spawn_coin()
        last_coin_check = now
        next_coin_time = random.uniform(5, 10)
    if coin_visible and now > coin_timer:
        coin_visible = False
    if not bad_coin_visible and not game_over and game_started and not paused and now - last_bad_coin_check > next_bad_coin_time:
        bad_coin_x = random.randint(bad_coin_radius, WIDTH - bad_coin_radius)
        bad_coin_y = random.randint(bad_coin_radius, HEIGHT - bad_coin_radius)
        bad_coin_visible = True
        bad_coin_timer = time.time() + 3
        last_bad_coin_check = now
        next_bad_coin_time = random.uniform(8, 12)
import math
import random
import pygame


pygame.init()

WIDTH = 900
HEIGHT = 700
FPS = 60
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("MOONBYTE | A Cozy Guessing Game")

clock = pygame.time.Clock()

BG = (17, 19, 35)
PANEL = (32, 36, 61)
PANEL_LIGHT = (43, 47, 76)

WHITE = (245, 241, 255)
MUTED = (160, 166, 195)

PURPLE = (174, 142, 255)
PINK = (255, 132, 177)
MINT = (125, 239, 202)
YELLOW = (255, 218, 132)
RED = (255, 113, 135)

# ---------------- FONTS ----------------

FONT_SMALL = pygame.font.SysFont("segoeui", 16)
FONT_MEDIUM = pygame.font.SysFont("segoeui", 22, bold=True)
FONT_TITLE = pygame.font.SysFont("segoeui", 42, bold=True)
FONT_NUMBER = pygame.font.SysFont("segoeui", 52, bold=True)

# ---------------- GAME VARIABLES ----------------

DIFFICULTIES = {
    "CHILL": {"maximum": 20, "attempts": 8, "color": MINT},
    "COZY": {"maximum": 50, "attempts": 7, "color": PURPLE},
    "SPICY": {"maximum": 100, "attempts": 7, "color": PINK},
}

difficulty = "COZY"

score = 0
best_scores = {"CHILL": None, "COZY": None, "SPICY": None}

guess_history = []
particles = []

input_text = ""
message = "A little mystery is waiting in the stars."
message_color = MUTED

hint_used = False
game_over = False
won = False

# ---------------- STARS ----------------

stars = []

for _ in range(90):
    stars.append({
        "x": random.randint(0, WIDTH),
        "y": random.randint(0, HEIGHT),
        "radius": random.choice([1, 1, 2]),
        "phase": random.random() * math.pi * 2,
    })

# ---------------- HELPER FUNCTIONS ----------------

def draw_text(text, font, color, x, y, center=True):
    image = font.render(str(text), True, color)
    rect = image.get_rect()

    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)

    screen.blit(image, rect)


def draw_button(rect, text, color, mouse_pos, enabled=True):
    hovered = rect.collidepoint(mouse_pos)

    fill = color if enabled else PANEL_LIGHT

    if hovered and enabled:
        fill = tuple(min(255, channel + 18) for channel in color)

    pygame.draw.rect(screen, fill, rect, border_radius=13)

    pygame.draw.rect(
        screen,
        WHITE if hovered and enabled else PANEL_LIGHT,
        rect,
        width=1,
        border_radius=13,
    )

    draw_text(
        text,
        FONT_SMALL,
        WHITE if enabled else MUTED,
        rect.centerx,
        rect.centery,
    )

    return hovered


def new_round():
    global secret_number, attempts_left, input_text
    global message, message_color, hint_used
    global game_over, won, guess_history, particles

    maximum = DIFFICULTIES[difficulty]["maximum"]
    attempts_left = DIFFICULTIES[difficulty]["attempts"]

    secret_number = random.randint(1, maximum)

    input_text = ""
    guess_history = []
    particles = []

    hint_used = False
    game_over = False
    won = False

    message = f"Guess a number between 1 and {maximum}."
    message_color = MUTED


def submit_guess():
    global attempts_left, input_text, message
    global message_color, game_over, won, score

    if game_over:
        return

    if not input_text:
        message = "Enter a number first, stargazer!"
        message_color = YELLOW
        return

    try:
        guess = int(input_text)
    except ValueError:
        message = "Please enter a whole number."
        message_color = RED
        input_text = ""
        return

    maximum = DIFFICULTIES[difficulty]["maximum"]

    if guess < 1 or guess > maximum:
        message = f"Choose a number from 1 to {maximum}."
        message_color = YELLOW
        return

    if guess in guess_history:
        message = "You already tried that number!"
        message_color = YELLOW
        input_text = ""
        return

    guess_history.append(guess)
    attempts_left -= 1

    if guess == secret_number:
        won = True
        game_over = True
        score += 1

        previous = best_scores[difficulty]

        if previous is None or len(guess_history) < previous:
            best_scores[difficulty] = len(guess_history)

        message = "You found it! The stars are cheering!"
        message_color = MINT

        create_confetti()

    elif guess < secret_number:
        message = "A little higher! ↑"
        message_color = PURPLE

    else:
        message = "A little lower! ↓"
        message_color = PINK

    if attempts_left == 0 and not won:
        game_over = True
        message = f"Round over! The number was {secret_number}."
        message_color = RED

    input_text = ""


def use_hint():
    global hint_used, message, message_color

    if game_over:
        return

    if hint_used:
        message = "Your hint has already been used!"
        message_color = YELLOW
        return

    hint_used = True

    parity = "even" if secret_number % 2 == 0 else "odd"

    maximum = DIFFICULTIES[difficulty]["maximum"]

    if secret_number <= maximum // 2:
        half = "lower half"
    else:
        half = "upper half"

    message = f"Hint: The number is {parity}, in the {half}."
    message_color = MINT


def create_confetti():
    for _ in range(90):
        particles.append({
            "x": WIDTH // 2 + random.randint(-50, 50),
            "y": 250,
            "vx": random.uniform(-3, 3),
            "vy": random.uniform(-5, -1),
            "life": random.uniform(0.8, 1.8),
            "color": random.choice([PURPLE, PINK, MINT, YELLOW]),
        })


def draw_stars(elapsed):
    for star in stars:
        brightness = 120 + int(
            100 * (0.5 + 0.5 * math.sin(elapsed * 2 + star["phase"]))
        )

        brightness = min(255, brightness)

        color = (brightness, brightness, min(255, brightness + 10))

        pygame.draw.circle(
            screen,
            color,
            (star["x"], star["y"]),
            star["radius"],
        )


def update_confetti(dt):
    for particle in particles[:]:
        particle["x"] += particle["vx"]
        particle["y"] += particle["vy"]

        particle["vy"] += 8 * dt
        particle["life"] -= dt

        if particle["life"] <= 0:
            particles.remove(particle)


def draw_confetti():
    for particle in particles:
        pygame.draw.rect(
            screen,
            particle["color"],
            (
                int(particle["x"]),
                int(particle["y"]),
                6,
                6,
            ),
            border_radius=2,
        )


# ---------------- BUTTONS ----------------

difficulty_buttons = {
    "CHILL": pygame.Rect(270, 120, 110, 38),
    "COZY": pygame.Rect(395, 120, 110, 38),
    "SPICY": pygame.Rect(520, 120, 110, 38),
}

guess_button = pygame.Rect(285, 450, 330, 48)
hint_button = pygame.Rect(285, 510, 155, 42)
reset_button = pygame.Rect(455, 510, 160, 42)

input_box = pygame.Rect(285, 375, 330, 55)

# ---------------- START GAME ----------------

new_round()

running = True
elapsed = 0

# ---------------- MAIN GAME LOOP ----------------

while running:

    dt = min(clock.tick(FPS) / 1000, 0.05)
    elapsed += dt

    mouse_pos = pygame.mouse.get_pos()

    # Events

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:

            if event.key == pygame.K_ESCAPE:
                running = False

            elif event.key == pygame.K_RETURN:
                submit_guess()

            elif event.key == pygame.K_BACKSPACE:
                input_text = input_text[:-1]

            elif event.unicode.isdigit() and len(input_text) < 3:
                if not game_over:
                    input_text += event.unicode

        elif event.type == pygame.MOUSEBUTTONDOWN:

            if event.button == 1:

                for name, rect in difficulty_buttons.items():

                    if rect.collidepoint(event.pos):
                        difficulty = name
                        new_round()

                if guess_button.collidepoint(event.pos):
                    submit_guess()

                elif hint_button.collidepoint(event.pos):
                    use_hint()

                elif reset_button.collidepoint(event.pos):
                    new_round()

    # Update animations

    update_confetti(dt)

    # Background

    screen.fill(BG)
    draw_stars(elapsed)

    # Header

    draw_text("✦ MOONBYTE", FONT_TITLE, WHITE, WIDTH // 2, 43)

    draw_text(
        "A TINY NUMBER-GUESSING ADVENTURE",
        FONT_SMALL,
        MUTED,
        WIDTH // 2,
        82,
    )

    draw_text(
        "CHOOSE YOUR MOOD",
        FONT_SMALL,
        MUTED,
        WIDTH // 2,
        105,
    )

    # Difficulty buttons

    for name, rect in difficulty_buttons.items():

        color = DIFFICULTIES[name]["color"]

        draw_button(
            rect,
            name,
            color if difficulty == name else PANEL,
            mouse_pos,
        )

    # Main panel

    panel = pygame.Rect(225, 175, 450, 420)

    pygame.draw.rect(
        screen,
        (9, 11, 24),
        panel.move(0, 7),
        border_radius=25,
    )

    pygame.draw.rect(
        screen,
        PANEL,
        panel,
        border_radius=25,
    )

    pygame.draw.rect(
        screen,
        PANEL_LIGHT,
        panel,
        width=1,
        border_radius=25,
    )

    # Secret number range

    maximum = DIFFICULTIES[difficulty]["maximum"]
    accent = DIFFICULTIES[difficulty]["color"]

    draw_text(
        "THE SECRET NUMBER",
        FONT_SMALL,
        MUTED,
        WIDTH // 2,
        210,
    )

    draw_text(
        f"1 — {maximum}",
        FONT_NUMBER,
        WHITE,
        WIDTH // 2,
        260,
    )

    draw_text(
        f"{attempts_left} guesses remaining",
        FONT_SMALL,
        accent,
        WIDTH // 2,
        310,
    )

    # Attempt indicators

    start_x = WIDTH // 2 - (
        DIFFICULTIES[difficulty]["attempts"] - 1
    ) * 10

    for index in range(DIFFICULTIES[difficulty]["attempts"]):

        color = accent if index < attempts_left else PANEL_LIGHT

        pygame.draw.circle(
            screen,
            color,
            (start_x + index * 20, 340),
            5,
        )

    # Input field

    pygame.draw.rect(
        screen,
        PANEL_LIGHT,
        input_box,
        border_radius=12,
    )

    pygame.draw.rect(
        screen,
        accent,
        input_box,
        width=2,
        border_radius=12,
    )

    shown_text = input_text if input_text else "Type your guess..."

    text_color = WHITE if input_text else MUTED

    draw_text(
        shown_text,
        FONT_MEDIUM,
        text_color,
        input_box.x + 17,
        input_box.centery,
        center=False,
    )

    # Buttons

    draw_button(
        guess_button,
        "MAKE A GUESS  ↗",
        accent,
        mouse_pos,
        enabled=not game_over,
    )

    draw_button(
        hint_button,
        "✦ GET A HINT",
        PANEL_LIGHT,
        mouse_pos,
        enabled=not game_over and not hint_used,
    )

    draw_button(
        reset_button,
        "↻ NEW ROUND",
        PANEL_LIGHT,
        mouse_pos,
    )

    # Feedback

    draw_text(
        message,
        FONT_SMALL,
        message_color,
        WIDTH // 2,
        575,
    )

    # Session stats

    draw_text(
        f"ROUNDS WON: {score}",
        FONT_SMALL,
        MUTED,
        WIDTH // 2 - 100,
        650,
    )

    best = best_scores[difficulty]

    best_text = str(best) if best is not None else "—"

    draw_text(
        f"PERSONAL BEST: {best_text}",
        FONT_SMALL,
        MUTED,
        WIDTH // 2 + 115,
        650,
    )

    # Win particles

    draw_confetti()

    pygame.display.flip()

pygame.quit()

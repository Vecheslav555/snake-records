import pygame
import random
import sqlite3
import os
from datetime import datetime

WIDTH, HEIGHT = 600, 600
CELL = 20
FPS = 10
DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "records.db")


# ---------- БД ----------
def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            score INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def save_score(name, score):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO records (player_name, score, created_at) VALUES (?, ?, ?)",
        (name, score, datetime.now().isoformat())
    )
    conn.commit()
    conn.close()


# ---------- Ввод имени ДО игры ----------
def ask_name(screen, font, big_font):
    """Возвращает строку имени или None, если пользователь закрыл окно."""
    name = ""
    clock = pygame.time.Clock()
    title = big_font.render("🐍 Snake", True, (0, 220, 100))
    prompt = font.render("Введите имя и нажмите Enter:", True, (255, 255, 255))
    hint = font.render("A-Z, 0-9, _ - (до 15 символов)", True, (150, 150, 150))
    err = font.render("Имя не может быть пустым", True, (255, 80, 80))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    if name.strip():
                        return name.strip()
                    # пусто — просто покажем ошибку
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.key == pygame.K_ESCAPE:
                    return None
                elif event.unicode.isalnum() or event.unicode in "_ -":
                    if len(name) < 15:
                        name += event.unicode

        screen.fill((20, 20, 20))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 220))

        name_txt = big_font.render(name + "_", True, (255, 255, 255))
        screen.blit(name_txt, (WIDTH // 2 - name_txt.get_width() // 2, 280))

        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 360))
        if not name and pygame.key.get_pressed():  # подсказка, если пусто
            screen.blit(err, (WIDTH // 2 - err.get_width() // 2, 400))

        pygame.display.flip()
        clock.tick(30)


# ---------- Сама игра ----------
def run_game(player_name):
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption(f"Snake — {player_name}")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    big_font = pygame.font.SysFont("Arial", 40)

    def random_food(snake):
        while True:
            pos = (random.randrange(0, WIDTH // CELL),
                   random.randrange(0, HEIGHT // CELL))
            if pos not in snake:
                return pos

    snake = [(10, 10), (9, 10), (8, 10)]
    direction = (1, 0)
    food = random_food(snake)
    score = 0
    best = 0
    game_over = False
    saved = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return
            if event.type == pygame.KEYDOWN:
                if not game_over:
                    if event.key in (pygame.K_UP, pygame.K_w) and direction != (0, 1):
                        direction = (0, -1)
                    elif event.key in (pygame.K_DOWN, pygame.K_s) and direction != (0, -1):
                        direction = (0, 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a) and direction != (1, 0):
                        direction = (-1, 0)
                    elif event.key in (pygame.K_RIGHT, pygame.K_d) and direction != (-1, 0):
                        direction = (1, 0)
                else:
                    # на экране Game Over
                    if event.key == pygame.K_r:
                        snake = [(10, 10), (9, 10), (8, 10)]
                        direction = (1, 0)
                        food = random_food(snake)
                        score = 0
                        game_over = False
                        saved = False
                    elif event.key == pygame.K_q:
                        return

        if not game_over:
            hx, hy = snake[0]
            new_head = (hx + direction[0], hy + direction[1])

            if (new_head[0] < 0 or new_head[0] >= WIDTH // CELL or
                new_head[1] < 0 or new_head[1] >= HEIGHT // CELL or
                    new_head in snake):
                game_over = True
            else:
                snake.insert(0, new_head)
                if new_head == food:
                    score += 1
                    best = max(best, score)
                    food = random_food(snake)
                else:
                    snake.pop()

        # отрисовка
        screen.fill((20, 20, 20))
        for x, y in snake:
            pygame.draw.rect(screen, (0, 220, 100),
                             (x * CELL, y * CELL, CELL, CELL))
        pygame.draw.rect(screen, (220, 50, 50),
                         (food[0] * CELL, food[1] * CELL, CELL, CELL))

        # счёт и имя
        score_txt = font.render(f"{player_name}  |  Score: {score}  |  Best: {best}",
                                True, (255, 255, 255))
        screen.blit(score_txt, (10, 10))

        if game_over:
            over = big_font.render("GAME OVER", True, (255, 80, 80))
            screen.blit(over, (WIDTH // 2 - over.get_width() // 2, HEIGHT // 2 - 80))
            res = font.render(f"Итог: {score} (рекорд сохранён)", True, (255, 255, 255))
            screen.blit(res, (WIDTH // 2 - res.get_width() // 2, HEIGHT // 2))
            sub = font.render("R — играть снова   |   Q — выйти",
                              True, (200, 200, 200))
            screen.blit(sub, (WIDTH // 2 - sub.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(FPS)

        # Сохраняем рекорд ровно один раз при проигрыше
        if game_over and not saved:
            save_score(player_name, score)
            saved = True


# ---------- Точка входа ----------
if __name__ == "__main__":
    pygame.init()
    init_db()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Snake")
    font = pygame.font.SysFont("Arial", 24)
    big_font = pygame.font.SysFont("Arial", 40)

    player_name = ask_name(screen, font, big_font)
    if player_name is None:
        pygame.quit()
    else:
        run_game(player_name)
        pygame.quit()
import pygame
import sys
import random
import math

pygame.init()
screen = pygame.display.set_mode((1920, 1080))
pygame.display.set_caption("Валентинка ❤️")
clock = pygame.time.Clock()

# Загружаем фон
try:
    background = pygame.image.load("фон.jpg")
    background = pygame.transform.scale(background, (1920, 1080))
except:
    background = pygame.Surface((1920, 1080))
    background.fill((255, 200, 220))

# Начальные размеры и позиции
yes_rect = pygame.Rect(800, 600, 150, 60)
no_rect = pygame.Rect(970, 600, 150, 60)

# Состояния
no_clicks = 0
yes_clicked = False

# Сердечки
hearts = []
heart_timer = 0

font_big = pygame.font.Font(None, 72)
font = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

no_texts = ["НЕТ", "Точно нет?", "Подумай ещё", "Ну пожалуйста",
            "Очень прошу", "Сдавайся", "Ну давай", "Умоляю",
            "Куда ты убегаешь?", "Не убежишь!", "Сдавайся!!!",
            "Ну пожалуйста!!!", "Я не сдамся!"]


def draw_heart(surface, x, y, size, color):
    points = []
    for i in range(100):
        t = i * 2 * math.pi / 100
        heart_x = x + size * 16 * math.sin(t) ** 3
        heart_y = y - size * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t))
        points.append((heart_x, heart_y))
    pygame.draw.polygon(surface, color, points)


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if yes_rect.collidepoint(event.pos):
                yes_clicked = True

            if no_rect.collidepoint(event.pos) and not yes_clicked:
                no_clicks += 1

                # ДА увеличивается
                yes_rect.width += 100
                yes_rect.height += 75
                yes_rect.x -= 35
                yes_rect.y -= 15

                # НЕТ уменьшается И ТЕЛЕПОРТИРУЕТСЯ В СЛУЧАЙНОЕ МЕСТО
                no_rect.width = max(40, no_rect.width - 15)
                no_rect.height = max(25, no_rect.height - 6)

                # Рандомная позиция, но не слишком близко к кнопке ДА
                while True:
                    new_x = random.randint(50, 1770)
                    new_y = random.randint(50, 980)
                    # Проверяем, чтобы не накладывалась на кнопку ДА
                    temp_rect = pygame.Rect(new_x, new_y, no_rect.width, no_rect.height)
                    if not temp_rect.colliderect(yes_rect):
                        no_rect.x = new_x
                        no_rect.y = new_y
                        break

    # Отрисовка фона
    screen.blit(background, (0, 0))

    if not yes_clicked:
        # Вопрос по середине
        question = font_big.render("Ты будешь моей валентинкой?", True, (255, 255, 255))
        question_rect = question.get_rect(center=(960, 400))
        screen.blit(question, question_rect)

        # Кнопка ДА
        pygame.draw.rect(screen, (70, 120, 255), yes_rect, border_radius=15)
        yes_text = font.render("ДА", True, (255, 255, 255))
        screen.blit(yes_text, yes_text.get_rect(center=yes_rect.center))

        # Кнопка НЕТ (телепортируется)
        if no_rect.width > 40:
            pygame.draw.rect(screen, (70, 120, 255), no_rect, border_radius=10)
            no_text = font_small.render(no_texts[min(no_clicks, len(no_texts) - 1)], True, (255, 255, 255))
            screen.blit(no_text, no_text.get_rect(center=no_rect.center))

            # Подсказка где кнопка НЕТ (если она далеко)
            if no_clicks > 3:
                hint = font_small.render("👆 Она здесь!", True, (255, 255, 255))
                hint_rect = hint.get_rect(center=(no_rect.centerx, no_rect.top - 30))
                screen.blit(hint, hint_rect)
    else:
        # Финальный экран с сердцами
        win_text = font_big.render("УРААА! Я ЗНАЛ, ЧТО ТЫ СОГЛАСИШЬСЯ! 🎉❤️", True, (255, 255, 255))
        win_rect = win_text.get_rect(center=(960, 540))
        screen.blit(win_text, win_rect)

        # Создаем новые сердца
        heart_timer += 1
        if heart_timer > 8:
            hearts.append({
                'x': random.randint(100, 1820),
                'y': random.randint(100, 980),
                'size': random.uniform(0.5, 1.8),
                'speed': random.uniform(1, 4),
                'color': (random.randint(200, 255), random.randint(0, 50), random.randint(0, 50))
            })
            heart_timer = 0

        # Отрисовываем и двигаем сердца
        for heart in hearts[:]:
            draw_heart(screen, heart['x'], heart['y'], heart['size'], heart['color'])
            heart['y'] -= heart['speed']
            heart['x'] += random.uniform(-0.8, 0.8)

            if heart['y'] < -100:
                hearts.remove(heart)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()

import pygame
import sys
import random
import csv
import os
from datetime import datetime

pygame.init()

# -------------------- SETTINGS --------------------

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EEG Interview Experiment")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

font_large = pygame.font.SysFont(None, 70)
font_medium = pygame.font.SysFont(None, 50)

clock = pygame.time.Clock()

# -------------------- EXPERIMENT DATA --------------------

participant_id = "P01"

questions = [
    {
        "text": "Which approach is more time-efficient for \nsearching in a sorted array?\n\na. Linear Search\nb. Binary Search",
        "difficulty": "Easy"
    },
    {
        "text": "Which supports runtime polymorphism?\n\na. Method Overriding\nb. Method Overloading",
        "difficulty": "Medium"
    },
    {
        "text": "Which structure is used in BFS traversal?\n\na. Queue\nb. Stack",
        "difficulty": "Hard"
    }
]

# Randomize question order
trial_order = list(range(len(questions)))
random.shuffle(trial_order)

current_question = 0
state = "start"
number_positions = []

wheel_start_time = 0
cue_start_time = 0
current_cue = ""

# -------------------- SAVE FUNCTION --------------------

def save_to_csv(question_text, real_difficulty, cue_shown, selected_number, reaction_time):

    if 1 <= selected_number <= 5:
        option_side = "Option1"
        confidence = 6 - selected_number
    else:
        option_side = "Option2"
        confidence = selected_number - 5

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = os.path.isfile("responses.csv")

    with open("responses.csv", "a", newline="") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow([
                "participant_id",
                "trial",
                "cue_shown",
                "real_difficulty",
                "question_text",
                "selected_number",
                "option_side",
                "confidence_strength",
                "reaction_time_ms",
                "timestamp"
            ])

        writer.writerow([
            participant_id,
            current_question + 1,
            cue_shown,
            real_difficulty,
            question_text,
            selected_number,
            option_side,
            confidence,
            reaction_time,
            timestamp
        ])

# -------------------- DRAW FUNCTIONS --------------------

def draw_fixation():
    screen.fill(BLACK)
    pygame.draw.circle(screen, WHITE, (WIDTH//2, HEIGHT//2), 10)

def draw_cue():
    screen.fill(BLACK)
    cue_text = font_large.render(current_cue.upper(), True, WHITE)
    screen.blit(cue_text, (WIDTH//2 - cue_text.get_width()//2, HEIGHT//2 - 50))

def draw_question():
    screen.fill(BLACK)

    q_index = trial_order[current_question]
    lines = questions[q_index]["text"].split("\n")

    start_y = 300

    for i, line in enumerate(lines):
        text = font_large.render(line, True, WHITE)
        screen.blit(text, (WIDTH//2 - text.get_width()//2, start_y + i * 80))

    info = font_medium.render("Click to rate confidence", True, WHITE)
    screen.blit(info, (WIDTH//2 - info.get_width()//2, start_y + len(lines)*80 + 80))

def generate_wheel():
    global number_positions
    number_positions = []

    numbers = list(range(1, 11))
    random.shuffle(numbers)

    center = (WIDTH//2, HEIGHT//2)
    radius = 300

    for i, num in enumerate(numbers):
        angle = i * (360 / 10)
        vector = pygame.math.Vector2(1, 0).rotate(angle)

        x = center[0] + radius * vector.x
        y = center[1] + radius * vector.y

        text = font_large.render(str(num), True, WHITE)
        rect = text.get_rect(center=(x, y))

        number_positions.append((num, rect))

def draw_wheel():
    screen.fill(BLACK)

    title = font_medium.render("Confidence Wheel", True, WHITE)
    screen.blit(title, (WIDTH//2 - title.get_width()//2, 150))

    for num, rect in number_positions:
        text = font_large.render(str(num), True, WHITE)
        screen.blit(text, rect)

# -------------------- MAIN LOOP --------------------

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if state == "start":
                state = "cue"
                current_cue = random.choice(["Easy", "Medium", "Hard"])
                cue_start_time = pygame.time.get_ticks()

            elif state == "question":
                state = "wheel"
                generate_wheel()
                wheel_start_time = pygame.time.get_ticks()

            elif state == "wheel":
                mouse_pos = pygame.mouse.get_pos()

                for num, rect in number_positions:
                    if rect.collidepoint(mouse_pos):

                        reaction_time = pygame.time.get_ticks() - wheel_start_time

                        q_index = trial_order[current_question]

                        save_to_csv(
                            questions[q_index]["text"],
                            questions[q_index]["difficulty"],
                            current_cue,
                            num,
                            reaction_time
                        )

                        current_question += 1

                        if current_question >= len(questions):
                            running = False
                        else:
                            state = "cue"
                            current_cue = random.choice(["Easy", "Medium", "Hard"])
                            cue_start_time = pygame.time.get_ticks()

    # Auto transition cue → question after 2 seconds
    if state == "cue":
        if pygame.time.get_ticks() - cue_start_time > 2000:
            state = "question"

    # Draw according to state
    if state == "start":
        draw_fixation()
    elif state == "cue":
        draw_cue()
    elif state == "question":
        draw_question()
    elif state == "wheel":
        draw_wheel()

    pygame.display.update()
    clock.tick(60)

pygame.quit()
sys.exit()
import pygame
import sys
import random
import csv
import os
from datetime import datetime

pygame.init()

# ---------------- SETTINGS ----------------

WIDTH, HEIGHT = 1920, 1080
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("EEG Interview Experiment")

WHITE = (255,255,255)
BLACK = (0,0,0)

font_large = pygame.font.SysFont(None,70)
font_medium = pygame.font.SysFont(None,50)

clock = pygame.time.Clock()

# ---------------- EXPERIMENT DATA ----------------

participant_id = "P01"

questions = [
{
"text":"Which approach is more time-efficient for \nsearching in a sorted array?\n\na. Linear Search\nb. Binary Search",
"difficulty":"Easy"
},
{
"text":"Which supports runtime polymorphism?\n\na. Method Overriding\nb. Method Overloading",
"difficulty":"Medium"
},
{
"text":"Which structure is used in BFS traversal?\n\na. Queue\nb. Stack",
"difficulty":"Hard"
}
]

trial_order = list(range(len(questions)))
random.shuffle(trial_order)

current_question = 0
state = "start"

wheel_start_time = 0
cue_start_time = 0
blank_start_time = 0
fixation_start_time = 0

current_cue = ""

number_positions = []

# ---------------- SAVE CSV ----------------

def save_to_csv(question_text,real_difficulty,cue_shown,selected_number,reaction_time):

    if 1 <= selected_number <= 5:
        option_side = "Option1"
        confidence = 6-selected_number
    else:
        option_side = "Option2"
        confidence = selected_number-5

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    file_exists = os.path.isfile("responses.csv")

    with open("responses.csv","a",newline="") as file:

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
        current_question+1,
        cue_shown,
        real_difficulty,
        question_text,
        selected_number,
        option_side,
        confidence,
        reaction_time,
        timestamp
        ])

# ---------------- DRAW SCREENS ----------------

def draw_fixation():
    screen.fill(BLACK)
    pygame.draw.circle(screen,WHITE,(WIDTH//2,HEIGHT//2),10)

def draw_blank():
    screen.fill(BLACK)

def draw_cue():

    screen.fill(BLACK)

    cue_text = font_large.render(current_cue.upper(),True,WHITE)

    screen.blit(cue_text,(WIDTH//2 - cue_text.get_width()//2,HEIGHT//2-50))

def draw_question():

    screen.fill(BLACK)

    q_index = trial_order[current_question]

    lines = questions[q_index]["text"].split("\n")

    start_y = 300

    for i,line in enumerate(lines):

        text = font_large.render(line,True,WHITE)

        screen.blit(text,(WIDTH//2-text.get_width()//2,start_y+i*80))

    info = font_medium.render("Click to rate confidence",True,WHITE)

    screen.blit(info,(WIDTH//2-info.get_width()//2,start_y+len(lines)*80+80))

# ---------------- CONFIDENCE WHEEL ----------------

def generate_wheel():

    global number_positions

    number_positions = []

    numbers = list(range(1,11))
    random.shuffle(numbers)

    center = (WIDTH//2,HEIGHT//2)
    radius = 300

    for i,num in enumerate(numbers):

        start_angle = i*36
        end_angle = start_angle+36
        mid_angle = start_angle+18

        vector = pygame.math.Vector2(1,0).rotate(mid_angle)

        x = center[0]+(radius*0.6)*vector.x
        y = center[1]+(radius*0.6)*vector.y

        rect = pygame.Rect(0,0,1,1)
        rect.center = (x,y)

        number_positions.append({
        "num":num,
        "start":start_angle,
        "end":end_angle,
        "rect":rect,
        "slice":i
        })

def draw_wheel():

    screen.fill(BLACK)

    center = (WIDTH//2,HEIGHT//2)
    radius = 300

    title = font_medium.render("Confidence Wheel",True,WHITE)
    screen.blit(title,(WIDTH//2-title.get_width()//2,150))

    slices = 10
    step = 360/slices

    for i in range(slices):

        start_angle = i*step
        end_angle = start_angle+step

        # alternating colors
        if i % 2 == 0:
            color = (220,220,220)
        else:
            color = (100,100,100)

        points = [center]

        for a in range(int(start_angle),int(end_angle)+1,5):

            vec = pygame.math.Vector2(1,0).rotate(a)

            x = center[0]+radius*vec.x
            y = center[1]+radius*vec.y

            points.append((x,y))

        pygame.draw.polygon(screen,color,points)

    pygame.draw.circle(screen,WHITE,center,radius,3)

    for slice_data in number_positions:

        num = slice_data["num"]
        rect = slice_data["rect"]
        slice_index = slice_data["slice"]

        if slice_index % 2 == 0:
            text_color = BLACK
        else:
            text_color = WHITE

        text = font_large.render(str(num),True,text_color)

        text_rect = text.get_rect(center=rect.center)

        screen.blit(text,text_rect)

# ---------------- MAIN LOOP ----------------

running = True

while running:

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:

            if state == "start":

                state = "fixation"
                fixation_start_time = pygame.time.get_ticks()

            elif state == "question":

                state = "wheel"
                generate_wheel()
                wheel_start_time = pygame.time.get_ticks()

            elif state == "wheel":

                mouse_x,mouse_y = pygame.mouse.get_pos()

                center_x,center_y = WIDTH//2,HEIGHT//2

                dx = mouse_x-center_x
                dy = mouse_y-center_y

                distance = (dx**2+dy**2)**0.5

                if distance <= 300:

                    angle = (pygame.math.Vector2(dx,dy).angle_to((1,0))*-1)%360

                    for slice_data in number_positions:

                        if slice_data["start"] <= angle < slice_data["end"]:

                            num = slice_data["num"]

                            reaction_time = pygame.time.get_ticks()-wheel_start_time

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
                                state = "start"

    # -------- STATE TIMING --------

    if state == "fixation":
        if pygame.time.get_ticks()-fixation_start_time > 1000:
            state = "blank"
            blank_start_time = pygame.time.get_ticks()

    if state == "blank":
        if pygame.time.get_ticks()-blank_start_time > 500:
            state = "cue"
            current_cue = random.choice(["Easy","Medium","Hard"])
            cue_start_time = pygame.time.get_ticks()

    if state == "cue":
        if pygame.time.get_ticks()-cue_start_time > 2000:
            state = "question"

    # -------- DRAW --------

    if state == "start":
        draw_fixation()

    elif state == "fixation":
        draw_fixation()

    elif state == "blank":
        draw_blank()

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

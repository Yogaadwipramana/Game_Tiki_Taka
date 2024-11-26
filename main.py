import cv2
import pygame
import random
import mediapipe as mp
import time

pygame.init()

screen_width, screen_height = 1090, 690
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Tangkap Game Benda Jatuh")

WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLACK = (0, 0, 0)

object_width = 70
object_height = 120
object_y = screen_height - 100
object_x = screen_width // 2 - object_width // 2

# Latar belakang
background = pygame.image.load("Asset/background/Wallpaper.jpg")
background = pygame.transform.scale(background, (screen_width, screen_height))

# Tong sampah untuk masing-masing kategori
trash_bins = {
    "Organik": pygame.image.load("Asset/Organik/Tong_Organik.png"),
    "Anorganik": pygame.image.load("Asset/Anorganik/Tong_Anorganik.png"),
    "B3": pygame.image.load("Asset/B3/Tong_B3.png"),
}

trash_bins = {key: pygame.transform.scale(img, (object_width, object_height)) for key, img in trash_bins.items()}

# Objek untuk masing-masing kategori
objects_categories = {
    "Organik": [
        pygame.image.load("asset/Organik/OR_cau.PNG"),
        pygame.image.load("asset/Organik/OR_daun.png"),
        pygame.image.load("asset/Organik/OR_pencil.PNG"),
    ],
    "Anorganik": [
        pygame.image.load("asset/Anorganik/AN_botol_aqua.png"),
        pygame.image.load("asset/Anorganik/AN_cup gelas.png"),
        pygame.image.load("asset/Anorganik/AN_softener.PNG"),
    ],
    "B3": [
        pygame.image.load("asset/B3/B3_COCA.PNG"),
        pygame.image.load("asset/B3/B3_SABUN.PNG"),
        pygame.image.load("asset/B3/B3_SPRAY.PNG"),
    ],
}

objects_categories = {
    key: [pygame.transform.scale(img, (50, 50)) for img in imgs]
    for key, imgs in objects_categories.items()
}

object_speed = 5
objects = []

score = 0
font = pygame.font.Font(None, 36)

game_duration = 30
start_time = time.time()

# Awal kategori
current_category = random.choice(list(objects_categories.keys()))
category_change_interval = 7
last_category_change = start_time

mp_pose = mp.solutions.pose
pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)

cap = cv2.VideoCapture(0)

# Load sound effects
pop_sounds = [
    pygame.mixer.Sound("pop-1.mp3"),
    pygame.mixer.Sound("pop-2.mp3"),
    pygame.mixer.Sound("pop-3.mp3"),
]

def create_object():
    """Buat objek baru dari semua kategori."""
    for category, images in objects_categories.items():
        x = random.randint(0, screen_width - 70)
        y = 0
        image = random.choice(images)
        objects.append([x, y, image, category])  # Tambahkan kategori ke setiap objek

def reset_game():
    global score, start_time, objects, object_x, object_speed, current_category, last_category_change
    score = 0
    start_time = time.time()
    last_category_change = start_time
    objects = []
    object_x = screen_width // 2 - object_width // 2
    object_speed = 5
    current_category = random.choice(list(objects_categories.keys()))
    create_object()

running = True
game_over = False
clock = pygame.time.Clock()
create_object()

while running:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    results = pose.process(frame_rgb)

    if results.pose_landmarks:
        nose_x = results.pose_landmarks.landmark[mp_pose.PoseLandmark.NOSE].x * screen_width
        object_x = int(nose_x - object_width // 2)
        object_x = max(0, min(object_x, screen_width - object_width))

    elapsed_time = time.time() - start_time
    time_left = max(0, game_duration - int(elapsed_time))

    # Ganti kategori berdasarkan interval
    if time.time() - last_category_change >= category_change_interval:
        current_category = random.choice(list(objects_categories.keys()))
        last_category_change = time.time()

    # Meningkatkan kecepatan jatuh objek berdasarkan waktu tersisa
    object_speed = 5 + (game_duration - time_left) // 5

    if elapsed_time >= game_duration:
        game_over = True

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_over and event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if screen_width // 2 - 50 <= mouse_x <= screen_width // 2 + 50 and screen_height // 2 <= mouse_y <= screen_height // 2 + 40:
                reset_game()
                game_over = False
            elif screen_width // 2 - 50 <= mouse_x <= screen_width // 2 + 50 and screen_height // 2 + 70 <= mouse_y <= screen_height // 2 + 110:
                running = False

    if not game_over:
        for obj in objects:
            obj[1] += object_speed
            if obj[1] + 70 >= object_y and object_x < obj[0] < object_x + object_width:
                if obj[3] == current_category:  
                    score += 1
                    pygame.mixer.Sound.play(random.choice(pop_sounds))
                else:  
                    score = max(score - 1, 0)
                objects.remove(obj)
            elif obj[1] > screen_height:
                objects.remove(obj)

        if random.randint(1, 20) == 1:
            create_object()

        # Tampilkan latar belakang
        screen.blit(background, (0, 0))

        # Tampilkan tong sampah sesuai kategori saat ini
        screen.blit(trash_bins[current_category], (object_x, object_y))

        # Tampilkan objek yang sedang jatuh
        for obj in objects:
            screen.blit(obj[2], (obj[0], obj[1]))

        score_text = font.render(f"Score: {score}", True, RED)
        screen.blit(score_text, (10, 10))

        timer_text = font.render(f"Time: {time_left}s", True, RED)
        screen.blit(timer_text, (screen_width - 150, 10))

        category_text = font.render(f"Catch: {current_category}", True, RED)
        screen.blit(category_text, (screen_width // 2 - 100, 10))

    else:
        # Pastikan background tetap ditampilkan saat game over
        screen.blit(background, (0, 0))  # Gambar background

        game_over_text = font.render("Game Over!", True, BLACK)
        score_text = font.render(f"Final Score: {score}", True, BLACK)
        play_again_text = font.render("Play Again", True, RED)
        quit_text = font.render("Quit Game", True, RED)

        screen.blit(game_over_text, (screen_width // 2 - game_over_text.get_width() // 2, screen_height // 2 - 60))
        screen.blit(score_text, (screen_width // 2 - score_text.get_width() // 2, screen_height // 2 - 20))

        pygame.draw.rect(screen, BLACK, (screen_width // 2 - 50, screen_height // 2 + 20, 100, 40))
        screen.blit(play_again_text, (screen_width // 2 - play_again_text.get_width() // 2, screen_height // 2 + 30))

        pygame.draw.rect(screen, BLACK, (screen_width // 2 - 50, screen_height // 2 + 70, 100, 40))
        screen.blit(quit_text, (screen_width // 2 - quit_text.get_width() // 2, screen_height // 2 + 80))

    pygame.display.flip()
    clock.tick(30)

cap.release()
pygame.quit()

import pygame
import random
import math
import json
import sys
from PIL import Image

import os
import sys

def resource_path(relative_path):
     """Get absolute path to resource for PyInstaller or dev"""
     base_path = getattr(sys, '_MEIPASS', os.path.dirname(__file__))
     return os.path.join(base_path,relative_path)



# Setup
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fates Roller")

# Load & scale image
spiral = pygame.image.load(resource_path("assets/img/explosion-glow-spiral-yellow.webp")).convert_alpha()
pygame.display.set_icon(spiral)
spiral_rect = spiral.get_rect(center=(WIDTH // 2, HEIGHT // 2))
orb_angles = [0, 45, 90]
orb_positions = [(WIDTH//2 - 200, HEIGHT//2 - 50),
                 (WIDTH//2,       HEIGHT//2 - 100),
                 (WIDTH//2 + 200, HEIGHT//2 - 50)]
softness =  .5

# Fonts
TITLE_FONT = pygame.font.SysFont("palatino linotype", 48, bold=True)
LABEL_FONT = pygame.font.SysFont("consolas", 24)
RESULT_FONT = pygame.font.SysFont("consolas", 28)

# Colors
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
BG = (0, 0, 0)
BTN_COLOR = (40, 40, 40)
BTN_HOVER = (70, 70, 70)

def brightness_to_soft_alpha(path):
    img = Image.open(path).convert("L")  # grayscale for brightness
    width, height = img.size
    cx, cy = width // 2, height // 2
    max_dist = math.hypot(cx, cy)

    rgba = Image.new("RGBA", (width, height))
    for y in range(height):
        for x in range(width):
            # Get pixel brightness (0–255)
            b = img.getpixel((x, y))

            # Compute distance from center (normalized 0–1)
            dx, dy = x - cx, y - cy
            dist = math.hypot(dx, dy) / max_dist

            # Create radial alpha falloff (1.0 at center, 0.0 at edges)
            radial_alpha = max(0.0, 1.0 - dist**softness)
            boost = 1.0 + (1.5 * (1.0 - dist))

            # Multiply brightness by falloff
            final_alpha = int((b / 255.0) * radial_alpha * boost * 255)
            final_alpha = min(final_alpha, 255)

            rgba.putpixel((x, y), (255, 255, 255, final_alpha))

    return pygame.image.fromstring(rgba.tobytes(), rgba.size, rgba.mode).convert_alpha()

#Load image Pt. 2
orb_image = brightness_to_soft_alpha(resource_path("assets/img/explosion-star-small-blue-yellow.webp"))

with open(resource_path("assets/json/RollTable-nouns.json"), "r", encoding="utf-8") as f:
            global fate_table
            fate_table = json.load(f)
    
# Result placeholders
results = [" ", " ", " "]

# Button definition
button_rect = pygame.Rect(WIDTH//2 - 100, HEIGHT//2 + 100, 200, 50)

# Spiral rotation
angle = 0
clock = pygame.time.Clock()

def roll_fates():
    global results
    results = [random.choice(fate_table["results"])["text"].split(',')[0] for _ in range(3)]

def draw_interface():
    # Title
    title_surf = TITLE_FONT.render("Fates Roller", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, 60)))
    
    offset_x, offset_y = -22.5, 2.5 # the true center of the spiral image

    # Result labels
    spacing = 200
    base_x = WIDTH // 2 - spacing
    y_pos = HEIGHT // 2 - 50

    # Base position for centered result column
    block_center = WIDTH // 2

    for i in range(3):
        orb_angles[i] += 0.5 + i * 0.1
        rotated = pygame.transform.rotozoom(orb_image, orb_angles[i], 1.0)
        rect = rotated.get_rect(center=orb_positions[i])
        screen.blit(rotated, rect)
        #label = LABEL_FONT.render(f"R{i+1} =", True, BG)

        theta = -math.radians(orb_angles[i])
        rx = offset_x * math.cos(theta)  - offset_y * math.sin(theta)
        ry = offset_x * math.sin(theta)  + offset_y * math.cos(theta)
        
        center_x = orb_positions[i][0] + rx
        center_y = orb_positions[i][1] + ry

        value = RESULT_FONT.render(results[i], True, BG)
        #screen.blit(label, (base_x + i * spacing, y_pos))
        #word_x = base_x + i * spacing + 60
        #word_rect = value.get_rect(center=(word_x, y_pos + 15))
        word_rect = value.get_rect(center=(center_x, center_y))
        screen.blit(value, word_rect)

    # Button
    mouse_pos = pygame.mouse.get_pos()
    is_hover = button_rect.collidepoint(mouse_pos)
    pygame.draw.rect(screen, BTN_HOVER if is_hover else BTN_COLOR, button_rect, border_radius=6)
    button_text = LABEL_FONT.render("Roll the Fates", True, WHITE)
    screen.blit(button_text, button_text.get_rect(center=button_rect.center))

    title_surf = RESULT_FONT.render("by @exanimomeo", True, WHITE)
    screen.blit(title_surf, title_surf.get_rect(center=(WIDTH//2, HEIGHT - 50)))


running = True
while running:
    screen.fill(BG)

    # Update and draw spiral
    angle -= 0.25
    rotated = pygame.transform.rotozoom(spiral, angle, 1.0)
    scaled = pygame.transform.scale(rotated, (int(rotated.get_width() * 5), int(rotated.get_height() * 3)))
    scaled_rect = scaled.get_rect(center=(WIDTH//2, HEIGHT//2))
    screen.blit(scaled, scaled_rect)

    # Overlay UI
    draw_interface()

    pygame.display.flip()
    clock.tick(60)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and button_rect.collidepoint(event.pos):
                roll_fates()

pygame.quit()
sys.exit()



import pygame
import sys
from pygame.locals import *
# Se till att du har importerat load_from_cache från rätt modul
from historic_data import getEvents, load_from_cache
import re

# Initialisering av Pygame
pygame.init()
pygame.mixer.init()

# Ladda cachad data
cached_events = load_from_cache()
if cached_events is not None:
    all_historic_events = cached_events
else:
    print("Ingen cachad data hittad. Vänligen kör skrapningsmodulen först.")
    sys.exit()  # Avslutar om ingen data finns


# Hämta skärmens dimensioner och sätt fönsterbredden till hälften av skärmens bredd
display_info = pygame.display.Info()
screen_width = int(display_info.current_w // 1.5)
screen_height = 600  # Du kan behålla eller justera höjden efter behov

screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Historiska Händelser")

base_font = pygame.font.Font(None, 32)
user_text = ''
input_rect = pygame.Rect(screen_width // 4, screen_height // 4 + 60, screen_width // 2, 32)
color_active = pygame.Color('lightskyblue3')
color_passive = pygame.Color('gray15')
color = color_passive
active = False

label_font = pygame.font.Font(None, 40)
label_text = label_font.render("Tidsmaskin", True, (255, 255, 255))
label_rect = label_text.get_rect(center=(screen_width // 2, screen_height // 4))

prompt_text = base_font.render("Skriv in det årtal dit du vill resa:", True, (255, 255, 255))
prompt_rect = prompt_text.get_rect(topleft=(input_rect.x, input_rect.y - 25))

background_image = pygame.image.load("bilder/timemachine.png").convert_alpha()
background_image = pygame.transform.scale(background_image, (screen_width, screen_height))  # Skala om bilden
background_image.set_alpha(int(255 * 0.3))  # Sätt opacity till 30%

events_to_display = []
scroll_y = 0  # Initial scroll-position

# Variabel för att lagra den sökta årsrubriken
searched_year_label = None

running = True
time_travel_sound = pygame.mixer.Sound("ljud/time_travel.mp3")

def load_historic_events():
    prel = all_historic_events
    return prel

all_historic_events = load_historic_events()

# I din Pygame-fil, innan spelet startar
cached_events = load_from_cache()
if cached_events:
    all_historic_events = cached_events
else:
    print("Ingen cachad data hittad. Vänligen kör skrapningsmodulen först.")

def getEvents(year):
    found_events = []
    
    for event_tuple in all_historic_events:
        # Antag att event_tuple är en tupel i formen (år, händelse)
        event_year, event_text = event_tuple  # Packa upp tupeln

        # Nu när du har året som en sträng, behöver du inte söka med regex
        if event_year == year:
            # Om det matchar det sökta året, lägg till hela händelsen (eller bara texten, beroende på vad du vill visa)
            found_events.append(event_text)
           
    if not found_events:
        found_events.append("Ingen händelse registrerad för detta år.")

    return found_events


while running:
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        elif event.type == MOUSEBUTTONDOWN:
            if input_rect.collidepoint(event.pos):
                active = not active
            else:
                active = False
            color = color_active if active else color_passive
        elif event.type == KEYDOWN:
            if active:
                if event.key == K_RETURN:
                    year = int(user_text) if user_text.isdigit() else None
                    if year:
                        events_to_display = getEvents(str(year))
                        events_to_display = ["Ingen händelse registrerad för detta år." if event.strip() == "·" else event for event in events_to_display]
                        # Om vi har träffar som inte bara är "Ingen händelse registrerad..."
                        if not all(event == "Ingen händelse registrerad för detta år." for event in events_to_display):
                            time_travel_sound.play()  # Spela upp ljudeffekten
                        events_to_display = [text.split('\n') for text in events_to_display]
                        events_to_display = [line for sublist in events_to_display for line in sublist]
                        searched_year_label = base_font.render(f"Händelser för år {user_text}", True, (255, 255, 255))
                        user_text = ''  # Återställ text efter sökning
                elif event.key == K_BACKSPACE:
                    user_text = user_text[:-1]
                else:
                    user_text += event.unicode
            if event.key == pygame.K_UP:  # Scrolla upp
                scroll_y = min(scroll_y + 20, 0)
            elif event.key == pygame.K_DOWN:  # Scrolla ner
                scroll_y -= 20

    screen.fill((0, 0, 0))
    screen.blit(background_image, (0, 0))

    txt_surface = base_font.render(user_text, True, color)
    screen.blit(prompt_text, prompt_rect)
    screen.blit(txt_surface, (input_rect.x + 5, input_rect.y + 5))
    pygame.draw.rect(screen, color, input_rect, 2)

    screen.blit(label_text, label_rect)

    # Rita ut rubriktexten för det sökta året om den finns
    if searched_year_label:
        year_label_rect = searched_year_label.get_rect(center=(screen_width // 2, input_rect.y - 100))
        screen.blit(searched_year_label, year_label_rect)

    for i, event_text in enumerate(events_to_display):
        event_surface = base_font.render(event_text, True, (255, 255, 255))
        screen.blit(event_surface, (50, (screen_height // 2 + i * 30) + scroll_y))

    pygame.display.flip()

pygame.quit()

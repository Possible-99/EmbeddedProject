import pygame
import time

def play_startup_image_and_sound(image_path, sound_path, display_time=None):
    pygame.init()

    # Set up the display
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Startup")

    # Load the image
    image = pygame.image.load(image_path)
    image = pygame.transform.scale(image, (screen.get_width(), screen.get_height()))

    # Load the sound
    pygame.mixer.init()
    sound = pygame.mixer.Sound(sound_path)

    # Display the image
    screen.blit(image, (0, 0))
    pygame.display.update()

    # Play the sound
    sound.play()

    # If display_time is specified, wait for that duration
    # Otherwise, wait for the duration of the sound
    if display_time is None:
        display_time = sound.get_length()

    time.sleep(display_time)

    pygame.quit()

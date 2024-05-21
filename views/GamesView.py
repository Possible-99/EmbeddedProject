import os
import pygame
import sys
from blinker import signal

class GamesView:
    def __init__(self, game_clicked):
        self.game_clicked = game_clicked
        self.initialized = False
        self.running = False
        self.stop_signal = signal('stop')
        self.stop_signal.connect(self.handle_stop_signal)
        self.initialize_pygame()

    def initialize_pygame(self):
        if self.initialized:
            return
        
        try:
            # Use the framebuffer
            os.putenv('SDL_VIDEODRIVER', 'fbcon')
            os.putenv('SDL_FBDEV', '/dev/fb0')

            # Initialize Pygame and joystick
            pygame.init()
            pygame.joystick.init()
            self.joystick = pygame.joystick.Joystick(0)
            self.joystick.init()

            # Get display info
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h

            # Set up the screen
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
            # Hide the system mouse cursor
            pygame.mouse.set_visible(False)
            self.initialized = True

        except Exception as e:
            print(f"Exception during initialization: {e}")
            self.cleanup()

    def cleanup(self):
        if self.initialized:
            pygame.quit()
            self.initialized = False
        print("Resources cleaned up.")

    def show(self, gamesList):
        self.initialize_pygame()
        self.running = True
        
        pygame.display.set_caption("Game List")
        colors = {
            "background": (46, 52, 64),
            "list_bg": (59, 66, 82),
            "list_element_bg": (76, 86, 106),
            "list_element_hover_bg": (94, 129, 172),
            "text": (236, 239, 244),
            "instruction_text": (136, 192, 208)
        }

        def draw_text(text, color, surface, x, y):
            # Ensure Pygame font is initialized
            if not pygame.font.get_init():
                pygame.font.init()
            font = pygame.font.SysFont('Arial', 16)
            textobj = font.render(text, True, color)
            textrect = textobj.get_rect()
            textrect.topleft = (x, y)
            surface.blit(textobj, textrect)

        margin = 0.01 * self.screen_width
        list_bg_width = self.screen_width - 2 * margin
        list_bg_height = self.screen_height - 2 * margin
        list_bg_x = margin
        list_bg_y = margin

        pointer_x, pointer_y = self.screen_width // 2, self.screen_height // 2

        while self.running:
            self.screen.fill(colors["background"])
            list_bg_rect = pygame.Rect(list_bg_x, list_bg_y, list_bg_width, list_bg_height)
            pygame.draw.rect(self.screen, colors["list_bg"], list_bg_rect)
            instruction_x = list_bg_x + 20
            instruction_y = list_bg_y + 20
            draw_text("Please select a game:", colors["instruction_text"], self.screen, instruction_x, instruction_y)

            element_height = 40
            element_margin_y = 60
            for i, game in enumerate(gamesList):
                element_y = instruction_y + element_margin_y + i * (element_height + 10)
                element_rect = pygame.Rect(instruction_x, element_y, list_bg_width - 40, element_height)
                
                if element_rect.collidepoint((pointer_x, pointer_y)):
                    pygame.draw.rect(self.screen, colors["list_element_hover_bg"], element_rect)
                else:
                    pygame.draw.rect(self.screen, colors["list_element_bg"], element_rect)
                
                draw_text(game, colors["text"], self.screen, element_rect.x + 10, element_rect.y + 10)

                if pygame.joystick.Joystick(0).get_button(0) and element_rect.collidepoint((pointer_x, pointer_y)):
                    self.game_clicked.send(game, gameClicked=game)
                    self.stop_view()
                    return  # Exit the function after stopping the view

            pygame.draw.circle(self.screen, colors["text"], (pointer_x, pointer_y), 5)

            axis_x = self.joystick.get_axis(0)
            axis_y = self.joystick.get_axis(1)
            pointer_x += int(axis_x * 10)
            pointer_y += int(axis_y * 10)
            pointer_x = max(0, min(self.screen_width, pointer_x))
            pointer_y = max(0, min(self.screen_height, pointer_y))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            pygame.display.flip()

        self.cleanup()

    def stop_view(self):
        print('Stopping view and cleaning up resources.')
        self.running = False
        self.cleanup()

    def handle_stop_signal(self, sender):
        print("Received stop signal in GamesView")
        self.stop_view()
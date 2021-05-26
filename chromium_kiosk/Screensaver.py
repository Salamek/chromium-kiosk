import random
import pygame
import signal
import sys
import os


class Screensaver:
    exit = False
    background_color = (0, 0, 0)

    def __init__(self, text: str,  fullscreen: bool = False):
        signal.signal(signal.SIGTERM, self.handle_term)

        window_id = os.environ.get('XSCREENSAVER_WINDOW')
        if window_id:
            os.environ['SDL_WINDOWID'] = window_id

        pygame.init()
        info_object = pygame.display.Info()
        self.clock = pygame.time.Clock()
        self.width = info_object.current_w
        self.height = info_object.current_h

        self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN) if fullscreen else pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Bouncing text screensaver')
        pygame.mouse.set_visible(False)
        self.font = pygame.font.Font(pygame.font.get_default_font(), 36)
        self.animated = self.font.render(text, True, (66, 133, 244))

        self.animated_size = self.animated.get_rect().size

        self.x = random.randint(50, self.width - 60)
        self.y = random.randint(50, self.height - 60)
        self.x_speed = 2.5
        self.y_speed = 2.5

    def handle_term(self, signal=None, frame=None):
        pygame.quit()
        sys.exit(0)

    def move(self, x, y):
        self.screen.blit(self.animated, (x, y))

    def run(self):

        while not self.exit:
            self.screen.fill(self.background_color)
            if (self.x + self.animated_size[0] >= self.width) or (self.x <= 0):
                self.x_speed = -self.x_speed
            if (self.y + self.animated_size[1] >= self.height) or (self.y <= 0):
                self.y_speed = -self.y_speed
            self.x += self.x_speed
            self.y += self.y_speed
            self.move(self.x, self.y)
            pygame.display.update()
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.exit = True

        self.handle_term()
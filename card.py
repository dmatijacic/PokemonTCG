import pygame

class Card:
    def __init__(self, name, image_path, position, max_width=100):
        self.name = name
        self.image_original = pygame.image.load(image_path).convert_alpha()

        # Automatski skaliraj na temelju max_width
        ratio = self.image_original.get_height() / self.image_original.get_width()
        self.width = max_width
        self.height = int(max_width * ratio)
        self.image = pygame.transform.scale(self.image_original, (self.width, self.height))

        self.rect = self.image.get_rect(topleft=position)

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def update_position(self, pos):
        self.rect.topleft = pos

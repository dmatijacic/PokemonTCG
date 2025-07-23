import os
import random
import pygame
from card import Card

class Deck:
    def __init__(self, folder="assets/cards", back_image_name="pokemon_card_game", max_width=100):
        self.cards = []
        self.card_size = (0, 0)

        back_image_path = os.path.join(folder, back_image_name + ".png")
        self.back_image = pygame.image.load(back_image_path).convert_alpha()
        ratio = self.back_image.get_height() / self.back_image.get_width()
        width = max_width
        height = int(max_width * ratio)
        self.back_image = pygame.transform.scale(self.back_image, (width, height))

        for filename in os.listdir(folder):
            if filename.lower().endswith(".png"):
                name = os.path.splitext(filename)[0]
                path = os.path.join(folder, filename)
                self.cards.append(Card(name, path, self.back_image, (0, 0), width))  # ← DODANO: (0, 0)

        random.shuffle(self.cards)

        if self.cards:
            self.card_size = self.cards[0].image.get_size()

            

    def draw(self):
        return self.cards.pop() if self.cards else None
import os
import random
from card import Card

class Deck:
    def __init__(self, folder="assets/cards"):
        self.cards = []
        self.card_size = (0, 0)

        for filename in os.listdir(folder):
            if filename.lower().endswith(".png"):
                name = os.path.splitext(filename)[0]
                path = os.path.join(folder, filename)
                self.cards.append(Card(name, path, (0, 0)))  # ← DODANO: (0, 0)

        random.shuffle(self.cards)

        if self.cards:
            self.card_size = self.cards[0].image.get_size()
            

    def draw(self):
        return self.cards.pop() if self.cards else None
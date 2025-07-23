


class GameState:
    def __init__(self, deck):
        self.turn_player = 1  # 1 for player, 2 for opponent
        self.turn_count = 1
        self.deck = deck
        self.player_hand = []
        self.discard_pile = []
        self.opponent_hand = []
        self.battle_zone = []

    def end_turn(self):
        self.turn_player = 2 if self.turn_player == 1 else 1
        self.turn_count += 1
        print(f"Turn {self.turn_count}: Now it's player {self.turn_player}'s turn.")

    def draw_card(self, hand):
        if self.deck:
            card = self.deck.pop()
            hand.append(card)

    def discard_card(self, card):
        self.discard_pile.append(card)
        
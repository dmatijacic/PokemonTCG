import pygame
import sys
from deck import Deck
from game_state import GameState

def draw_hand(deck, hand, screen_width, y_pos):
    spacing = 20
    # card_width = 100  # ili koristi card.image.get_width() ako znaš točnu veličinu
    card_width = deck.card_size[0]  
    total_width = 7 * card_width + 6 * spacing
    start_x = (screen_width - total_width) // 2

    for i in range(7):
        card = deck.draw()
        if card:
            card.rect.topleft = (start_x + i * (card_width + spacing), y_pos)
            hand.append(card)

def draw_opponent_hand(deck, hand, screen_width, y_pos):
    spacing = 20
    card_width = deck.card_size[0]
    total_width = 7 * card_width + 6 * spacing
    start_x = (screen_width - total_width) // 2

    for i in range(7):
        card = deck.draw()
        if card:
            card.rect.topleft = (start_x + i * (card_width + spacing), y_pos)
            hand.append(card)

def arrange_played_cards(zone_rect, cards, card_size):
    spacing = 20
    total_width = len(cards) * card_size[0] + (len(cards) - 1) * spacing
    start_x = zone_rect.centerx - total_width // 2
    y_pos = zone_rect.centery - card_size[1] // 2

    for i, card in enumerate(cards):
        card.rect.topleft = (start_x + i * (card_size[0] + spacing), y_pos)

def draw_end_turn_button(surface, mouse_pos):
    color = button_hover_color if button_rect.collidepoint(mouse_pos) else button_color
    pygame.draw.rect(surface, color, button_rect, border_radius=8)
    text = button_font.render("End Turn", True, button_text_color)
    text_rect = text.get_rect(center=button_rect.center)
    surface.blit(text, text_rect)

# Inicijalizacija Pygame
pygame.init()
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
clock = pygame.time.Clock()
FPS = 60


# Inicijalizacija špila i početne ruke
deck = Deck()
game_state = GameState(deck)
draw_pile_rect = pygame.Rect(
    40, screen.get_height() // 2 - deck.card_size[1] // 2,
    deck.card_size[0], deck.card_size[1]
)

# Ruka igrača
player_y = screen.get_height() - deck.card_size[1] - 40  # donji dio
played_cards = []
play_zone_rect = pygame.Rect(
    screen.get_width() // 2 - 200,
    screen.get_height() // 2 + 40,
    400,
    deck.card_size[1] + 20
)
draw_hand(deck, game_state.player_hand, screen.get_width(), player_y)

if not played_cards:
    for i in range(3):
        card = deck.draw()
        if card:
            played_cards.append(card)
    arrange_played_cards(play_zone_rect, played_cards, deck.card_size)


# Ruka protivnika
opponent_y = 40  # gornji dio
opponent_played_cards = []
opponent_zone_rect = pygame.Rect(
    screen.get_width() // 2 - 200,
    screen.get_height() // 2 - deck.card_size[1] - 60,
    400,
    deck.card_size[1] + 20
)
draw_opponent_hand(deck, game_state.opponent_hand, screen.get_width(), opponent_y)

dragging_card = None
offset_x = offset_y = 0

if not opponent_played_cards:
    for i in range(3):
        card = deck.draw()
        if card:
            opponent_played_cards.append(card)
    arrange_played_cards(opponent_zone_rect, opponent_played_cards, deck.card_size)

button_font = pygame.font.SysFont(None, 36)
button_color = (200, 0, 0)
button_hover_color = (255, 0, 0)
button_text_color = (255, 255, 255)
button_rect = pygame.Rect(screen.get_width() - 160, screen.get_height() - 60, 140, 40)

# Glavna petlja
running = True
while running:
    # Crtanje
    screen.fill((34, 139, 34))  # zelena podloga kao stol

    # Iscrtavanje zone za bacanje
    pygame.draw.rect(screen, (50, 50, 50), play_zone_rect, border_radius=10)  # sivo područje
    pygame.draw.rect(screen, (200, 200, 200), play_zone_rect, 4, border_radius=10)  # okvir
    font = pygame.font.SysFont(None, 36)
    text_player = font.render("PLAYER ZONE", True, (255, 255, 255))
    screen.blit(text_player, (play_zone_rect.centerx - text_player.get_width() // 2, play_zone_rect.top - 40))

    # Zona protivnika (siva)
    pygame.draw.rect(screen, (100, 100, 100), opponent_zone_rect, border_radius=12)
    text_opponent = font.render("OPPONENT ZONE", True, (255, 255, 255))
    screen.blit(text_opponent, (opponent_zone_rect.centerx - text_opponent.get_width() // 2, opponent_zone_rect.top - 40))

    # Draw pile
    pygame.draw.rect(screen, (60, 60, 60), draw_pile_rect)
    if game_state.deck.cards:
        screen.blit(deck.back_image, draw_pile_rect.topleft)
    draw_text = font.render("DRAW", True, (255, 255, 255))
    screen.blit(draw_text, (draw_pile_rect.centerx - draw_text.get_width() // 2, draw_pile_rect.bottom + 5))
    card_count_text = font.render(str(len(game_state.deck.cards)), True, (255, 255, 255))
    screen.blit(card_count_text, draw_pile_rect.bottomleft)

    # Discard pile
    discard_pile_rect = pygame.Rect(screen.get_width() - 40 - deck.card_size[0], screen.get_height() // 2 - deck.card_size[1] // 2, deck.card_size[0], deck.card_size[1])
    pygame.draw.rect(screen, (80, 80, 80), discard_pile_rect)
    discard_text = font.render("DISCARD", True, (255, 255, 255))
    screen.blit(discard_text, (discard_pile_rect.centerx - discard_text.get_width() // 2, discard_pile_rect.centery - 15))
    if game_state.discard_pile:
        top_discard = game_state.discard_pile[-1]
        screen.blit(top_discard.image, discard_pile_rect.topleft)
    discard_count_text = font.render(str(len(game_state.discard_pile)), True, (255, 255, 255))
    screen.blit(discard_count_text, discard_pile_rect.bottomleft)

    font = pygame.font.SysFont(None, 36)
    text = font.render(f"Player {game_state.turn_player}'s turn", True, (255, 255, 255))
    screen.blit(text, (20, 20))

    for event in pygame.event.get():
        if event.type == pygame.QUIT or (
            event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE
        ):
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # lijevi klik
                for card in reversed(game_state.player_hand):  # zadnje nacrtane su na vrhu
                    if card.rect.collidepoint(event.pos):
                        dragging_card = card
                        game_state.player_hand.remove(card)
                        game_state.player_hand.append(card)  # pomakni na vrh
                        offset_x = event.pos[0] - card.rect.x
                        offset_y = event.pos[1] - card.rect.y
                        break

            elif event.button == 3:  # desni klik
                for card in reversed(game_state.player_hand):
                    if card.rect.collidepoint(event.pos):
                        game_state.player_hand.remove(card)
                        game_state.discard_pile.append(card)
                        break
            if button_rect.collidepoint(event.pos):
                game_state.end_turn()

        elif event.type == pygame.MOUSEBUTTONUP:
            if dragging_card:
                if play_zone_rect.collidepoint(dragging_card.rect.center):
                    played_cards.append(dragging_card)
                    arrange_played_cards(play_zone_rect, played_cards, deck.card_size)
                else:
                    game_state.player_hand.append(dragging_card)
                dragging_card = None

            if event.button == 1:  # lijevi klik
                if draw_pile_rect.collidepoint(event.pos):
                    if game_state.turn_player == 1 and game_state.deck.cards:
                        card = game_state.deck.cards.pop()
                        game_state.player_hand.append(card)
                        draw_hand(deck, [card], screen.get_width(), player_y)
                else:
                    for card in reversed(game_state.player_hand):
                        if card.rect.collidepoint(event.pos):
                            dragging_card = card
                            game_state.player_hand.remove(card)
                            game_state.player_hand.append(card)
                            offset_x = event.pos[0] - card.rect.x
                            offset_y = event.pos[1] - card.rect.y
                            break

        elif event.type == pygame.MOUSEMOTION:
            if dragging_card:
                dragging_card.rect.x = event.pos[0] - offset_x
                dragging_card.rect.y = event.pos[1] - offset_y

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                game_state.end_turn()

    # Crtanje karata
    for card in game_state.player_hand:
        card.draw(screen)

    for card in played_cards:
        card.draw(screen)  # <- Ovdje dodajemo iscrtavanje karata u zoni

    for card in game_state.opponent_hand:
        card.draw(screen)

    for card in opponent_played_cards:
        card.draw(screen)

    mouse_pos = pygame.mouse.get_pos()
    draw_end_turn_button(screen, mouse_pos)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()

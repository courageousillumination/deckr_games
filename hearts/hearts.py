"""
This file provides a simple, single round implementation of the card game
hearts.
"""

from random import shuffle

from deckr.contrib.card import Card
from deckr.contrib.playing_card import create_deck, PlayingCard
from deckr.core.game import action, Game, restriction


def is_point_card(card):
    return (card.suit == 'hearts' or
            (card.number == 12 and card.suit == 'spades'))

class Hearts(Game):

    game_zones = [
        {'name': 'play_zone'},
        {'name': 'pocket'}
    ]

    player_zones = [
        {'name': 'hand'},
        {'name': 'discard'}
    ]

    #pylint: disable=unused-argument
    def __init__(self, *args, **kwargs):
        super(Hearts, self).__init__(*args, **kwargs)

        self.is_passing_phase = True
        self.leading_suit = None
        self.current_player = None

    def set_up(self):
        """
        Set up the game: This involves building a deck, and dealing out the
        cards, etc.
        """

        deck = create_deck()
        self.register(deck)
        shuffle(deck)

        # Deal the cards to the players
        cards_per_player = len(deck) / len(self.players)
        for player in self.players:
            for i in range(cards_per_player):
                card = deck.pop()
                card.owner = player
                card.set_game_attribute('face_up', True, player)
                player.hand.push(card)

        # Put the remaining cards in the pocket
        for i in range(len(deck)):
            self.pocket.push(deck.pop())


    # Various restrictions
    @restriction("You can't pass cards at this time.")
    def passing_phase(self, **kwargs):
        return self.is_passing_phase

    @restriction("You have selected an invalid set of cards to pass.")
    def pass_valid(self, player, cards, **kwargs):
        if len(cards) != 3:
            return False
        for card in cards:
            if card not in player.hand:
                return False
        return True

    @restriction("It's not your turn")
    def is_players_turn(self, player, **kwargs):
        return self.current_player == player

    @restriction("Your card is not in suite")
    def is_in_suite(self, card, **kwargs):
        return self.leading_suit is None or card.suit == self.leading_suit

    @restriction("That's not a valid card for the first turn")
    def first_turn_valid(self, card, **kwargs):
        return not is_point_card(card)

    @restriction("The trick isn't finished")
    def trick_finished(self, **kwargs):
        return len(self.play_zone) == len(self.players)

    @restriction("You didn't win that trick")
    def can_take_trick(self, player, **kwargs):
        valid_cards = [x for x in self.play_zone if x.suit == self.leading_suit]
        max_card = max(valid_cards, key=lambda x: x.number)
        return max_card.owner == player

    # Possible actions
    @action(params={'cards': Card}, restrictions=[passing_phase, pass_valid])
    def pass_cards(self, player, cards):
        # Right now we only implement a pass left semantic. Further passing would
        # require tracking more state in the game.
        pass_to = self.player_to_left(player)
        for card in cards:
            player.hand.remove(card)
            pass_to.hand.add(card)

    @action(params={'card': Card},
            restrictions=[is_players_turn, is_in_suite, first_turn_valid])
    def play_card(self, player, card):
        player.hand.remove(card)
        self.play_zone.add(card)

        # Check if we need to set the leading suit
        if self.leading_suit is None:
            self.leading_suit = card.suit

        self.current_player = self.player_to_left(self.current_player)

    @action(restrictions=[trick_finished, can_take_trick])
    def take_trick(self, player):
        for card in self.play_zone:
            player.discard.add(card)
        self.play_zone.clear()
        self.leading_suit = None
        self.current_player = player

    # Utility functions
    def player_to_left(self, player):
        """
        Get the player to the left of the inputted player.
        """

        index = self.players.index(player)
        if index == (len(self.players) - 1):
            return self.players[0]
        return self.players[index + 1]

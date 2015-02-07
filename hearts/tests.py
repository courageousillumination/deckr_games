from unittest import TestCase

from deckr.contrib.playing_card import PlayingCard
from deckr.core.exceptions import FailedRestrictionException
from hearts import Hearts


class HeartsTestCase(TestCase):

    def setUp(self):
        self.game = Hearts()
        self.player1 = self.game.add_player()
        self.player2 = self.game.add_player()
        self.player3 = self.game.add_player()
        self.player4 = self.game.add_player()
        self.game.set_up()

    def test_set_up(self):
        """
        Make sure that set up properly deals out cards.
        """

        game = Hearts()
        player1 = game.add_player()
        player2 = game.add_player()
        player3 = game.add_player()

        game.set_up()
        self.assertEqual(len(player1.hand), 17)
        self.assertEqual(len(player2.hand), 17)
        self.assertEqual(len(player3.hand), 17)
        self.assertEqual(len(game.pocket), 1)

        game = Hearts()
        player1 = game.add_player()
        player2 = game.add_player()
        player3 = game.add_player()
        player4 = game.add_player()

        game.set_up()
        self.assertEqual(len(player1.hand), 13)
        self.assertEqual(len(player2.hand), 13)
        self.assertEqual(len(player3.hand), 13)
        self.assertEqual(len(player4.hand), 13)
        self.assertEqual(len(game.pocket), 0)

    def test_pass(self):
        """
        Make sure we can properly pass cards.
        """

        cards = self.player1.hand[0:3]
        self.game.pass_cards(player=self.player1, cards=cards)
        for card in cards:
            self.assertIn(card, self.player2.hand)

    def test_play_card(self):
        """
        Make sure we can properly play a card.
        """

        # First we set up the game

        # Hack the first card to be the 2 of clubs
        self.player1.hand.clear()
        self.game.current_player = self.player1

        card = PlayingCard(2, 'clubs')
        self.player1.hand.add(card)

        self.game.play_card(player=self.player1, card=card)
        self.assertIn(card, self.game.play_zone)
        self.assertNotIn(card, self.player1.hand)

        # Try to play an invalid suit
        card = PlayingCard(1, 'hearts')
        self.player2.hand.add(card)
        self.assertRaises(FailedRestrictionException, self.game.play_card,
                          player=self.player2, card=card)
        card.suit = 'clubs'
        self.game.play_card(player=self.player2, card=card)

    def test_take_trick(self):
        """
        Make sure we can take a trick.
        """

        pass

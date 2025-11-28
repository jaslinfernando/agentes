# test_bets.py
import unittest
from bets import BettingSystem, User, Bet, get_bet

class BettingSystemTest(unittest.TestCase):
    def setUp(self):
        self.system = BettingSystem()
        self.user = self.system.create_account("Alice", 100.0)

    def test_create_account(self):
        self.assertEqual(self.user.username, "Alice")
        self.assertEqual(self.user.balance, 100.0)

    def test_place_bet_success(self):
        bet = self.system.place_bet(self.user.user_id, 'soccer', ('TeamA', 'TeamB'), 50.0)
        self.assertIsNotNone(bet)
        self.assertEqual(bet.sport, 'soccer')
        self.assertEqual(self.system.users[self.user.user_id].balance, 50.0)

    def test_place_bet_failure_due_to_insufficient_funds(self):
        bet = self.system.place_bet(self.user.user_id, 'soccer', ('TeamA', 'TeamB'), 150.0)
        self.assertIsNone(bet)

    def test_modify_bet(self):
        bet = self.system.place_bet(self.user.user_id, 'soccer', ('TeamA', 'TeamB'), 50.0)
        self.system.modify_bet(self.user.user_id, bet.bet_id, 30.0, 1.6)
        self.assertEqual(bet.amount, 30.0)
        self.assertEqual(self.user.balance, 70.0)

    def test_report_investments(self):
        self.system.place_bet(self.user.user_id, 'soccer', ('TeamA', 'TeamB'), 50.0)
        investments = self.system.report_investments(self.user.user_id)
        self.assertEqual(investments, 50.0)

    def test_report_profit_loss(self):
        self.system.place_bet(self.user.user_id, 'soccer', ('TeamA', 'TeamB'), 50.0)
        profit_loss = self.system.report_profit_loss(self.user.user_id)
        self.assertEqual(profit_loss, -50.0)

    def test_list_user_transactions(self):
        bet = self.system.place_bet(self.user.user_id, 'basketball', ('TeamX', 'TeamY'), 40.0)
        transactions = self.system.list_user_transactions(self.user.user_id)
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0], (bet.bet_id, 'basketball', 40.0, 'pending'))

    def test_get_bet(self):
        self.assertEqual(get_bet('soccer'), 1.5)
        self.assertEqual(get_bet('unknown_sport'), 1.0)

if __name__ == '__main__':
    unittest.main()
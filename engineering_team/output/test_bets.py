import unittest
from bets import Bet, get_bet

class TestBet(unittest.TestCase):
    
    def setUp(self):
        # Setting up a Bet instance and creating a user for testing
        self.bet_system = Bet()
        self.bet_system.create_user('test_user', 1000)
    
    def test_create_user(self):
        # Test user creation
        self.bet_system.create_user('new_user', 500)
        self.assertIn('new_user', self.bet_system.users)
    
    def test_create_user_exists_raises(self):
        # Test if creating an existing user raises a ValueError
        with self.assertRaises(ValueError):
            self.bet_system.create_user('test_user', 1000)

    def test_place_bet(self):
        # Test placing a valid bet
        self.bet_system.place_bet('test_user', 'soccer', 100)
        self.assertEqual(self.bet_system.users['test_user']['balance'], 900)
    
    def test_place_bet_insufficient_funds_raises(self):
        # Test placing a bet with insufficient funds
        with self.assertRaises(ValueError):
            self.bet_system.place_bet('test_user', 'soccer', 1100)

    def test_modify_bet(self):
        # Test modifying an existing bet
        self.bet_system.place_bet('test_user', 'soccer', 100)
        self.bet_system.modify_bet('test_user', 'soccer', 150)
        self.assertEqual(self.bet_system.users['test_user']['balance'], 850)
        self.assertEqual(self.bet_system.users['test_user']['portfolio']['soccer'], 150)

    def test_modify_nonexistent_bet_raises(self):
        # Test modifying a non-existing bet
        with self.assertRaises(ValueError):
            self.bet_system.modify_bet('test_user', 'soccer', 150)

    def test_calculate_portfolio_value(self):
        # Test calculating portfolio value
        self.bet_system.place_bet('test_user', 'soccer', 200)
        self.bet_system.place_bet('test_user', 'basketball', 300)
        value = self.bet_system.calculate_portfolio_value('test_user')
        self.assertEqual(value, 500)

    def test_calculate_profit_loss(self):
        # Test calculating profit and loss
        self.bet_system.place_bet('test_user', 'soccer', 200)
        self.bet_system.place_bet('test_user', 'basketball', 300)
        profit_loss = self.bet_system.calculate_profit_loss('test_user')
        self.assertEqual(profit_loss, -500)
    
    def test_report_investments(self):
        # Test reporting investments
        self.bet_system.place_bet('test_user', 'soccer', 200)
        investments = self.bet_system.report_investments('test_user')
        self.assertEqual(investments['soccer'], 200)
    
    def test_report_transactions(self):
        # Test reporting transactions
        self.bet_system.place_bet('test_user', 'soccer', 200)
        transactions = self.bet_system.report_transactions('test_user')
        self.assertEqual(len(transactions), 2)  # Deposit + 1 Bet
    
    def test_validate_bet_negative_amount_raises(self):
        # Test validation for negative bet amount
        with self.assertRaises(ValueError):
            self.bet_system.place_bet('test_user', 'soccer', -10)
    
    def test_validate_bet_invalid_sport_raises(self):
        # Test placing a bet on an invalid sport
        with self.assertRaises(ValueError):
            self.bet_system.place_bet('test_user', 'hockey', 50)
    
    def test_is_valid_bet(self):
        # Test if is_valid_bet function works properly
        self.assertTrue(self.bet_system.is_valid_bet('soccer'))
        self.assertFalse(self.bet_system.is_valid_bet('hockey'))

if __name__ == '__main__':
    unittest.main()
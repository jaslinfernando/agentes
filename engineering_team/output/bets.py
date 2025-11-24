class Bet:
    def __init__(self):
        self.users = {}

    def create_user(self, username: str, initial_deposit: float) -> None:
        if username in self.users:
            raise ValueError("User already exists")
        self.users[username] = {
            'balance': initial_deposit,
            'portfolio': {},
            'transactions': [{'type': 'deposit', 'amount': initial_deposit}]
        }

    def place_bet(self, username: str, sport: str, amount: float) -> None:
        self.validate_bet(username, sport, amount)
        self.users[username]['balance'] -= amount
        if sport in self.users[username]['portfolio']:
            self.users[username]['portfolio'][sport] += amount
        else:
            self.users[username]['portfolio'][sport] = amount
        self.users[username]['transactions'].append({'type': 'bet', 'sport': sport, 'amount': amount})

    def modify_bet(self, username: str, sport: str, new_amount: float) -> None:
        if sport not in self.users[username]['portfolio']:
            raise ValueError("No existing bet on this sport to modify")
        current_amount = self.users[username]['portfolio'][sport]
        difference = new_amount - current_amount
        self.validate_bet(username, sport, difference)
        self.users[username]['portfolio'][sport] = new_amount
        self.users[username]['balance'] -= difference
        self.users[username]['transactions'].append({'type': 'modify_bet', 'sport': sport, 'old_amount': current_amount, 'new_amount': new_amount})

    def calculate_portfolio_value(self, username: str) -> float:
        return sum(self.users[username]['portfolio'].values())

    def calculate_profit_loss(self, username: str) -> float:
        initial_deposit = next((t['amount'] for t in self.users[username]['transactions'] if t['type'] == 'deposit'), 0)
        current_balance_with_bets = self.users[username]['balance'] + self.calculate_portfolio_value(username)
        return current_balance_with_bets - initial_deposit

    def report_investments(self, username: str) -> dict:
        return self.users[username]['portfolio'].copy()

    def report_transactions(self, username: str) -> list:
        return self.users[username]['transactions'].copy()

    def validate_bet(self, username: str, sport: str, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Bet amount must be positive")
        if self.users[username]['balance'] < amount:
            raise ValueError("Insufficient funds")
        if not self.is_valid_bet(sport):
            raise ValueError("Cannot place bet on this match")

    def is_valid_bet(self, sport: str) -> bool:
        # Placeholder for match validation logic
        # Assume all sports are valid except those that return 0
        return get_bet(sport) > 0

def get_bet(sport: str) -> float:
    # Test implementation of get_bet(sport) function with fixed return values
    bets = {
        "soccer": 100.0,
        "basketball": 150.0,
        "baseball": 200.0
    }
    return bets.get(sport.lower(), 0)
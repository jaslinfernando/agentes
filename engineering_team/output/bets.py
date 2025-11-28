import datetime

# Mock implementation of get_bet function

def get_bet(sport: str) -> float:
    """Returns the current betting odds for a given sport."""
    odds = {
        'soccer': 1.5,
        'basketball': 2.0,
        'baseball': 1.8
    }
    return odds.get(sport, 1.0)

class User:
    def __init__(self, user_id: int, username: str, initial_deposit: float):
        self.user_id = user_id
        self.username = username
        self.balance = initial_deposit
        self.initial_deposit = initial_deposit
        self.bets = []

    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= self.balance:
            self.balance -= amount

    def get_portfolio_value(self) -> float:
        return self.balance + sum(bet.amount for bet in self.bets if bet.status == 'pending')

    def calculate_profit_loss(self) -> float:
        return self.balance - self.initial_deposit

    def list_transactions(self) -> list:
        return [(bet.bet_id, bet.sport, bet.amount, bet.status) for bet in self.bets]

class Bet:
    def __init__(self, bet_id: int, user_id: int, sport: str, momio: float, teams: tuple, amount: float):
        self.bet_id = bet_id
        self.user_id = user_id
        self.sport = sport
        self.momio = momio
        self.teams = teams
        self.amount = amount
        self.status = 'pending'
        self.created_at = datetime.datetime.now()

    def update_bet(self, amount: float, momio: float) -> None:
        self.amount = amount
        self.momio = momio

    def finalize_bet(self, result: str) -> None:
        self.status = result

    def is_valid(self, current_time: datetime.datetime, user_balance: float) -> bool:
        return self.amount <= user_balance #self.created_at <= current_time and 
        

class BettingSystem:
    def __init__(self):
        self.users = {}
        self.bets = {}
        self.current_bet_id = 0
        self.current_user_id = 0

    def create_account(self, username: str, initial_deposit: float) -> User:
        self.current_user_id += 1
        user = User(self.current_user_id, username, initial_deposit)
        self.users[self.current_user_id] = user
        return user

    def place_bet(self, user_id: int, sport: str, teams: tuple, amount: float) -> Bet:
        user = self.users.get(user_id)
        if not user or amount > user.balance:
            return None
        current_time = datetime.datetime.now()
        self.current_bet_id += 1
        momio = get_bet(sport)
        bet = Bet(self.current_bet_id, user_id, sport, momio, teams, amount)
        if bet.is_valid(current_time, user.balance):
            user.balance -= amount
            user.bets.append(bet)
            self.bets[self.current_bet_id] = bet
            return bet
        return None

    def modify_bet(self, user_id: int, bet_id: int, amount: float, momio: float) -> None:
        bet = self.bets.get(bet_id)
        user = self.users.get(user_id)
        if bet and user and bet.user_id == user_id:
            initial_amount = bet.amount
            if amount <= (user.balance + initial_amount):
                bet.update_bet(amount, momio)
                user.balance += initial_amount - amount

    def report_investments(self, user_id: int) -> float:
        user = self.users.get(user_id)
        if user:
            return sum(bet.amount for bet in user.bets if bet.status == 'pending')
        return 0.0

    def report_profit_loss(self, user_id: int) -> float:
        user = self.users.get(user_id)
        if user:
            return user.calculate_profit_loss()
        return 0.0

    def list_user_transactions(self, user_id: int) -> list:
        user = self.users.get(user_id)
        if user:
            return user.list_transactions()
        return []

    def validate_bet(self, team: str) -> bool:
        # Placeholder for actual game status check
        return True

# Example Usage
if __name__ == "__main__":
    system = BettingSystem()
    user = system.create_account("Alice", 100.0)
    system.place_bet(user.user_id, 'soccer', ('TeamA', 'TeamB'), 50.0)
    print(system.report_investments(user.user_id))
    print(system.report_profit_loss(user.user_id))
    print(system.list_user_transactions(user.user_id))
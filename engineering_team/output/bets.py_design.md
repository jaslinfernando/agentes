```markdown
# bets.py Module Design

This module, `bets.py`, is designed to manage a betting system where users can create accounts, place bets on sporting events, view their investments, and track their profits or losses. All classes and methods in this module are detailed below.

## Classes and Methods

### Class: User

- **Attributes:**
  - `user_id (int)`: A unique identifier for the user.
  - `username (str)`: The user's name.
  - `balance (float)`: The current balance available for the user to bet.
  - `initial_deposit (float)`: The starting amount deposited by the user.
  - `bets (list of Bet)`: A list to track all the bets placed by the user.

- **Methods:**
  - `__init__(self, user_id: int, username: str, initial_deposit: float)`: Initializes a new user with a specified ID, name, and initial deposit.
  - `deposit(self, amount: float) -> None`: Adds funds to the user's balance.
  - `withdraw(self, amount: float) -> None`: Removes funds from the user's balance if sufficient funds exist.
  - `get_portfolio_value(self) -> float`: Returns the total value of the user's portfolio.
  - `calculate_profit_loss(self) -> float`: Calculates and returns the user's profit or loss from their initial deposit.
  - `list_transactions(self) -> list`: Returns a list of all the user's transactions.

### Class: Bet

- **Attributes:**
  - `bet_id (int)`: A unique identifier for the bet.
  - `user_id (int)`: The ID of the user who placed the bet.
  - `sport (str)`: The sport on which the bet is placed.
  - `momio (float)`: The odds for the bet.
  - `teams (tuple of str)`: The teams involved in the bet.
  - `amount (float)`: The amount of money placed on the bet.
  - `status (str)`: The status of the bet (e.g., "pending," "won," "lost").
  - `created_at (datetime)`: The timestamp when the bet was created.

- **Methods:**
  - `__init__(self, bet_id: int, user_id: int, sport: str, momio: float, teams: tuple, amount: float)`: Initializes a new bet with the given details and sets its status to "pending".
  - `update_bet(self, amount: float, momio: float) -> None`: Updates the bet's amount and momio.
  - `finalize_bet(self, result: str) -> None`: Finalizes the bet status based on the match result.
  - `is_valid(self, current_time: datetime, user_balance: float) -> bool`: Checks if the bet is valid based on available balance and game status.

### Function: get_bet(sport: str) -> float

- **Description:** External function used to obtain the current bet odds for a given sport. A test implementation returns fixed odds for soccer, basketball, and baseball.

### Class: BettingSystem

- **Attributes:**
  - `users (dict of int: User)`: A dictionary mapping user IDs to User objects.
  - `bets (dict of int: Bet)`: A dictionary mapping bet IDs to Bet objects.
  - `current_bet_id (int)`: A counter to generate unique bet IDs.
  - `current_user_id (int)`: A counter to generate unique user IDs.

- **Methods:**
  - `__init__(self)`: Initializes the betting system with empty users and bets.
  - `create_account(self, username: str, initial_deposit: float) -> User`: Creates a new user account and returns the User object.
  - `place_bet(self, user_id: int, sport: str, teams: tuple, amount: float) -> Bet`: Registers a new bet for a user and returns the Bet object.
  - `modify_bet(self, user_id: int, bet_id: int, amount: float, momio: float) -> None`: Modifies an existing bet with new details.
  - `report_investments(self, user_id: int) -> float`: Provides the total investments for a user.
  - `report_profit_loss(self, user_id: int) -> float`: Provides the total profit or loss for a user.
  - `list_user_transactions(self, user_id: int) -> list`: Lists all transactions for a user.
  - `validate_bet(self, team: str) -> bool`: Validates if a bet can be placed for the given team.

This design ensures that all functionality as described in the requirements will be met, and the system will be ready to be integrated with a simple UI for further interactions.
```

from pydantic import BaseModel
from dotenv import load_dotenv
from database import write_account, read_account, write_log
from datetime import datetime

import json
import uuid


# Mock implementation of get_bet function

INITIAL_BALANCE = 10_0.0
INITIAL_USER_ID= 0

def get_bet(sport: str) -> float:
    """Returns the current betting odds for a given sport."""
    odds = {
        'soccer': 1.5,
        'basketball': 2.0,
        'baseball': 1.8
    }
    return odds.get(sport, 1.0)

class Sport(BaseModel):
    name: str
    #sport_id: str

class Team(BaseModel):
    name: str
    sport: Sport

class Game(BaseModel):
    local_team: Team
    visit_team: Team
    final_score: str
    winner_team: Team
    #date_time: datetime

class Momio(BaseModel):
    game: Game
    bet_type: str #Ej: Ganador (Moneyline), Hándicap, Over/Under
    local_momio: float #Cuota para el equipo local
    visit_momio: float #Cuota para el equipo visitante
    draw_momio: float # Cuota para el empate (Si aplica)

class Bet(BaseModel):

    username: str
    momio: Momio
    chosen_team: Team
    bet_amount: float
    status: str #Pendiente, Ganada, Perdida, Anulada
    total_profit: float #"Monto total retornado si gana (Monto Apostado * Momio)
    net_profit_amount: float #Ganancia total - Monto Apostado
    rationale: str
    bet_id: str

    
    def update_bet(self, team_name: str, status: str):
        total_profit = 0.0 #"Monto total retornado si gana (Monto Apostado * Momio)"
        net_profit_amount = 0.0 #Ganancia total - Monto Apostado

        chosen_team_name= self.chosen_team.name       
        team_sender = Team(name=team_name,sport=self.momio.game.local_team.sport)

        if team_name.upper() == chosen_team_name.upper(): #reviso si mi equipo ha ganado o perdido
            if status.upper() == "Win".upper():
                self.status = "Win"
                self.momio.game.winner_team = self.chosen_team 
                total_profit = self.bet_amount * self.momio.local_momio
                net_profit_amount = total_profit - self.bet_amount
                print(f"***Win total_profit:{total_profit} = {self.bet_amount}*{self.momio.local_momio }")
            elif status.upper() == "Lose".upper():
                self.momio.game.winner_team = self.momio.game.visit_team 
                self.status = "Lose"
                print(f"***Lose total_profit:{total_profit} ")
            elif status.upper() == "Draw".upper():
                print(f"***Draw total_profit:{total_profit} = {self.bet_amount}*{self.momio.draw_momio }")              
            elif status.upper() == "Pending".upper():
                print(f"***Pending total_profit:{total_profit} ")               
            elif status.upper() == "Canceled".upper():
                print(f"***Canceled total_profit:{total_profit} ")
        else:
            if status.upper() == "Win".upper():
                self.momio.game.winner_team = team_sender
                self.status = "Lose" #si el otro equipo gana yo pierdo
            elif status.upper() == "Lose".upper():#si el otro equipo pierde yo gano
                self.status = "Win"
                self.momio.game.winner_team = self.chosen_team
                total_profit = self.bet_amount * self.momio.local_momio
                net_profit_amount = total_profit - self.bet_amount              


        self.net_profit_amount = net_profit_amount
        self.total_profit = total_profit
        b = self
       
        return b

        

    def finalize_bet(self, result: str) -> None:
        self.status = result

    def is_valid(self, current_time: datetime, user_balance: float) -> bool:
        return self.bet_amount <= user_balance #self.created_at <= current_time and 

class User(BaseModel):
   
    username: str 
    initial_deposit: float
    balance: float
    bets: list[Bet]
    holdings: dict[str, int]

    strategy: str
    portfolio_value_time_series: list[tuple[str, float]]
   

    @classmethod
    def get(cls, name: str):
        #print(f"***Getting name:{name}")
        fields = read_account(name.lower())
        if not fields:

            fields = {
                "user_id": uuid.uuid4().__str__(),
                "username": name.lower(),                
                "initial_deposit": INITIAL_BALANCE,
                "balance": INITIAL_BALANCE,
                "strategy": "",
                "bets": [],
                "holdings": {},
                "portfolio_value_time_series": []
            }

            write_account(name, fields)
        return cls(**fields)


    def deposit(self, amount: float) -> None:
        self.balance += amount

    def withdraw(self, amount: float) -> None:
        if amount <= self.balance:
            self.balance -= amount

    def get_portfolio_value(self) -> float:
        return self.balance + sum(bet.amount for bet in self.bets if bet.status == 'pending')

    def calculate_profit_loss(self,portfolio_value: float) -> float:
        return self.balance - self.initial_deposit

    def list_transactions(self) -> list:       
        
        dataList = []
        for t in self.bets:
            data = {}
            #data["username"] = t.username
            data["Sport"] = t.momio.game.local_team.sport.name
            data["Momio"] = f"local({t.momio.local_momio}) - visit({t.momio.visit_momio})"
            data["Amount"] = t.bet_amount
            data["Teams"] = f"local ({t.momio.game.local_team.name} ) - visit({t.momio.game.visit_team.name}))"
            data["Winner"] = t.momio.game.winner_team.name
            data["Chosen"] = t.chosen_team.name
            data["Status"] = t.status
            data["Rationale"] = t.rationale            
            dataList.append(data)

        return dataList
        #return [transaction.model_dump() for transaction in self.bets]
        
    
    def get_holdings(self):
        """ Report the current holdings of the user. """
        return self.holdings
    
    def save(self):
        write_account(self.username.lower(), self.model_dump())
    
    def report(self) -> str:
        """ Return a json string representing the account.  """
        portfolio_value = self.get_portfolio_value()
        self.portfolio_value_time_series.append((datetime.now().strftime("%Y-%m-%d %H:%M:%S"), portfolio_value))
        self.save()
        pnl = self.calculate_profit_loss(portfolio_value)
        data = self.model_dump()
        data["total_portfolio_value"] = portfolio_value
        data["total_profit_loss"] = pnl
        #write_log(self.username, "account", f"Retrieved account details")
        write_log(self.username, "account", f"Retrieved account details balance: {self.balance}")
        return json.dumps(data)
    
    def get_strategy(self) -> str:
        """ Return the strategy of the account """
        write_log(self.username, "account", f"Retrieved strategy")
        return self.strategy
    
    def change_strategy(self, strategy: str) -> str:
        """ At your discretion, if you choose to, call this to change your investment strategy for the future """
        self.strategy = strategy
        self.save()
        write_log(self.username, "account", f"Changed strategy")
        return "Changed strategy"
    

    def place_bet( self,username: str, momio: Momio,chosen_team: Team, bet_amount: float, status: str,rationale:str) -> Bet:
        
        total_profit = 0.0 #"Monto total retornado si gana (Monto Apostado * Momio)"
        net_profit_amount = 0.0 #Ganancia total - Monto Apostado
        bet_id = uuid.uuid4()
       
        user = User.get(username)
        if not user or bet_amount > user.balance:
            return None
        current_time = datetime.now()

        status = "Pending" #by default       
        
        bet = Bet(username=username,momio=momio,chosen_team=chosen_team,bet_amount=bet_amount, status=status, total_profit=total_profit,net_profit_amount=net_profit_amount,rationale=rationale
                  ,bet_id = bet_id.__str__())
        if bet.is_valid(current_time, user.balance):
            self.username = username
            self.bets.append(bet)     
            
            write_log(self.username, "account", f"bet {bet_amount} to[ {momio.game.local_team.name} vs {momio.game.visit_team.name} in {momio.game.local_team.sport.name}]")
            return "Completed. Latest details:\n" + self.report()
            #return bet
        return None
    
    def update_bet( self,username: str, bet_id:str, team_name: str, status: str) -> Bet:

        total_profit = 0.0 #"Monto total retornado si gana (Monto Apostado * Momio)"
        net_profit_amount = 0.0 #Ganancia total - Monto Apostado
        
        user = User.get(username)
        if not user:
            return None
        
        f = None
        index = -1
        for b in user.bets:
            index += 1
            if b.bet_id == bet_id:
                f = b.update_bet(team_name=team_name,status=status)                
        
        if f is not None:
            team_name = team_name
            chosen_team_name= f.chosen_team.name
            if team_name.upper() == chosen_team_name.upper():
                if status.upper() == "Win".upper():
                    f.status = "Win"
                    f.momio.game.winner_team = f.chosen_team 
                    self.balance += f.total_profit
                    print(f"*** updating bet total_profit:{total_profit} = {f.bet_amount}*{f.momio.local_momio }")
                    self.holdings[f.chosen_team.sport.name] = self.holdings.get(f.chosen_team.sport.name, 0) + f.total_profit
                else:
                    self.balance -= f.bet_amount
                    self.holdings[f.chosen_team.sport.name] = self.holdings.get(f.chosen_team.sport.name, 0) - f.bet_amount

            else: #es el otro team
                if status.upper() == "Win".upper():
                    self.balance -= f.bet_amount #yo pierdo mi apuesta
                    self.holdings[f.chosen_team.sport.name] = self.holdings.get(f.chosen_team.sport.name, 0) - f.bet_amount
                    f.status = "Lose" #si el otro equipo gana yo pierdo
                    self.momio.game.winner_team = self.momi
                elif status.upper() == "Lose".upper():#si el otro equipo pierde yo gano
                    self.balance += f.total_profit
                    self.holdings[f.chosen_team.sport.name] = self.holdings.get(f.chosen_team.sport.name, 0) + f.total_profit
                    f.status = "Win"
            self.bets[index] = f
            self.save()
        return self.report()
    
        

# class BettingSystem:
#     def __init__(self):
#         self.users = {}
#         self.bets = {}
#         self.current_bet_id = 0
#         self.current_user_id = 0


#     # users: dict[User,int]
#     # bets: dict[Bet,int]
#     # current_bet_id: int
#     # current_user_id: int
    

#     def create_account(self, username: str, initial_deposit: float) -> User:
#         self.current_user_id += 1
#         user = User(self.current_user_id, username, initial_deposit)
#         self.users[self.current_user_id] = user
#         return user

#     def place_bet(self, user_id: int, sport: str, teams: tuple, amount: float) -> Bet:
#         user = self.users.get(user_id)
#         if not user or amount > user.balance:
#             return None
#         current_time = datetime.datetime.now()
#         self.current_bet_id += 1
#         momio = get_bet(sport)
#         bet = Bet(self.current_bet_id, user_id, sport, momio, teams, amount)
#         if bet.is_valid(current_time, user.balance):
#             user.balance -= amount
#             user.bets.append(bet)
#             self.bets[self.current_bet_id] = bet
#             return bet
#         return None

#     def modify_bet(self, user_id: int, bet_id: int, amount: float, momio: float) -> None:
#         bet = self.bets.get(bet_id)
#         user = self.users.get(user_id)
#         if bet and user and bet.user_id == user_id:
#             initial_amount = bet.amount
#             if amount <= (user.balance + initial_amount):
#                 bet.update_bet(amount, momio)
#                 user.balance += initial_amount - amount

#     def report_investments(self, user_id: int) -> float:
#         user = self.users.get(user_id)
#         if user:
#             return sum(bet.amount for bet in user.bets if bet.status == 'pending')
#         return 0.0

#     def report_profit_loss(self, user_id: int) -> float:
#         user = self.users.get(user_id)
#         if user:
#             return user.calculate_profit_loss()
#         return 0.0

#     def list_user_transactions(self, user_id: int) -> list:
#         user = self.users.get(user_id)
#         if user:
#             return user.list_transactions()
#         return []

#     def validate_bet(self, team: str) -> bool:
#         # Placeholder for actual game status check
#         return True

# # Example Usage
# if __name__ == "__main__":
#     system = BettingSystem()
#     user = system.create_account("jaslin", 100.0)
#     system.place_bet(user.user_id, 'soccer', ('TeamA', 'TeamB'), 50.0)
#     print(system.report_investments(user.user_id))
#     print(system.report_profit_loss(user.user_id))
#     print(system.list_user_transactions(user.user_id))


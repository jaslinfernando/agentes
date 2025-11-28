from mcp.server.fastmcp import FastMCP
from bets import User,Sport,Team,Game,Momio,Bet
from datetime import datetime
from typing import Dict 

mcp = FastMCP("bets_server")

@mcp.tool(name="get_holdings", description="Get the holdings of the given account name")
async def get_holdings(name: str) -> dict[str, int]:
    """Get the holdings of the given account name.

    Args:
        name: The name of the account holder
    """
    return User.get(name).holdings

@mcp.tool(name="place_bate", description="Place bet of the given account name")
async def place_bate(name: str, sportname: str, local_team_name: str, visit_team_name:str, local_momio_value: float, bet_amount: float, rationale: str):
    """Place bet of the given account name.

    Args:
        name: The name of the account holder
        sportname: The sport
        local_team_name: The local team
        visit_team_name: The visit team  
        local_momio_value local momio value
        bet_amount bet amount
        rationale: The rationale for the purchase and fit with the account's strategy
    """

    sport= Sport(name=sportname)
    local_team = Team(name=local_team_name,sport=sport)
    visit_team = Team(name=visit_team_name,sport=sport)
    final_score = ""
    date_time = datetime.now()
    winner_team = Team(name="",sport=sport) # X equipo que ha ganado
    game = Game(local_team=local_team,visit_team=visit_team,final_score=final_score,winner_team=winner_team)
    
    bet_type = "Moneyline"
    local_momio= local_momio_value
    visit_momio = 1.0
    draw_momio = 0.0
    chosen_team = local_team 

    momio =  Momio(game=game,bet_type=bet_type,local_momio=local_momio,visit_momio=visit_momio,draw_momio=draw_momio)
    bet = User.get(name=name).place_bet(username=name,momio=momio,chosen_team=chosen_team,bet_amount=bet_amount, status="Pending", rationale= rationale)    

    return bet.model_dump()



@mcp.tool(name="update_bet", description="Updates the status and calculates profit/loss for a user's bet.")
async def update_bet(username: str, bet_id: str, team_name: str, status: str)-> Dict:
    """
    Actualiza el estado de una apuesta específica, calcula ganancias y ajusta el saldo del usuario.

    Args:
        username: El nombre de la cuenta del usuario.
        bet_id: El ID único de la apuesta a actualizar.
        team_name: El nombre del equipo declarado ganador del juego.
        status: El estado de la apuesta ('Win', 'Lose', 'Push').
    """
    
    bet = User.get(name=username).update_bet(username=username,bet_id=bet_id,team_name=team_name,status=status)   
    return bet.model_dump()

@mcp.tool(name="get_balance", description="Get the balance of the user.")
async def get_balance(username: str)-> float:
    """
    Get the balance of the user.

    Args:
        username: El nombre de la cuenta del usuario.
    """
    
    b = User.get(name=username).balance 
    return b

@mcp.resource("accounts://bets_server/{name}")
async def read_account_resource(name: str) -> str:
    account = User.get(name.lower())
    return account.report()

@mcp.resource("accounts://strategy/{name}")
async def read_strategy_resource(name: str) -> str:
    account = User.get(name.lower())
    return account.get_strategy()

if __name__ == "__main__":
    mcp.run(transport='stdio')
    
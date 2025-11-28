import gradio as gr
from bets import BettingSystem, get_bet

# Initialize the betting system
system = BettingSystem()

def create_account(username, initial_deposit):
    user = system.create_account(username, initial_deposit)
    return f"Account created for {username} with initial deposit of {initial_deposit}. Current balance: {user.balance}"

def place_bet(username, sport, team1, team2, amount):
    user_id = next((uid for uid, user in system.users.items() if user.username == username), None)
    if user_id is None:
        return "User account not found."
    bet = system.place_bet(user_id, sport, (team1, team2), amount)
    if bet:
        return f"Placed bet on {sport} between {team1} and {team2}. Amount: {amount}"
    return "Failed to place bet. Check balance or bet validity."

def modify_bet(username, bet_id, new_amount, new_momio):
    user_id = next((uid for uid, user in system.users.items() if user.username == username), None)
    if user_id is None:
        return "User account not found."
    system.modify_bet(user_id, bet_id, new_amount, new_momio)
    return f"Bet {bet_id} modified to new amount: {new_amount}, new momio: {new_momio}"

def report_investments(username):
    user_id = next((uid for uid, user in system.users.items() if user.username == username), None)
    if user_id is None:
        return "User account not found."
    investments = system.report_investments(user_id)
    return f"Total investments for {username}: {investments}"

def report_profit_loss(username):
    user_id = next((uid for uid, user in system.users.items() if user.username == username), None)
    if user_id is None:
        return "User account not found."
    profit_loss = system.report_profit_loss(user_id)
    return f"Current profit/loss for {username}: {profit_loss}"

def list_transactions(username):
    user_id = next((uid for uid, user in system.users.items() if user.username == username), None)
    if user_id is None:
        return "User account not found."
    transactions = system.list_user_transactions(user_id)
    return f"Transactions for {username}: {transactions}"

with gr.Blocks() as demo:
    with gr.Column():
        username = gr.Textbox(label="Username", placeholder="Enter your username")
        initial_deposit = gr.Number(label="Initial Deposit", value=100.0)
        create_account_button = gr.Button("Create Account")
        create_account_output = gr.Textbox(label="Create Account Output")
        create_account_button.click(create_account, [username, initial_deposit], create_account_output)

    with gr.Column():
        sport = gr.Dropdown(["soccer", "basketball", "baseball"], label="Sport")
        team1 = gr.Textbox(label="Team 1")
        team2 = gr.Textbox(label="Team 2")
        amount = gr.Number(label="Bet Amount", value=10.0)
        place_bet_button = gr.Button("Place Bet")
        place_bet_output = gr.Textbox(label="Place Bet Output")
        place_bet_button.click(place_bet, [username, sport, team1, team2, amount], place_bet_output)

    with gr.Column():
        bet_id = gr.Number(label="Bet ID", value=1)
        new_amount = gr.Number(label="New Bet Amount", value=10.0)
        new_momio = gr.Number(label="New Momio", value=1.5)
        modify_bet_button = gr.Button("Modify Bet")
        modify_bet_output = gr.Textbox(label="Modify Bet Output")
        modify_bet_button.click(modify_bet, [username, bet_id, new_amount, new_momio], modify_bet_output)

    with gr.Column():
        report_investments_button = gr.Button("Report Investments")
        report_investments_output = gr.Textbox(label="Investments")
        report_investments_button.click(report_investments, username, report_investments_output)

    with gr.Column():
        report_profit_loss_button = gr.Button("Report Profit/Loss")
        report_profit_loss_output = gr.Textbox(label="Profit/Loss")
        report_profit_loss_button.click(report_profit_loss, username, report_profit_loss_output)

    with gr.Column():
        list_transactions_button = gr.Button("List Transactions")
        list_transactions_output = gr.Textbox(label="Transactions")
        list_transactions_button.click(list_transactions, username, list_transactions_output)

demo.launch()
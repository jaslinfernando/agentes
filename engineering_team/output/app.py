
# app.py

import gradio as gr
from bets import Bet, get_bet

# Initialize the betting back-end controller
bet_system = Bet()

# Function to create a user
def create_user(username, initial_deposit):
    try:
        bet_system.create_user(username, float(initial_deposit))
        return f"User {username} created with initial deposit of ${initial_deposit}."
    except ValueError as e:
        return str(e)

# Function to place a bet
def place_bet(username, sport, amount):
    try:
        bet_system.place_bet(username, sport, float(amount))
        return f"Placed {amount} bet on {sport} for user {username}."
    except ValueError as e:
        return str(e)

# Function to modify a bet
def modify_bet(username, sport, new_amount):
    try:
        bet_system.modify_bet(username, sport, float(new_amount))
        return f"Modified bet on {sport} to new amount {new_amount} for user {username}."
    except ValueError as e:
        return str(e)

# Function to calculate portfolio value
def calculate_portfolio(username):
    try:
        value = bet_system.calculate_portfolio_value(username)
        return f"Total portfolio value for {username} is ${value}."
    except KeyError:
        return "User does not exist."

# Function to calculate profit or loss
def calculate_profit_loss(username):
    try:
        profit_loss = bet_system.calculate_profit_loss(username)
        return f"Profit/Loss for {username} is ${profit_loss}."
    except KeyError:
        return "User does not exist."

# Function to report investments
def report_investments(username):
    try:
        investments = bet_system.report_investments(username)
        return f"Investments for {username}: {investments}"
    except KeyError:
        return "User does not exist."

# Function to report transactions
def report_transactions(username):
    try:
        transactions = bet_system.report_transactions(username)
        return f"Transactions for {username}: {transactions}"
    except KeyError:
        return "User does not exist."

# Initialize Gradio Interface
def gradio_interface():
    with gr.Blocks() as demo:
        gr.Markdown("# Simple Betting System Demo")

        with gr.Tab("Create User"):
            username_input = gr.Textbox(placeholder="Enter username", label="Username")
            deposit_input = gr.Number(label="Initial Deposit")
            create_button = gr.Button("Create User")
            create_output = gr.Textbox(label="Response")
            create_button.click(fn=create_user, inputs=[username_input, deposit_input], outputs=create_output)

        with gr.Tab("Place Bet"):
            username_bet_input = gr.Textbox(placeholder="Enter username", label="Username")
            sport_input = gr.Radio(["soccer", "basketball", "baseball"], label="Sport")
            amount_input = gr.Number(label="Bet Amount")
            bet_button = gr.Button("Place Bet")
            bet_output = gr.Textbox(label="Response")
            bet_button.click(fn=place_bet, inputs=[username_bet_input, sport_input, amount_input], outputs=bet_output)

        with gr.Tab("Modify Bet"):
            username_modify_input = gr.Textbox(placeholder="Enter username", label="Username")
            sport_modify_input = gr.Radio(["soccer", "basketball", "baseball"], label="Sport")
            new_amount_input = gr.Number(label="New Bet Amount")
            modify_button = gr.Button("Modify Bet")
            modify_output = gr.Textbox(label="Response")
            modify_button.click(fn=modify_bet, inputs=[username_modify_input, sport_modify_input, new_amount_input], outputs=modify_output)

        with gr.Tab("Portfolio Value"):
            username_portfolio_input = gr.Textbox(placeholder="Enter username", label="Username")
            portfolio_button = gr.Button("Check Portfolio Value")
            portfolio_output = gr.Textbox(label="Response")
            portfolio_button.click(fn=calculate_portfolio, inputs=username_portfolio_input, outputs=portfolio_output)

        with gr.Tab("Profit/Loss"):
            username_profit_input = gr.Textbox(placeholder="Enter username", label="Username")
            profit_button = gr.Button("Check Profit/Loss")
            profit_output = gr.Textbox(label="Response")
            profit_button.click(fn=calculate_profit_loss, inputs=username_profit_input, outputs=profit_output)

        with gr.Tab("Investments Report"):
            username_investments_input = gr.Textbox(placeholder="Enter username", label="Username")
            investments_button = gr.Button("Report Investments")
            investments_output = gr.Textbox(label="Response")
            investments_button.click(fn=report_investments, inputs=username_investments_input, outputs=investments_output)

        with gr.Tab("Transactions Report"):
            username_transactions_input = gr.Textbox(placeholder="Enter username", label="Username")
            transactions_button = gr.Button("Report Transactions")
            transactions_output = gr.Textbox(label="Response")
            transactions_button.click(fn=report_transactions, inputs=username_transactions_input, outputs=transactions_output)

    return demo

if __name__ == "__main__":
    app = gradio_interface()
    app.launch()

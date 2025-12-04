import gradio as gr
from util import css, js, Color
import pandas as pd
from bets_configuration import names, lastnames, short_model_names,run_every_n_minutes
import plotly.express as px
from database import read_log

from bets import User
import json
import asyncio
import threading

mapper = {
    "trace": Color.WHITE,
    "agent": Color.CYAN,
    "function": Color.GREEN,
    "generation": Color.YELLOW,
    "response": Color.MAGENTA,
    #"account": Color.RED,
    "account": Color.ORANGE,
}

REFRESH_TIMER= 60 #120
REFRESH_LOG_TIMER=60 #0.5
# Global flag to control the background loop
KEEP_RUNNING = True

class Gambler:
    def __init__(self, name: str, lastname: str, model_name: str):
        self.name = name
        self.lastname = lastname
        self.model_name = model_name
        self.account = User.get(name)
        

    def reload(self):
        self.account = User.get(self.name)
        
    def get_title(self) -> str:
        return f"""<div style='text-align: center;font-size:34px;'>{self.name}
        <span style='color:#ccc;font-size:24px;'> ({self.model_name}) - {self.lastname}</span>
        </div>
        <div style='text-align: center;font-size:13px;'>
        <bold> Strategy:<bold>  {self.get_strategy()}
        </div>
        """
    
    def get_strategy(self) -> str:
        return self.account.get_strategy()
    
    def get_portfolio_value(self) -> str:
        """Calculate total portfolio value based on current prices"""
        portfolio_value = self.account.get_portfolio_value() or 0.0
        pnl = self.account.calculate_profit_loss(portfolio_value) or 0.0
        color = "green" if pnl >= 0 else "red"
        emoji = "⬆" if pnl >= 0 else "⬇"
        return f"<div style='text-align: center;background-color:{color};'><span style='font-size:32px'>${portfolio_value:,.0f}</span><span style='font-size:24px'>&nbsp;&nbsp;&nbsp;{emoji}&nbsp;${pnl:,.0f}</span></div>"
    
    
    def get_portfolio_value_df(self) -> pd.DataFrame:
        df = pd.DataFrame(self.account.portfolio_value_time_series, columns=["datetime", "value"])
        df["datetime"] = pd.to_datetime(df["datetime"])
        return df
    
    def get_portfolio_value_chart(self):
        df = self.get_portfolio_value_df()
        fig = px.line(df, x="datetime", y="value")
        margin = dict(l=40, r=20, t=20, b=40)
        fig.update_layout(
            height=300,
            margin=margin,
            xaxis_title=None,
            yaxis_title=None,
            paper_bgcolor="#bbb",
            plot_bgcolor="#dde",
        )
        fig.update_xaxes(tickformat="%m/%d", tickangle=45, tickfont=dict(size=8))
        fig.update_yaxes(tickfont=dict(size=8), tickformat=",.0f")
        return fig
    
    def get_logs(self, previous=None) -> str:
        logs = read_log(self.name, last_n=13)
        response = ""
        for log in logs:
            print(f"***log:{log}")
            timestamp, type, message = log
            color = mapper.get(type, Color.WHITE).value
            response += f"<span style='color:{color}'>{timestamp} : [{type}] {message}</span><br/>"
        response = f"<div style='height:250px; overflow-y:auto;'>{response}</div>"
        if response != previous:
            return response
        return gr.update()
    
    def get_holdings_df(self) -> pd.DataFrame:
        """Convert holdings to DataFrame for display"""
        holdings = self.account.get_holdings()
        if not holdings:
            return pd.DataFrame(columns=["Sport", "Total"])

        df = pd.DataFrame(
            [{"Sport": sport, "Total": revenue} for sport, revenue in holdings.items()]
        )
        return df
    
    def get_bets_df(self) -> pd.DataFrame:
        """Convert bets to DataFrame for display"""
        transactions = self.account.list_transactions()

        if not transactions:
            return pd.DataFrame(columns=["Timestamp", "Sport",  "Momio", "Amount", "Teams","Winner","Chose", "Status", "Rationale"])

        return pd.DataFrame(transactions)    
    
        

class GamblerView:
    def __init__(self, trader: Gambler):
        self.trader = trader
        self.portfolio_value = None
        self.chart = None
        self.holdings_table = None
        self.transactions_table = None


    def get_row_data(self, evt: gr.SelectData, transactions_data: pd.DataFrame, t: gr.Textbox):
    
        # Check if a row was actually clicked (not a header)
        if evt.index is None: #or not isinstance(evt.index, tuple):
            return None
            
        # Get the index of the clicked row
        row_index = evt.index[0] 
        
        # Extract the complete data for the selected row
        #transactions_table = DataFrame
        selected_row = transactions_data.iloc[row_index].to_dict()
        
        # Format the data nicely for the popup
        popup_content = (
        f"--- Detail (Sport: {selected_row['Sport']}) ---\n"
        f"Amount 💰:  {selected_row['Amount']}\n"
        f"Teams: {selected_row['Teams']}\n"
        f"Chosen: {selected_row['Chosen']}\n"
        f"Winner: {selected_row['Winner']}\n"
        f"Status: You {selected_row['Status']}\n"
        f"Score -->  {selected_row['Score']}\n"
        f"Rationale 🧠:  \n{selected_row['Rationale']}"
        )
        
       
        return popup_content


    def make_ui(self):
        
        popup_msg = gr.Textbox(visible=False, label= f"Popup Content Holder for: {self.trader.name}", elem_id=id)        
        
        with gr.Column():
            gr.HTML(self.trader.get_title())

            # with gr.Row():
            #     popup_msg
            with gr.Row():
                self.portfolio_value = gr.HTML(self.trader.get_portfolio_value)
            with gr.Row():
                self.chart = gr.Plot(
                    self.trader.get_portfolio_value_chart, container=True, show_label=False
                )
            
            with gr.Row():
                self.holdings_table = gr.Dataframe(
                    value=self.trader.get_holdings_df,
                    label="Profit/Loss",
                    headers=["Sport", "Tolatl"], #add Perdidas- Losses
                    row_count=(5, "dynamic"),
                    col_count=2,
                    max_height=300,
                    elem_classes=["dataframe-fix-small"],
                )
            with gr.Row():
                df_method = self.trader.get_bets_df
                self.transactions_table = gr.Dataframe(
                    value=df_method,
                    label="Recent bets",
                    headers=["Timestamp", "Sport", "Momio", "Amount","Teams", "Rationale"],
                    row_count=(5, "dynamic"),
                    col_count=(6,'fixed'),
                    max_height=300,
                    wrap=True,
                    elem_classes=["dataframe-fix"],
                    interactive=False,
                )            
                
                
            with gr.Row(variant="panel"):
                self.log = gr.HTML(self.trader.get_logs)

        # When a row is selected (clicked)...
        #transactions_table = DataFrame
        self.transactions_table.select(
                    fn=self.get_row_data,
                    inputs=[self.transactions_table,popup_msg,],
                    outputs=popup_msg, # ...put the formatted data into the hidden textbox.
                    queue=False #ensures quick response time
                )
        popup_msg.change(
                fn=lambda content: None, # Function to clear the box
                inputs=[popup_msg], 
                #outputs=[popup_msg],
                js=js_code, # The alert logic
                queue=False
            )
        
        timer = gr.Timer(value=REFRESH_TIMER)
        timer.tick(
            fn=self.refresh,
            inputs=[],
            outputs=[
                self.portfolio_value,
                self.chart,
                self.holdings_table,
                self.transactions_table,
            ],
            show_progress="hidden",
            queue=False,
        )

        log_timer = gr.Timer(value=REFRESH_LOG_TIMER)
        log_timer.tick(
            fn=self.trader.get_logs,
            inputs=[self.log],
            outputs=[self.log],
            show_progress="hidden",
            queue=False,
        )

    def refresh(self):
        print("***Refreshing GUI\n")
        self.trader.reload()
        return (
            self.trader.get_portfolio_value(),
            self.trader.get_portfolio_value_chart(),
            self.trader.get_holdings_df(),
            self.trader.get_bets_df(),
            #self.trader.get_title(),
        )            
    

# Main UI construction
js_code = """
        (message_string) => {
            if (message_string) {
            console.log("row: "+ message_string);
                alert(message_string);
                // Return null to clear the component's value, ensuring the next click registers as a change.
                return ; 
            }
            return;
        }
    """


def create_ui():
    """Create the main Gradio UI for the bet simulation"""

    traders = [
        Gambler(trader_name, lastname, model_name)
        for trader_name, lastname, model_name in zip(names, lastnames, short_model_names)
    ]
    trader_views = [GamblerView(trader) for trader in traders]

    with gr.Blocks(
        title="Gamblers", css=css, js=js, theme=gr.themes.Default(primary_hue="sky"), fill_width=True        
    ) as ui:
        
       
        with gr.Row():
            for trader_view in trader_views:
                id = "id_" + trader_view.trader.name                
                trader_view.make_ui()

    return ui


def start_async_loop_in_thread(coroutine_func):
    """
    Synchronous wrapper to start the asyncio loop in the new thread.
    """
    # This function is what the threading.Thread executes
    asyncio.run(coroutine_func())

if __name__ == "__main__":
    ui = create_ui()
    # Create and start the background thread
    background_thread = threading.Thread(
        target=start_async_loop_in_thread,
        args=(run_every_n_minutes,),#la coma depues del nombre de la función es importante
        daemon=True # IMPORTANT: Ensures thread dies when the main program exits
    )

    background_thread.start()
    print("[MAIN] Background thread started in parallel.")

    # Launch the synchronous Gradio UI (This line BLOCKS execution)
    try:
        ui.launch(share=False) 
    except KeyboardInterrupt:
        # Graceful exit if the user presses Ctrl+C
        print("\n[MAIN] Caught KeyboardInterrupt. Shutting down...")
    finally:
        # Ensure the background thread loop stops
        KEEP_RUNNING = False
        if background_thread.is_alive():
            background_thread.join(timeout=1) # Wait briefly for the thread to finish
        print("[MAIN] Application fully exited.")

    

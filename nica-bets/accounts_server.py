from mcp.server.fastmcp import FastMCP
from accounts import Account

mcp = FastMCP("accounts_server")



@mcp.resource("accounts://accounts_server/{name}")
async def read_account_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.report()

@mcp.resource("accounts://strategy/{name}")
async def read_strategy_resource(name: str) -> str:
    account = Account.get(name.lower())
    return account.get_strategy()

if __name__ == "__main__":
    mcp.run(transport='stdio')
import asyncio
import logging
from datetime import datetime, timedelta

from rich.console import Console

from ibwebapi.contract_search.contract_search import Exchange, IBKRContractSearch
from ibwebapi.market_data.market_data import BarSize, IBKRMarketData, TimePeriod
from ibwebapi.portfolio.portfolio import IBKRPortfolio

console = Console()

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://192.168.178.118:5010/v1/api"


async def main():
    async with IBKRMarketData(base_url=BASE_URL) as market_data_client:
        console.print("[bold]Getting historical data for AAPL:[/bold]")
        historical_data = await market_data_client.get_historical_data_json(
            conid="265598",
            period=TimePeriod.DAY_1,
            bar=BarSize.HOUR_1,
            start_time=(datetime.now() - timedelta(days=1)).replace(
                hour=9, minute=30, second=0, microsecond=0
            ),
            outside_rth=False,
        )
        console.print(historical_data)

    async with IBKRContractSearch(base_url=BASE_URL) as client:
        # Search for a contract
        console.print("[bold]Searching for AAPL contract:[/bold]")
        contract_details = await client.search_contract("AAPL")
        console.print(contract_details)

        # Get stock info
        console.print("\n[bold]Getting stock info for AAPL:[/bold]")
        stock_info = await client.get_stock_info("AAPL")
        console.print(stock_info)

        # Assuming we got a conid from the search_contract result
        conid = (
            contract_details[0]["conid"] if contract_details else 265598
        )  # AAPL's conid

        # Get contract details
        console.print(f"\n[bold]Getting contract details for conid {conid}:[/bold]")
        contract_details = await client.get_contract_details(conid)
        console.print(contract_details)

        # Get contract rules
        console.print(f"\n[bold]Getting contract rules for conid {conid}:[/bold]")
        contract_rules = await client.get_contract_rules(conid)
        console.print(contract_rules)

        # Get secdef info (for options)
        console.print("\n[bold]Getting secdef info for SPX option:[/bold]")
        secdef_info = await client.get_secdef_info(416904)
        console.print(secdef_info)

        # Get all conids for exchange NASDAQ
        console.print("\n[bold]Getting all conids for NASDAQ:[/bold]")
        all_conids = await client.get_all_conids(Exchange.NASDAQ)
        console.print(f"Total contracts: {len(all_conids)}")
        console.print(all_conids[:5])  # Print first 5 contracts

        # Get all conids for exchange NYSE
        console.print("\n[bold]Getting all conids for NYSE:[/bold]")
        all_conids = await client.get_all_conids(Exchange.NYSE)
        console.print(f"Total contracts: {len(all_conids)}")
        console.print(all_conids[:5])  # Print first 5 contracts

        # Get AAPL conid
        console.print("\n[bold]Getting AAPL conid:[/bold]")
        aapl_conid = await client.get_contract_for_stock("AAPL", Exchange.NASDAQ, True)
        if aapl_conid:
            console.print(f"AAPL conid: {aapl_conid}")
        else:
            console.print("AAPL contract not found")

        # Get MSFT conid
        console.print("\n[bold]Getting MSFT conid:[/bold]")
        msft_conid = await client.get_contract_for_stock("MSFT", Exchange.NASDAQ, True)
        if msft_conid:
            console.print(f"MSFT conid: {msft_conid}")
        else:
            console.print("MSFT contract not found")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
from datetime import datetime, timedelta

from rich import print

from ibwebapi.contract_search.contract_search import Exchange, IBKRContractSearch
from ibwebapi.market_data.market_data import BarSize, IBKRMarketData, TimePeriod
from ibwebapi.portfolio.portfolio import IBKRPortfolio

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BASE_URL = "https://192.168.178.118:5010/v1/api"


async def main():
    async with IBKRMarketData(base_url=BASE_URL) as market_data_client:
        print("[bold]Getting historical data for AAPL:[/bold]")
        historical_data = await market_data_client.get_historical_data_json(
            conid="265598",
            period=TimePeriod.WEEK_1,
            bar=BarSize.MIN_1,
            start_time=datetime(2004, 11, 17).replace(
                hour=1, minute=30, second=0, microsecond=0
            ),
            outside_rth=False,
        )
        # Create a copy of historical_data to modify
        formatted_data = historical_data.copy()
        # Convert timestamps in data array to readable dates
        if "data" in formatted_data:
            for bar in formatted_data["data"]:
                if "t" in bar:
                    bar["t"] = datetime.fromtimestamp(bar["t"] / 1000).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
        print(formatted_data)

    async with IBKRContractSearch(base_url=BASE_URL) as client:
        # Search for a contract
        print("[bold]Searching for AAPL contract:[/bold]")
        contract_details = await client.search_contract("AAPL")
        print(contract_details)

        # Get stock info
        print("\n[bold]Getting stock info for AAPL:[/bold]")
        stock_info = await client.get_stock_info("AAPL")
        print(stock_info)

        # Assuming we got a conid from the search_contract result
        conid = (
            contract_details[0]["conid"] if contract_details else 265598
        )  # AAPL's conid

        # Get contract details
        print(f"\n[bold]Getting contract details for conid {conid}:[/bold]")
        contract_details = await client.get_contract_details(conid)
        print(contract_details)

        # Get contract rules
        print(f"\n[bold]Getting contract rules for conid {conid}:[/bold]")
        contract_rules = await client.get_contract_rules(conid)
        print(contract_rules)

        # Get secdef
        print(f"\n[bold]Getting secdef for conid {conid}:[/bold]")
        secdef = await client.get_secdef(conid)
        print(secdef)

        # Get secdef info (for options)
        print("\n[bold]Getting secdef info for SPX option:[/bold]")
        secdef_info = await client.get_secdef_info(416904)
        print(secdef_info)

        # Get all conids for exchange NASDAQ
        print("\n[bold]Getting all conids for NASDAQ:[/bold]")
        all_conids = await client.get_all_conids(Exchange.NASDAQ)
        print(f"Total contracts: {len(all_conids)}")
        print(all_conids[:5])  # Print first 5 contracts

        # Get all conids for exchange NYSE
        print("\n[bold]Getting all conids for NYSE:[/bold]")
        all_conids = await client.get_all_conids(Exchange.NYSE)
        print(f"Total contracts: {len(all_conids)}")
        print(all_conids[:5])  # Print first 5 contracts

        # Get AAPL conid
        print("\n[bold]Getting AAPL conid:[/bold]")
        aapl_conid = await client.get_contract_for_stock("AAPL", Exchange.NASDAQ, True)
        if aapl_conid:
            print(f"AAPL conid: {aapl_conid}")
        else:
            print("AAPL contract not found")

        # Get MSFT conid
        print("\n[bold]Getting MSFT conid:[/bold]")
        msft_conid = await client.get_contract_for_stock("MSFT", Exchange.NASDAQ, True)
        if msft_conid:
            print(f"MSFT conid: {msft_conid}")
        else:
            print("MSFT contract not found")


if __name__ == "__main__":
    asyncio.run(main())

import asyncio
import logging
from datetime import datetime, timedelta

from ibwebapi.market_data.market_data import BarSize, IBKRMarketData, TimePeriod
from ibwebapi.portfolio.portfolio import IBKRPortfolio

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def main():
    async with IBKRMarketData(
        base_url="https://192.168.178.118:5010/v1/api"
    ) as market_data_client:
        historical_data = await market_data_client.get_historical_data(
            conid="265598",
            period=TimePeriod.DAY_1,
            bar=BarSize.HOUR_1,
            start_time=datetime.now() - timedelta(days=1),
            outside_rth=False,
        )
        logger.info(f"Historical data for AAPL: {historical_data}")

    async with IBKRPortfolio(
        base_url="https://192.168.178.118:5010/v1/api"
    ) as portfolio_client:
        accounts = await portfolio_client.get_portfolio_accounts()
        logger.info(f"Portfolio accounts: {accounts}")

        if accounts:
            account_id = accounts[0]["id"]
            summary = await portfolio_client.get_account_summary(account_id)
            logger.info(f"Account summary for {account_id}: {summary}")


if __name__ == "__main__":
    asyncio.run(main())

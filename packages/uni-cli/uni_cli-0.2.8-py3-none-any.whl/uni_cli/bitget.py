import typer

from crypto.bitget import bitget_close, bitget_open, mix_tickers, spot_tickers
from utils.mysql import get_database_engine

app = typer.Typer()


@app.command()
def sync(env_path: str = "d:/.env", csv_path: str = "d:/github/txnj/data/bitget_0.csv"):
    """同步mysql中grid数据到csv文件"""
    engine = get_database_engine(env_path)
    bitget_open(engine, csv_path)
    bitget_close(engine, csv_path)


@app.command()
def spot(
    symbols: str,
    proxy: str = typer.Option(
        None, "--proxy", "-p", help="代理服务器地址，例如: http://127.0.0.1:7890"
    ),
):
    """
    从bitget获取加密货币现货价格.

    参数:
    symbols:加密货币符号,可以是多个,用逗号分隔,例如:"BTCUSDT,ETHUSDT"
    """
    spot_tickers(symbols.split(","), proxy)


@app.command()
def mix(
    symbols: str,
    proxy: str = typer.Option(
        None, "--proxy", "-p", help="代理服务器地址，例如: http://127.0.0.1:7890"
    ),
):
    """
    从bitget获取加密货币合约价格.

    参数:
    symbols:加密货币符号,可以是多个,用逗号分隔,例如:"BTCUSDT,ETHUSDT"
    """
    mix_tickers(symbols.split(","), proxy)

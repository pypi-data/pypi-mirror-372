import typer

import utils
from crypto.grid_strategy import (
    grid_sync_close,
    grid_sync_open,
    strategy_sync_close,
    strategy_sync_open,
)

app = typer.Typer()


@app.command()
def grid(env_path: str = "d:/.env", csv_path: str = "d:/github/txnj/data/grid_0.csv"):
    """同步mysql中grid数据到csv文件"""
    engine = utils.get_database_engine(env_path)
    grid_sync_close(engine, csv_path)
    grid_sync_open(engine, csv_path)


@app.command()
def strategy(
    env_path: str = "d:/.env", csv_path: str = "d:/github/txnj/data/strategy_0.csv"
):
    """同步mysql中strategy数据到csv文件"""
    engine = utils.get_database_engine(env_path)
    strategy_sync_close(engine, csv_path)
    strategy_sync_open(engine, csv_path)

from sqlalchemy import Engine

from crypto.mysql_utils import mysql_to_csv


def grid_sync_open(engine: Engine, csv_path: str):
    query = "select id,created_at,name,act_name,symbol,qty,cex,status,up_status,path,level,earn,cost,buy_px,benefit,sell_px,profit,order_id,client_order_id,fx_order_id,fx_client_order_id,open_at,close_at from tx where (cost is not null or benefit is not null) and profit is null and up_status = 0;"
    row_count = mysql_to_csv(
        engine,
        csv_path,
        "tx",
        query,
        update_status=1,
        d_column_names=["client_order_id"],
    )
    print(f"🧮 grid open count:({row_count})")


def grid_sync_close(engine: Engine, csv_path: str):
    query = "select id,created_at,name,act_name,symbol,qty,cex,status,up_status,path,level,earn,cost,buy_px,benefit,sell_px,profit,order_id,client_order_id,fx_order_id,fx_client_order_id,open_at,close_at from tx where profit is not null and up_status in (0,1);"
    row_count = mysql_to_csv(
        engine,
        csv_path,
        "tx",
        query,
        update_status=2,
        d_column_names=["client_order_id"],
    )
    print(f"🧮 grid close count:({row_count})")


def strategy_sync_open(engine: Engine, csv_path: str):
    query = "select id,created_at,cex,act_name,symbol,lever,spot_size,futures_size,up_status,spot_px,futures_px,spot_trigger_px,trigger_px,fx_trigger_px,pnl,pnl_ratio,end_time,spot_order_id,spot_client_order_id,spot_profit_order_id,spot_profit_client_order_id,spot_open_usdt,spot_open_px,spot_close_usdt,spot_close_px,futures_order_id,futures_client_order_id,futures_loss_market_order_id,futures_loss_market_client_order_id,futures_profit_market_order_id,futures_profit_market_client_order_id,futures_open_usdt,futures_open_px,futures_close_usdt,futures_close_px,position_side from binance_tx where ((spot_open_usdt is not null and futures_open_usdt is not null) or (spot_open_usdt is not null and futures_client_order_id is null) or (futures_open_usdt is not null and spot_client_order_id is null)) and up_status = 0;"
    row_count = mysql_to_csv(
        engine,
        csv_path,
        "binance_tx",
        query,
        update_status=1,
        d_column_names=["spot_client_order_id", "futures_client_order_id"],
    )
    print(f"🎯 strategy open count:({row_count})")


def strategy_sync_close(engine: Engine, csv_path: str):
    query = "select id,created_at,cex,act_name,symbol,lever,spot_size,futures_size,up_status,spot_px,futures_px,spot_trigger_px,trigger_px,fx_trigger_px,pnl,pnl_ratio,end_time,spot_order_id,spot_client_order_id,spot_profit_order_id,spot_profit_client_order_id,spot_open_usdt,spot_open_px,spot_close_usdt,spot_close_px,futures_order_id,futures_client_order_id,futures_loss_market_order_id,futures_loss_market_client_order_id,futures_profit_market_order_id,futures_profit_market_client_order_id,futures_open_usdt,futures_open_px,futures_close_usdt,futures_close_px,position_side from binance_tx where pnl is not null and up_status in (0,1);"
    row_count = mysql_to_csv(
        engine,
        csv_path,
        "binance_tx",
        query,
        update_status=2,
        d_column_names=["spot_client_order_id", "futures_client_order_id"],
    )
    print(f"🎯 strategy close count:({row_count})")

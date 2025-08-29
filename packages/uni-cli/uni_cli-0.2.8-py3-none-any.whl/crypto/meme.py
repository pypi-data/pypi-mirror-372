from sqlalchemy import Engine

from crypto.mysql_utils import mysql_to_csv


def meme_open(engine: Engine, csv_path: str):
    query = "select created_at,chain,chain_id,symbol,token_address,user_wallet_address,decimals,buy_amount,buy_price,buy_usdt,buy_hash,sell_amount,sell_price,sell_usdt,sell_hash,profit,profit_rate,up_status,tx_status,end_time from meme where tx_status = 'success' and up_status = 0;"
    row_count = mysql_to_csv(
        engine,
        csv_path,
        "meme",
        query,
        update_status=1,
        d_column_names=["buy_hash"],
    )
    print(f"🐸 meme open count:({row_count})")


def meme_close(engine: Engine, csv_path: str):
    query = "select created_at,chain,chain_id,symbol,token_address,user_wallet_address,decimals,buy_amount,buy_price,buy_usdt,buy_hash,sell_amount,sell_price,sell_usdt,sell_hash,profit,profit_rate,up_status,tx_status,end_time from meme where tx_status = 'success1' and up_status = (0,1);"
    row_count = mysql_to_csv(
        engine,
        csv_path,
        "meme",
        query,
        update_status=2,
        d_column_names=["buy_hash"],
    )
    print(f"🐸 meme close count:({row_count})")

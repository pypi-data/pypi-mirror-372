import os

from dotenv import load_dotenv
from sqlalchemy import Engine, create_engine, text


def get_database_engine(env_path: str) -> Engine:
    """创建数据库引擎"""
    load_dotenv(env_path)
    host = os.getenv("UNI_CLI_MYSQL_HOST")
    port = os.getenv("UNI_CLI_MYSQL_PORT")
    user = os.getenv("UNI_CLI_MYSQL_USER")
    password = os.getenv("UNI_CLI_MYSQL_PASSWORD")
    database = os.getenv("UNI_CLI_MYSQL_DATABASE")

    engine = create_engine(
        f"mysql+pymysql://{user}:{password}@{host}:{port}/{database}"
    )

    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as e:
        print(f"数据库连接失败: {str(e)}")
        raise

    return engine

import platform
import secrets
import string
import sys
import uuid as u
from datetime import datetime

import arrow
import pytz
import typer
from babel.dates import format_datetime
from cowsay.__main__ import cli

app = typer.Typer()


@app.command()
def sid(
    length: int = typer.Option(30, "--length", "-l", help="生成secure_id的长度"),
):
    chars = string.ascii_letters + string.digits
    id = "".join(secrets.choice(chars) for _ in range(length))
    print(id)


@app.command()
def uuid():
    print(u.uuid4())


@app.command()
def os():
    print(platform.system())


@app.command()
def ts():
    timestamp = arrow.now().timestamp()
    print(int(timestamp))


@app.command()
def ms():
    timestamp = arrow.now().timestamp()
    print(int(timestamp * 1000))


@app.command()
def v():
    print(f"🧊 python:{sys.version}")


def strf_time(zone: str):
    tz = pytz.timezone(zone)
    now = datetime.now(tz)
    # locale="zh_CN" 会使月份和星期的名称显示为中文
    # locale="en_US" 则会显示为英文
    return format_datetime(
        now, "yyyy年MM月dd日 HH:mm:ss EEEE ZZZZ zzzz", locale="zh_CN"
    )


@app.command()
def st():
    t0 = strf_time("UTC")
    t1 = strf_time("America/New_York")
    t2 = strf_time("Asia/Shanghai")

    print(t0)
    print(t1)
    print(t2)


def say():
    cli()

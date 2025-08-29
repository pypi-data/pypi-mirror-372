import click
import MetaTrader5 as mt5
from datetime import datetime, timedelta
from . import conf
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

logger = setup_logger("pivot")


@click.command()
@click.version_option(package_name="mtcli-pivot")
@click.option("--symbol", "-s", default="WINV25", help="Símbolo do ativo.")
def pp(symbol):
    """Exibe níveis de ponto pivô com suporte e resistência para o ativo"""

    conectar()

    rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_D1, 1, 2)
    if rates is None or len(rates) < 2:
        click.echo("❌ Não foi possível obter os dados do ativo.")
        shutdown()
        return

    # Usa o candle do dia anterior
    prev_candle = rates[0]
    high = prev_candle["high"]
    low = prev_candle["low"]
    close = prev_candle["close"]

    # Cálculo dos níveis clássicos de ponto pivô
    pivot = (high + low + close) / 3
    r1 = 2 * pivot - low
    s1 = 2 * pivot - high
    r2 = pivot + (high - low)
    s2 = pivot - (high - low)
    r3 = high + 2 * (pivot - low)
    s3 = low - 2 * (high - pivot)
    digitos = conf.digitos

    click.echo(f"Ponto Pivô ({symbol}):")
    click.echo(f"  Pivot: {pivot:.{digitos}f}")
    click.echo(f"  R1: {r1:.{digitos}f} | R2: {r2:.{digitos}f} | R3: {r3:.{digitos}f}")
    click.echo(f"  S1: {s1:.{digitos}f} | S2: {s2:.{digitos}f} | S3: {s3:.{digitos}f}")

    shutdown()


if __name__ == "__main__":
    pp()

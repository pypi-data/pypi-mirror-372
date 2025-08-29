import click
import MetaTrader5 as mt5
from tabulate import tabulate
from . import conf
from mtcli.conecta import conectar, shutdown
from mtcli.logger import setup_logger

logger = setup_logger("book")


@click.command()
@click.version_option(package_name="mtcli-book")
@click.option(
    "--symbol", "-s", default="WINV25", help="Símbolo do ativo (default WINV25)."
)
@click.option("--depth", "-d", type=int, default=10, help="Número de níveis do book a exibir.")
def book(symbol, depth):
    """Exibe o book de ofertas (Depth of Market) do ativo."""
    conectar()

    book_data = mt5.market_book_get(symbol)
    if book_data is None:
        msg = f"❌ Não foi possível obter o book para {symbol}"
        click.echo(msg)
        logger.warning(msg)
        shutdown()
        return

    bids = [b for b in book_data if b.type == mt5.BOOK_TYPE_BUY]
    asks = [b for b in book_data if b.type == mt5.BOOK_TYPE_SELL]

    bids_sorted = sorted(bids, key=lambda x: x.price, reverse=True)[:depth]
    asks_sorted = sorted(asks, key=lambda x: x.price)[:depth]

    table = []
    click.echo(f"\n Book de ofertas para {symbol} (top {depth} níveis):\n")
    click.echo(f"{'Preço':^10} | {'Compra':>12} | | {'Venda':<12}")
    click.echo("-" * 40)

    for i in range(max(len(bids_sorted), len(asks_sorted))):
        bid = bids_sorted[i] if i < len(bids_sorted) else None
        ask = asks_sorted[i] if i < len(asks_sorted) else None

        table.append(
            [
                f"{bid.price:.{conf.digitos}f}" if bid else ask.price if ask else "",
                f"{bid.volume:.2f}" if bid else "",
                f"{ask.volume:.2f}" if ask else "",
            ]
        )

    click.echo(tabulate(table, headers=["Preço", "Compra", "Venda"]))
    shutdown()


if __name__ == "__main__":
    book()

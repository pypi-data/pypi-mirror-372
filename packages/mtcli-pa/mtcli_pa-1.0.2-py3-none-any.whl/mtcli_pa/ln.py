"""
Calcula linhas de canal
"""

import click


@click.command()
@click.argument("preco1", type=float)
@click.argument("preco2", type=float)
@click.option("--digitos", "-d", type=int, default=0, envvar="DIGITOS", help="Digitos apos o separador decimal")
def ln(preco1, preco2, digitos):
    """Calcula linhas de canal"""
    dif = preco2 - preco1
    linha = preco2 + dif
    click.echo("%.{0}f".format(digitos) % abs(linha))


if __name__ == "__main__":
    ln()

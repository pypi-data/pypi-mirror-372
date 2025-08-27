"""
Calcula o gap do dia
"""

import click


@click.command()
@click.argument("coy", envvar="COY", type=float)
@click.argument("ood", envvar="OOD", type=float)
@click.option("--digitos", type=int, default=0, envvar="DIGITOS", help="Digitos apos o separador decimal")
def gp(coy, ood, digitos):
    """Calcula o gap do dia"""
    gap = ood - coy
    click.echo("%.{0}f".format(digitos) % gap)


if __name__ == "__main__":
    gp()

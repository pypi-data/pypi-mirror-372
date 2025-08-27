"""
Calcula pullback e projeções de rompimento
"""

import click


@click.command()
@click.argument("final", type=float)
@click.argument("inicio", type=float)
@click.option("--digitos", "-d", type=int, default=0, envvar="DIGITOS", help="Digitos apos o separador decimal")
def bo(final, inicio, digitos):
    """Calcula pullbacks e projecoes de rompimento"""
    tamanho = final - inicio
    click.echo("%.{0}f pt".format(digitos) % abs(tamanho))
    projecao1 = final + tamanho
    projecao2 = final + tamanho * 2
    #    click.echo("%.{0}f 2X".format(digits) % projecao2)
    click.echo("%.{0}f 1X".format(digitos) % projecao1)
    click.echo("%.{0}f".format(digitos) % final)
    niveis = [0.33, 0.50, 0.66]
    pullback = []
    i = 0
    for n in niveis:
        pullback.append(final - tamanho * n)
        click.echo("%.{0}f %.2f".format(digitos) % (pullback[i], n))
        i += 1


if __name__ == "__main__":
    bo()

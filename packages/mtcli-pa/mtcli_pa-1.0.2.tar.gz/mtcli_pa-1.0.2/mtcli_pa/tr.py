"""
Calcula projeções e níveis em lateralidade
"""

import click


@click.command()
@click.argument("maxima", type=float)
@click.argument("minima", type=float)
@click.option("--digitos", "-d", type=int, default=0, envvar="DIGITOS", help="Digitos apos o separador decimal")
def tr(maxima, minima, digitos):
    """Calcula projecoes e niveis em lateralidade"""
    tamanho = maxima - minima
    click.echo("%.{0}f pt".format(digitos) % abs(tamanho))
    projecao_acima = maxima + tamanho
    click.echo("%.{0}f 1X".format(digitos) % projecao_acima)
    click.echo("%.{0}f".format(digitos) % maxima)
    niveis = [0.33, 0.66]
    nivel = []
    i = 0
    for n in niveis:
        nivel.append(maxima - tamanho * n)
        click.echo("%.{0}f %.2f".format(digitos) % (nivel[i], n))
        i += 1
    click.echo("%.{0}f".format(digitos) % minima)
    projecao_abaixo = minima - tamanho
    click.echo("%.{0}f 1X".format(digitos) % projecao_abaixo)


if __name__ == "__main__":
    tr()

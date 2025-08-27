"""
Aplicativo CLI para calcular níveis  e projeções de price action
"""

import click
from .bo import bo
from .ln import ln
from .tr import tr
from .gp import gp


@click.group()
@click.version_option(package_name="mtcli-pa")
def pa():
    """Calcula niveis e projecoes de price action"""
    pass


pa.add_command(bo)
pa.add_command(ln)
pa.add_command(tr)
pa.add_command(gp)


if __name__ == "__main__":
    pa()

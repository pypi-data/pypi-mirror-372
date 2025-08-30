import typer
from enum import Enum

import sds.config as config
import sds.ipam_ip as ipam_ip
import sds.ipam_space as ipam_space
import sds.ipam_network as ipam_network

app = typer.Typer()
app.add_typer(ipam_ip.app, name="ip")
app.add_typer(ipam_space.app, name="space")
app.add_typer(ipam_network.app, name="network")


# @app.command()
# def network():
#     config.err_console.log('network not yet implemented')


if __name__ == "__main__":
    app()

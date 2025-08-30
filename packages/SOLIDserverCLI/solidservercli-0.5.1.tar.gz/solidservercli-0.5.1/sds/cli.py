import typer
from typing_extensions import Annotated
from enum import Enum
import logging

import sds.config as config
from sds.config import log
import sds.ipam as ipam
import sds.dns as dns
import sds.server as server


class LogLevel(str, Enum):
    none = "none"
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


def name_callback(json: Annotated[bool,
                                  typer.Option(help='output as json (log level raised at error)',
                                               envvar="SDS_JSON")] = False,
                  loglvl: Annotated[LogLevel,
                                    typer.Option("--log",
                                                 help='log level',
                                                 envvar="SDS_LOGLEVEL")] = LogLevel.info):

    if json:
        config.vars['json_output'] = True
        log.setLevel(logging.ERROR)

    if loglvl == LogLevel.info:
        log.setLevel(logging.INFO)
    elif loglvl == LogLevel.error:
        log.setLevel(logging.ERROR)
    elif loglvl == LogLevel.warning:
        log.setLevel(logging.WARNING)
    elif loglvl == LogLevel.debug:
        log.setLevel(logging.DEBUG)
    elif loglvl == LogLevel.critical:
        log.setLevel(logging.CRITICAL)
    elif loglvl == LogLevel.none:
        log.setLevel(logging.NOTSET)

    config.read_config()
    config.connect()

    # log.debug("debug")
    # log.info("info")
    # log.warning("warning")
    # log.error("error")
    # log.critical("critical")


def init_app():
    app = typer.Typer(help="""
This is the cli command for the SOLIDserver. It uses API calls to perform action on the DDI solution.
                      """,
                      callback=name_callback,
                      add_completion=False)

    app.add_typer(server.app,
                  name="server",
                  help="SOLIDserver connection information and actions")
    app.add_typer(ipam.app,
                  name="ipam",
                  help="action in the IPAM like manipulating ip, network, space")
    app.add_typer(dns.app,
                  name="dns")
    return app


def main():
    app = init_app()

    app()


if __name__ == "__main__":
    # read configuration file and connect to SDS
    main()

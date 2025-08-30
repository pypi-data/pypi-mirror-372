from rich.console import Console
from rich import print
from rich.logging import RichHandler
import configparser
import logging

from SOLIDserverRest import *
from SOLIDserverRest import adv as sdsadv

__all__ = ['err_console', 'vars', 'read_config', 'connect', 'log']

err_console = Console(stderr=True,
                      style="red")


logging.basicConfig(
    # level="NOTSET",
    level="INFO",
    format="%(message)s",
    datefmt="[%d/%m %T.%f]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True)],
)

vars = {
    'sds': None,
    'json_output': False
}

log = logging.getLogger("rich")


def read_config():
    if 'sds_name' in vars or 'sds_ip' in vars:
        return vars

    config = configparser.ConfigParser()

    config.read('sds.ini')

    vars['sds_name'] = config.get('server', 'name', fallback=None)
    vars['sds_ip'] = config.get('server', 'ip', fallback=None)
    vars['sds_token_id'] = config.get('server', 'token_id', fallback=None)
    vars['sds_token_key'] = config.get('server', 'token_key', fallback=None)

    if not vars['json_output']:
        log.info("[green]read configuration file[/green]")

    return vars


def connect():
    params = read_config()

    vars['sds'] = sdsadv.SDS()

    if 'sds_ip' in params and params['sds_ip']:
        vars['sds'].set_server_ip(params['sds_ip'])
    elif 'sds_name' in params and params['sds_name']:
        vars['sds'].set_server_name(params['sds_name'])
    else:
        log.error("need an SDS host configuration in sds.ini, template like:")
        log.info("\[server]"
                 "\nname = ipam.emea.demo"
                 "\ntoken_id = xyz"
                 "\ntoken_key = uiop")
        exit()

    if 'sds_token_id' in params and params['sds_token_id']:
        vars['sds'].set_token_creds(keyid=params['sds_token_id'],
                                    keysecret=params['sds_token_key'])
        vars['sds'].connect(method="token", timeout=10)

        # print(vars['sds'])
        if not vars['json_output']:
            log.info("[green]connected to SOLIDserver[/green]")
        return

    err_console.log("not connected")
    exit()

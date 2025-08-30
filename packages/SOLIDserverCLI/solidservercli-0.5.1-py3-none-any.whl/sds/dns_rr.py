import typer
from typing_extensions import Annotated
from typing import List, Optional

from rich import print
from rich.text import Text

import ipaddress
import uuid
import json
import re
import time

from SOLIDserverRest import *
from SOLIDserverRest import adv as sdsadv

import sds.config as config
from sds.config import log
import sds.classparams as cp

app = typer.Typer()


def convert_dict(ipadd: sdsadv.IpAddress = None) -> dict:
    """convert the IP adv object to a dictionary structure
       for easy output as json

    Args:
        ipadd (sdsadv.IpAddress, optional): IP address object to convert.

    Returns:
        dict: the dictionary object
    """
    if ipadd:
        _j = ipadd.__dict__
        if config.vars['json_output']:
            # print(_j)
            _jr = {
                'id': _j['myid'],
                'ipv4': _j['ipv4'],
                'name': _j['name'],
                'space': _j['space'].name,
                'subnet_id': _j['params']['subnet_id'],
            }

            if _j['class_name']:
                _jr['class'] = _j['class_name']

            if _j['mac']:
                _jr['mac'] = _j['mac']

            _cparam = {}
            for _k, _v in _j['_ClassParams__private_class_params'].items():
                if _k != 'hostname':
                    _cparam[_k] = _v
            if len(_cparam) > 0:
                _jr['class_params'] = _cparam

            return _jr

    return {}


@app.command()
def create(fqdn: Annotated[str,
                           typer.Argument(
                               help='fqdn')],

           server: Annotated[str,
                             typer.Option(help='server or smart name')],


           rr_type: Annotated[str,
                              typer.Option('--type',
                                           help='the type of the record')
                              ],

           val: Annotated[Optional[List[str]],
                          typer.Option(help='values of the record, can be provided multiple times')],

           ttl: Annotated[int,
                          typer.Option(help='TTL in seconds')] = 3600,

           view: Annotated[str,
                           typer.Option(help='view to create the record in')] = "",

           meta: Annotated[str,
                           typer.Option(
                               help='class params: a=\'1\',b1=\'foo bar\' ')
                           ] = ""):
    _start_time = time.time()

    dns = sdsadv.DNS(name=server, sds=config.vars['sds'])
    try:
        dns.refresh()
    except:
        log.critical("DNS server or Smart not found")
        exit()

    dns_rr = sdsadv.DNS_record(sds=config.vars['sds'],
                               name=fqdn,
                               rr_type=rr_type)

    dns_rr.set_values(val)

    dns_rr.set_dns(dns)

    dns_rr.set_ttl(ttl)

    if view != "":
        dns_view = sdsadv.DNS_view(sds=config.vars['sds'],
                                   name=view)

        dns_view.set_dns(dns)
        try:
            dns_view.refresh()
        except:
            log.critical("DNS view not found")
            exit()

        dns_rr.set_view(dns_view)

    if meta != "":
        cp.add_classparams_from_string(dns_rr, meta)

    try:
        dns_rr.create()
    except SDSDNSError as e:
        log.error(f"[red]create failed[/red] {e.message}")


if __name__ == "__main__":
    app()

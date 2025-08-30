import typer
from typing_extensions import Annotated

from rich import print
# from rich.progress import Progress
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


def _find_ipaddress(address, space):
    add = None

    ip_id = -1
    ip_add = None

    try:
        ip_add = ipaddress.IPv4Address(address)
    except ipaddress.AddressValueError:
        try:
            ip_id = int(address)
        except ValueError:
            log.abort("address is not an IP, nor an id")
            exit()

    if ip_id > -1:
        add = sdsadv.IpAddress(sds=config.vars['sds'])
        add.myid = ip_id
    else:
        # get the space
        space = sdsadv.Space(sds=config.vars['sds'],
                             name=space)
        try:
            space.refresh()
        except:
            log.error(f"cannot find the space {space} on the SDS")
            return None

        # set the IP address object for creation
        if isinstance(ip_add, ipaddress.IPv4Address):
            add = sdsadv.IpAddress(sds=config.vars['sds'],
                                   space=space,
                                   ipv4=str(ip_add))
        else:
            log.warning("nothing to search, exiting")
            return None

    try:
        add.refresh()
    except SDSError as e:
        msg = f"[red]error on IP info[/red] ({e.message})"
        log.error(msg)
        return None

    return add


@app.command()
def create(address: Annotated[str,
                              typer.Argument(
                                  help='ipv4')],
           name: Annotated[str,
                           typer.Option(help='the name of the IP in the IPAM')
                           ] = f'cli-{str(uuid.uuid4())[0:8]}',
           macaddress: Annotated[str,
                                 typer.Option(help='the mac for this IP')
                                 ] = '0e:00:00:00:00:00',
           space: Annotated[str,
                            typer.Option(help='the space name',
                                         envvar="SDS_SPACE")
                            ] = "Local",
           ip_class: Annotated[str,
                               typer.Option('--class',
                                            help='the class associated with IP')
                               ] = None,
           meta: Annotated[str,
                           typer.Option(
                               help='class params: a=\'1\',b1=\'foo bar\' ')
                           ] = ""):
    _start_time = time.time()

    add = None

    try:
        ip_add = ipaddress.IPv4Address(address)
    except ipaddress.AddressValueError:
        try:
            ip_add = ipaddress.IPv6Address(address)
        except ipaddress.AddressValueError:
            log.critical("invalid ip address")
            exit()

    # get the space
    space = sdsadv.Space(sds=config.vars['sds'],
                         name=space)
    try:
        space.refresh()
    except:
        log.critical(
            f"\ncannot find the space {space} on the SDS")
        exit()

    # set the IP address object for creation
    if isinstance(ip_add, ipaddress.IPv6Address):
        log.warning("IPv6 not yet implemented")
        exit()

    if isinstance(ip_add, ipaddress.IPv4Address):
        add = sdsadv.IpAddress(sds=config.vars['sds'],
                               space=space,
                               ipv4=str(ip_add))
        add.set_name(name)

        if macaddress != '0e:00:00:00:00:00':
            add.set_mac(macaddress)

        if meta != "":
            cp.add_classparams_from_string(add, meta)

        if ip_class and ip_class != "":
            add.set_class_name(ip_class)

        try:
            add.create()
        except SDSError as e:
            msg = f"[red]error on IP create[/red] ({e.message})"
            log.error(msg)
            add = None

    if add:
        if config.vars['json_output']:
            _jr = convert_dict(add)
            _jr['_elapsed'] = round(time.time()-_start_time, 4)
            print(json.dumps(_jr))
        else:
            text = Text.assemble("IP created in IPAM: ",
                                 (f"{add.ipv4}", "green"),
                                 ", name=",
                                 (f"{add.name}", "green"))
            log.info(text)


@app.command()
def info(address: Annotated[str,
                            typer.Argument(
                                help='ipv4 or id')],
         #  name: Annotated[str,
         #                  typer.Option(help='the name of the IP in the IPAM')] = f'cli-{str(uuid.uuid4())[0:8]}',
         space: Annotated[str,
                          typer.Option(help='the space name',
                                       envvar="SDS_SPACE")] = "Local"):

    _start_time = time.time()

    add = _find_ipaddress(address, space)
    if not add:
        exit()

    if config.vars['json_output']:
        _jr = convert_dict(add)
        _jr['_elapsed'] = round(time.time()-_start_time, 4)
        print(json.dumps(_jr))
    else:
        text = f"IP in IPAM: [green]{add.ipv4}[/green]"
        text += f" \[{add.myid}]"
        text += f", name={add.name}"
        text += f", space={add.space.name}"
        if add.class_name and add.class_name != "":
            text += f", class={add.class_name}"
        if add.mac and add.mac != "":
            text += f", mac={add.mac}"

        log.info(text)


@app.command()
def delete(address: Annotated[str,
                              typer.Argument(
                                  help='ipv4 or id')],
           space: Annotated[str,
                            typer.Option(help='the space name',
                                         envvar="SDS_SPACE")] = "Local"):

    _start_time = time.time()

    add = _find_ipaddress(address, space)
    if not add:
        exit()

    add.delete()


if __name__ == "__main__":
    app()

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


def convert_dict(net: sdsadv.Network = None) -> dict:
    """convert the network adv object to a dictionary structure
       for easy output as json

    Args:
        ipadd (sdsadv.IpAddress, optional): IP address object to convert.

    Returns:
        dict: the dictionary object
    """
    if net:
        _j = net.__dict__
        if config.vars['json_output']:
            # print(_j)
            _jr = {
                'id': _j['myid'],
                'network': f"{_j['subnet_addr']}/{_j['subnet_prefix']}",
                'address': f"{_j['subnet_addr']}",
                'prefix': f"{_j['subnet_prefix']}",
                'name': _j['name'],
                'space': _j['space'].name,
                'is_block': _j['is_block'],
                'is_terminal': _j['is_terminal'],
                'ip_free_size': _j['params']['subnet_ip_free_size'],
                'description': ''
            }

            if _j['description']:
                _jr['description'] = _j['description']

            if _j['class_name']:
                _jr['class'] = _j['class_name']

            _cparam = {}
            for _k, _v in _j['_ClassParams__private_class_params'].items():
                _cparam[_k] = _v

            for _k, _v in _j['_ClassParams__class_params'].items():
                if _k not in [
                    'dns_view_name',
                    'rev_dns_view_name',
                    'use_ipam_name',
                    'ipv6_mapping',
                    'dns_id',
                    'rev_dns_id',
                    'dns_update',
                    'dhcp_failover_name',
                    'dhcpstatic',
                    'dns_name',
                        'rev_dns_name',
                        '__eip_description']:
                    _cparam[_k] = _v
            if len(_cparam) > 0:
                _jr['class_params'] = _cparam

            return _jr

    return {}


@app.command()
def create(address: Annotated[str,
                              typer.Argument(
                                  help='ipv4/prefix')],
           name: Annotated[str,
                           typer.Option(help='the name of the IP in the IPAM')
                           ] = f'cli-{str(uuid.uuid4())[0:8]}',
           net_space: Annotated[str,
                                typer.Option('--space',
                                             help='the space name',
                                             envvar="SDS_SPACE")
                                ] = "Local",
           is_block: Annotated[bool,
                               typer.Option('--block',
                                            help='the network is a block')
                               ] = False,
           is_terminal: Annotated[bool,
                                  typer.Option('--terminal',
                                               help='the network is terminal')
                                  ] = False,
           parent_network: Annotated[str,
                                     typer.Option('--parent',
                                                  help='the parent network id or name')
                                     ] = "",
           net_class: Annotated[str,
                                typer.Option('--class',
                                             help='the class associated with the network')
                                ] = None,
           meta: Annotated[str,
                           typer.Option(
                               help='class params: a=\'1\',b1=\'foo bar\' ')
                           ] = ""):
    _start_time = time.time()

    if is_block and is_terminal:
        log.critical("the network cannot be block and terminal")
        exit()

    ip_net = None

    try:
        ip_net = ipaddress.IPv4Network(address)
    except ipaddress.AddressValueError:
        log.critical("invalid network address")
        exit()

    space = None
    if net_space:
        # get the space
        space = sdsadv.Space(sds=config.vars['sds'],
                             name=net_space)
        try:
            space.refresh()
        except:
            log.critical(
                f"\ncannot find the space {space} on the SDS")
            exit()

    net = sdsadv.Network(sds=config.vars['sds'],
                         space=space,
                         name=name)

    net.set_address_prefix(ip_net.network_address,
                           ip_net.prefixlen)
    net.set_is_block(is_block)
    net.set_is_terminal(is_terminal)

    if parent_network != '':
        bfound = False
        parent = sdsadv.Network(sds=config.vars['sds'],
                                space=space,
                                name=parent_network)

        try:
            parent.refresh()
            bfound = True
        except SDSNetworkError:
            bfound = False

        if not bfound:
            try:
                parent.myid = int(parent_network)
                parent.refresh()
                bfound = True
            except SDSNetworkError:
                bfound = False
            except ValueError:
                bfound = False

        if not bfound:
            log.critical("cannot find the parent"
                         f" network {parent_network}")
            exit()

        net.set_parent(parent)

    if meta != "":
        cp.add_classparams_from_string(net, meta)

    if net_class and net_class != "":
        net.set_class_name(net_class)

    try:
        net.create()
    except SDSError as e:
        msg = f"[red]error on  networkcreate[/red] ({e.message})"
        log.error(msg)
        net = None

    if config.vars['json_output']:
        _jr = convert_dict(net)
        _jr['_elapsed'] = round(time.time()-_start_time, 4)
        print(json.dumps(_jr))
    else:
        text = f"Network in IPAM: [green]{net.subnet_addr}/{net.subnet_prefix}[/green]"
        text += f", name={net.name}"
        text += f", space={net.space.name}"
        if net.is_block:
            text += ", block"
        if net.is_terminal:
            text += ", terminal"

        if net.class_name and net.class_name != "":
            text += f", class={net.class_name}"

        if net.description and net.description != "":
            text += f", descr=\"{net.description}\""

        log.info(text)


@app.command()
def info(address: Annotated[str,
                            typer.Argument(
                                help='ipv4/prefix or id')],
         net_space: Annotated[str,
                              typer.Option('--space',
                                           help='the space name',
                                           envvar="SDS_SPACE")] = "Local"):

    _start_time = time.time()

    net_id = -1
    net_add = None

    try:
        net_add = ipaddress.IPv4Network(address)
    except ipaddress.AddressValueError:
        try:
            net_id = int(address)
        except ValueError:
            log.abort("address is not a network address, nor an id")
            exit()

    space = None
    if net_space:
        # get the space
        space = sdsadv.Space(sds=config.vars['sds'],
                             name=net_space)
        try:
            space.refresh()
        except:
            log.critical(
                f"\ncannot find the space {space} on the SDS")
            exit()

    net = sdsadv.Network(sds=config.vars['sds'],
                         space=space)

    if isinstance(net_add, ipaddress.IPv4Network):
        net.set_address_prefix(net_add.network_address,
                               net_add.prefixlen)

    elif net_id > -1:
        net.myid = net_id
    else:
        log.warning("nothing to search, exiting")
        exit()

    try:
        net.refresh()
    except SDSError as e:
        msg = f"[red]error on network info[/red] ({e.message})"
        log.error(msg)
        return

    if config.vars['json_output']:
        _jr = convert_dict(net)
        _jr['_elapsed'] = round(time.time()-_start_time, 4)
        print(json.dumps(_jr))
    else:
        text = f"Network in IPAM: [green]{net.subnet_addr}/{net.subnet_prefix}[/green]"
        text += f", name={net.name}"
        text += f", space={net.space.name}"
        if net.is_block:
            text += ", block"
        if net.is_terminal:
            text += ", terminal"

        if net.class_name and net.class_name != "":
            text += f", class={net.class_name}"

        if net.description and net.description != "":
            text += f", descr=\"{net.description}\""

        log.info(text)


@app.command()
def list(address: Annotated[str,
                            typer.Argument(
                                help='ipv4/prefix or id of the top network')],
         net_space: Annotated[str,
                              typer.Option('--space',
                                           help='the space name',
                                           envvar="SDS_SPACE")] = "Local"):

    _start_time = time.time()

    net_id = -1
    net_add = None

    try:
        net_add = ipaddress.IPv4Network(address)
    except ipaddress.AddressValueError:
        try:
            net_id = int(address)
        except ValueError:
            log.abort("address is not a network address, nor an id")
            exit()

    space = None
    if net_space:
        # get the space
        space = sdsadv.Space(sds=config.vars['sds'],
                             name=net_space)
        try:
            space.refresh()
        except:
            log.critical(
                f"\ncannot find the space {space} on the SDS")
            exit()

    net = sdsadv.Network(sds=config.vars['sds'],
                         space=space)

    if isinstance(net_add, ipaddress.IPv4Network):
        net.set_address_prefix(net_add.network_address,
                               net_add.prefixlen)

    elif net_id > -1:
        net.myid = net_id
    else:
        log.warning("nothing to search, exiting")
        exit()

    try:
        net.refresh()
    except SDSError as e:
        msg = f"[red]error on network info[/red] ({e.message})"
        log.error(msg)
        return

    net_list = net.get_subnet_list(depth=2, only_under_block=True)
    net_list = sorted(net_list, key=lambda d: d['start_hex_ip']+d['level'])

    if config.vars['json_output']:
        _jr = {'nets': []}

        for net in net_list:
            del net['start_hex_ip']
            _jr['nets'].append(net)

        _jr['_elapsed'] = round(time.time()-_start_time, 4)
        print(json.dumps(_jr))
    else:
        text = f"Networks in IPAM starting at [green]{net.subnet_addr}/{net.subnet_prefix}[/green]"
        text += f" in space {net_space}:"

        for net in net_list:
            text += f"\n" + \
                ' '*int(net['level']) + \
                f"[{net['id']}] {net['subnet_name']} | "
            text += f" {net['start_hostaddr']}/{net['subnet_size']}"

            if net['terminal']:
                text += ", terminal"
            else:
                text += ", block"

            if net['class'] != "":
                text += f", class={net['class']}"

            if 'used_ip_percent' in net:
                text += f", used={net['used_ip_percent']}%"

        log.info(text)


if __name__ == "__main__":
    app()

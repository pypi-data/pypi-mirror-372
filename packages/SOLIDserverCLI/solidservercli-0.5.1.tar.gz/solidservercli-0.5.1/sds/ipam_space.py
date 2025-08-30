import typer
from typing_extensions import Annotated

from rich import print
from rich.text import Text
from rich.tree import Tree
from rich.table import Table
from rich.console import Console

import uuid
import json
import re
import time
from enum import Enum

from SOLIDserverRest import SDSSpaceError, SDSError
from SOLIDserverRest import adv as sdsadv

import sds.config as config
from sds.config import log
import sds.classparams as cp

app = typer.Typer()


def convert_dict(space: sdsadv.Space = None) -> dict:
    """convert the space adv object to a dictionary structure
       for easy output as json

    Args:
        space (sdsadv.Space, optional): space object to convert.

    Returns:
        dict: the dictionary object
    """
    if space:
        _j = space.__dict__
        # print(_j)
        _jr = {}

        if space.myid > 0:
            _jr['id'] = space.myid

        if space.name:
            _jr['name'] = space.name

        if _j['class_name']:
            _jr['class'] = _j['class_name']

        if _j['description']:
            _jr['description'] = _j['description']

        if _j['parent']:
            _jr['parent'] = _j['parent'].name

        _cparam = {}
        for _k, _v in _j['_ClassParams__private_class_params'].items():
            if _k != 'hostname':
                _cparam[_k] = _v
        if len(_cparam) > 0:
            _jr['class_params'] = _cparam

        return _jr

    return {}


@app.command()
def create(name: Annotated[str,
                           typer.Argument(
                               help='the name of the space in the IPAM')
                           ] = f'cli-{str(uuid.uuid4())[0:8]}',
           parent: Annotated[str,
                             typer.Option(help='the parent space name',
                                          envvar="SDS_SPACE")
                             ] = None,
           space_class: Annotated[str,
                                  typer.Option('--class',
                                               help='the class associated with the space')
                                  ] = None,
           description: Annotated[str,
                                  typer.Option(
                                      help='the description for this space')
                                  ] = None,
           meta: Annotated[str,
                           typer.Option(
                               help='class params: a=\'1\',b1=\'foo bar\' ')
                           ] = None):
    _start_time = time.time()

    space = sdsadv.Space(sds=config.vars['sds'],
                         name=name)

    if parent and parent != '':
        try:
            space.set_parent_byname(parent)
        except SDSSpaceError as e:
            log.critical(
                f"cannot find the parent {parent}")
            log.critical(e)
            exit()

    if meta and meta != "":
        cp.add_classparams_from_string(space, meta)

    if space_class and space_class != "":
        space.set_class_name(space_class)

    if description and description != "":
        space.set_description(description)

    try:
        space.create()
    except SDSError as e:
        msg = f"[red]error on space create[/red] ({e.message})"
        log.error(msg)
        space = None

    if space:
        if config.vars['json_output']:
            _jr = convert_dict(space)
            _jr['_elapsed'] = round(time.time()-_start_time, 4)
            print(json.dumps(_jr))
        else:
            text = Text.assemble("Space created in IPAM: ",
                                 (f"{space.name}", "green"))
            log.info(text)


@app.command()
def info(name: Annotated[str,
                         typer.Argument(
                             help='the name (or id) of the space in the IPAM')
                         ] = ''):

    _start_time = time.time()

    if name == '':
        log.critical('missing name')
        exit()

    space = sdsadv.Space(sds=config.vars['sds'],
                         name=name)

    bfound = False

    # check space with its name
    try:
        space.refresh()
        bfound = True
    except SDSError as e:
        bFound = False

    if not bfound:
        try:
            space.myid = int(name)
            space.refresh()
            bfound = True
        except:
            bFound = False

    if not bfound:
        log.critical(f"cannot find the space {name}")
        exit()

    if space:
        _jr = convert_dict(space)

        if config.vars['json_output']:
            _jr['_elapsed'] = round(time.time()-_start_time, 4)
            print(json.dumps(_jr))
        else:
            text = f"Space: [green]{space.name}[/green]"
            if space.description and space.description != "":
                text += f" \"{space.description}\""

            if space.class_name and space.class_name != "":
                text += f", class={space.class_name}"

            if space.parent:
                text += f", parent={space.parent.name}"

            if 'class_params' in _jr:
                text += ", meta=" + json.dumps(_jr['class_params'])

            log.info(text)


@app.command()
def update(name: Annotated[str,
                           typer.Argument(
                               help='the name (or id) of the space in the IPAM')
                           ] = '',
           rename: Annotated[str,
                             typer.Option(help='the new name for this space')
                             ] = None,
           space_class: Annotated[str,
                                  typer.Option('--class',
                                               help='the class associated with the space')
                                  ] = None,
           description: Annotated[str,
                                  typer.Option(
                                      help='the description for this space')
                                  ] = None,
           meta: Annotated[str,
                           typer.Option(
                               help='class params: a=\'1\',b1=\'foo bar\' ')
                           ] = None):

    _start_time = time.time()

    if name == '':
        log.critical('no space name provided')
        exit()

    space = sdsadv.Space(sds=config.vars['sds'],
                         name=name)

    bfound = False

    # check space with its name
    try:
        space.refresh()
        bfound = True
    except SDSError as e:
        bFound = False

    if not bfound:
        try:
            space.myid = int(name)
            space.refresh()
            bfound = True
        except:
            bFound = False

    if not bfound:
        log.critical(f"cannot find the space {name}")
        exit()

    if isinstance(meta, str):
        cp.add_classparams_from_string(space, meta)

    if isinstance(space_class, str):
        space.set_class_name(space_class)

    if isinstance(description, str):
        space.set_description(description)

    if isinstance(rename, str) and rename != '':
        space.name = rename

    try:
        space.update()
    except SDSError as e:
        msg = f"[red]error on space update[/red] ({e.message})"
        log.error(msg)
        space = None

    if space:
        if config.vars['json_output']:
            _jr = convert_dict(space)
            _jr['_elapsed'] = round(time.time()-_start_time, 4)
            print(json.dumps(_jr))
        else:
            text = Text.assemble("Space updated in IPAM: ",
                                 (f"{space.name}", "green"))
            log.info(text)


@app.command()
def delete(name: Annotated[str,
                           typer.Argument(
                               help='the name (or id) of the space in the IPAM')
                           ] = None):

    _start_time = time.time()

    space = sdsadv.Space(sds=config.vars['sds'],
                         name=name)

    bfound = False

    # check space with its name
    try:
        space.refresh()
        bfound = True
    except SDSError as e:
        bFound = False

    if not bfound:
        try:
            space.myid = int(name)
            space.refresh()
            bfound = True
        except:
            bFound = False

    if not bfound:
        log.critical(f"cannot find the space {name}")
        exit()

    if space:
        _name = space.name
        space.delete()

        _jr = convert_dict(space)

        if config.vars['json_output']:
            _jr['_elapsed'] = round(time.time()-_start_time, 4)
            _jr['state'] = 'deleted'
            _jr['name'] = _name
            print(json.dumps(_jr))
        else:
            text = f"space deleted: [green]{_name}[/green]"
            log.info(text)


class PrintType(str, Enum):
    tree = "tree"
    table = "table"
    simple = "simple"


@app.command("list")
def display_list(limit: Annotated[int,
                                  typer.Option(
                                      help='the number max of spaces to list, 0 for no limit')
                                  ] = 50,
                 offset: Annotated[int,
                                   typer.Option(
                                       help='if a limit is used, starts at te offset position')
                                   ] = 0,
                 page: Annotated[int,
                                 typer.Option(
                                     help='number of object to get on each API call')
                                 ] = 50,
                 style: Annotated[PrintType,
                                  typer.Option(
                                      help='how to display the list')
                                  ] = PrintType.table,
                 ):

    if limit == 0:
        offset = 0

    space = sdsadv.Space(sds=config.vars['sds'])
    space_list = space.list_spaces(offset=offset, limit=limit, page=page)

    if config.vars['json_output']:
        print(json.dumps(space_list))
        return

    if style == PrintType.table:
        table = Table(title="Space list",
                      show_lines=True)

        table.add_column("id",   justify="right", style="yellow")
        table.add_column("name",   justify="left", style="blue", no_wrap=True)
        table.add_column("parent", justify="left", style="blue", no_wrap=False)
        table.add_column("class", justify="left",
                         style="green", no_wrap=False)
        table.add_column("description", style="cyan", justify="left",
                         no_wrap=False)
        table.add_column("meta", justify="left", style="red", no_wrap=False)

        for i in space_list:
            _cps = ''
            _sep = ''
            for _k, _v in i['meta'].items():
                _cps += _sep+_k+': '+_v
                _sep = '\n'

            table.add_row(i['id'],
                          i['name'], i['parent'], i['class'],
                          i['description'],
                          _cps)

        console = Console()
        console.print(table)

    elif style == PrintType.simple:
        _line = f"{'id':<5}"
        _line += f"{'name':<40}"
        _line += f"{'class':<15}"
        _line += f"{'description':<20}"
        print(_line)

        for i in space_list:
            _line = f"[yellow]{i['id']:<5}[/yellow]"
            if i['tree_level'] > 0:
                _sep = '| '*i['tree_level']
            else:
                _sep = ''
            _line += f"{_sep+i['name']:<40}"
            _line += f"{i['class'][:14]:<15}"
            _line += f"{i['description']:<20}"
            print(_line)

    elif style == PrintType.tree:
        tree = Tree("Space list")

        def add_leaf(treeobj=None, spaceinfo=None, lvl=0):
            for i in space_list:
                if i['tree_level'] == lvl:
                    _text = f"[blue]{i['name']}[/blue] (#[yellow]{i['id']}[/yellow])"
                    if i['class'] != '':
                        _text += f" class=[green]{i['class']}[/green]"
                    if i['description'] != '':
                        _text += f" descr=\"[cyan]{i['description']}\"[/cyan]"

                    _cps = ''
                    _sep = ''
                    for _k, _v in i['meta'].items():
                        _cps += _sep+_k+':'+_v
                        _sep = ','

                    if _cps != '':
                        _text += f" meta=[red]{_cps}[/red]"

                    if lvl > 0:
                        if spaceinfo['name'] == i['parent']:
                            _leaf = treeobj.add(_text)
                            add_leaf(_leaf, i, lvl+1)
                    else:
                        _leaf = treeobj.add(_text)
                        add_leaf(_leaf, i, lvl+1)

        add_leaf(treeobj=tree, spaceinfo=None, lvl=0)
        print(tree)

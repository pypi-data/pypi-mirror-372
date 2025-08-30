import typer
from enum import Enum
import json

import sds.config as config
from sds.config import log

app = typer.Typer()


@app.command()
def status():
    _j = config.vars['sds'].__dict__

    _jr = {
        'host': _j['sds_ip'],
        'auth_method': _j['auth_method'],
        'timeout': _j['timeout'],
    }
    if 'version' in _j and _j['version']:
        _jr['version'] = _j['version']

    if 'user' in _j and _j['user']:
        _jr['user'] = _j['user']
    else:
        _jr['user'] = "ukn"
        if _jr['auth_method'] == "token":
            _jr['user'] += ' (token)'

    if 'proxy_socks' in _j and _j['proxy_socks']:
        _jr['proxy_socks'] = _j['proxy_socks']

    if config.vars['json_output']:
        print(json.dumps(_jr))
    else:
        text = (f"SOLIDserver: "
                f"[bold]{_jr['host']}[/bold]"
                f", authentication: [bold]{_jr['auth_method']}[/bold]"
                )
        if 'version' in _jr:
            text += f", version: {_jr['version']}"

        if 'proxy_socks' in _jr:
            text += f", socks: on"

        text += f", timeout: {_jr['timeout']}s"

        log.info(text)

        if not 'version' in _jr:
            log.warning("version not available, requires admin permission")


if __name__ == "__main__":
    app()

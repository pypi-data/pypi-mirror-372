import typer

import sds.config as config
import sds.dns_rr as dns_rr

app = typer.Typer()
app.add_typer(dns_rr.app, name="rr")


@app.command()
def zone():
    config.err_console.log('not yet implemented')


if __name__ == "__main__":
    app()

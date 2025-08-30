from typer.testing import CliRunner

if True:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')))
    from sds import cli
    import sds.config as config
    _conf = config.read_config()

runner = CliRunner()


def test_server_status():
    app = cli.init_app()

    result = runner.invoke(app, ["--json", "server", "status"])

    assert result.exit_code == 0
    assert _conf['sds_name'] in result.output
    assert _conf['sds'] != None

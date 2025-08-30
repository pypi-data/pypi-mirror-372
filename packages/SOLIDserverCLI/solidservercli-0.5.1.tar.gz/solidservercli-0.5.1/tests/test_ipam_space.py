from typer.testing import CliRunner
import uuid
import logging
import json

if True:
    import sys
    import os
    sys.path.insert(0, os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..')))
    from sds import cli
    import sds.config as config
    _conf = config.read_config()
    app = cli.init_app()

runner = CliRunner()


def test_simple_space():
    """create, info and delete simple space
    """
    space_name = 'tauto-'+str(uuid.uuid4())[:8]

    # create
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "create",
                                 space_name])

    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert _conf['sds'] != None
    assert int(_json['id']) > 0
    assert _json['name'] == space_name

    # info
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "info",
                                 space_name])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert int(_json['id']) > 0
    assert _json['name'] == space_name

    # info by id
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "info",
                                 str(_json['id'])])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert int(_json['id']) > 0
    assert _json['name'] == space_name

    # delete
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "delete",
                                 space_name])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert _json['state'] == 'deleted'
    assert _json['name'] == space_name


def test_space_class():
    """create, info and delete space with class
    """
    space_name = 'tauto-'+str(uuid.uuid4())[:8]
    space_class = 'tauto-class-'+str(uuid.uuid4())[:4]

    # create
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "create",
                                 space_name,
                                 "--class", space_class])

    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert _conf['sds'] != None
    assert int(_json['id']) > 0
    assert _json['name'] == space_name
    assert _json['class'] == space_class

    # info
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "info",
                                 space_name])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert int(_json['id']) > 0
    assert _json['name'] == space_name
    assert _json['class'] == space_class

    # update
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "update",
                                 space_name,
                                 "--class", "updated"])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert int(_json['id']) > 0
    assert _json['name'] == space_name
    assert _json['class'] != space_class

    # delete
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "delete",
                                 space_name])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert _json['state'] == 'deleted'
    assert _json['name'] == space_name


def test_space_descr():
    """create, info and delete space with description
    """
    space_name = 'tauto-'+str(uuid.uuid4())[:8]
    space_descr = 'tauto-descr-'+str(uuid.uuid4())[:4]

    # create
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "create",
                                 space_name,
                                 "--description", space_descr])

    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert _conf['sds'] != None
    assert int(_json['id']) > 0
    assert _json['name'] == space_name
    assert _json['description'] == space_descr

    # info
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "info",
                                 space_name])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert int(_json['id']) > 0
    assert _json['name'] == space_name
    assert _json['description'] == space_descr

    # update
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "update",
                                 space_name,
                                 "--description", "updated"])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert int(_json['id']) > 0
    assert _json['name'] == space_name
    assert _json['description'] != space_descr

    # delete
    result = runner.invoke(app, ["--json",
                                 "ipam",
                                 "space",
                                 "delete",
                                 space_name])
    # logging.error(result.output)
    _json = json.loads(result.output)

    assert result.exit_code == 0
    assert _json['state'] == 'deleted'
    assert _json['name'] == space_name

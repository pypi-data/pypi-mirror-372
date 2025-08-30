# SOLIDserver cli

This package contains a command to manage the SOLIDserver and its objects.

## install

* in a virtual environment
* install the package: `pip install SOLIDserverCLI`
* configure the access to the SOLIDserver by creating a file named `sds.ini` which contains:

```text
[server]
name = server
token_id = xxx
token_key = yyy
```

## Usage

The command `sds` can be used directly from the shell. It is organized with commands and subcommands, you can at each level add the `--help` option to get more information.

By using the `--json` at the top level, all outputs will be in the json format, providing the ability to use jq to manipulate the result.

Examples:

```text
> sds server status
SOLIDserver: sds-test.intranet, authentication: token, version: 8.4.2, timeout: 10s

> sds --json server status
{"host": "sds-test.intranet", "auth_method": "token", "timeout": 10, "version": "8.4.2", "user": "ukn (token)"}
```

## Commands

```text
├─ server
│  └─ status
└─ ipam
   ├─ space
   │  ├─ create
   │  ├─ info
   │  ├─ update
   │  ├─ delete
   │  └─ list
   ├─ ip
   │  ├─ create
   │  ├─ delete
   │  └─ info
   └─ network
      ├─ create
      ├─ list
      └─ info
```
# healthcheck-lite

A lightweight, flexible system healthcheck utility for Linux using a simple INI configuration file.

## Features

- Check systemd services, memory usage, disk usage, TCP ports, file contents, zombie processes, SSL certs, and more.
- Configurable severity level.
- INI file structure with support for multiple sections.
- Supports output in JSON or HTML.
- Watch mode for continuous monitoring.
- Test mode for validating configuration files.

## Installation

```bash
pip install healthcheck-lite
```

## Usage

```bash
healthcheck-lite --config mychecks.ini
```

### Available Options

- `--config FILE` – Path to the configuration INI file.
- `--exec TYPE1,TYPE2,...` – Run only specific check types (e.g. `memory,file`).
- `--name NAME` – Run only the check with the given name.
- `--output results.json|results.html` – Save the output to a file.
- `--strict` – Mark script as failed on any failed check, regardless of severity.
- `--test` – Only validate the INI configuration file, without running checks.
- `--watch N` – Run checks every N minutes in a loop.

### Example INI

```ini
[global]
severity=3
green=\033[92m
red=\033[91m
reset=\033[0m

[service]
name=Check SSH
service=ssh
severity=2

[process]
name=Check Gunicorn
regex=.*gunicorn.*
countmin=1
severity=3

[port]
name=HTTP Port
host=localhost
port=80
severity=3

[filesystem]
name=Root FS
filesystem=/
used=80
severity=3

[memory]
name=Memory usage
used=90
severity=3

[file]
name=Log check
file=/var/log/syslog
regex=.*ERROR.*
severity=3

[establish]
name=MySQL connections
dest=127.0.0.1:3306
used=50
severity=2

[command]
name=Check hostname
command=hostname
expect_regex=.*   # any non-empty output
severity=3

[filecheck]
name=Check /etc/passwd
path=/etc/passwd
must_exist=true
mode=644
owner=root
group=root
severity=2

[ping]
name=Ping Google DNS
host=8.8.8.8
count=2
severity=3

[load]
name=System Load
load1=4.0
severity=3

[sslcheck]
name=Google SSL
host=google.com
port=443
days_warn=7
severity=2

[zombies]
name=Zombie check
max=0
severity=1
```

## License

MIT License

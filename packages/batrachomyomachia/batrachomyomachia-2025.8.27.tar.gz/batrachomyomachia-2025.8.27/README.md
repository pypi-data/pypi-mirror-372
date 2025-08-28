# Batrachomyomachia

Batrachomyomachia is a self-service automation tool that integrates with Forgejo to simplify
Git patch submission workflows.
It enables pull request authors to preview and submit patch series to mailing lists, automatically
handling patch series versioning, email formatting, and review management.

## How do I use this? AKA: User Commands

Users can perform the following commands by typing them in pull request comments:

* `/allow`: Authorizes a user to use bot commands.
* `/submit`: Sends the patch series to the configured mailing list.
* `/preview`: Sends a preview of the patch series to the author's public email.

Only previously authorized users may use these commands. Unauthorized attempts are politely
rejected with guidance.
The automation is quite strict in what it accepts. Additional whitespace is ok but non whitespace
characters will cause the comment to be silently ignored.

## How do I set up and administer this?

* You need to have a forgejo instance running.
* You need to have a valkey or redict instance running. This is because
  they act as task brokers for [Celery](https://docs.celeryq.dev/en/stable/),
  a distributed task queue used to make the webhook fast enough for its
  intended purpose.
* You install batrachomyomachia using typical python tools such as uv or pip.
* You configure this tool based on the Configuration section below
* You use the bmm command line to start:
  * the webhook listener (which will open an http port and listen on events)
  * the workers (which will actually do the work)
  * (optionally) flower, a web gui for monitoring the task queue.
* You configure forgejo to signal events to the webhook either globally
  or on a per organization basis using the forgejo UI.

This operation can be automated using ansible. Check the
sourceware_forge_batrachomyomachia role in this repository for detailed
instructions.

### Administrator CLI Commands

The `bmm` CLI interface is a tool that can be used by admins that have access
to the server.
It provides the following commands explained above:

* `worker [--concurrency N] [--loglevel level] [--solo] [--skip-cron]`
  Start a group of Celery workers for processing events such as webhook
  messages and regular repository synchronization.
  The `--solo` option is essentially there for debugging.
  The `--skip-cron` option disables scheduled repository mirroring.

* `webhook [--host <addr>] [--port <port>] [--uvicorn] [--debug]`
  Start the webhook server.

* `flower [--host <addr>] [--port <port>] [--debug]`
  Start the Celery Flower monitoring interface.

Additionally, the following administrative operations can be performed:

* `allow --username <user>`
  Add a user to the allowlist to run `/allow` and `/submit`.

* `freeze --pr <url> [--force]`
  Freeze a PR into a new version and update the version history comment.

* `preview --pr <url>`
  Email the patch preview of a pull request to the author.

* `submit --pr <url> --to <email>`
  Submit the patch series of a pull request to the given recipient.

* `summary --pr <url> --to <email>`
  Send a summary email describing the pull request contents.

* `welcome --pr <url>`
  Add a welcome comment to the pull request with guidance.

## Configuration

Settings are read from several YAML sources:

* `default-settings.yml` (bundled with the package)
* System specific `/etc/xdg/batrachomyomachia/settings.yml`
* User-specific `$HOME/.config/batrachomyomachia/settings.yml`
* `settings.yml` in the current working directory
* `.secrets.yml` in the current working directory for sensitive data
  that must not leak into source control.

Most settings can be overridden on a per-repository basis.
The `default-settings.yml` contains a comprehensive list of all possible configuration options.
Comments above each setting document the setting.

### Configuring Forgejo Webhooks

Refer to [Forgejo's webhook documentation](https://forgejo.org/docs/latest/user/webhooks) for configuration guidance.

Webhooks may be set globally, per organization, or per repository.
The endpoint URL should resemble `http://localhost:4000/webhook` if co-hosted with Forgejo.

Ensure that the `Secret` configured in the Forgejo UI matches the `webhook_secret` setting or the `BMM_WEBHOOK_SECRET` environment variable.

### Required permissions

The bot user should have the ability to force push refs and notes on the repository.

The webhook must have the following events enabled:
- Pull request events > Modification
- Pull request events > Comments

The bot user should have an API key enabled with the following access:
- issue: read and write (to post comments)
- repository: read (to read pull request data)

The bot user should have at least the following permissions on the target repositories:
- Code: Write
- Issues: Read
- Pull Requests: Read

### Environment Variable Configuration

All settings can be overridden using environment variables.
Refer to the [Dynaconf documentation](https://www.dynaconf.com/envvars/) for usage details.
Use `default-settings.yml` to determine variable names (prefixed with `BMM`).

Example:

```bash
BMM_FORGEJO_URL="https://forge.sourceware.org/"
BMM_API_KEY=xxxx

BMM_MAIL_FROM="Bot account <bot@source.org>"

BMM_SMTP__HOST=mail.server.com
BMM_SMTP__PORT=25
BMM_SMTP__TLS=true
BMM_SMTP__DEBUG=0
```

## Project Structure and Development Hints

There are two main entry points:

* The bmm command line tool for admins, implemented in `cli.py`. Each subcommand is
  implemented by a `@click.command` decorated method in that file.
* The webhook server, implemented in `webhook.py`. The `webhook_receiver` function actually
  receives the messages and hands them off to celery via a redis object broker.
  The celery workers then run the `deal_with` method in parallel for each message.

Here is an overview of the main files in the codebase:

```text
batrachomyomachia/
├── allowlist.py              # User permission management
├── cli.py                    # Entry point for all CLI commands
├── config.py                 # Configuration loader and utility accessors
├── cron.py                   # Code that sets up regular tasks, specifically repository synchronization
├── default-settings.yml      # Default configuration file
├── email.py                  # Patch generation and email logic
├── forgejo_api_ops.py        # Forgejo API interactions
├── local_git_ops.py          # Git operations for freezing versions and formatting patches
├── templates.py              # Jinja2 template rendering for emails and comments
├── utilities.py              # Common utilities and data classes
├── webhook.py                # Webhook handling logic
└── templates/                # Default Jinja2 Templates used for generating messages
```

The author uses uv for dealing with dependencies, an editor that will apply the contents of
env files to the environment when running commands and tox to run all needed linters.

```bash
cd batrachomyomachia
uv pip install -e '.[dev]'
. ./.venv/bin/activate
uv run bmm welcome --pr https://forge.sourceware.org/gcc/gcc-TEST/pulls/49
tox
```

## License

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <http://www.gnu.org/licenses/>.

See the COPYING file at the top level of this repository for more information.

## Why is it called Batrachomyomachia?

[Batrachomyomachia](https://en.wikipedia.org/wiki/Batrachomyomachia) is a comic epic, or a parody of the Iliad.
The word has come to mean "a trivial altercation". This project aims to bridge the needs of people who have a preference
for pull-request and email based patch series workflows so that both can easily contribute and be kept in the loop
rather than keep them in opposition.

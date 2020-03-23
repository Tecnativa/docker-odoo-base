# [Doodba](https://hub.docker.com/r/tecnativa/doodba)

[![](https://images.microbadger.com/badges/version/tecnativa/doodba:latest.svg)](https://microbadger.com/images/tecnativa/doodba:latest "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/image/tecnativa/doodba:latest.svg)](https://microbadger.com/images/tecnativa/doodba:latest "Get your own image badge on microbadger.com")
[![](https://images.microbadger.com/badges/commit/tecnativa/doodba:latest.svg)](https://microbadger.com/images/tecnativa/doodba:latest "Get your own commit badge on microbadger.com")
[![](https://images.microbadger.com/badges/license/tecnativa/doodba.svg)](https://microbadger.com/images/tecnativa/doodba "Get your own license badge on microbadger.com")

[![](https://api.travis-ci.org/Tecnativa/doodba.svg)](https://travis-ci.org/Tecnativa/doodba)

**Doodba** stands for **Do**cker **Od**oo **Ba**se, and it is a highly opinionated image
ready to put [Odoo](https://www.odoo.com) inside it, but **without Odoo**.

## What?

Yes, the purpose of this is to serve as a base for you to build your own Odoo project,
because most of them end up requiring a big amount of custom patches, merges,
repositories, etc. With this image, you have a collection of good practices and tools to
enable your team to have a standard Odoo project structure.

BTW, we use [Debian][]. I hope you like that.

[debian]: https://debian.org/

## Why?

Because developing Odoo is hard. You need lots of customizations, dependencies, and if
you want to move from one version to another, it's a pain.

Also because nobody wants Odoo as it comes from upstream, you most likely will need to
add custom patches and addons, at least, so we need a way to put all together and make
it work anywhere quickly.

## How?

You can start working with this straight away with our [scaffolding][].

<!-- toc -->

- [Image usage](#image-usage)
  - [`/opt/odoo/custom`: The important one](#optodoocustom-the-important-one)
    - [`/opt/odoo/custom/entrypoint.d`](#optodoocustomentrypointd)
    - [`/opt/odoo/custom/build.d`](#optodoocustombuildd)
    - [`/opt/odoo/custom/conf.d`](#optodoocustomconfd)
    - [`/opt/odoo/custom/ssh`](#optodoocustomssh)
    - [`/opt/odoo/custom/src`](#optodoocustomsrc)
      - [`/opt/odoo/custom/src/odoo`](#optodoocustomsrcodoo)
      - [`/opt/odoo/custom/src/private`](#optodoocustomsrcprivate)
      - [`/opt/odoo/custom/src/repos.yaml`](#optodoocustomsrcreposyaml)
        - [Automatic download of repos](#automatic-download-of-repos)
      - [`/opt/odoo/custom/src/addons.yaml`](#optodoocustomsrcaddonsyaml)
      - [`/opt/odoo/custom/dependencies/*.txt`](#optodoocustomdependenciestxt)
  - [`/opt/odoo/common`: The useful one](#optodoocommon-the-useful-one)
  - [`/opt/odoo/auto`: The automatic one](#optodooauto-the-automatic-one)
    - [`/opt/odoo/auto/addons`](#optodooautoaddons)
    - [`/opt/odoo/auto/odoo.conf`](#optodooautoodooconf)
- [The `Dockerfile`](#the-dockerfile)
- [Bundled tools](#bundled-tools)
  - [`addons`](#addons)
  - [`click-odoo` and related scripts](#click-odoo-and-related-scripts)
  - [`nano`](#nano)
  - [`log`](#log)
  - [`pot`](#pot)
  - [`psql`](#psql)
  - [`ptvsd`](#ptvsd)
  - [`pudb`](#pudb)
  - [`git-aggregator`](#git-aggregator)
  - [`autoaggregate`](#autoaggregate)
    - [Example `repos.yaml` file](#example-reposyaml-file)
  - [`odoo`](#odoo)
  - [GeoLite2](#geolite2)
- [Scaffolding](#scaffolding)
  - [Skip the boring parts](#skip-the-boring-parts)
  - [Tell me the boring parts](#tell-me-the-boring-parts)
    - [Environments](#environments)
      - [Development](#development)
        - [`wdb`](#wdb)
        - [MailHog](#mailhog)
        - [Network isolation](#network-isolation)
      - [Production](#production)
        - [Adding secrets](#adding-secrets)
        - [Global inverse proxy](#global-inverse-proxy)
        - [Booting production](#booting-production)
        - [Backups](#backups)
      - [Testing](#testing)
        - [Global whitelist](#global-whitelist)
    - [Other usage scenarios](#other-usage-scenarios)
      - [Inspect the database](#inspect-the-database)
      - [Restart Odoo](#restart-odoo)
      - [Run unit tests for some addon](#run-unit-tests-for-some-addon)
      - [Reading the logs](#reading-the-logs)
      - [Install some addon without stopping current running process](#install-some-addon-without-stopping-current-running-process)
      - [Update some addon without stopping current running process](#update-some-addon-without-stopping-current-running-process)
      - [Update changed addons only](#update-changed-addons-only)
      - [Export some addon's translations to stdout](#export-some-addons-translations-to-stdout)
      - [Open an odoo shell](#open-an-odoo-shell)
      - [Open another UI instance linked to same filestore and database](#open-another-ui-instance-linked-to-same-filestore-and-database)
- [FAQ](#faq)
  - [Will there be not retrocompatible changes on the image?](#will-there-be-not-retrocompatible-changes-on-the-image)
  - [How to have good QA and test in my CI with Doodba?](#how-to-have-good-qa-and-test-in-my-ci-with-doodba)
  - [I need to force addition or removal of `www.` prefix in production](#i-need-to-force-addition-or-removal-of-www-prefix-in-production)
  - [How to run a parallel Odoo container without crashing Traefik?](#how-to-run-a-parallel-odoo-container-without-crashing-traefik)
  - [How to allow access from several host names?](#how-to-allow-access-from-several-host-names)
  - [How to choose initial DB creation language?](#how-to-choose-initial-db-creation-language)
  - [I use Fish shell, how to export needed variables?](#i-use-fish-shell-how-to-export-needed-variables)
  - [When I boot `devel.yaml` for the first time, Odoo crashes](#when-i-boot-develyaml-for-the-first-time-odoo-crashes)
  - [How can I run a Posbox/IoT box service for development?](#how-can-i-run-a-posboxiot-box-service-for-development)
  - [This project is too opinionated, but can I question any of those opinions?](#this-project-is-too-opinionated-but-can-i-question-any-of-those-opinions)
  - [What's this `hooks` folder here?](#whats-this-hooks-folder-here)
  - [Can I have my own scaffolding?](#can-i-have-my-own-scaffolding)
  - [Can I skip the `-f docker-compose.yaml -f .yaml` part for `docker-compose` commands?](#can-i-skip-the--f-docker-composeyaml--f-yaml-part-for-docker-compose-commands)
  - [How can I pin an image version?](#how-can-i-pin-an-image-version)
  - [How to get proper assets when printing reports?](#how-to-get-proper-assets-when-printing-reports)
  - [How to change report fonts?](#how-to-change-report-fonts)
  - [How can I whitelist a service and allow external access to it?](#how-can-i-whitelist-a-service-and-allow-external-access-to-it)
  - [How can I help?](#how-can-i-help)
- [Related Projects](#related-projects)

<!-- tocstop -->

## Image usage

Basically, every directory you have to worry about is found inside `/opt/odoo`. This is
its structure:

    custom/
        entrypoint.d/
        build.d/
        conf.d/
        ssh/
            config
            known_hosts
            id_rsa
            id_rsa.pub
        dependencies/
            apt_build.txt
            apt.txt
            gem.txt
            npm.txt
            pip.txt
        src/
            private/
            odoo/
            addons.yaml
            repos.yaml
    common/
        entrypoint.sh
        build.sh
        entrypoint.d/
        build.d/
        conf.d/
    auto
        addons/
        odoo.conf

Let's go one by one.

### `/opt/odoo/custom`: The important one

Here you will put everything related to your project.

#### `/opt/odoo/custom/entrypoint.d`

Any executables found here will be run when you launch your container, before running
the command you ask.

#### `/opt/odoo/custom/build.d`

Executables here will be aggregated with those in `/opt/odoo/common/build.d`.

The resulting set of executables will then be sorted alphabetically (ascending) and then
subsequently run.

#### `/opt/odoo/custom/conf.d`

Files here will be environment-variable-expanded and concatenated in
`/opt/odoo/auto/odoo.conf` in the entrypoint.

#### `/opt/odoo/custom/ssh`

It must follow the same structure as a standard `~/.ssh` directory, including `config`
and `known_hosts` files. In fact, it is completely equivalent to `~root/.ssh`.

The `config` file can contain `IdentityFile` keys to represent the private key that
should be used for that host. Unless specified otherwise, this defaults to
`identity[.pub]`, `id_rsa[.pub]` or `id_dsa[.pub]` files found in this same directory.

This is very useful **to use deployment keys** that grant git access to your private
repositories.

Example - a private key file in the `ssh` folder named `my_private_key` for the host
`repo.example.com` would have a `config` entry similar to the below:

```
Host repo.example.com
  IdentityFile ~/.ssh/my_private_key
```

Or you could just drop the key in `id_rsa` and `id_rsa.pub` files and it should work by
default without the need of adding a `config` file.

Host key checking is enabled by default, which means that you also need to provide a
`known_hosts` file for any repos that you wish to access via SSH.

In order to disable host key checks for a repo, your config would look something like
this:

```
Host repo.example.com
  StrictHostKeyChecking no
```

For additional information regarding this directory, take a look at this [Digital Ocean
Article][ssh-conf].

#### `/opt/odoo/custom/src`

Here you will put the actual source code for your project.

When putting code here, you can either:

- Use [`repos.yaml`][], that will fill anything at build time.
- Directly copy all there.

Recommendation: use [`repos.yaml`][] for everything except for [`private`][], and ignore
in your `.gitignore` and `.dockerignore` files every folder here except [`private`][],
with rules like these:

    odoo/custom/src/*
    !odoo/custom/src/private
    !odoo/custom/src/*.*

##### `/opt/odoo/custom/src/odoo`

**REQUIRED.** The source code for your odoo project.

You can choose your Odoo version, and even merge PRs from many of them using
[`repos.yaml`][]. Some versions you might consider:

- [Original Odoo][], by [Odoo S.A.][].

- [OCB][] (Odoo Community Backports), by [OCA][]. The original + some features - some
  stability strictness.

- [OpenUpgrade][], by [OCA][]. The original, frozen at new version launch time +
  migration scripts.

##### `/opt/odoo/custom/src/private`

**REQUIRED.** Folder with private addons for the project.

##### `/opt/odoo/custom/src/repos.yaml`

A [git-aggregator](#git-aggregator) configuration file.

It should look similar to this:

```yaml
# Odoo must be in the `odoo` folder for Doodba to work
odoo:
  defaults:
    # This will use git shallow clones.
    # $DEPTH_DEFAULT is 1 in test and prod, but 100 in devel.
    # $DEPTH_MERGE is always 100.
    # You can use any integer value, OTOH.
    depth: $DEPTH_MERGE
  remotes:
    origin: https://github.com/OCA/OCB.git
    odoo: https://github.com/odoo/odoo.git
    openupgrade: https://github.com/OCA/OpenUpgrade.git
  # $ODOO_VERSION is... the Odoo version! "11.0" or similar
  target: origin $ODOO_VERSION
  merges:
    - origin $ODOO_VERSION
    - odoo refs/pull/25594/head # Expose `Field` from search_filters.js

web:
  defaults:
    depth: $DEPTH_MERGE
  remotes:
    origin: https://github.com/OCA/web.git
    tecnativa: https://github.com/Tecnativa/partner-contact.git
  target: origin $ODOO_VERSION
  merges:
    - origin $ODOO_VERSION
    - origin refs/pull/1007/head # web_responsive search
    - tecnativa 11.0-some_addon-custom # Branch for this customer only
```

###### Automatic download of repos

Doodba is smart enough to download automatically git repositories even if they are
missing in `repos.yaml`. It will happen if it is used in [`addons.yaml`][], except for
the special [`private`][] repo. This will help you keep your deployment definitions DRY.

You can configure this behavior with these environment variables (default values shown):

- `DEFAULT_REPO_PATTERN="https://github.com/OCA/{}.git"`
- `DEFAULT_REPO_PATTERN_ODOO="https://github.com/OCA/OCB.git"`

As you probably guessed, we use something like `str.format(repo_basename)` on top of
those variables to compute the default remote origin. If, i.e., you want to use your own
repositories as default remotes, just add these build arguments to your
`docker-compose.yaml` file:

```yaml
# [...]
services:
  odoo:
    build:
      args:
        DEFAULT_REPO_PATTERN: &origin "https://github.com/Tecnativa/{}.git"
        DEFAULT_REPO_PATTERN_ODOO: *origin
# [...]
```

So, for example, if your [`repos.yaml`][] file is empty and your [`addons.yaml`][]
contains this:

```yaml
server-tools:
  - module_auto_update
```

A `/opt/odoo/auto/repos.yaml` file with this will be generated and used to download git
code:

```yaml
/opt/odoo/custom/src/odoo:
  defaults:
    depth: $DEPTH_DEFAULT
  remotes:
    origin: https://github.com/OCA/OCB.git
  target: origin $ODOO_VERSION
  merges:
    - origin $ODOO_VERSION
/opt/odoo/custom/src/server-tools:
  defaults:
    depth: $DEPTH_DEFAULT
  remotes:
    origin: https://github.com/OCA/server-tools.git
  target: origin $ODOO_VERSION
  merges:
    - origin $ODOO_VERSION
```

All of this means that, you only need to define the git aggregator spec in
[`repos.yaml`][] if anything diverges from the standard:

- You need special merges.
- You need a special origin.
- The folder name does not match the origin pattern.
- The branch name does not match `$ODOO_VERSION`.
- Etc.

##### `/opt/odoo/custom/src/addons.yaml`

One entry per repo and addon you want to activate in your project. Like this:

```yaml
website:
  - website_cookie_notice
  - website_legal_page
web:
  - web_responsive
```

Advanced features:

- You can bundle [several YAML documents][] if you want to logically group your addons
  and some repos are repeated among groups, by separating each document with `---`.

- Addons under `private` and `odoo/addons` are linked automatically unless you specify
  them.

- You can use `ONLY` to supply a dictionary of environment variables and a list of
  possible values to enable that document in the matching environments.

- You can use `ENV` to supply a dictionary of environment variables to be used on
  downloading repositories. Following variables are supported:

  - `DEFAULT_REPO_PATTERN`
  - `DEFAULT_REPO_PATTERN_ODOO`
  - `DEPTH_DEFAULT`
  - `ODOO_VERSION` - can be used as repository branch

- If an addon is found in several places at the same time, it will get linked according
  to this priority table:

  1. Addons in [`private`][].
  2. Addons in other repositories (in case one is matched in several, it will be random,
     BEWARE!). Better have no duplicated names if possible.
  3. Core Odoo addons from [`odoo/addons`][`odoo`].

- If an addon is specified but not available at runtime, it will fail silently.

- You can use any wildcards supported by [Python's glob module][glob].

This example shows these advanced features:

```yaml
# Spanish Localization
l10n-spain:
  - l10n_es # Overrides built-in l10n_es under odoo/addons
server-tools:
  - "*date*" # All modules that contain "date" in their name
  - auditlog
web:
  - "*" # All web addons
---
# Different YAML document to separate SEO Tools
website:
  - website_blog_excertp_img
server-tools: # Here we repeat server-tools, but no problem because it's a
  # different document
  - html_image_url_extractor
  - html_text
---
# Enable demo ribbon only for devel and test environments
ONLY:
  PGDATABASE: # This environment variable must exist and be in the list
    - devel
    - test
web:
  - web_environment_ribbon
---
# Enable special authentication methods only in production environment
ONLY:
  PGDATABASE:
    - prod
server-tools:
  - auth_*
---
# Custom repositories
ENV:
  DEFAULT_REPO_PATTERN: https://github.com/Tecnativa/{}.git
  ODOO_VERSION: 13.0-new-feature
some-repo: # Cloned from https://github.com/Tecnativa/some-repo.git branch 13.0-new-feature
  - some_custom_module
```

##### `/opt/odoo/custom/dependencies/*.txt`

Files to indicate dependencies of your subimage, one for each of the supported package
managers:

- `apt_build.txt`: build-time dependencies, installed before any others and removed
  after all the others too. Usually these would include Debian packages such as
  `build-essential` or `python-dev`. From Doodba 11.0, this is most likely not needed,
  as build dependencies are shipped with the image, and local python develpment headers
  should be used instead of those downloaded from apt.
- `apt.txt`: run-time dependencies installed by apt.
- `gem.txt`: run-time dependencies installed by gem.
- `npm.txt`: run-time dependencies installed by npm.
- `pip.txt`: a normal [pip `requirements.txt`][] file, for run-time dependencies too. It
  will get executed with `--update` flag, just in case you want to overwrite any of the
  pre-bundled dependencies.

### `/opt/odoo/common`: The useful one

This folder is full of magic. I'll document it some day. For now, just look at the code.

Only some notes:

- Will compile your code with [`PYTHONOPTIMIZE=1`][] by default.

- Will remove all code not used from the image by default (not listed in
  `/opt/odoo/custom/src/addons.yaml`), to keep it thin.

### `/opt/odoo/auto`: The automatic one

This directory will have things that are automatically generated at build time.

#### `/opt/odoo/auto/addons`

It will be full of symlinks to the addons you selected in [`addons.yaml`][].

#### `/opt/odoo/auto/odoo.conf`

It will have the result of merging all configurations under
`/opt/odoo/{common,custom}/conf.d/`, in that order.

## The `Dockerfile`

I will document all build arguments and environment variables some day, but for now keep
this in mind:

- This is just a base image, full of tools. **You need to build your project subimage**
  from this one, even if your project's `Dockerfile` only contains these 2 lines:

      FROM tecnativa/doodba
      MAINTAINER Me <me@example.com>

- The above sentence becomes true because we have a lot of `ONBUILD` sentences here, so
  at least **your project must have a `./custom` folder** along with its `Dockerfile`
  for it to work.

- All should be magic if you adhere to our opinions here. Just put the code where it
  should go, and relax.

## Bundled tools

There is a good collections of tools available in the image that help dealing with Odoo
and its peculiarities:

### `addons`

A handy CLI tool to automate addon management based on the current environment. It
allows you to install, update, test and/or list private, extra and/or core addons
available to current container, based on current [`addons.yaml`][] configuration.

Call `addons --help` for usage instructions.

### `click-odoo` and related scripts

The great [`click-odoo`][] scripting framework and the collection of scripts found in
[`click-odoo-contrib`][] are included. Refer to their sites to know how to use them.

\* Note: This replaces the deprecated `python-odoo-shell` binary.

### [`nano`](https://www.nano-editor.org/)

The CLI text editor we all know, just in case you need to inspect some bug in hot
deployments.

### `log`

Just a little shell script that you can use to add logs to your build or entrypoint
scripts:

    log INFO I'm informing

### `pot`

Little shell shortcut for exporting a translation template from any addon(s). Usage:

    pot my_addon,my_other_addon

### [`psql`](https://www.postgresql.org/docs/current/app-psql.html)

Environment variables are there so that if you need to connect with the database, you
just need to execute:

    docker-compose run -l traefik.enable=false --rm odoo psql

The same is true for any other [Postgres client applications][].

### [`ptvsd`](https://github.com/DonJayamanne/pythonVSCode)

[VSCode][] debugger. If you use this editor with its python module, you will find it
useful.

To debug at a certain point of the code, add this Python code somewhere:

```python
import ptvsd
ptvsd.enable_attach("doodba-rocks", address=("0.0.0.0", 6899))
print("ptvsd waiting...")
ptvsd.wait_for_attach()
```

To start Odoo within a ptvsd environment, which will obey the breakpoints established in
your IDE (but will work slowly), just add `-e PTVSD_ENABLE=1` to your odoo container.

If you use the official [scaffolding][], you can boot it in ptvsd mode with:

```bash
export DOODBA_PTVSD_ENABLE=1
docker-compose -f docker-compose.yaml -f devel.yaml up -d
```

Of course, you need to have properly configured your [VSCode][]. To do so, make sure in
your project there is a `.vscode/launch.json` file with these minimal contents:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Attach to debug in devel.yaml",
      "type": "python",
      "request": "attach",
      "pathMappings": [
        {
          "localRoot": "${workspaceRoot}/odoo",
          "remoteRoot": "/opt/odoo"
        }
      ],
      "port": 6899,
      "host": "localhost"
    }
  ]
}
```

Then, execute that configuration as usual.

### [`pudb`](https://github.com/inducer/pudb)

This is another great debugger that includes remote debugging via telnet, which can be
useful for some cases, or for people that prefer it over [wdb](#wdb).

To use it, inject this in any Python script:

```python
import pudb.remote
pudb.remote.set_trace(term_size=(80, 24))
```

Then open a telnet connection to it (running in `0.0.0.0:6899` by default).

It is safe to use in [production][] environments **if you know what you are doing and do
not expose the debugging port to attackers**. Usage:

    docker-compose exec odoo telnet localhost 6899

### [`git-aggregator`](https://pypi.python.org/pypi/git-aggregator)

We found this one to be the most useful tool for downlading code, merging it and placing
it somewhere.

### `autoaggregate`

This little script wraps `git-aggregator` to make it work fine and automatically with
this image. Used in the [scaffolding][]'s `setup-devel.yaml` step.

#### Example `repos.yaml` file

This [`repos.yaml`][] example merges [several sources][`odoo`]:

```yaml
./odoo:
  defaults:
    # Shallow repositores are faster & thinner. You better use
    # $DEPTH_DEFAULT here when you need no merges.
    depth: $DEPTH_MERGE
  remotes:
    ocb: https://github.com/OCA/OCB.git
    odoo: https://github.com/odoo/odoo.git
  target: ocb $ODOO_VERSION
  merges:
    - ocb $ODOO_VERSION
    - odoo refs/pull/13635/head
  shell_command_after:
    # Useful to merge a diff when there's no git history correlation
    - curl -sSL https://github.com/odoo/odoo/pull/37187.diff | patch -fp1
```

### [`odoo`](https://www.odoo.com/documentation/10.0/reference/cmdline.html)

We set an `$OPENERP_SERVER` environment variable pointing to
[the autogenerated configuration file](#optodooautoodooconf) so you don't have to worry
about it. Just execute `odoo` and it will work fine.

Note that version 9.0 has an `odoo` binary to provide forward compatibility (but it has
the `odoo.py` one too).

### GeoLite2

To enable geoip support for Odoo you need to signup for a Maxmind account for GeoLite2:
https://www.maxmind.com/en/geolite2/signup

Create a license key in your maxmind account and provide your account id and license key
on build to the scaffolding.

The `GEOIP_ACCOUNT_ID` environment variable should hold the account id and
`GEOIP_LICENSE_KEY` the license key. Both are visible on the "My License Key" page under
your [account](https://www.maxmind.com/en/account) when you create the license key.

Example config (docker-compose.yml)

```yaml
services:
  odoo:
    environment:
      ...
      # This product includes GeoLite2 data created by MaxMind, available from https://www.maxmind.com
      GEOIP_ACCOUNT_ID: 1234
      GEOIP_LICENSE_KEY: aBcDeF
  ...
```

When booting you should see a message `Activating GeoIP/GeoLite2 updates`.

Upon (re)start the container will perform the updates as requested by the
[eula](https://www.maxmind.com/en/geolite2/eula). You also can update the database by
calling `geoipupdate` inside the running container.

When you run geoip in an isolated environment (odoo is only able to access whitelisted
addresses) make sure odoo is able to access `updates.maxmind.com`. You could do so by
adding the whitelist proxy like this to your docker-compose.yml:

```yaml
    odoo:
        ...
        depends_on:
            ...
            - maxmind_proxy
            ...
        ...
    ...

    maxmind_proxy:
        image: tecnativa/whitelist
        networks:
            default:
                aliases:
                    - updates.maxmind.com
            public:
        environment:
            TARGET: updates.maxmind.com
            PRE_RESOLVE: 1
    ...

```

## Scaffolding

Get up and running quickly with the provided
[scaffolding](https://github.com/Tecnativa/doodba-scaffolding).

### Skip the boring parts

You will need these tools, so install them locally (and learn how to use them, check
their docs, Doodba is not the place to learn them 😉):

- [Git](https://git-scm.com/do)
- [Docker Engine](https://www.docker.com/products/docker-engine) (running locally)
- [Docker Compose](https://docs.docker.com/compose/overview/)

Then run these Bash commands:

```bash
git clone https://github.com/Tecnativa/doodba-scaffolding.git myproject
cd myproject
ln -s devel.yaml docker-compose.override.yml
chmod -R ug+rwX odoo/auto
export UID GID="$(id -g $USER)" UMASK="$(umask)"
docker-compose build --pull
docker-compose -f setup-devel.yaml run --rm odoo
docker-compose up
```

And if you don't want to have a chance to do a `git pull` and get possible future
scaffolding updates merged in your project's `git log`:

```bash
rm -Rf .git
git init
```

### Tell me the boring parts

The scaffolding provides you a boilerplate-ready project to start developing Odoo in no
time.

#### Environments

This scaffolding comes with some environment configurations, ready for you to extend
them. Each of them is a
[Docker Compose file](https://docs.docker.com/compose/compose-file/) almost ready to
work out of the box (or almost), but that will assume that you understand it and will
modify it.

After you clone the scaffolding, **search for `XXX` comments**, they will help you on
making it work.

##### Development

Set it up with:

    export UID GID="$(id -g $USER)" UMASK="$(umask)"
    docker-compose -f setup-devel.yaml run --rm odoo

Once finished, you can start using Odoo with:

    docker-compose -f docker-compose.yaml -f devel.yaml up --build

This allows you to track only what Git needs to track and provides faster Docker builds.

You might consider adding this line to your `~/.bashrc`:

    export UID GID="$(id -g $USER)" UMASK="$(umask)"

To browse Odoo go to `http://localhost:${ODOO_MAJOR}069` (i.e. for Odoo 11.0 this would
be `http://localhost:11069`).

This environment has several special features:

###### [`wdb`](https://github.com/Kozea/wdb/)

This is one of the greatest Python debugger available, and even more for Docker-based
development, so here you have it preinstalled.

I told you, this image is opinionated. :wink:

To use it, write this in any Python script:

```python
import wdb
wdb.set_trace()
```

It's available by default on the [development][] environment, where you can browse
http://localhost:1984 to use it.

**DO NOT USE IT IN PRODUCTION ENVIRONMENTS.** (I had to say it).

###### [MailHog](https://github.com/mailhog/MailHog)

It provides a fake SMTP server that intercepts all mail sent by Odoo and displays a
simple interface that lets you see and debug all that mail comfortably, including
headers sent, attachments, etc.

- For [development][], it's in http://localhost:8025
- For [testing][], it's in http://$DOMAIN_TEST/smtpfake/
- For [production][], it's not used.

All environments are configured by default to use the bundled SMTP relay. They are
configured by these environment variables:

- `SMTP_SERVER`
- `SMTP_PORT`
- `SMTP_USER`
- `SMTP_PASSWORD`
- `SMTP_SSL`
- `EMAIL_FROM`

For them to be useful, you need to remove any `ir.mail_server` records in your database.

###### Network isolation

The Docker network is in `--internal` mode, which means that it has no access to the
Internet. This feature protects you in cases where a [production][] database is restored
and Odoo tries to connect to SMTP/IMAP/POP3 servers to send or receive emails. Also when
you are using [connectors](https://github.com/OCA/connector),
[mail trackers](https://www.odoo.com/apps/modules/browse?search=mail_tracking) or any
API sync/calls.

If you still need to have public access, set `internal: false` in the environment file,
detach all containers from that network, remove the network, reatach all containers to
it, and possibly restart them. You can also just do:

    docker-compose down
    docker-compose up -d

Usually a better option is
[whitelisting](#how-can-i-whitelist-a-service-and-allow-external-access-to-it).

##### Production

This environment is just a template. **It is not production-ready**. You must change
many things inside it, it's just a guideline.

It includes pluggable `smtp` and `backup` services.

###### Adding secrets

Before booting this environment, you need to create a few files, which are excluded in
Git and contain some secrets, needed to make this environment safe:

- `./.docker/odoo.env` must define `ADMIN_PASSWORD`.
- `./.docker/db-access.env` must define `PGPASSWORD`.
- `./.docker/db-creation.env` must define `POSTGRES_PASSWORD` (must be equal to
  `PGPASSWORD` above).
- `./.docker/smtp.env` must define `RELAY_PASSWORD` (password to access the real SMTP
  relay).
- `./.docker/backup.env` must define `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`
  (obtained from S3 provider) and `PASSPHRASE` (to encrypt backup archives).

###### Global inverse proxy

For [production][] and [testing][] templates to work fine, you need to have a working
[Traefik][] inverse proxy in each node.

To have it, use this `inverseproxy.yaml` file:

```yaml
version: "2.1"

services:
  proxy:
    image: traefik:1.6-alpine
    networks:
      shared:
      private:
      public:
    volumes:
      - acme:/etc/traefik/acme:rw,Z
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - dockersocket
    restart: unless-stopped
    privileged: true
    tty: true
    command:
      - --ACME.ACMELogging
      - --ACME.Email=you@example.com
      - --ACME.EntryPoint=https
      - --ACME.HTTPChallenge.entryPoint=http
      - --ACME.OnHostRule
      - --ACME.Storage=/etc/traefik/acme/acme.json
      - --DefaultEntryPoints=http,https
      - --EntryPoints=Name:http Address::80 Redirect.EntryPoint:https
      - --EntryPoints=Name:https Address::443 TLS
      - --LogLevel=INFO
      - --Docker
      - --Docker.EndPoint=http://dockersocket:2375
      - --Docker.ExposedByDefault=false
      - --Docker.Watch

  dockersocket:
    image: tecnativa/docker-socket-proxy
    privileged: true
    networks:
      private:
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      CONTAINERS: 1
      NETWORKS: 1
      SERVICES: 1
      SWARM: 1
      TASKS: 1
    restart: unless-stopped

networks:
  shared:
    internal: true
    driver_opts:
      encrypted: 1

  private:
    internal: true
    driver_opts:
      encrypted: 1

  public:

volumes:
  acme:
```

Then boot it up with:

    docker-compose -p inverseproxy -f inverseproxy.yaml up -d

This will intercept all requests coming from port 80 (`http`) and redirect them to port
443 (`https`), it will download and install required SSL certificates from [Let's
Encrypt][] whenever you boot a new [production][] instance, add the required proxy
headers to the request, and then redirect all traffic to/from odoo automatically.

It includes [a security-enhaced proxy][docker-socket-proxy] to reduce attack surface
when listening to the Docker socket.

This allows you to:

- Have multiple domains for each Odoo instance.
- Have multiple Odoo instances in each node.
- Add an SSL layer automatically and for free.

###### Booting production

Once you fixed everything needed and started
[global inverse proxy](#global-inverse-proxy), run the production environment with:

    docker-compose -f docker-compose.yaml -f prod.yaml up --build --remove-orphans

###### Backups

Backups are only available in the production environment. They are provided by
[tecnativa/duplicity:postgres-s3](https://github.com/Tecnativa/docker-duplicity). The
structure of the backed up folder:

```
├── prod.sql
└── odoo/
    ├── addons/
    └── filestore/
        └── prod/
            ├── ...
            └── ...
```

To make backup immediatly execute following command:

```sh
# Executes all jobs scheduled for daily run.
# With default configuration it's equal to making full backup
docker-compose exec backup /etc/periodic/daily/jobrunner
```

To restore backup:

```sh
# stop odoo if it's running
docker-compose stop odoo

# start backup and db
docker-compose up -d backup

# switch to some version
docker-compose exec backup restore --time TIME_IN_BACKUP_NAME --force

# ⚠️ DELETE PRODUCTION database
#docker-compose backup dropdb

# create new empty database
docker-compose exec backup createdb

# restore database
docker-compose exec backup sh -c 'psql -f $SRC/$PGDATABASE.sql'

# start odoo
docker-compose up -d
```

##### Testing

A good rule of thumb is test in testing before uploading to production, so this
environment tries to imitate the [production][] one in everything, but _removing
possible pollution points_:

- It has a fake `smtp` service based on [MailHog][].

- It has no `backup` service.

- It is [isolated](#network-isolation).

To use it, you need to [add secrets files just like for production](#adding-secrets),
although secrets for smtp and backup containers are not needed because those don't exist
here. Also, start [global inverse proxy](#global-inverse-proxy) before running the test
environment.

Test it in your machine with:

    docker-compose -f docker-compose.yaml -f test.yaml up --build

###### Global whitelist

Since the testing environment is [network-isolated](#network-isolation), this can change
some deadlocks or big timeouts in code chunks that are not ready for such situation.
Odoo happens to have some of them.

The [development][] environment includes the default recommended whitelist proxies, but
for [testing][], it is recommended to have a separate docker compose project running
along in the same server that provides a `globalwhitelist_default` network where all
whitelist proxies exist. This is a better practice for a testing environment where many
services might coexist, because it will let you save lots of processing power and IP
addresses.

The recommended `globalwhitelist/docker-compose.yaml` file should contain:

```yaml
version: "2.1"

networks:
  public:
    driver_opts:
      encrypted: 1
  shared:
    internal: true
    driver_opts:
      encrypted: 1

services:
  cdnjs_cloudflare_com:
    image: tecnativa/whitelist
    restart: unless-stopped
    networks:
      public:
      shared:
        aliases:
          - "cdnjs.cloudflare.com"
    environment:
      TARGET: "cdnjs.cloudflare.com"
      PRE_RESOLVE: 1

  fonts_googleapis_com:
    image: tecnativa/whitelist
    restart: unless-stopped
    networks:
      public:
      shared:
        aliases:
          - "fonts.googleapis.com"
    environment:
      TARGET: "fonts.googleapis.com"
      PRE_RESOLVE: 1

  fonts_gstatic_com:
    image: tecnativa/whitelist
    restart: unless-stopped
    networks:
      public:
      shared:
        aliases:
          - "fonts.gstatic.com"
    environment:
      TARGET: "fonts.gstatic.com"
      PRE_RESOLVE: 1

  www_google_com:
    image: tecnativa/whitelist
    restart: unless-stopped
    networks:
      public:
      shared:
        aliases:
          - "www.google.com"
    environment:
      TARGET: "www.google.com"
      PRE_RESOLVE: 1

  www_gravatar_com:
    image: tecnativa/whitelist
    restart: unless-stopped
    networks:
      public:
      shared:
        aliases:
          - "www.gravatar.com"
    environment:
      TARGET: "www.gravatar.com"
      PRE_RESOLVE: 1

  updates_maxmind_com:
    image: tecnativa/whitelist
    restart: unless-stopped
    networks:
      public:
      shared:
        aliases:
          - "updates.maxmind.com"
    environment:
      TARGET: "updates.maxmind.com"
      PRE_RESOLVE: 1
```

#### Other usage scenarios

In examples below I will skip the `-f docker-compose.yaml -f <environment>.yaml` part
and assume you know which environment you want to use.

Also, we recommend to use `run` subcommand to create a new container with same settings
and volumes. Sometimes you may prefer to use `exec` instead, to execute an arbitrary
command in a running container.

##### Inspect the database

    docker-compose run --rm odoo psql

##### Restart Odoo

You will need to restart it whenever any Python code changes, so to do that:

    docker-compose restart odoo

In development mode odoo restarts by itself thanks to `--dev=reload` option.

##### Run unit tests for some addon

```bash
modules=addon1,addon2
# Install their dependencies first
docker-compose run --rm odoo addons init --dependencies --with $modules
# Test them at install
docker-compose run --rm odoo addons init --test --with $modules
# Test them again at update
docker-compose run --rm odoo addons update --test --with $modules
```

\* Note: This replaces the old deprecated `unittest` script.

##### Reading the logs

For all services in the environment:

    docker-compose logs -f --tail 10

Only Odoo's:

    docker-compose logs -f --tail 10 odoo

##### Install some addon without stopping current running process

    docker-compose run --rm odoo odoo -i addon1,addon2 --stop-after-init

##### Update some addon without stopping current running process

    docker-compose run --rm odoo odoo -u addon1,addon2 --stop-after-init

##### Update changed addons only

Just run:

```bash
docker-compose run --rm odoo click-odoo-update --watcher-max-seconds 30
```

This script is part of [`click-odoo-contrib`][]; check it for more details.

\* Note: `--watcher-max-seconds` is available because we ship a
[patched](https://github.com/acsone/click-odoo-contrib/pull/38) version. Check that PR
for docs.

\* Note: This replaces the old deprecated `autoupdate` script.

##### Export some addon's translations to stdout

    docker-compose run --rm odoo pot addon1[,addon2]

Now copy the relevant parts to your `addon1.pot` file.

##### Open an odoo shell

    docker-compose run --rm odoo odoo shell

##### Open another UI instance linked to same filestore and database

    docker-compose run --rm -p 127.0.0.1:$SomeFreePort:8069 odoo

Then open `http://localhost:$SomeFreePort`.

## FAQ

### Will there be not retrocompatible changes on the image?

This image is production-ready, but it is constantly evolving too, so some new features
can break some old ones, or conflict with them, and some old features might get
deprecated and removed at some point.

The best you can do is to [subscribe to the compatibility breakage announcements
issue][retrobreak].

### How to have good QA and test in my CI with Doodba?

Inside this image, there's the `/qa` folder, which provides some necessary plumbing to
perform quality assurance and continous integration if you use [doodba-qa][], which is a
separate (but related) project with that purpose.

Go there to get more instructions.

### I need to force addition or removal of `www.` prefix in production

These instructions assume you use the official [scaffolding][]. To **remove** the `www.`
prefix, set these params in the `.env` file:

    DOMAIN_PROD=example.com
    DOMAIN_PROD_ALT=www.example.com

To **add** the `www.` prefix, it is almost the same:

    DOMAIN_PROD=www.example.com
    DOMAIN_PROD_ALT=example.com

Of course, both domains should point to the same machine before booting, or Let's
Encrypt might ban your server for some time.

### How to run a parallel Odoo container without crashing Traefik?

Just run it in this fashion:

```bash
docker-compose run --rm -l traefik.enable=false odoo bash
```

With that label, Traefik will ignore that container.

### How to allow access from several host names?

In `.env`, set `DOMAIN_PROD` to `host1.com,host2.com,www.host1.com`, etc.

### How to choose initial DB creation language?

This image includes a hack that will set the initial language to load when Odoo creates
its database for the first time. These conditions must match:

- `$PGDATABASE` is set.
- That database does not yet exist.
- `$INITIAL_LANG` is set to any Odoo lang code. I.e. `es_ES`.
- Odoo is booted.

### I use Fish shell, how to export needed variables?

In [Fish][] you need to do following:

    set -x UID (id -u $USER)
    set -x GID (id -g $USER)
    set -x UMASK (umask)

You can make those variables universal (available in all terminals you open from now on)
by using `set -Ux` instead of `set -x`.

### When I boot `devel.yaml` for the first time, Odoo crashes

Most likely you are using versions `8.0` or `9.0` of the image. If so:

1. Edit `devel.yaml`.
2. Search for the line that starts with `command:` in the `odoo` service.
3. Change it for a command that actually works with your version:
   - `odoo --workers 0` for Odoo 8.0.
   - `odoo --workers 0 --dev` for Odoo 9.0.

### How can I run a Posbox/IoT box service for development?

Posbox has special needs that are not useful for most projects, and is quite tightly
related to specific hardware and peripherals, so it makes not much sense to ship it by
default in Doodba and its [scaffolding][].

However, for testing connection issues, developing, etc., you might want to boot a
resource-limited posbox instance imitation.

The best you can do is buy a Posbox/IoT box and peripherals and use it, but for quick
tests that do not involve specific hardware, you can boot it with Doodba by:

- Add the `apt` dependency `usbutils` (which contains `lsusb` binary).
- Add the `pip` dependencies `evdev` and `netifaces`.
- Add a `posbox` container, which:
  - Can read usb devices, privileged.
  - Loads at boot all required `hw_*` addons, except for `hw_posbox_upgrade`.
  - Exposes a port that doesn't conflict with Odoo, such as `8070` i.e.

<details>
<summary>Example patch for official scaffolding</summary>

```diff
diff --git a/devel.yaml b/devel.yaml
index e029d48..2f800de 100644
--- a/devel.yaml
+++ b/devel.yaml
@@ -15,7 +15,7 @@ services:
             PORT: "6899 8069"
             TARGET: odoo

-    odoo:
+    odoo: &odoo
         extends:
             file: common.yaml
             service: odoo
@@ -53,6 +53,21 @@ services:
             # XXX Odoo v8 has no `--dev` mode; Odoo v9 has no parameters
             - --dev=reload,qweb,werkzeug,xml

+    posbox:
+        <<: *odoo
+        ports:
+            - "127.0.0.1:8070:8069"
+        privileged: true
+        networks: *public
+        volumes:
+            - ./odoo/custom:/opt/odoo/custom:ro,z
+            - ./odoo/auto/addons:/opt/odoo/auto/addons:rw,z
+            - /dev/bus/usb
+        command:
+            - odoo
+            - --workers=0
+            - --load=web,hw_proxy,hw_posbox_homepage,hw_scale,hw_scanner,hw_escpos,hw_blackbox_be,hw_screen
+
     db:
         extends:
             file: common.yaml
diff --git a/odoo/custom/dependencies/apt.txt b/odoo/custom/dependencies/apt.txt
index 8b13789..e32891b 100644
--- a/odoo/custom/dependencies/apt.txt
+++ b/odoo/custom/dependencies/apt.txt
@@ -1 +1 @@
+usbutils
diff --git a/odoo/custom/dependencies/pip.txt b/odoo/custom/dependencies/pip.txt
index e69de29..6eef737 100644
--- a/odoo/custom/dependencies/pip.txt
+++ b/odoo/custom/dependencies/pip.txt
@@ -0,0 +1,2 @@
+evdev
+netifaces
```

</details>

Once you apply those changes, to use it:

1. `docker-compose build` to install the new dependencies.
1. `docker-compose up -d` to start all services.
1. Visit `http://localhost:8070` to see the posbox running.
1. Visit `http://localhost:${ODOO_MAJOR}069` to see Odoo.
1. Install `point_of_sale` in Odoo.
1. Configure the POS in Odoo to connect to Posbox in `localhost:8070`.

Of course this won't be fully functional, but it will give you an overview on the posbox
stuff.

[Beware about possible mixed content errors][mixed-content-posbox].

### This project is too opinionated, but can I question any of those opinions?

Of course. There's no guarantee that we will like it, but please do it. :wink:

### What's this `hooks` folder here?

It runs triggers when doing the automatic build in the Docker Hub.
[Check this](https://hub.docker.com/r/thibaultdelor/testautobuildhooks/).

### Can I have my own scaffolding?

You probably **should**, and rebase on our updates. However, if you are planning on a
general update to it that you find interesting for the general-purpose one, please send
us a pull request.

### Can I skip the `-f docker-compose.yaml -f <environment>.yaml` part for `docker-compose` commands?

Let's suppose you want to use [`test.yaml`][testing] environment by default, no matter
where you clone the project:

    ln -s test.yaml docker-compose.override.yaml
    git add docker-compose.override.yaml
    git commit

Let's suppose you only want to use `devel.yaml` in your local development machine by
default:

    ln -s devel.yaml docker-compose.override.yml

Notice the difference in the prefix (`.yaml` vs. `.yml`). Docker Compose will use the
`.yml` one if both are found, so that's the one we considered you should use in your
local clones, and that's the one that will be git-ignored by default by the scaffolding
`.gitignore` file.

As a design choice, the scaffolding defaults to being explicit.

### How can I pin an image version?

Version-pinning is a good idea to keep your code from differing among image updates.
It's the best way to ensure no updates got in between the last time you checked the
image and the time you deploy it to production.

You can do it through **its sha256 code**.

Get any image's code through inspect, running from a computer where the correct image
version is downloaded:

    docker image inspect --format='{{.RepoDigests}}' tecnativa/doodba:10.0-onbuild

Alternatively, you can browse [this image's builds][builds], click on the one you know
it works fine for you, and search for the `digest` word using your browser's _search in
page_ system (Ctrl+F usually).

You will find lines similar to:

    [...]
    10.0: digest: sha256:fba69478f9b0616561aa3aba4d18e4bcc2f728c9568057946c98d5d3817699e1 size: 4508
    [...]
    8.0: digest: sha256:27a3dd3a32ce6c4c259b4a184d8db0c6d94415696bec6c2668caafe755c6445e size: 4508
    [...]
    9.0: digest: sha256:33a540eca6441b950d633d3edc77d2cc46586717410f03d51c054ce348b2e977 size: 4508
    [...]

Once you find them, you can use that pinned version in your builds, using a Dockerfile
similar to this one:

```Dockerfile
# Hash-pinned version of tecnativa/doodba:10.0-onbuild
FROM tecnativa/doodba@sha256:fba69478f9b0616561aa3aba4d18e4bcc2f728c9568057946c98d5d3817699e1
```

### How to get proper assets when printing reports?

Make sure there's a `ir.config_parameter` called `report.url` with the value
`http://localhost:8069`.

### How to change report fonts?

Doodba ships [Liberation fonts](https://wikipedia.org/wiki/Liberation_fonts) as
defaults.

If you want to make another font package _available_, just add it to
[`apt.txt`][dependencies] (if it's a normal Debian package) or install it in a [custom
build script][build.d] called i.e. `build.d/200-custom-fonts` (if you need to install it
in a more complex way).

If, in addition to that, you want those fonts to be the _defaults_, then add one (or
more) of these build arguments:

- `FONT_MONO`
- `FONT_SANS`
- `FONT_SERIF`

### How can I whitelist a service and allow external access to it?

This can become useful when you have isolated environments (like in `devel.yaml` and
`test.yaml` by default) but you need to allow some external API access for them. I.e.,
you could use Google Fonts API for your customer's reports, and those reports would take
forever and end up rendering badly in staging environments.

In such case, we recommend using the
[tecnativa/whitelist](https://hub.docker.com/r/tecnativa/whitelist/) image. Read its
docs there.

### How can I help?

Just [head to our project](https://github.com/Tecnativa/doodba) and open an issue or
pull request.

If you plan to open a pull request, remember that you will usually have to open two of
them:

1. Targeting the `master` branch, from which the main images are built. This pull
   request must include tests.
2. Targeting the `scaffolding` branch, which serves as the base for projects using this
   base image. This one is not always required.

If you need to add a feature or fix for `scaffolding`, before merging that PR, we need
tests that ensure that backwards compatibility with previous scaffolding versions is
preserved.

## Related Projects

- [QA tools for Doodba-based projects][doodba-qa]
- [Ansible role for automated deployment / update from Le Filament](https://github.com/remi-filament/ansible_role_odoo_docker)
- Find others by searching
  [GitHub projects tagged with `#doodba`](https://github.com/topics/doodba)

[`/opt/odoo/auto/addons`]: #optodooautoaddons
[`addons.yaml`]: #optodoocustomsrcaddonsyaml
[`compose_file` environment variable]:
  https://docs.docker.com/compose/reference/envvars/#/composefile
[`odoo.conf`]: #optodooautoodooconf
[`odoo`]: #optodoocustomsrcodoo
[`private`]: #optodoocustomsrcprivate
[`pythonoptimize=1`]: https://docs.python.org/3/using/cmdline.html#envvar-PYTHONOPTIMIZE
[`repos.yaml`]: #optodoocustomsrcreposyaml
[`click-odoo`]: https://github.com/acsone/click-odoo
[`click-odoo-contrib`]: https://github.com/acsone/click-odoo-contrib
[build.d]: #optodoocustombuildd
[builds]: https://hub.docker.com/r/tecnativa/doodba/builds/
[dependencies]: #optodoocustomdependenciestxt
[development]: #development
[docker-socket-proxy]: https://hub.docker.com/r/tecnativa/docker-socket-proxy/
[doodba-qa]: https://github.com/Tecnativa/doodba-qa
[fish]: http://fishshell.com/
[glob]: https://docs.python.org/3/library/glob.html
[let's encrypt]: https://letsencrypt.org/
[mailhog]: #mailhog
[mixed-content-posbox]: https://github.com/odoo/odoo/issues/3156#issuecomment-443727760
[oca]: https://odoo-community.org/
[ocb]: https://github.com/OCA/OCB
[odoo s.a.]: https://www.odoo.com
[openupgrade]: https://github.com/OCA/OpenUpgrade/
[original odoo]: https://github.com/odoo/odoo
[pip `requirements.txt`]:
  https://pip.readthedocs.io/en/latest/user_guide/#requirements-files
[postgres client applications]:
  https://www.postgresql.org/docs/current/static/reference-client.html
[production]: #production
[retrobreak]: https://github.com/Tecnativa/doodba/issues/67
[scaffolding]: #scaffolding
[several yaml documents]: http://www.yaml.org/spec/1.2/spec.html#id2760395
[ssh-conf]:
  https://www.digitalocean.com/community/tutorials/how-to-configure-custom-connection-options-for-your-ssh-client
[testing]: #testing
[traefik]: https://traefik.io/
[vscode]: https://code.visualstudio.com/

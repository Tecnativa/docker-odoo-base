# [Doodba](https://hub.docker.com/r/tecnativa/doodba)

![ci](https://github.com/Tecnativa/doodba/workflows/ci/badge.svg)
[![](https://images.microbadger.com/badges/version/tecnativa/doodba:latest.svg)](https://microbadger.com/images/tecnativa/doodba:latest "Get your own version badge on microbadger.com")
[![](https://images.microbadger.com/badges/image/tecnativa/doodba:latest.svg)](https://microbadger.com/images/tecnativa/doodba:latest "Get your own image badge on microbadger.com")
[![](https://images.microbadger.com/badges/commit/tecnativa/doodba:latest.svg)](https://microbadger.com/images/tecnativa/doodba:latest "Get your own commit badge on microbadger.com")
[![](https://images.microbadger.com/badges/license/tecnativa/doodba.svg)](https://microbadger.com/images/tecnativa/doodba "Get your own license badge on microbadger.com")

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

You can start working with this straight away with our [template][].

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
  - [`inotify`](#inotify)
  - [`debugpy`](#debugpy)
  - [`pudb`](#pudb)
  - [`git-aggregator`](#git-aggregator)
  - [`autoaggregate`](#autoaggregate)
    - [Example `repos.yaml` file](#example-reposyaml-file)
  - [`odoo`](#odoo)
- [Subproject template](#subproject-template)
- [FAQ](#faq)
  - [Will there be not retrocompatible changes on the image?](#will-there-be-not-retrocompatible-changes-on-the-image)
  - [This project is too opinionated, but can I question any of those opinions?](#this-project-is-too-opinionated-but-can-i-question-any-of-those-opinions)
  - [What's this `hooks` folder here?](#whats-this-hooks-folder-here)
  - [How can I pin an image version?](#how-can-i-pin-an-image-version)
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
  ODOO_VERSION: 14.0-new-feature
some-repo: # Cloned from https://github.com/Tecnativa/some-repo.git branch 14.0-new-feature
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

> :warning: **Deprecated**: Configuration file is now generated via environment
variables set as such `$ODOO_CFG_{ODOO_CFG_PARAMETER}`

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

### [`inotify`](https://github.com/dsoprea/PyInotify)

Enables hot code reloading when odoo is started with `--dev` and passed `reload` or
`all` as an argument.

[copier template](https://github.com/Tecnativa/doodba-copier-template) enables this by
default in the development environment.

Doodba supports this feature under versions 11.0 and later. Check
[CLI docs](https://www.odoo.com/documentation/13.0/reference/cmdline.html#developer-features)
for details.

### [`debugpy`](https://github.com/microsoft/vscode-python)

[VSCode][] debugger. If you use this editor with its python module, you will find it
useful.

To debug at a certain point of the code, add this Python code somewhere:

```python
import debugpy
debugpy.listen(6899)
print("Waiting for debugger attach")
debugpy.wait_for_client()
debugpy.breakpoint()
print('break on this line')
```

To start Odoo within a debugpy environment, which will obey the breakpoints established
in your IDE (but will work slowly), just add `-e DEBUGPY_ENABLE=1` to your odoo
container.

If you use the official [template][], you can boot it in debugpy mode with:

```bash
export DOODBA_DEBUGPY_ENABLE=1
docker-compose -f devel.yaml up -d
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
this image. Used in the [template][]'s `setup-devel.yaml` step.

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

## Subproject template

That's a big structure! Get it up and running quickly using the
[copier template](https://github.com/Tecnativa/doodba-copier-template) we provide to
help you generate your subproject.

Check its docs to know how to use it.

## FAQ

### Will there be not retrocompatible changes on the image?

This image is production-ready, but it is constantly evolving too, so some new features
can break some old ones, or conflict with them, and some old features might get
deprecated and removed at some point.

The best you can do is to [subscribe to the compatibility breakage announcements
issue][retrobreak].

### This project is too opinionated, but can I question any of those opinions?

Of course. There's no guarantee that we will like it, but please do it. :wink:

### What's this `hooks` folder here?

It runs triggers when doing the automatic build in the Docker Hub.
[Check this](https://hub.docker.com/r/thibaultdelor/testautobuildhooks/).

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

### How can I help?

Just [head to our project](https://github.com/Tecnativa/doodba) and open a discussion,
issue or pull request.

## Related Projects

- Of course,
  [the Doodba Copier Template](https://github.com/Tecnativa/doodba-copier-template).
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
[doodba-qa]: https://github.com/Tecnativa/doodba-qa
[fish]: http://fishshell.com/
[glob]: https://docs.python.org/3/library/glob.html
[mailhog]: #mailhog
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
[template]: #subproject-template
[several yaml documents]: http://www.yaml.org/spec/1.2/spec.html#id2760395
[ssh-conf]:
  https://www.digitalocean.com/community/tutorials/how-to-configure-custom-connection-options-for-your-ssh-client
[testing]: #testing
[traefik]: https://traefik.io/
[vscode]: https://code.visualstudio.com/

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Run tests for this base image.

Each test must be a valid docker-compose.yaml file with a ``odoo`` service.
"""
import logging
import unittest
from itertools import product
from os import environ
from os.path import dirname, join
from subprocess import Popen

logging.basicConfig(level=logging.DEBUG)

DIR = dirname(__file__)
ODOO_PREFIX = ("odoo", "--stop-after-init", "--workers=0")
ODOO_VERSIONS = frozenset(environ.get("DOCKER_TAG", "11.0 12.0 13.0 14.0").split())
PG_VERSIONS = frozenset(environ.get("PG_VERSIONS", "13").split())
SCAFFOLDINGS_DIR = join(DIR, "scaffoldings")
GEIOP_CREDENTIALS_PROVIDED = environ.get("GEOIP_LICENSE_KEY", False) and environ.get(
    "GEOIP_ACCOUNT_ID", False
)

# This decorator skips tests that will fail until some branches and/or addons
# are migrated to the next release. It is used in situations where Doodba is
# preparing the pre-release for the next version of Odoo, which hasn't been
# released yet.
prerelease_skip = unittest.skipIf(
    ODOO_VERSIONS == {"14.0"}, "Tests not supported in pre-release"
)


def matrix(
    odoo=ODOO_VERSIONS, pg=PG_VERSIONS, odoo_skip=frozenset(), pg_skip=frozenset()
):
    """All possible combinations.

    We compute the variable matrix here instead of in ``.travis.yml`` because
    this generates faster builds, given the scripts found in ``hooks``
    directory are already multi-version-build aware.
    """
    return map(
        dict,
        product(
            product(("ODOO_MINOR",), ODOO_VERSIONS & odoo - odoo_skip),
            product(("DB_VERSION",), PG_VERSIONS & pg - pg_skip),
        ),
    )


class ScaffoldingCase(unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.compose_run = ("docker-compose", "run", "--rm", "odoo")

    def popen(self, *args, **kwargs):
        """Shortcut to open a subprocess and ensure it works."""
        logging.info("Subtest execution: %s", self._subtest)
        self.assertFalse(Popen(*args, **kwargs).wait())

    def compose_test(self, workdir, sub_env, *commands):
        """Execute commands in a docker-compose environment.

        :param workdir:
            Path where the docker compose commands will be executed. It should
            contain a valid ``docker-compose.yaml`` file.

        :param dict sub_env:
            Specific environment variables that will be appended to current
            ones to execute the ``docker-compose`` tests.

            You can set in this dict a ``COMPOSE_FILE`` key to choose different
            docker-compose files in the same directory.

        :param tuple()... commands:
            List of commands to be tested in the odoo container.
        """
        full_env = dict(environ, **sub_env)
        with self.subTest(PWD=workdir, **sub_env):
            try:
                self.popen(("docker-compose", "build"), cwd=workdir, env=full_env)
                for command in commands:
                    with self.subTest(command=command):
                        self.popen(
                            self.compose_run + command, cwd=workdir, env=full_env
                        )
            finally:
                self.popen(("docker-compose", "down", "-v"), cwd=workdir, env=full_env)

    def test_addons_filtered(self):
        """Test addons filtering with ``ONLY`` keyword in ``addons.yaml``."""
        project_dir = join(SCAFFOLDINGS_DIR, "dotd")
        for sub_env in matrix():
            self.compose_test(
                project_dir,
                dict(sub_env, DBNAME="prod"),
                ("test", "-e", "auto/addons/web"),
                ("test", "-e", "auto/addons/private_addon"),
                (
                    "bash",
                    "-xc",
                    'test "$(addons list -p)" == disabled_addon,private_addon',
                ),
                ("bash", "-xc", 'test "$(addons list -ip)" == private_addon'),
                ("bash", "-xc", "addons list -c | grep ,crm,"),
                # absent_addon is missing and should fail
                ("bash", "-xc", "! addons list -px"),
                # Test addon inclusion, exclusion, dependencies...
                (
                    "bash",
                    "-xc",
                    'test "$(addons list -dw private_addon)" == base,dummy_addon,website',
                ),
                (
                    "bash",
                    "-xc",
                    'test "$(addons list -dwprivate_addon -Wwebsite)" == base,dummy_addon',
                ),
                (
                    "bash",
                    "-xc",
                    'test "$(addons list -dw private_addon -W dummy_addon)" == base,website',
                ),
                ("bash", "-xc", 'test "$(addons list -nd)" == base,iap',),
                (
                    "bash",
                    "-xc",
                    'test "$(addons list --enterprise)" == make_odoo_rich',
                ),
            )
            self.compose_test(
                project_dir,
                dict(sub_env, DBNAME="limited_private"),
                ("test", "-e", "auto/addons/web"),
                ("test", "!", "-e", "auto/addons/private_addon"),
                ("bash", "-xc", 'test -z "$(addons list -p)"'),
                (
                    "bash",
                    "-xc",
                    '[ "$(addons list -s. -pwfake1 -wfake2)" == fake1.fake2 ]',
                ),
                ("bash", "-xc", "! addons list -wrepeat -Wrepeat"),
                ("bash", "-xc", "addons list -c | grep ,crm,"),
            )
            self.compose_test(
                project_dir,
                dict(sub_env, DBNAME="limited_core"),
                ("test", "!", "-e", "auto/addons/web"),
                ("test", "!", "-e", "auto/addons/private_addon"),
                ("bash", "-xc", 'test -z "$(addons list -p)"'),
                ("bash", "-xc", 'test "$(addons list -c)" == crm,sale'),
            )
            self.compose_test(
                project_dir,
                dict(sub_env, DBNAME="prod"),
                ("bash", "-xc", 'test "$(addons list -ped)" == base,web,website'),
                # ``dummy_addon`` and ``private_addon`` exist
                ("test", "-d", "auto/addons/dummy_addon"),
                ("test", "-h", "auto/addons/dummy_addon"),
                ("test", "-f", "auto/addons/dummy_addon/__init__.py"),
                ("test", "-e", "auto/addons/dummy_addon"),
                # Addon from extra repo takes higher priority than core version
                ("realpath", "auto/addons/product"),
                (
                    "bash",
                    "-xc",
                    'test "$(realpath auto/addons/product)" == '
                    "/opt/odoo/custom/src/other-doodba/odoo/src/private/product",
                ),
                ("bash", "-xc", 'test "$(addons list -e)" == dummy_addon,product'),
            )
            self.compose_test(
                project_dir,
                dict(sub_env, DBNAME="limited_private"),
                ("test", "-e", "auto/addons/dummy_addon"),
                ("bash", "-xc", 'test "$(addons list -e)" == dummy_addon,product'),
            )
            self.compose_test(
                project_dir,
                dict(sub_env, DBNAME="limited_core"),
                ("test", "-e", "auto/addons/dummy_addon"),
                (
                    "bash",
                    "-xc",
                    '[ "$(addons list -s. -pwfake1 -wfake2)" == fake1.fake2 ]',
                ),
                ("bash", "-xc", 'test "$(addons list -e)" == dummy_addon,product'),
                ("bash", "-xc", 'test "$(addons list -c)" == crm,sale'),
                ("bash", "-xc", 'test "$(addons list -cWsale)" == crm'),
            )

    @prerelease_skip
    def test_qa(self):
        """Test that QA tools are in place and work as expected."""
        folder = join(SCAFFOLDINGS_DIR, "settings")
        commands = (
            ("./custom/scripts/qa-insider-test",),
            ("/qa/node_modules/.bin/eslint", "--version"),
            ("/qa/venv/bin/flake8", "--version"),
            ("/qa/venv/bin/pylint", "--version"),
            ("/qa/venv/bin/python", "--version"),
            ("/qa/venv/bin/python", "-c", "import pylint_odoo"),
            ("test", "-d", "/qa/mqt"),
        )
        for sub_env in matrix():
            self.compose_test(folder, sub_env, *commands)

    @prerelease_skip
    def test_settings(self):
        """Test settings are filled OK"""
        folder = join(SCAFFOLDINGS_DIR, "settings")
        commands = (
            # Odoo should install
            ("--stop-after-init",),
            # Odoo settings work
            ("./custom/scripts/test_settings.py",),
        )
        if "11.0" in ODOO_VERSIONS:
            commands += (
                # Check Odoo settings using python-odoo-shell, which is available
                # only for Odoo 9-11 (for 8 too, but it had no built-in shell)
                ("./custom/scripts/test_settings_python_odoo_shell.py",),
            )
        commands += (
            # DB was created with the correct language
            (
                "bash",
                "-xc",
                """test "$(psql -Atqc "SELECT code FROM res_lang
                                    WHERE active = TRUE")" == es_ES""",
            ),
            # If `preparedb` is executed, we should have `report.url` set
            ("preparedb",),
            ("./custom/scripts/test_ir_config_parameters.py",),
        )
        for sub_env in matrix():
            self.compose_test(folder, sub_env, *commands)

    def test_smallest(self):
        """Tests for the smallest possible environment."""
        liberation = 'Liberation{0}-Regular.ttf: "Liberation {0}" "Regular"'
        commands = (
            # Must generate a configuration file
            ("test", "-f", "/opt/odoo/auto/odoo.conf"),
            ("test", "-d", "/opt/odoo/custom/src/private"),
            ("test", "-d", "/opt/odoo/custom/ssh"),
            ("addons", "list", "-cpix"),
            ("pg_activity", "--version"),
            # Default fonts must be liberation
            (
                "bash",
                "-xc",
                """test "$(fc-match monospace)" == '{}'""".format(
                    liberation.format("Mono")
                ),
            ),
            (
                "bash",
                "-xc",
                """test "$(fc-match sans-serif)" == '{}'""".format(
                    liberation.format("Sans")
                ),
            ),
            (
                "bash",
                "-xc",
                """test "$(fc-match serif)" == '{}'""".format(
                    liberation.format("Serif")
                ),
            ),
            # Must be able to install base addon
            ODOO_PREFIX + ("--init", "base"),
            # Auto updater must work
            ("click-odoo-update",),
            # Needed tools exist
            ("curl", "--version"),
            ("git", "--version"),
            ("pg_activity", "--version"),
            ("psql", "--version"),
            ("msgmerge", "--version"),
            ("ssh", "-V"),
            ("python", "-c", "import plumbum"),
            # We are able to dump
            ("pg_dump", "-f/var/lib/odoo/prod.sql", "prod"),
            # Geoip should not be activated
            ("bash", "-xc", 'test "$(which geoipupdate)" != ""'),
            ("test", "!", "-e", "/usr/share/GeoIP/GeoLite2-City.mmdb"),
            ("bash", "-xc", "! geoipupdate"),
        )
        smallest_dir = join(SCAFFOLDINGS_DIR, "smallest")
        for sub_env in matrix():
            self.compose_test(
                smallest_dir, sub_env, *commands, ("python", "-c", "import watchdog")
            )

    # HACK https://github.com/itpp-labs/misc-addons/issues/1014
    # TODO Remove decorator
    @prerelease_skip
    def test_addons_env(self):
        """Test environment variables in addons.yaml"""
        # The test is hacking ODOO_VERSION to pin a commit
        for sub_env in matrix():
            self.compose_test(
                join(SCAFFOLDINGS_DIR, "addons_env"),
                sub_env,
                # check module from custom repo pattern
                ("test", "-d", "custom/src/misc-addons"),
                ("test", "-d", "custom/src/misc-addons/web_debranding"),
                ("test", "-e", "auto/addons/web_debranding"),
                # Migrations folder is only in OpenUpgrade
                ("test", "-e", "auto/addons/crm"),
                ("test", "-d", "auto/addons/crm/migrations"),
            )

    # HACK https://github.com/itpp-labs/misc-addons/issues/1014
    # TODO Remove decorator
    @prerelease_skip
    def test_addons_env_double(self):
        """Test double addon reference in addons.yaml"""
        common_tests = (
            ("test", "-d", "custom/src/rma-old/rma"),
            ("test", "!", "-d", "custom/src/rma-old/rma_sale"),
            ("test", "-d", "custom/src/rma-new/rma"),
            ("test", "!", "-d", "custom/src/rma-new/rma_sale"),
        )
        # The test is hacking ODOO_VERSION to pin a commit
        for sub_env in matrix():
            self.compose_test(
                join(SCAFFOLDINGS_DIR, "addons_env_double"),
                dict(sub_env, DOODBA_ENVIRONMENT="test"),
                *common_tests,
                # Check version is 12.0.1.6.1
                ("grep", "-q", "12.0.1.6.1", "auto/addons/rma/__manifest__.py"),
            )
            self.compose_test(
                join(SCAFFOLDINGS_DIR, "addons_env_double"),
                dict(sub_env, DOODBA_ENVIRONMENT="prod"),
                *common_tests,
                # Check version is 12.0.2.0.0
                ("grep", "-q", "12.0.2.0.0", "auto/addons/rma/__manifest__.py"),
            )

    def test_dotd(self):
        """Test environment with common ``*.d`` directories."""
        for sub_env in matrix():
            self.compose_test(
                join(SCAFFOLDINGS_DIR, "dotd"),
                sub_env,
                # ``custom/build.d`` was properly executed
                ("test", "-f", "/home/odoo/created-at-build"),
                # ``custom/entrypoint.d`` was properly executed
                ("test", "-f", "/home/odoo/created-at-entrypoint"),
                # ``custom/conf.d`` was properly concatenated
                ("grep", "test-conf", "auto/odoo.conf"),
                # ``custom/dependencies`` were installed
                ("test", "!", "-e", "/usr/sbin/sshd"),
                ("test", "!", "-e", "/var/lib/apt/lists/lock"),
                ("busybox", "whoami"),
                ("bash", "-xc", "echo $NODE_PATH"),
                ("node", "-e", "require('test-npm-install')"),
                ("hello-world",),
                (
                    "bash",
                    "-c",
                    'test "$(hello-world)" == "this is executable hello-world"',
                ),
                ("python", "-xc", "import Crypto; print(Crypto.__version__)"),
                ("sh", "-xc", "rst2html.py --version | grep 'Docutils 0.14'"),
                # ``requirements.txt`` from addon repos were processed
                ("python", "-c", "import numpy"),
                # Local executable binaries found in $PATH
                ("sh", "-xc", "pip install --user -q flake8 && which flake8"),
                # Addon cleanup works correctly
                ("test", "!", "-e", "custom/src/private/dummy_addon"),
                ("test", "!", "-e", "custom/src/dummy_repo/dummy_link"),
                ("test", "-d", "custom/src/private/private_addon"),
                ("test", "-f", "custom/src/private/private_addon/__init__.py"),
                ("test", "-e", "auto/addons/private_addon"),
                # ``odoo`` command works
                ("odoo", "--version"),
                # Implicit ``odoo`` command also works
                ("--version",),
            )

    # TODO Remove decorator when base_search_fuzzy is migrated to 14.0
    @prerelease_skip
    def test_dependencies(self):
        """Test dependencies installation."""
        dependencies_dir = join(SCAFFOLDINGS_DIR, "dependencies")
        for sub_env in matrix():
            self.compose_test(
                dependencies_dir,
                sub_env,
                ("test", "!", "-f", "custom/dependencies/apt.txt"),
                ("test", "!", "-f", "custom/dependencies/gem.txt"),
                ("test", "!", "-f", "custom/dependencies/npm.txt"),
                ("test", "!", "-f", "custom/dependencies/pip.txt"),
                # It should have base_search_fuzzy available
                ("test", "-d", "custom/src/server-tools/base_search_fuzzy"),
                # Patched Werkzeug version
                (
                    "bash",
                    "-xc",
                    (
                        'test "$(python -c "import werkzeug; '
                        'print(werkzeug.__version__)")" == 0.14.1'
                    ),
                ),
                # apt_build.txt
                ("test", "-f", "custom/dependencies/apt_build.txt"),
                ("test", "!", "-e", "/usr/sbin/sshd"),
                # apt-without-sequence.txt
                ("test", "-f", "custom/dependencies/apt-without-sequence.txt"),
                ("test", "!", "-e", "/bin/busybox"),
                # 070-apt-bc.txt
                ("test", "-f", "custom/dependencies/070-apt-bc.txt"),
                ("test", "-e", "/usr/bin/bc"),
                # 150-npm-aloha_world-install.txt
                (
                    "test",
                    "-f",
                    ("custom/dependencies/" "150-npm-aloha_world-install.txt"),
                ),
                ("node", "-e", "require('test-npm-install')"),
                # 200-pip-without-ext
                ("test", "-f", "custom/dependencies/200-pip-without-ext"),
                ("python", "-c", "import Crypto; print(Crypto.__version__)"),
                ("sh", "-xc", "rst2html.py --version | grep 'Docutils 0.14'"),
                # 270-gem.txt
                ("test", "-f", "custom/dependencies/270-gem.txt"),
                ("hello-world",),
            )

    def test_modified_uids(self):
        """tests if we can build an image with a custom uid and gid of odoo"""
        uids_dir = join(SCAFFOLDINGS_DIR, "uids_1001")
        for sub_env in matrix():
            self.compose_test(
                uids_dir,
                sub_env,
                # verify that odoo user has the given ids
                ("bash", "-xc", 'test "$(id -u)" == "1001"'),
                ("bash", "-xc", 'test "$(id -g)" == "1002"'),
                ("bash", "-xc", 'test "$(id -u -n)" == "odoo"'),
                # all those directories need to belong to odoo (user or group odoo)
                (
                    "bash",
                    "-xc",
                    'test "$(stat -c \'%U:%G\' /var/lib/odoo)" == "odoo:odoo"',
                ),
                (
                    "bash",
                    "-xc",
                    'test "$(stat -c \'%U:%G\' /opt/odoo/auto/addons)" == "root:odoo"',
                ),
                (
                    "bash",
                    "-xc",
                    'test "$(stat -c \'%U:%G\' /opt/odoo/custom/src)" == "root:odoo"',
                ),
            )

    def test_uids_mac_os(self):
        """tests if we can build an image with a custom uid and gid of odoo"""
        uids_dir = join(SCAFFOLDINGS_DIR, "uids_mac_os")
        for sub_env in matrix():
            self.compose_test(
                uids_dir,
                sub_env,
                # verify that odoo user has the given ids
                ("bash", "-c", 'test "$(id -u)" == "501"'),
                ("bash", "-c", 'test "$(id -g)" == "20"'),
                ("bash", "-c", 'test "$(id -u -n)" == "odoo"'),
                # all those directories need to belong to odoo (user or group odoo/dialout)
                (
                    "bash",
                    "-c",
                    'test "$(stat -c \'%U:%g\' /var/lib/odoo)" == "odoo:20"',
                ),
                (
                    "bash",
                    "-c",
                    'test "$(stat -c \'%U:%g\' /opt/odoo/auto/addons)" == "root:20"',
                ),
                (
                    "bash",
                    "-c",
                    'test "$(stat -c \'%U:%g\' /opt/odoo/custom/src)" == "root:20"',
                ),
            )

    def test_default_uids(self):
        uids_dir = join(SCAFFOLDINGS_DIR, "uids_default")
        for sub_env in matrix():
            self.compose_test(
                uids_dir,
                sub_env,
                # verify that odoo user has the given ids
                ("bash", "-xc", 'test "$(id -u)" == "1000"'),
                ("bash", "-xc", 'test "$(id -g)" == "1000"'),
                ("bash", "-xc", 'test "$(id -u -n)" == "odoo"'),
                # all those directories need to belong to odoo (user or group odoo)
                (
                    "bash",
                    "-xc",
                    'test "$(stat -c \'%U:%G\' /var/lib/odoo)" == "odoo:odoo"',
                ),
                (
                    "bash",
                    "-xc",
                    'test "$(stat -c \'%U:%G\' /opt/odoo/auto/addons)" == "root:odoo"',
                ),
                (
                    "bash",
                    "-xc",
                    'test "$(stat -c \'%U:%G\' /opt/odoo/custom/src)" == "root:odoo"',
                ),
            )

    @unittest.skipIf(
        not GEIOP_CREDENTIALS_PROVIDED, "GeoIP credentials missing in environment"
    )
    def test_geoip(self):
        geoip_dir = join(SCAFFOLDINGS_DIR, "geoip")
        for sub_env in matrix():
            self.compose_test(
                geoip_dir,
                sub_env,
                # verify that geoipupdate works after waiting for entrypoint to finish its update
                (
                    "bash",
                    "-c",
                    "timeout 60s bash -c 'while (ls -l /proc/*/exe 2>&1 | grep geoipupdate); do sleep 1; done' &&"
                    " geoipupdate",
                ),
                # verify that geoip database exists after entrypoint finished its update
                # using ls and /proc because ps is missing in image for 13.0
                (
                    "bash",
                    "-c",
                    "timeout 60s bash -c 'while (ls -l /proc/*/exe 2>&1 | grep geoipupdate); do sleep 1; done' &&"
                    " test -e /opt/odoo/auto/geoip/GeoLite2-City.mmdb",
                ),
                # verify that geoip database is configured
                (
                    "grep",
                    "-R",
                    "geoip_database = /opt/odoo/auto/geoip/GeoLite2-City.mmdb",
                    "/opt/odoo/auto/odoo.conf",
                ),
            )

    def test_postgres_client_version(self):
        postgres_client_version_dir = join(SCAFFOLDINGS_DIR, "postgres_client_version")
        for sub_env in matrix():
            self.compose_test(
                postgres_client_version_dir,
                sub_env,
                ("psql", "--version"),
                # verify that psql --version is as expected
                (
                    "bash",
                    "-c",
                    '[[ "$(psql --version)" == "psql (PostgreSQL) %s."* ]]'
                    % sub_env["DB_VERSION"],
                ),
                ("pg_dump", "--version"),
                # verify that pg_dump --version is as expected
                (
                    "bash",
                    "-c",
                    '[[ "$(pg_dump --version)" == "pg_dump (PostgreSQL) %s."* ]]'
                    % sub_env["DB_VERSION"],
                ),
                ("pg_restore", "--version"),
                # verify that pg_restore --version is as expected
                (
                    "bash",
                    "-c",
                    '[[ "$(pg_restore --version)" == "pg_restore (PostgreSQL) %s."* ]]'
                    % sub_env["DB_VERSION"],
                ),
            )

    def test_symlinks(self):
        symlink_dir = join(SCAFFOLDINGS_DIR, "symlinks")
        for sub_env in matrix():
            self.compose_test(
                symlink_dir,
                sub_env,
                # there should be no addon for broken symlinks
                ("test", "!", "-e", "/opt/odoo/auto/addons/broken_addon_link"),
                # there should be an addon for working symlinks
                ("test", "-e", "/opt/odoo/auto/addons/addon_alias"),
                # and the addon should have a manifest (this addon link would probably not work in odoo,
                # we are just testing filesystem here)
                (
                    "test",
                    "-e",
                    "/opt/odoo/auto/addons/addon_alias/__manifest__.py",
                    "-o",
                    "-e",
                    "/opt/odoo/auto/addons/addon_alias/__openerp__.py",
                ),
                # verify that symlinking outside the src directory doesn't enable changing permission of important stuff
                ("bash", "-c", '[[ "$(stat -c %U:%G /bin/date)" == "root:root" ]]',),
                # verify that everything in src dir (except symlinks) is accessible by odoo
                (
                    "bash",
                    "-c",
                    "files=$(find /opt/odoo/custom/src -not -group odoo -and -not -type l "
                    " | wc -l) &&"
                    " [[ $files == 0 ]]",
                ),
            )

    def test_repo_merge(self):
        symlink_dir = join(SCAFFOLDINGS_DIR, "repo_merge")
        for sub_env in matrix():
            self.compose_test(
                symlink_dir,
                sub_env,
                (
                    "git",
                    "--git-dir=/opt/odoo/custom/src/odoo/.git",
                    "--no-pager",
                    "log",
                    "-n",
                    "2",
                ),
                # make sure the git log contains a merge commit signed by $GIT_AUTHOR_NAME (otherwise ff was enabled
                # and we did not test the merge commits)
                (
                    "bash",
                    "-c",
                    "git --git-dir=/opt/odoo/custom/src/odoo/.git log -n 1"
                    " | grep 'docker-odoo <https://hub.docker.com/r/tecnativa/odoo>'",
                ),
            )


if __name__ == "__main__":
    unittest.main()

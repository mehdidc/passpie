from functools import partial
from tempfile import mkdtemp
import os
import tarfile

from click.testing import CliRunner
import pytest
import yaml

from passpie.cli import cli
from passpie.config import Config
from passpie.gpg import GPG
from passpie.database import Database
from passpie.utils import mkdir, safe_join, Archive, extract


MOCK_PUBLIC_KEY = """-----BEGIN PGP PUBLIC KEY BLOCK-----

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
INs=
=B11z
-----END PGP PUBLIC KEY BLOCK-----"""

MOCK_PRIVATE_KEY = """-----BEGIN PGP PRIVATE KEY BLOCK-----

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
WGEg2w==
=69bD
-----END PGP PRIVATE KEY BLOCK-----"""

MOCK_KEYPAIR = MOCK_PUBLIC_KEY + MOCK_PRIVATE_KEY


@pytest.yield_fixture
def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    yield mopen()


class CliRunnerWithDB(CliRunner):

    db_path = None

    def run(self, cmd, params, *args, **kwargs):
        kwargs.setdefault("catch_exceptions", False)
        return self.invoke(cmd, params.split(), *args, **kwargs)

    def passpie(self, params, *args, **kwargs):
        from passpie.cli import cli
        return self.run(cli, params, *args, **kwargs)

    @property
    def db_extracted_path(self):
        if self.db_path:
            return self.db_path
        else:
            self.db_path = extract("passpie.db", "gztar")
            return self.db_path


@pytest.yield_fixture
def config(mocker):
    yield Config.DEFAULT


@pytest.yield_fixture
def irunner_empty(mocker):
    mocker.patch("passpie.cli.generate_keys")
    mocker.patch("passpie.cli.export_keys", return_value=MOCK_KEYPAIR)
    runner = CliRunnerWithDB()
    with runner.isolated_filesystem():
        yield runner


@pytest.yield_fixture
def irunner(mocker):
    from passpie.utils import yaml_dump, make_archive, touch, auto_archive, mkdir

    mocker.patch("passpie.cli.generate_keys")
    mocker.patch("passpie.cli.export_keys", return_value=MOCK_KEYPAIR)
    runner = CliRunnerWithDB()
    with runner.isolated_filesystem():
        mkdir("passpie.db")
        yaml_dump([MOCK_KEYPAIR], safe_join("passpie.db", "keys.yml"))
        yaml_dump({}, safe_join("passpie.db", "config.yml"))
        touch(safe_join("passpie.db", ".passpie"))
        make_archive("passpie.db", "passpie.db", "gztar")
        passphrase = "k"
        with auto_archive("passpie.db") as archive:
            cfg = Config(safe_join(archive.path, "config.yml"))
            gpg = GPG(safe_join(archive.path, "keys.yml"),
                      passphrase,
                      cfg["GPG_HOMEDIR"],
                      cfg["GPG_RECIPIENT"])
            with Database(archive, cfg, gpg) as database:
                database.repo = mocker.MagicMock()
                runner.db = database
                yield runner


@pytest.fixture
def mock_run(mocker):
    return mocker.patch('passpie.cli.run')


@pytest.fixture
def mock_open():
    try:
        from mock import mock_open as mopen
    except:
        from unittest.mock import mock_open as mopen
    return mopen()


@pytest.fixture
def tempdir():
    return mkdtemp()


@pytest.fixture
def tempdir_with_git(tempdir):
    mkdir(safe_join(tempdir, ".git"))
    return tempdir

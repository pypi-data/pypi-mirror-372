import logging
from pathlib import Path

from pytest import LogCaptureFixture, fixture, mark

from ..src.config import *


def get_cfg_content() -> str:
    return '[app]\n\tname = "MyPyUtils"\n\tlogging_level = "Debug"\n\trandom_number = 1.5\n\t[app.author]\n\t\tname = "Jaimead7"\n\t\turl = "https://github.com/Jaimead7"'

@fixture(autouse= True)
def set_caplog_lvl(caplog: LogCaptureFixture) -> None:
    caplog.set_level(logging.DEBUG)
    caplog.clear()

@fixture(autouse= True)
def configure_test_folder(tmp_path: Path) -> None:
    dist: Path = tmp_path / 'dist'
    dist.mkdir()
    config: Path = tmp_path / 'dist' / 'config'
    config.mkdir()
    configFile: Path = tmp_path / 'dist' / 'config' / 'config.toml'
    configFile.write_text(get_cfg_content())

@fixture
def prj_test_dict(tmp_path: Path) -> ProjectPathsDict:
    prj_test_dict = ProjectPathsDict()
    prj_test_dict.set_app_path(tmp_path)
    return prj_test_dict

@fixture
def cfg_manager(prj_test_dict: ProjectPathsDict) -> ConfigFileManager:
    return ConfigFileManager(prj_test_dict[ProjectPathsDict.CONFIG_FILE_PATH])


class TestProjectPaths:
    def test_default_paths(
        self,
        prj_test_dict: ProjectPathsDict,
        tmp_path: Path
    ) -> None:
        assert prj_test_dict[ProjectPathsDict.APP_PATH] == tmp_path
        assert prj_test_dict[ProjectPathsDict.DIST_PATH] == tmp_path / 'dist'
        assert prj_test_dict[ProjectPathsDict.CONFIG_PATH] == tmp_path / 'dist' / 'config'
        assert prj_test_dict[ProjectPathsDict.CONFIG_FILE_PATH] == tmp_path / 'dist' / 'config' / 'config.toml'

    def test_errors(
        self,
        prj_test_dict: ProjectPathsDict,
        caplog: LogCaptureFixture
    ) -> None:
        prj_test_dict['ERROR_PATH'] = 'noPath'
        record: logging.LogRecord = caplog.records[0]
        assert record.levelno == logging.WARNING
        assert prj_test_dict['ERROR_PATH'] == None


class TestConfigFileManager:
    def test_access(self, cfg_manager: ConfigFileManager) -> None:
        assert cfg_manager.app.name == 'MyPyUtils'
        assert cfg_manager.app.random_number == 1.5
        assert type(cfg_manager.app.author) == ConfigDict
        assert cfg_manager.app.author == {
            'name': 'Jaimead7',
            'url': 'https://github.com/Jaimead7'
        }
        assert cfg_manager.app.author.name == 'Jaimead7'

    def test_routes(self, cfg_manager: ConfigFileManager) -> None:
        assert cfg_manager.app.author.route == ['app', 'author']

    def test_file_manager(self, cfg_manager: ConfigFileManager) -> None:
        assert cfg_manager.app.author.file_manager == cfg_manager

    @mark.parametrize('content, expected', [
        ('[app]\n\tname = "MyPyUtils"\n\tlogging_level = "Info"\n\t[app.author]\n\t\tname = "Jaimead7"\n\t\turl = "https://github.com/Jaimead7"',
         '[app]\n\tname = "MyPyUtils"\n\tlogging_level = "Info"\n\t[app.author]\n\t\tname = "Jaimead7"\n\t\turl = "https://github.com/Jaimead7"'),
        ({'app': {'name': 'MyPyUtils', 'logging_level': 'Warning', 'author': {'name': 'Jaimead7', 'url': 'https://github.com/Jaimead7'}}},
         '[app]\nname = "MyPyUtils"\nlogging_level = "Warning"\n\n[app.author]\nname = "Jaimead7"\nurl = "https://github.com/Jaimead7"\n'),
    ])
    def test_write_file(
        self,
        content: str | dict,
        expected: str,
        cfg_manager: ConfigFileManager
    ) -> None:
        cfg_manager.write_file(content)
        with open(cfg_manager._file_path) as f:
            assert expected == f.read()

    def test_write_var(self, cfg_manager: ConfigFileManager) -> None:
        cfg_manager.write_var(['app', 'logging_level'], 'critical')
        assert cfg_manager.app.logging_level == 'critical'
        cfg_manager.app.logging_level = 'error'
        assert cfg_manager.app.logging_level == 'error'
        cfg_manager.app.random_number = 2.1
        assert cfg_manager.app.random_number == 2.1

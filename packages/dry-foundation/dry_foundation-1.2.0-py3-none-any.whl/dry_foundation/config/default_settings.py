"""Default configuration settings."""

import json
from abc import ABC
from pathlib import Path

DEFAULT_CONFIG_DIR = Path("/etc")


class Config(ABC):
    """A base configuration object with some default settings."""

    # Flask app object configuration parameters
    REGISTRATION = True

    def __init__(
        self, import_name, app_name=None, db_path=None, custom_config_filepaths=()
    ):
        # App slug loosely corresponds to Flask `import_name`
        self.SLUG = import_name
        self.NAME = app_name or import_name
        self._custom_config_filepaths = custom_config_filepaths
        # Read parameters from the configuration files in order of specificity
        for config_filepath in filter(lambda p: p.exists(), self.config_filepaths):
            self._read_config_json(config_filepath)
        self.DATABASE = db_path

    @property
    def config_filename(self):
        return f"{self.SLUG}-config.json"

    @property
    def default_global_config_filepath(self):
        return DEFAULT_CONFIG_DIR / self.config_filename

    @property
    def default_config_filepaths(self):
        return [self.default_global_config_filepath]

    @property
    def config_filepaths(self):
        # Set config filepaths in increasing order of importance
        return [*self.default_config_filepaths, *self._custom_config_filepaths]

    @property
    def DATABASE(self):
        return self._database

    @DATABASE.setter
    def DATABASE(self, value):
        # Ensure that the database path is always set as a `pathlib.Path` object if set
        self._database = Path(value) if value else None

    def _read_config_json(self, config_path):
        # Read keys and values from a configuration JSON
        with config_path.open() as config_json:
            config_mapping = json.load(config_json)
        for key, value in config_mapping.items():
            setattr(self, key, value)


class InstanceBasedConfig(Config):
    """
    A base configuration object for app modes using instance directories.

    Notes
    -----
    Instance-based configurations will, by default, look for a database
    in the instance directory with a name derived from the app's slug.
    """

    # Flask app object configuration parameters
    TESTING = False

    def __init__(
        self,
        import_name,
        instance_path,
        app_name=None,
        db_path=None,
        custom_config_filepaths=(),
    ):
        self._instance_path = Path(instance_path)
        self._instance_path.mkdir(parents=True, exist_ok=True)
        super().__init__(
            import_name,
            app_name=app_name,
            db_path=db_path,
            custom_config_filepaths=custom_config_filepaths,
        )
        if not self.DATABASE and self.default_db_filename is not None:
            self.DATABASE = self._instance_path / self.default_db_filename

    @property
    def default_config_filepaths(self):
        # Include a config file in the instance path as a default configuration
        filepaths = super().default_config_filepaths
        if self.config_filename:
            filepaths.append(self._instance_path / self.config_filename)
        return filepaths

    @property
    def default_db_filename(self):
        return f"{self.SLUG}.sqlite"

import os
import configparser
import requests
import yaml

class Config:
    """
    Represents a configuration object that handles reading and writing configuration files.

    Attributes:
        config_path (str): The path to the configuration file.
        config (ConfigParser): The configuration parser object.
        profile (str): The current profile being used.
        AG_EXEC_TIMEOUT (int): The execution timeout value.

    Methods:
        __init__(): Initializes a new instance of the Config class.
        __getattr__(name): Gets called when an attribute with the given name is not found.
        load_config(): Loads the configuration from the file.
        read_config(profile): Reads the configuration for the specified profile.
        write_config(yaml_config, profile): Writes the configuration to the file for the specified profile.
        _write_config(): Writes the configuration to the file.
        _load_config_values(): Loads the configuration values into the class attributes.
    """

    def __init__(self):
        """
        Initializes a new instance of the Config class.

        The configuration file is located in the user's home directory under the '.agent' folder.
        The default profile is set to 'DEFAULT'.
        The default execution timeout is set to 1000 milliseconds.
        """
        home_dir = os.path.expanduser('~')
        self.config_dir = os.path.join(home_dir, '.agent')
        self.config_path = os.path.join(self.config_dir, 'config')
        self.config = configparser.ConfigParser()
        self.profile = 'default'
        self.AG_EXEC_TIMEOUT = 1000

        # self.load_config()
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir)
    
    def __getattr__(self, name):
        """
        Gets called when an attribute with the given name is not found.

        Args:
            name (str): The name of the attribute.

        Raises:
            AttributeError: If the attribute is not found in the configuration file.

        Returns:
            None
        """
        raise AttributeError(f"Please update the config file {self.config_path} profile {self.profile} with the attribute {name}")

    def load_config(self, config_url: str = None, profile: str='default'):
        """
        Loads the configuration from the AGENT Console URL.

        If the configuration file does not exist, a message is printed.
        Otherwise, the configuration is read for the current profile.
        """
        if config_url:
            try:
                response = requests.get(config_url)
                response.raise_for_status()
                self.write_config(response.json(), profile)
            except Exception as e:
                print(f"An error occurred while reading the config from url: {e}")
        elif not os.path.exists(self.config_path):
            print(f"Config file not found at {self.config_path} Please use the 'write_config' method to create a new config.")
        else:
            self.read_config(self.profile)

    def read_config(self, profile):
        """
        Reads the configuration for the specified profile from ~/.agent/config.

        Args:
            profile (str): The profile to read the configuration for.

        Raises:
            Exception: If an error occurs while reading the configuration.

        Returns:
            None
        """
        try:
            self.profile = profile
            self.config.read(self.config_path)
            self._load_config_values()
        except Exception as e:
            print(f"An error occurred while reading the config: {e}")

    def write_config(self, config, profile="default"):
        """
        Writes the configuration to the file for the specified profile.

        Args:
            config (str) or (dict): The configuration to write to the file.
            profile (str): The profile to write the configuration for.

        Raises:
            Exception: If an error occurs while writing the configuration.

        Returns:
            None
        """
        try:
            self.profile = profile
            if type(config) != dict:
                config = yaml.safe_load(config)
            self.config[self.profile] = config
            with open(self.config_path, 'w') as config_file:
                self.config.write(config_file)
            self._load_config_values()
        except Exception as e:
            print(f"An error occurred while writing the config: {e}")


    def _write_config(self):
        """
        Writes the configuration to the file.

        This method is called internally when writing the configuration.
        """
        with open(self.config_path, 'w') as config_file:
            self.config.write(config_file)

    def _load_config_values(self):
        """
        Loads the configuration values into the class attributes.

        This method is called internally when reading the configuration.
        """
        for key, value in self.config[self.profile].items():
            setattr(self, key.upper(), value)
        for section in self.config.sections():
            section_dict = getattr(self, section.upper(), {})
            for key, value in self.config[section].items():
                section_dict[key.upper()] = value
            setattr(self, section.upper(), section_dict)

config = Config()
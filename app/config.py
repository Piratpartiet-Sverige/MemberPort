import os
from configparser import ConfigParser
from hashlib import sha256
from time import time


class Config:
    __instance = None

    _config = ConfigParser()

    @staticmethod
    def get_config() -> ConfigParser:
        if Config.__instance is None:
            Config()
        return Config.__instance._config  # type: ConfigParser

    def __init__(self):
        if Config.__instance is not None:
            raise Exception("This class is a singleton!")
        else:
            Config.__instance = self

        base_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), "..")
        self._config_file = os.path.join(base_dir, "config/config.ini")

        if os.path.isfile(self._config_file):
            # Load values from file if it exists
            self._config.read(self._config_file)

        if self._update_config():  # Fill config with missing values
            self._write_config()   # Write config only if necessary

    def _update_config(self):
        self._config_updated = False

        def add_section(section):
            if section not in self._config:
                self._config[section] = {}
                self._config_updated = True

        def add_section_attribute(section, attribute, value):
            if attribute not in self._config[section]:
                self._config[section][attribute] = value
                self._config_updated = True

        add_section("WebServer")
        add_section_attribute("WebServer", "cookie_secret", sha256(str(time()).encode("utf8")).hexdigest())
        add_section_attribute("WebServer", "url", "http://localhost:8888")
        add_section_attribute("WebServer", "port", "8888")
        add_section_attribute("WebServer", "https", "off")
        add_section_attribute("WebServer", "certs", "/etc/pki/CA/certs/cert.crt")
        add_section_attribute("WebServer", "private", "/etc/pki/CA/private/private.key")
        add_section_attribute("WebServer", "debug", "off")

        add_section("PostgreSQL")
        add_section_attribute("PostgreSQL", "hostname", "")
        add_section_attribute("PostgreSQL", "dbname", "")
        add_section_attribute("PostgreSQL", "username", "")
        add_section_attribute("PostgreSQL", "password", "")

        add_section("Email")
        add_section_attribute("Email", "username", "")
        add_section_attribute("Email", "password", "")
        add_section_attribute("Email", "from", "")
        add_section_attribute("Email", "smtp_server", "")
        add_section_attribute("Email", "smtp_port", "")

        add_section("Users")
        add_section_attribute("Users", "max_username_length", "40")
        add_section_attribute("Users", "max_email_length", "254")
        add_section_attribute("Users", "max_password_length", "254")
        add_section_attribute("Users", "min_password_length", "5")

        add_section("PAP-API")
        add_section_attribute("PAP-API", "key", "")

        return self._config_updated

    def _write_config(self):
        with open(self._config_file, "w") as file:
            self._config.write(file)

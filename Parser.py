#Import/Export YAML Files

import yaml
import toml
from Config import Config
import io

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper

class ParserYAML(object):
    def __init__(self, shaper_path, compose_path):
        self._shaper_path = shaper_path
        self._compose_path = compose_path

    def create_config(self):
        shaper = self.load_shaper_config()
        compose = self.load_compose()
        templates = self.load_templates()
        config = Config(config=shaper, services=compose["services"], templates=templates,
                        networks=compose["networks"], volumes=compose["volumes"])

        return config

    def load_shaper_config(self):
        with open(self._shaper_path, 'r') as stream:
            try:
                return toml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def load_compose(self):
       with open(self._compose_path, 'r') as stream:
           try:
               return load(stream, Loader=Loader)
           except yaml.YAMLError as exc:
               print(exc)

    def load_templates(self):
        with open("./template/templates.yml", 'r') as stream:
            try:
                return load(stream, Loader=Loader)
            except yaml.YAMLError as exc:
                print(exc)

    def export_yaml(self, data, path):
        with io.open(path + '/docker-compose.yaml', 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    def export_toml(self, data, path):
        with open(path + "/traefik.toml", 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()

    def export_prometheus(self, path):
        with open("./template/prometheus.yml", 'r') as stream:
            try:
                data = load(stream, Loader=Loader)
            except yaml.YAMLError as exc:
                print(exc)
        with io.open(path + '/prometheus.yml', 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    def export_grafana(self, path, password):
        with open(path + "/config.monitoring", 'w') as f:
            f.write("GF_SECURITY_ADMIN_PASSWORD="+password + "\n")
            f.write("GF_USERS_ALLOW_SIGN_UP=false")
        f.close()




from Generator.TraefikGenerator import TraefikGenerator as traefik
from Generator.DockerComposeGenerator import ComposeGenerator as composer
from Generator.EnvironmentGenerator import EnvironmentGenerator as environment
from Generator.NginxGenerator import NGINX_Generator as nginx

import os
from shutil import copyfile
import yaml
import toml
from Config import Config
import io

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Optimizer(object):
    def __init__(self, shaper_config, output_path):
        self._shaper_config = shaper_config
        self._output_path = output_path

    def load_databases(self):
        databases = {}
        databases["postgres"] = self.import_yaml("./template/database/postgres.yml")
        databases["maria"] = self.import_yaml("./template/database/mariadb.yml")
        databases["mongo"] = self.import_yaml("./template/database/mongodb.yml")
        databases["mysql"] = self.import_yaml("./template/database/mysql.yml")
        return databases

    def load_monitoring(self):
        monitoring = []
        monitoring.append(self.import_yaml("./template/monitoring/cadvisor.yml"))

        # Different Export for Database
        monitoring.append(self.import_yaml("./template/monitoring/exporter.yml"))

        monitoring.append(self.import_yaml("./template/monitoring/grafana.yml"))
        monitoring.append(self.import_yaml("./template/monitoring/prometheus.yml"))
        return monitoring

    def load_api(self):
        api = {}
        api["flask"] = self.import_yaml("./template/api/api.yml")
        api["fastapi"] = self.import_yaml("./template/api/api.yml")
        return api

    def load_proxy(self):
        proxy = {}
        proxy["nginx"] = self.import_yaml("./template/proxy/nginx.yml")
        proxy["traefik"] = self.import_yaml("./template/proxy/traefik.yml")
        return proxy

    def load_notebook(self):
        return self.import_yaml("./template/frontend/notebook.yml")


    def create_projects(self):
        databases = self.load_databases()
        monitoring = self.load_monitoring()
        apis = self.load_api()
        proxy = self.load_proxy()
        notebook = self.load_notebook()

        configuration_sample = 0
        configuration_name = "configExample_"
        for database_key, database_value in databases.items():
            for proxy_key, proxy_value in proxy.items():
                for api_key, api_value in apis.items():
                    project_path = self._output_path+configuration_name+configuration_sample
                    os.makedirs(project_path)
                    configuration_sample = configuration_sample + 1

                    # Create Services
                    services = {}
                    services["services"] = [proxy_value, database_value, notebook, api_value]
                    services["services"].extend(monitoring)

                    # Create Config Element
                    # TODO Change Config System
                    config = Config(self._shaper_config, services)

                    # Create Compose File
                    # TODO Change Template Services System
                    # TODO Add Network to Services
                    # TODO Add Port to API and Frontend
                    compose_generator = composer(Config)
                    compose_file = compose_generator.generate()
                    self.export_yaml(compose_file, project_path + '/docker-compose.yaml')

                    if proxy_key == "nginx":
                        # NGINX Proxy
                        os.makedirs(project_path + "/nginx/")
                        # TODO CHECK NGINX GENERATION
                        nginx_gen = nginx(config)
                        nginx_data = nginx_gen.generate()
                        self.export_nginx_conf(nginx_data, project_path + "/nginx")

                        # Monitoring
                        prometheus = self.import_yaml("./template/monitoring/prometheus/prometheus_nginx.yml")
                    elif proxy_key == "traefik":
                        # Traefik Proxy
                        # TODO CHECK TRAEFIK GENERATION
                        traefik_gen = traefik(config)
                        traefik_data = traefik_gen.generate()
                        self.export_toml(traefik_data, project_path)

                        # Monitoring
                        prometheus = self.import_yaml("./template/monitoring/prometheus/prometheus_traefik.yml")
                    else:

                        # Monitoring
                        prometheus = self.import_yaml("./template/monitoring/prometheus/prometheus_nginx.yml")

                    self.export_yaml(prometheus, project_path + "/prometheus.yml")

                    # API
                    # TODO FastAPI Connect to Database
                    # TODO FastAPI Load Data into Table
                    # TODO FLASK Connect to Database
                    # TODO FLASK  Load Data into Table
                    os.makedirs(project_path + "/api")
                    if api_key == "flaks":
                        copyfile("./template/api/fastapi/Dockerfile", project_path + "/api")
                        copyfile("./template/api/fastapi/fastapi.py", project_path + "/api")
                    elif api_key == "fastapi":
                        copyfile("./template/api/flask/Dockerfile", project_path + "/api")
                        copyfile("./template/api/flask/flask.py", project_path + "/api")

                    # Environment File
                    # TODO ENVIRONMENT
                    environment_gen = environment(services)
                    environment_data = environment_gen.generate()
                    self.export_environment(environment_data)

    def import_yaml(self, path):
        with open(path, 'r') as stream:
            try:
                return load(stream, Loader=Loader)
            except yaml.YAMLError as exc:
                print(exc)

    def export_yaml(self, data, path):
        with io.open(path, 'w', encoding='utf8') as outfile:
            yaml.dump(data, outfile, default_flow_style=False, allow_unicode=True)

    def export_toml(self, data, path):
        with open(path + "/traefik.toml", 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()

    def export_nginx_conf(self, data, path):
        with open(path + "/nginx.conf", 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()

    def export_environment(self, data, path):
        with open(path + "/.env", 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()

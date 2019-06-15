from Generator.TraefikGenerator import TraefikGenerator as traefik
from Generator.DockerComposeGenerator import ComposeGenerator as composer
from Generator.EnvironmentGenerator import EnvironmentGenerator as environment
#from Generator.NginxGenerator import NGINX_Generator as nginx
from Generator.NginxGenerator import NGINX_Service_Generator as nginx
from Generator.AnsibleGenerator import AnsibleGenerator as Ansible

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
        if "services" in self._shaper_config and "database" in self._shaper_config["services"]:
            if "mysql" in self._shaper_config["services"]["database"]:
                databases["mysql"] = self.import_yaml("./template/database/mysql.yml")
            if "postgres" in self._shaper_config["services"]["database"]:
                databases["mysql"] = self.import_yaml("./template/database/postgres.yml")
            if "maria" in self._shaper_config["services"]["database"]:
                databases["mysql"] = self.import_yaml("./template/database/maria.yml")
            if "mongo" in self._shaper_config["services"]["database"]:
                databases["mysql"] = self.import_yaml("./template/database/mongo.yml")
            if "None" in self._shaper_config["services"]["database"]:
                databases["None"] = None
        else:
            databases["postgres"] = self.import_yaml("./template/database/postgres.yml")
            databases["maria"] = self.import_yaml("./template/database/mariadb.yml")
            databases["mongo"] = self.import_yaml("./template/database/mongodb.yml")
            databases["mysql"] = self.import_yaml("./template/database/mysql.yml")
            databases["None"] = None
        return databases

    def load_monitoring(self):
        monitoring = {}
        monitoring.update(self.import_yaml("./template/monitoring/cadvisor.yml"))
        # Different Export for Database
        monitoring.update(self.import_yaml("./template/monitoring/exporter.yml"))
        monitoring.update(self.import_yaml("./template/monitoring/grafana.yml"))
        monitoring.update(self.import_yaml("./template/monitoring/prometheus.yml"))
        return monitoring

    def load_api(self):
        api = {}
        if "services" in self._shaper_config and "api" in self._shaper_config["services"]:
            if "fastapi" in self._shaper_config["services"]["api"]:
                api["fastapi"] = self.import_yaml("./template/api/api.yml")
            if "flask" in self._shaper_config["services"]["api"]:
                api["flask"] = self.import_yaml("./template/api/api.yml")
        else:
            api["flask"] = self.import_yaml("./template/api/api.yml")
            api["fastapi"] = self.import_yaml("./template/api/api.yml")
        return api

    def load_proxy(self):
        proxy = {}
        if "services" in self._shaper_config and "proxy" in self._shaper_config["services"]:
            if "nginx" in self._shaper_config["services"]["proxy"]:
                proxy["nginx"] = self.import_yaml("./template/proxy/nginx.yml")
            if "traefik" in self._shaper_config["services"]["proxy"]:
                proxy["traefik"] = self.import_yaml("./template/proxy/traefik.yml")
        else:
            proxy["nginx"] = self.import_yaml("./template/proxy/nginx.yml")
            proxy["traefik"] = self.import_yaml("./template/proxy/traefik.yml")
        return proxy

    def load_consul(self):
        return self.import_yaml("./template/proxy/consul.yml")

    def load_registry(self):
        return self.import_yaml("./template/proxy/registry.yml")

    def load_notebook(self):
        return self.import_yaml("./template/frontend/notebook.yml")

    def load_nginx_letsencrypt(self):
        return self.import_yaml("./template/proxy/nginx_letsencrypt.yml")

    def create_directory(self, path):
        if not os.path.exists(path):
            os.mkdir(path)

    def create_projects(self):
        print("Generate Configs")
        databases = self.load_databases()
        monitoring = self.load_monitoring()
        apis = self.load_api()
        proxy = self.load_proxy()
        notebook = self.load_notebook()

        configuration_sample = 0
        configuration_name = "configExample_"

        #Cluster Replica Config
        replica = {"proxy": [1, 5, 10], "api": [1, 10, 25]}
        config_list = []
        for database_key, database_value in databases.items():
            for proxy_key, proxy_value in proxy.items():
                for api_key, api_value in apis.items():
                    for proxy_replica in replica["proxy"]:
                        for api_replica in replica["api"]:
                            print("Generate Config")
                            print("Reverse Proxy:\t" + str(proxy_key))
                            print("Replica;\t" + str(proxy_replica))
                            print("Database:\t" + str(database_key))
                            print("API:\t" + str(api_key))
                            print("Replica:\t" + str(api_replica))


                            project_name = "config_" + str(database_key) + "_" + str(proxy_key) + "_" + str(api_key) + "_" + str(proxy_replica) + "_" + str(api_replica)
                            config_list.append(project_name)
                            #project_path = self._output_path+configuration_name+str(configuration_sample)
                            project_path = self._output_path + project_name
                            project_path_compose = project_path
                            self.create_directory(project_path)
                            self.create_directory(project_path_compose)
                            configuration_sample = configuration_sample + 1

                            """
                            services = {}
                            services.update(self.load_registry())
                            # Create Config Element
                            config = Config(self._shaper_config, services)

                            # Create Compose File
                            compose_generator = composer(config=config, proxy=proxy_key,
                                                         proxy_replica=proxy_replica, api_replica=api_replica)
                            compose_file = compose_generator.generate()
                            network = compose_generator.create_network()
                            self.export_yaml(compose_file, project_path_compose + '/docker-requirements.yaml')
                            """
                            # Create Services
                            services = {}
                            if database_key != "None":
                                services.update(database_value)
                            services.update(proxy_value)
                            services.update(api_value)
                            services.update(monitoring)
                            services.update(notebook)
                            if proxy_key == "traefik" and "cluster" in self._shaper_config:
                                services.update(self.load_consul())
                            elif proxy_key == "nginx" and "security" in self._shaper_config:
                                services.update(self.load_nginx_letsencrypt())
                            # Create Config Element
                            config = Config(self._shaper_config, services)

                            # Create Compose File
                            compose_generator = composer(config=config, proxy=proxy_key,
                                                         proxy_replica=proxy_replica, api_replica=api_replica)
                            compose_file = compose_generator.generate()
                            network = compose_generator.create_network()
                            self.export_yaml(compose_file, project_path_compose + '/docker-compose.yaml')

                            # PROXY
                            self.generate_proxy(config, proxy_key, project_path_compose)

                            #Monitoring
                            self.generate_monitoring(proxy_key, project_path_compose)

                            # API
                            self.generate_API(api_key, project_path_compose)

                            # Environment File
                            environment_gen = environment(self._shaper_config)
                            environment_data = environment_gen.generate()
                            #print("Environment Data:")
                            #print(environment_data)
                            self.export_environment(environment_data, project_path_compose)


                            #Create Ansible Project
                            self.create_directory(project_path + "/roles/")
                            self.create_directory(project_path + "/group_vars/")
                            self.create_directory(project_path + "/roles/create-network/")
                            self.create_directory(project_path + "/roles/create-network/tasks")

                            self.create_directory(project_path + "/roles/copy-docker-stack/")
                            self.create_directory(project_path + "/roles/copy-docker-stack/tasks")

                            self.create_directory(project_path + "/roles/deploy-docker-stack/")
                            self.create_directory(project_path + "/roles/deploy-docker-stack/tasks")
                            ansible = Ansible(config, project_path, network, project_name)
                            ansible.generate()

                            #Create Volume Directories
                            self.create_directory(project_path + "/jupyter/")
                            self.create_directory(project_path + "/jupyter/working/")
                            self.create_directory(project_path + "/jupyter/dataset/")
                            self.create_directory(project_path + "/jupyter/module/")
                            self.create_directory(project_path + "/jupyter/ssl/")

                            self.create_directory(project_path + "/grafana/")
                            self.create_directory(project_path + "/grafana/provisioning")

        print("Create Ansible for Testing All Configs")
        inventory = ansible.create_inventory()
        ansible.export_file(inventory, self._output_path + "/inventory.ini")
        config = ansible.create_all_config(config_list, self._output_path)
        ansible.export_file(config, self._output_path + "/test-all.yml")
        print("Total Configs Created: " + str(configuration_sample))


    def generate_monitoring(self, key, project_path_compose):
        if key == "traefik":
            # Monitoring
            prometheus = self.import_yaml("./template/monitoring/prometheus/prometheus_traefik.yml")
        else:
            # Monitoring
            prometheus = self.import_yaml("./template/monitoring/prometheus/prometheus_nginx.yml")

        self.create_directory(project_path_compose + "/prometheus")
        self.export_yaml(prometheus, project_path_compose + "/prometheus/prometheus.yml")

    def generate_proxy(self, config, proxy_key, project_path_compose):
        if proxy_key == "nginx":
            # NGINX Proxy
            #self.create_directory(project_path_compose + "/nginx/")
            #nginx_gen = nginx(config)
            #nginx_data = nginx_gen.generate()
            #self.export_nginx_conf(nginx_data, project_path_compose + "/nginx")

            # Monitoring
            prometheus = self.import_yaml("./template/monitoring/prometheus/prometheus_nginx.yml")
        elif proxy_key == "traefik":
            # Traefik Proxy
            traefik_gen = traefik(config)
            traefik_data = traefik_gen.generate()
            self.export_toml(traefik_data, project_path_compose)



    def generate_API(self, api_key, project_path_compose):
        # API
        self.create_directory(project_path_compose + "/api")
        self.create_directory(project_path_compose + "/api/app")
        if api_key == "flask":
            copyfile("./template/api/fastapi/Dockerfile", project_path_compose + "/api/Dockerfile")
            copyfile("./template/api/fastapi/app/app.py", project_path_compose + "/api/app/app.py")
            copyfile("./template/api/fastapi/app/requirements.txt", project_path_compose + "/api/app/requirements.txt")
        elif api_key == "fastapi":
            copyfile("./template/api/flask/Dockerfile", project_path_compose + "/api/Dockerfile")
            copyfile("./template/api/flask/app/app.py", project_path_compose + "/api/app/app.py")
            copyfile("./template/api/flask/app/requirements.txt", project_path_compose + "/api/app/requirements.txt")

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

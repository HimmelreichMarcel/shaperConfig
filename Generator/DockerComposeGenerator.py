
from Config import Config

class ComposeGenerator:
    def __init__(self, config=Config, proxy="nginx", cluster=True):
        self.__config = config
        self._proxy = proxy
        self._cluster = cluster
        print(config)

    def generate(self):
        compose = {}
        compose["version"] = "3.7"
        compose["services"] = self.create_services()
        compose["networks"] = self.create_network()
        compose["volumes"] = self.create_volumes()
        return compose

    def create_services(self):
        compose_services = {}

        if "monitoring" in self.__config.get_config():
            for key, value in self.create_traefik_monitoring_service().items():
                compose_services[key] = self.create_traefik_monitoring_service()[key]

        print(self.__config.get_compose_services())
        print(self.__config.get_services())
        for key, value in self.__config.get_compose_services().items():
            compose_service = self.__config.get_compose_service(key)
            labels = []
            if self._proxy== "traefik":
                for key_service, value_service in self.__config.get_services().items():
                    if key_service == key:
                        service = self.__config.get_service(key)
                        labels = self.create_traefik_labels(service)
            """
            if "cluster" in self.__config.get_config():
                compose_service["deploy"].extend({"labels": labels})
                if compose_service["manager"]:
                    compose_service["deploy"]["placement"]['contraints"'] = "node.role == manager"
            else:
            """
            if "labels" in compose_service:
                compose_service["labels"].extend(labels)
            else:
                compose_service["labels"] = labels

            # Create Service Network
            compose_service["networks"] = self.create_service_network(key)

            compose_services[key] = compose_service
        return compose_services

    def create_service_network(self, key):
        networks = []
        if key == "api" or key == "notebook":
            networks.append("web")
        elif key == "traefik" or key == "nginx":
            networks.append("web")
            networks.append("proxy")
        elif key == "prometheus" or key == "grafana" or key == "cadvisor":
            networks.append("web")
        elif key == "consul":
            networks.append("proxy")
        else:
            networks.append("web")
        return networks

    def create_traefik_labels(self, service):
        labels = []
        labels.append("traefik.enable=true")
        domain = self.__config.get_config()["security"]["domain"]
        if "backend" in service:
            labels.append("traefik.backend=" + service["backend"])
        if "frontend" in service:
            label = "traefik.frontend.rule=Host:" + str(service["frontend"]) + "." + str(domain) + "\""
            labels.append(label)
        if "network" in service:
            labels.append("traefik.docker.network=" + service["network"])
        if "port" in service:
            labels.append("traefik.port=" + service["port"])
        print(labels)
        return labels

    def create_traefik_monitoring_service(self):
        services = {}
        domain = self.__config.get_config()["security"]["domain"]
        for key, value in self.__config.get_compose_services()["services"].items():
            service = self.__config.get_compose_services()["services"][key]
            if key == "prometheus" or key == "grafana" or key == "cadvisor":
                labels = []
                labels.append("traefik.enable=true")
                labels.append("traefik.frontend.rule=Host:" + str(key)+ "." + str(domain) + "\"")
                labels.append("traefik.port= " + str(service["ports"]))
                service["labels"] = labels
                services[key] = service
        return services

    def create_network(self):
        networks = {}
        networks["web"] = {}
        networks["proxy"] = {}
        networks["web"]["external"] = "true"

        if self._cluster:
            for key, value in networks().items():
                network = value
                network["driver"] = "overlay"
                networks[key] = network
        return networks

    def create_volumes(self):
        volumes = {}
        if self._proxy == "traefik":
            volumes["consul-data"] = {}
            volumes["consul-data"]["driver"] = "[not local]"
        volumes["prometheus_data"] = {}
        volumes["grafana_data"] = {}
        volumes["database"] = {}
        return volumes

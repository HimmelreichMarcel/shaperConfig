
from Config import Config

class ComposeGenerator:
    def __init__(self, config=None, proxy="nginx", cluster=True):
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
        config = self.__config.get_config()
        if "monitoring" in config:
            compose_services.update(self.create_traefik_monitoring_service())

        print("SERVICES: ")
        print(self.__config.get_compose_services())

        for key, value in self.__config.get_compose_services().items():
            compose_service = self.__config.get_compose_service(key)

            """
            if "cluster" in self.__config.get_config():
                compose_service["deploy"].extend({"labels": labels})
                if compose_service["manager"]:
                    compose_service["deploy"]["placement"]['contraints"'] = "node.role == manager"
            else:
            """

            # Create Service Network
            compose_service["networks"] = self.create_service_network(key)

            #Create Traefik Labels
            if self._proxy == "traefik":
                if key == "api" or key == "notebook":
                    labels = []
                    labels = self.create_traefik_labels(key, value)
                    print(labels)
                    compose_service["labels"] = labels
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

    def create_traefik_labels(self, name, service):
        labels = []
        labels.append("traefik.enable=true")
        domain = self.__config.get_config()["security"]["domain"]
        labels.append("traefik.backend=" + name)
        labels.append("traefik.frontend.rule=Host:" + name + "." + str(domain) + "\"")
        if "network" in service:
            labels.append("traefik.docker.network=" + service["network"])
        if "ports" in service:
            labels.append("traefik.port=" + str(service["ports"][0]))
        return labels

    def create_traefik_monitoring_service(self):
        services = {}
        domain = self.__config.get_config()["security"]["domain"]
        for key, value in self.__config.get_compose_services().items():
            service = self.__config.get_compose_services()[key]
            if key == "prometheus" or key == "grafana" or key == "cadvisor":
                labels = []
                labels.append("traefik.enable=true")
                labels.append("traefik.frontend.rule=Host:" + str(key)+ "." + str(domain) + "\"")
                labels.append("traefik.port= " + str(service["ports"][0]))
                service["labels"] = labels
                services[key] = service
        return services

    def create_network(self):
        networks = {}
        networks["web"] = {}
        networks["proxy"] = {}
        networks["web"]["external"] = True

        if self._cluster:
            for key, value in networks.items():
                network = value
                #network["driver"] = "overlay"
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

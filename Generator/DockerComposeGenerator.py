
from Config import Config

class ComposeGenerator:
    def __init__(self, config=None, proxy="nginx", cluster=True, proxy_replica=1, api_replica=1, https=False):
        self.__config = config
        self._proxy = proxy
        self._cluster = cluster
        self.__api_rep = api_replica
        self.__proxy_rep = proxy_replica
        self._https = https

    def generate(self):
        compose = {}
        print("Generate Compose File ")
        compose["version"] = "3.7"
        compose["services"] = self.create_services()
        compose["networks"] = self.create_network()
        compose["volumes"] = self.create_volumes()
        return compose

    def create_services(self):
        compose_services = {}
        config = self.__config
        #if config.get_security():
        #    compose_services.update(self.create_traefik_monitoring_service())

        #print("SERVICES: ")
        #print(self.__config.get_compose_services())

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

            if self._proxy == "nginx" and key not in ["nginx", "exporter", "nginx_letsencrypt"]:
                environment = self.create_nginx_environment(key, compose_service)
                compose_service["environment"] = environment

            #Create Deploy  Config
            if config.get_cluster():
                compose_service["deploy"] = self.create_deploy(key, value)

            #Create Traefik Labels
            if self._proxy == "traefik" and not config.get_cluster():
                if config.get_cluster():
                    labels = []
                    labels = self.create_traefik_labels(key, value)
                    #print(labels)
                    compose_service["labels"] = labels
                elif key == "api" or key == "notebook":
                    labels = []
                    labels = self.create_traefik_labels(key, value)
                    #print(labels)
                    compose_service["labels"] = labels
            compose_services[key] = compose_service
        return compose_services

    def create_nginx_environment(self, key, service):
        environment = []
        environment.append("VIRTUAL_HOST=" + str(key) + "." + str(self.__config.get_domain()))
        if self._https:
            environment.append("VIRTUAL_PROTO=https")
        if "ports" in service:
            if len(service["ports"]) > 1 or len(service["ports"]) == 1:
                environment.append("VIRTUAL_PORT=" + str(service["ports"][0]))
            elif not isinstance(service["ports"], list):
                environment.append("VIRTUAL_PORT=" + str(service["ports"]))
        return environment

    def create_service_network(self, key):
        networks = []
        if key == "api" or key == "notebook":
            networks.append("web")
        elif key == "traefik" or key == "nginx" or key == "nginx_letsencrypt":
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
        domain = self.__config.get_domain()
        labels.append("traefik.backend=" + name)
        labels.append("traefik.frontend.rule=Host:" + name + "." + str(domain) + "\"")
        if "network" in service:
            labels.append("traefik.docker.network=" + service["network"])
        if "ports" in service:
            labels.append("traefik.port=" + str(service["ports"][0]))
        return labels

    def create_traefik_monitoring_service(self):
        services = {}
        domain = self.__config.get_domain()
        for key, value in self.__config.get_compose_services().items():
            service = self.__config.get_compose_service(key)
            if key == "prometheus" or key == "grafana" or key == "cadvisor":
                labels = []
                labels.append("traefik.enable=true")
                labels.append("traefik.frontend.rule=Host:" + str(key)+ "." + str(domain) + "\"")
                labels.append("traefik.port= " + str(service["ports"][0]))
                service["labels"] = labels
                services[key] = service
        return services

    def create_deploy(self, key, value):
        deploy = {}
        deploy["placement"] = {}
        if key == "api" or key == "notebook":
            deploy["replicas"] = self.__api_rep
            deploy["placement"]["constraints"] = ["node.role==worker"]
        elif key== "traefik" or key == "nginx":
            deploy["placement"]["constraints"] = ["node.role==manager"]
            deploy["replicas"] = self.__proxy_rep
            deploy["restart_policy"] = {}
            deploy["restart_policy"]["condition"] = "any"
        elif key == "prometheus" or key == "grafana" or key == "cadvisor":
            deploy["placement"]["constraints"] = ["node.role==manager"]
            deploy["replicas"] = 1
        else:
            deploy["placement"]["constraints"] = ["node.role==worker"]
            deploy["replicas"] = 1

        if self._proxy == "traefik":
            if self.__config.get_cluster():
                labels = []
                labels = self.create_traefik_labels(key, value)
                #print(labels)
                deploy["labels"] = labels
            elif key == "api" or key == "notebook" or key == "prometheus" or key == "grafana" or key == "cadvisor":
                labels = []
                labels = self.create_traefik_labels(key, value)
                #print(labels)
                deploy["labels"] = labels

        return deploy

    def create_network(self):
        networks = {}
        networks["web"] = {}
        networks["proxy"] = {}
        networks["web"]["external"] = True

        for key, value in networks.items():
            network = value
            if self.__config.get_cluster():
                network["driver"] = "overlay"
            else:
                network["driver"] = "bridge"
            networks[key] = network
        return networks

    def create_volumes(self):
        volumes = {}
        if self._proxy == "traefik" and self.__config.get_cluster():
            volumes["consul-data"] = {}
            volumes["consul-data"]["driver"] = "[not local]"
        volumes["prometheus_data"] = {}
        volumes["grafana_data"] = {}
        volumes["database"] = {}
        volumes["proxy"] = {}
        volumes["notebook"] = {}
        return volumes

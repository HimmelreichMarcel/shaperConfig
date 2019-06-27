
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
        #compose["secrets"] = self.create_secrets()
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
            if key=="notebook":
                compose_service["environment"] = []
                compose_service["environment"].append("JUPYTER_TOKEN="+ self.__config.get_token())

            environment = []
            if key == "api":
                compose_service["image"] = str(self.__config.get_docker_user())+"/api"

            if key == "registry":
                environment.append("REGISTRY_HTTP_ADDR=0.0.0.0:5000") #+ str(self.__config.get_domain()) + ":5000")
                environment.append("REGISTRY_HTTP_TLS_CERTIFICATE=/etc/ssl/crt/" + str(self.__config.get_domain()) + ".crt")
                environment.append("REGISTRY_HTTP_TLS_KEY=/etc/ssl/private/" + str(self.__config.get_domain()) + ".pem")

            # Create Service Network
            compose_service["networks"] = self.create_service_network(key)

            if key == "nginx" and key not in ["nginx", "exporter", "nginx_letsencrypt"]:
                environment = environment + self.create_nginx_environment(key, compose_service)
            if len(environment) > 0:
                compose_service["environment"] = environment


            #Create Deploy  Config
            if config.get_cluster() and key != "consul-leader":
                compose_service["deploy"] = self.create_deploy(key, value)

            #Create Traefik Labels
            if self._proxy == "traefik" and not config.get_cluster() and key is not "traefik":
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

    def create_short_traefik_command(self):
        command = []

        #Consul
        command.append("--consul")
        command.append("--consul.endpoint=consul:8500")
        command.append("--consulk.prefix=traefik")

        return command

    def create_traefik_command(self):
        command = []
        command.append("storeconfig")
        command.append("--api")

        #Entrypoints
        command.append("--entrypoints=Name: http Adress::80 Redirect.EntryPoint:https")
        command.append("--entrypoints=Name:https Address::443 TLS")
        command.append("--defaultentrypoints=http,https")

        #ACME
        command.append("--acme")
        command.append("--acme.storage=traefik/acme/account")
        command.append("--acme.entryPoint=https")
        command.append("--acme.httpChallenge.entryPoint=http")
        command.append("--acme.onHostRule=true")
        command.append("--acme.onDemand=false")
        command.append("--acme.email=" + str(self.__config.get_email()))

        #Docker
        command.append("--docker")
        command.append("--docker.swarmMode")
        command.append("--docker.watch")

        #Consul
        command.append("--consul")
        command.append("--consul.endpoint=consul:8500")
        command.append("--consulk.prefix=traefik")

        return command

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
        elif key == "prometheus" or key == "grafana" or key == "cadvisor" or key == "registry":
            networks.append("web")
        elif key == "consul" or key == "traefik_init":
            networks.append("proxy")
        else:
            networks.append("web")
        return networks

    def create_traefik_labels(self, name, service):
        labels = []
        labels.append("traefik.enable=true")
        domain = self.__config.get_domain()
        labels.append("traefik.backend=" + name)
        labels.append("traefik.frontend.rule=Host:" + name + "." + str(domain))
        #labels.append("traefik.redirectorservice.frontend.entryPoints=http")
        #labels.append("traefik.redirectorservice.frontend.redirect.entryPoint=https")
        if "networks" in service:
            labels.append("traefik.docker.network=" + service["networks"][0])
        if "ports" in service:
            labels.append("traefik.port=" + str(service["ports"][0].split(":")[0]))
        #labels.append("traefik.webservice.frontend.entryPoints=https")
        #labels.append("traefik.frontend.auth.basic.users=${USER}:${PWD}")
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
            deploy["mode"] = "replicated"
            deploy["placement"]["constraints"] = ["node.role==manager"]
        elif key== "traefik" or key == "nginx":
            deploy["placement"]["constraints"] = ["node.role==manager"]
            deploy["replicas"] = self.__api_rep
            deploy["restart_policy"] = {}
            deploy["restart_policy"]["condition"] = "any"
        elif key == "prometheus" or key == "grafana" or key == "registry":
            deploy["placement"]["constraints"] = ["node.role==manager"]
            deploy["replicas"] = 1
        elif key == "minio":
            deploy["placement"]["constraints"] = ["node.role==worker"]
            deploy["replicas"] = 1
        elif key == "database" or key == "traefik_init":
            deploy["placement"]["constraints"] = ["node.role==manager"]
        else:
            deploy["placement"]["constraints"] = ["node.role==manager"]
            deploy["mode"] = "global"

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
            volumes["consul-data-leader"] = {}
            volumes["consul-data-replica"] = {}
        volumes["prometheus_data"] = {}
        volumes["grafana_data"] = {}
        volumes["database"] = {}
        volumes["proxy"] = {}
        volumes["notebook"] = {}
        volumes["registry"] = {}
        volumes["minio"] = {}
        return volumes

    def create_secrets(self):
        secrets = {}
        secrets["builder_domain.crt"] = {"file": "/etc/ssl/crt/" + str(self.__config.get_domain()) + ".crt"}
        secrets["builder_domain.key"] = {"file": "/etc/ssl/private/" + str(self.__config.get_domain()) + ".pem"}
        return secrets

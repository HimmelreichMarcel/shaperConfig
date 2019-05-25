import Config as conf


class ComposeGenerator:
    def __init__(self, config={}):
        self.__config = config
        print(config)

    def generate(self):
        compose = {}
        compose["version"] = "3.7"
        compose["services"] = self.create_services()
        compose["networks"] =  self.create_network()
        compose["volumes"] = self.create_volumes()

        return compose

    def create_services(self):
        compose_services = {}

        if "cluster" in self.__config.get_config():
            for key, value in self.create_cluster.items():
                compose_services[key] = self.create_cluster()[key]

        if "monitoring" in self.__config.get_config():
            for key, value in self.create_monitoring_service().items():
                compose_services[key] = self.create_monitoring_service()[key]

        for key, value in self.create_traefik_service().items():
            compose_services[key] = self.create_traefik_service()[key]
        print(self.__config.get_compose_services())
        print(self.__config.get_services())
        for key, value in self.__config.get_compose_services().items():
            compose_service = self.__config.get_compose_service(key)
            labels = []
            for key_service, value_service in self.__config.get_services().items():
                print("key: " + key + " key-service: " +key_service)
                if key_service == key:
                    service = self.__config.get_service(key)
                    labels = self.create_traefik_labels(service)
            if "cluster" in self.__config.get_config():
                compose_service["deploy"].extend({"labels": labels})
                if compose_service["manager"]:
                    compose_service["deploy"]["placement"]['contraints"'] = "node.role == manager"
            else:
                if "labels" in compose_service:
                    compose_service["labels"].extend(labels)
                else:
                    compose_service["labels"] = labels
            if "networks" in compose_service:
                compose_service["networks"].append("traefik")
            else:
                compose_service["networks"] = ["traefik"]
            compose_services[key] = compose_service
            print("labels: " + str(labels))

        return compose_services

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

    def create_traefik_service(self):
        services = {}
        if "cluster" in self.__config.get_config():
            services["traefik"] = self.__config.get_templates()["services"]["traefik-cluster"]
        else:
            services["traefik"] = self.__config.get_templates()["services"]["traefik"]

        return services

    def create_monitoring_service(self):
        services = {}
        domain = self.__config.get_config()["security"]["domain"]
        for key, value in self.__config.get_templates()["services"].items():
            service = self.__config.get_templates()["services"][key]
            if key == "node-exporter":
                services["node-exporter"] = service
            if key == "prometheus":
                labels = []
                labels.append("traefik.enable=true")
                labels.append("traefik.frontend.rule=Host:" + str(key)+ "." + str(domain) + "\"")
                labels.append("traefik.port= " + str(service["ports"]))
                service["labels"] = labels
                services["prometheus"] = service
            if key == "grafana":
                labels = []
                labels.append("traefik.enable=true")
                labels.append("traefik.frontend.rule=Host:" + str(key)+ "." + str(domain) + "\"")
                labels.append("traefik.port= " + str(service["ports"]))
                service["labels"] = labels
                services["grafana"] = service
            if key == "cadvisor":
                labels = []
                labels.append("traefik.enable=true")
                labels.append("traefik.frontend.rule=Host:" + str(key)+ "." + str(domain) + "\"")
                labels.append("traefik.port= " + str(service["ports"]))
                service["labels"] = labels
                services["cadvisor"] = service

        return services

    def create_cluster(self):
        services = {}
        if "cluster" in self.__config.get_config():
            services["consul"] = self.__config.get_templates()["services"]["consul"]

        return services

    def create_network(self):
        networks = {}
        if "cluster" in self.__config.get_config():
            for key, value in self.__config.get_networks().items():
                network = self.__config.get_networks()[key]
                network["driver"] = "overlay"
                networks[key] = network
        for key, value in self.__config.get_templates()["networks"].items():
            network = self.__config.get_templates()["networks"][key]
            #network["driver"] = "bridge"
            networks[key] = network

        return networks

    def create_volumes(self):
        volumes = {}
        if "cluster" in self.__config.get_config():
            volumes["consul-data"] = self.__config.get_templates()["volumes"]["consul-data"]
        if "monitoring" in self.__config.get_config():
            volumes["prometheus_data"] = self.__config.get_templates()["volumes"]["prometheus_data"]
            volumes["grafana_data"] = self.__config.get_templates()["volumes"]["grafana_data"]
        for key, value in self.__config.get_volumes().items():
            volume = self.__config.get_volume(key)
            volumes[key] = volume

        return volumes

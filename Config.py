
class Config(object):
    def __init__(self, config, services, templates, networks, volumes):
        self.__config = config
        self.__compose_services = services
        self.__templates = templates
        self.__networks = networks
        self.__volumes = volumes
        print(config)
        print(services)

    def get_config(self):
        return self.__config

    def get_service(self, name):
        return self.__config["services"][name]

    def get_services(self):
        return self.__config["services"]

    def get_compose_service(self, name):
        return self.__compose_services[name]

    def get_compose_services(self):
        return self.__compose_services

    def get_networks(self):
        return self.__networks

    def get_network(self, name):
        return self.__networks[name]

    def get_volumes(self):
        return self.__volumes

    def get_volume(self, name):
        return self.__volumes[name]

    def get_templates(self):
        return self.__templates

    def set_config(self, config):
        self.__config = config

    def set_services(self, services):
        self.__config["services"] = services

    def set_compose_services(self, services):
        self.__compose_services =  services

    def set_networks(self, networks):
        self.__networks = networks

    def set_volumes(self, volumes):
        self.__volumes = volumes

    def set_templates(self, templates):
        self.__templates = templates

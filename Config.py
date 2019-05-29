
class Config(object):
    def __init__(self, config, services, networks=[], volumes=[], replicas={}):
        self.__config = config
        self.__compose_services = services
        self.__networks = networks
        self.__volumes = volumes
        self.__replicas = replicas

        if "security" in self.__config:
            self._security = True
            self._domain = self.__config["security"]["domain"]
            self._email = self.__config["security"]["email"]
        else:
            self._security = False
            self._domain = "localhost"
            self._email = ""

        if "monitoring" in self.__config:
            self._monitoring = True
        else:
            self._monitoring = False

        if "admin" in self.__config:
            self._user = self.__config["admin"]["user"]
            self._password = self.__config["admin"]["password"]
            self._database = self.__config["admin"]["database"]
        else:
            self._user = "admin"
            self._password = "admin"
            self._database = "database"

        if "cluster" in self.__config:
            self._cluster = True
            self._manager = self.__config["cluster"]["manager"]
            self._worker = self.__config["cluster"]["worker"]
        else:
            self._cluster = False
            self._manager = []
            self._worker = []

        print(self.__compose_services)

    def get_domain(self):
        return self._domain

    def get_email(self):
        return self._email

    def get_security(self):
        return self._security

    def get_monitoring(self):
        return self._monitoring

    def get_user(self):
        return self._user

    def get_password(self):
        return self._password

    def get_database(self):
        return self._database

    def get_cluster(self):
        return self._cluster

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

    def set_config(self, config):
        self.__config = config

    def set_services(self, services):
        self.__config["services"] = services

    def set_compose_services(self, services):
        self.__compose_services = services

    def set_networks(self, networks):
        self.__networks = networks

    def set_volumes(self, volumes):
        self.__volumes = volumes


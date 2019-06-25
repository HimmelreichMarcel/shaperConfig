
class Config(object):
    def __init__(self, config, services, networks=[], volumes=[], replicas={}, metadata={}):
        self.__config = config
        self.__compose_services = services
        self.__networks = networks
        self.__volumes = volumes
        self.__replicas = replicas
        self.__metadata = metadata

        if "security" in self.__config:
            self._security = True
        else:
            self._security = False

        self._email = self.__config["admin"]["email"]
        if "monitoring" in self.__config:
            self._monitoring = True
        else:
            self._monitoring = False

        if "ssh" in self.__config:
            self._ssh = True
            if "manager" in self.__config["ssh"]:
                self._ssh_manager_users = self.__config["ssh"]["manager"]["users"]
                self._ssh_manager_hosts = self.__config["ssh"]["manager"]["hosts"]
            if "worker" in self.__config["ssh"]:
                self._ssh_worker_users = self.__config["ssh"]["worker"]["users"]
                self._ssh_worker_hosts = self.__config["ssh"]["worker"]["hosts"]
        else:
            self._ssh = False
            self._ssh_manager_users = None
            self._ssh_manager_hosts = None
            self._ssh_worker_users = None
            self._ssh_worker_hosts = None


        if "admin" in self.__config:
            self._domain = self.__config["admin"]["domain"]
            self._user = self.__config["admin"]["user"]
            self._password = self.__config["admin"]["password"]
            self._database = self.__config["admin"]["database"]
            self._docker_user = self.__config["admin"]["docker_user"]
            self._docker_password = self.__config["admin"]["docker_password"]
        else:
            self._domain = "localhost"
            self._user = "admin"
            self._password = "admin"
            self._database = "database"

        self._feature_count = 500
        self._table = "train_table"

        if "cluster" in self.__config:
            self._cluster = True
            self._cluster_name = self.__config["cluster"]["name"]
            self._manager = self.__config["cluster"]["manager"]
            self._worker = self.__config["cluster"]["worker"]
            self._manager_ip = self.__config["cluster"]["manager_ip"]
            self._worker_ip = self.__config["cluster"]["worker_ip"]
            self._ssh_user = self.__config["cluster"]["user"]
            self._ssh_password = self.__config["cluster"]["password"]
        else:
            self._cluster = False
            self._manager = []
            self._worker = []

    def get_db_port(self):
        if "postgres" in self.__compose_services.items():
            return self.__compose_services["postgres"]["ports"].split(':')[0]
        elif "mongo" in self.__compose_services.items():
            return self.__compose_services["mongo"]["ports"].split(':')[0]
        elif "mysql" in self.__compose_services.items():
            return self.__compose_services["mysql"]["ports"].split(':')[0]
        elif "maria" in self.__compose_services.items():
            return self.__compose_services["maria"]["ports"].split(':')[0]

    def get_db_adress(self):
        if "postgres" in self.__compose_services.items():
            return "postgres"
        elif "mongo" in self.__compose_services.items():
            return "mongo"
        elif "mysql" in self.__compose_services.items():
            return "mysql"
        elif "maria" in self.__compose_services.items():
            return "maria"

    def get_db_dialect(self):
        if "postgres" in self.__compose_services.items():
            return "postgresql"
        elif "mongo" in self.__compose_services.items():
            return "mongo"
        elif "mysql" in self.__compose_services.items() or "maria" in self.__compose_services.items():
            return "mysql+pymysql"

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

    def get_table(self):
        return self._table

    def get_feature_count(self):
        return self._feature_count

    def get_password(self):
        return self._password

    def get_database(self):
        return self._database

    def get_cluster_name(self):
        return self._cluster_name

    def get_metadata(self):
        return self.__metadata

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

    def get_ssh(self):
        return self._ssh

    def get_manager_users(self):
        return self._ssh_manager_users

    def get_manager_hosts(self):
        return self._ssh_manager_hosts

    def get_worker_users(self):
        return self._ssh_worker_users

    def get_worker_hosts(self):
        return self._ssh_worker_hosts

    def get_manager(self):
        return self._manager

    def get_worker(self):
        return self._worker

    def get_manager_ip(self):
        return self._manager_ip

    def get_worker_ip(self):
        return self._worker_ip

    def get_ssh_user(self):
        return self._ssh_user

    def get_ssh_password(self):
        return self._ssh_password

    def get_docker_user(self):
        return self._docker_user

    def get_docker_password(self):
        return self._docker_password

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


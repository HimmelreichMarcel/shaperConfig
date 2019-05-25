

class Service(object):
    def __init__(self, name, hostname, image):
        self._name = name
        self._domain = None
        self._ssl = True
        self._remote_path = None
        self._location = "/"
        self._size = 1
        self._expose = None

        # Docker
        self._image = image
        self._port = []
        self._volume = []
        self._config = None
        self._network = []


        # NGINX Load Balancing
        self._hostname = hostname
        self._ip_hash = True
        self._weight = 1
        self._max_fails = 3
        self._fail_timeout = "15s"
        self._remote_port = None


        #Traefik
        self._backend = None
        self._frontend = None
        self._enable = True
        self._port = None
        self._network = None

    def create_traefik(self):
        traefik = []
        return traefik

    def get_port(self):
        return self._port

    def get_name(self):
        return self._name

    def get_image(self):
        return self._image

    def export_yaml(self):
        yaml = None

        return yaml

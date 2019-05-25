
class EnvironmentGenerator(object):
    def __init__(self, shaper_config, services):
        self._shaper_config = shaper_config
        self._services = services

        #Environment
        self._user = ""
        self._password = ""
        self._database = ""

    def generate(self):
        environment = []
        environment.append("${USER} = " + self._shaper_config["user"])
        environment.append("${PWD} = " + self._shaper_config["password"])
        environment.append("${DATABASE} = " + self._shaper_config["database"])

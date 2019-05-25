
class EnvironmentGenerator(object):
    def __init__(self, shaper_config, services):
        self._shaper_config = shaper_config
        self._services = services

    def generate(self):
        environment = []
        environment.append("${USER} = " + self._shaper_config["user"])
        environment.append("${PWD} = " + self._shaper_config["password"])
        environment.append("${DATABASE} = " + self._shaper_config["database"])
        environment.append("${LOCAL_WORKING_DIR} = " + "./jupyter/working")
        environment.append("${LOCAL_DATASETS} = " + "./jupyter/dataset")
        environment.append("${LOCAL_MODULES} = " + "./jupyter/module")
        environment.append("${LOCAL_SSL_CERTS} = " + "./jupyter/ssl")
        environment.append("${ACCESS_TOKEN} = " + self._shaper_config["access_token"])
        return environment


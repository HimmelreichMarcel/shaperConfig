
import random
import string
import IPython as IPython

class EnvironmentGenerator(object):
    def __init__(self, shaper_config):
        self._shaper_config = shaper_config

    def generate(self):
        environment = []
        environment.append("USER=" + self._shaper_config.get_config()["admin"]["user"])
        environment.append("PWD=" + self._shaper_config.get_config()["admin"]["password"])
        environment.append("DATABASE=" + self._shaper_config.get_config()["admin"]["database"])
        environment.append("DB_PORT=" + str(self._shaper_config.get_db_port()))
        environment.append("DB_ADRESS=" + str(self._shaper_config.get_db_adress()))
        environment.append("DB_DIALECT=" + str(self._shaper_config.get_db_dialect()))
        environment.append("TABLE=" + self._shaper_config.get_table())
        environment.append("LOCAL_WORKING_DIR=" + "./jupyter/working")
        environment.append("LOCAL_DATASETS=" + "./jupyter/dataset")
        environment.append("LOCAL_MODULES=" + "./jupyter/module")
        environment.append("LOCAL_SSL_CERTS=" + "./jupyter/ssl")
        environment.append("ACCESS_TOKEN=" + IPython.lib.passwd(self._shaper_config.get_config()["admin"]["password"]))
        environment.append("ACCESS_KEY=" + self.generate_token(10))
        environment.append("SECRET_KEY=" + self.generate_token(10))
        return environment

    def generate_token(self, stringLength=50):
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for i in range(stringLength))


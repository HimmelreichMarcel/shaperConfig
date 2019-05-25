import Config as conf


class TraefikGenerator(object):
    def __init__(self, config={}):
        self.__config = config

    def create_entry_points(self):
        entry= []
        entry.append("[entryPoints]")
        entry.append("\t [entryPoints.http]")
        entry.append("\t address = \":80\"")
        entry.append("\t \t [entryPoints.http.redirect]")
        entry.append("\t \t entryPoint = \"https\"")
        entry.append("\t [entryPoints.https]")
        entry.append("\t address = \":443\"")
        entry.append("\t [entryPoints.https.tls]")
        return entry

    def create_api(self):
        api = []
        api.append("[api]")
        api.append("entryPoint = \"traefik\"")
        api.append("dashboard = true")
        return api

    def create_acme(self):
        acme = []
        acme.append("[acme]")
        acme.append("email= \"" + str(self.__config.get_config()["security"]["email"]) + "\"")
        acme.append("storage = \"acme.json\"")
        acme.append("entryPoint = \"https\"")
        acme.append("onHostRule = true")
        if "provider" in self.__config.get_config()["security"]:
            acme.append("[acme.dnsChallenge]")
            acme.append("provider= \"" + self.__config.get_config()["security"]["provider"] + "\"")
            acme.append("delayBeforeCheck = 0")
        else:
            acme.append("[acme.httpChallenge]")
            acme.append("entryPoint = \"http\"")
        return acme

    def create_consul(self):
        consul = []
        consul.append("[consul]")
        consul.append("endpoint = \"127.0.0.1:8500\"")
        consul.append("watch = true")
        consul.append("prefix = \"traefik\"")
        return consul

    def create_docker(self):
        docker = []
        docker.append("[docker]")
        docker.append("endpoint = \"unix:///var/run/docker.sock\" ")
        docker.append("domain = \"" + str(self.__config.get_config()["security"]["domain"]) + "\"")
        docker.append("watch = true")
        docker.append("exposedByDefault = false")
        if "cluster" in self.__config.get_config():
            docker.append("swarmMode = true")
        return docker

    def create_metrics(self):
        metrics = []
        metrics.append("[metrics]")
        metrics.append("[metrics.prometheus]")
        return metrics

    def generate(self):
        config = []
        config.append("debug = false")
        config.append("logLevel = \"ERROR\"")
        config.append("defaultEntryPoints = [\"https\",\"http\"]")
        config.extend(self.create_entry_points())
        config.extend(self.create_docker())
        if "security" in self.__config.get_config():
            config.extend(self.create_acme())
        if "monitoring" in self.__config.get_config():
            config.extend(self.create_metrics())
        if "cluster" in self.__config.get_config():
            config.extend(self.create_consul())
        return config



"""

debug = false

logLevel = "ERROR"
defaultEntryPoints = ["https","http"]

[entryPoints]
  [entryPoints.http]
  address = ":80"
    [entryPoints.http.redirect]
    entryPoint = "https"
  [entryPoints.https]
  address = ":443"
  [entryPoints.https.tls]

[retry]

[docker]
endpoint = "unix:///var/run/docker.sock"
domain = "my-awesome-app.org"
watch = true
exposedByDefault = false

[acme]
email = "your-email-here@my-awesome-app.org"
storage = "acme.json"
entryPoint = "https"
onHostRule = true
[acme.httpChallenge]
entryPoint = "http"
"""
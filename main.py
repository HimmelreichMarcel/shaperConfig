

from Config import Config
from Parser.ParserYAML import ParserYAML
from LoadBalancer.Traefik_Generator import TraefikGenerator
from ComposeGenerator import ComposeGenerator
import os

def main():
    compose_path = "/home/standardheld/PycharmProjects/shaper/Example/docker-compose.yml"
    shaper_path = "/home/standardheld/PycharmProjects/shaper/Example/shaper.toml"
    output_path = "/home/standardheld/testproject1/"
    parser = ParserYAML(shaper_path, compose_path)
    config = parser.create_config()

    #Create Directionaries
    for path in [output_path, output_path + "prometheus", output_path + "grafana/"]:
        if not os.path.exists(path):
            os.mkdir(path)
            print("Directory ", path, " Created ")
        else:
            print("Directory ", path, " already exists")

    generator = ComposeGenerator(config)
    traefik_generator = TraefikGenerator(config)
    compose = generator.generate()
    traefik = traefik_generator.generate()

    parser.export_yaml(compose, output_path)
    parser.export_toml(traefik, output_path)
    parser.export_prometheus(output_path + "prometheus")
    parser.export_grafana(output_path + "grafana/", "foobar")


if __name__ == "__main__":
    main()



from Config import Config
from Parser import ParserYAML
from LoadBalancer.Traefik_Generator import TraefikGenerator
from ComposeGenerator import ComposeGenerator
from Optimizer import Optimizer
import os
import toml
import yaml


def main():
    compose_path = "/home/standardheld/PycharmProjects/shaper/Example/docker-compose.yml"
    shaper_path = "/home/standardheld/PycharmProjects/shaper/Example/shaper.toml"
    output_path = "/home/standardheld/testproject1/"
    #parser = ParserYAML(shaper_path, compose_path)
    #config = parser.create_config()

    generator = Optimizer(load_shaper_config(shaper_path), output_path)
    generator.create_projects()

    """
    generator = ComposeGenerator(config)
    traefik_generator = TraefikGenerator(config)
    compose = generator.generate()
    traefik = traefik_generator.generate()

    parser.export_yaml(compose, output_path)
    parser.export_toml(traefik, output_path)
    parser.export_prometheus(output_path + "prometheus")
    parser.export_grafana(output_path + "grafana/", "foobar")
    """


def load_shaper_config(path):
    with open(path, 'r') as stream:
        try:
            return toml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == "__main__":
    main()

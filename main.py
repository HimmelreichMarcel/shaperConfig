

from Config import Config
from Parser import ParserYAML
from LoadBalancer.Traefik_Generator import TraefikGenerator
from ComposeGenerator import ComposeGenerator
from ConfigurationManager import ConfigurationManager
import os
import toml
import yaml


def main():
    shaper_path = "/home/standardheld/Documents/Github/shaperConfig/Example/shaper_ssh.toml"
    output_path = "/home/standardheld/CLUSTER2/"
    #compose_path = "/home/marcel/shaper/shaperConfig/Example/docker-compose.yml"
    #shaper_path = "/home/marcel/shaper/shaperConfig/Example/shaper_ssh.toml"
    #output_path = "/home/marcel/CONFIGS/"
    #parser = ParserYAML(shaper_path, compose_path)
    #config = parser.create_config()

    generator = ConfigurationManager(load_shaper_config(shaper_path), output_path)
    print("Done.")
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
            print("Loading Shaper Config...")
            return toml.load(stream)
        except yaml.YAMLError as exc:
            print(exc)

if __name__ == "__main__":
    main()

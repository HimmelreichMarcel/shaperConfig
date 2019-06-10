import os
import yaml
import io
from shutil import copyfile
import os
from distutils.dir_util import copy_tree

class AnsibleGenerator(object):
    def __init__(self, config, project_path, networks):
        self._config = config
        self._project_path = project_path
        self._networks = networks

    def deploy_swarm(self):
        print()

    def generate(self):
        print("Create Ansible Files")
        #Create Inventory
        inventory = self.create_inventory()
        self.export_inventory(inventory)

        config = self.create_ansible_config()
        self.export_ansible_config(config)

        if self._config.get_cluster():
            up_path = ""#os.path.dirname(os.getcwd())
            print("UP PATH")
            print(up_path)
            path = self._project_path + "/roles/"
            copyfile(up_path + "./template/ansible/swarm-roles/deploy-stack.yml", self._project_path + "/deploy-stack.yml")
            copyfile(up_path + "./template/ansible/swarm-roles/delete-swarm.yml", self._project_path + "/delete-swarm.yml")

            network = self.create_network()
            self.export_ansible_network(network, path + "/create-network/tasks/main.yml")

            copy_tree(up_path + "./template/ansible/swarm-roles/install-modules", path + "/install-modules/")

            copy_tree(up_path + "./template/ansible/swarm-roles/deploy-docker-stack", path + "/deploy-docker-stack/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-installation", path + "/docker-installation/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-add-manager", path + "/docker-swarm-add-manager/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-add-worker", path + "/docker-swarm-add-worker/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-init", path + "/docker-swarm-init/")
            copy_tree(up_path + "./template/ansible/swarm-roles/install-modules", path + "/install-modules/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-leave", path + "/docker-swarm-leave/")

    def create_role(self):
        print()

    def create_site(self):
        print()

    def create_network(self):
        network = []
        network.append("---")
        for key, value in self._networks.items():
            network.append("- name: Create Network " + str(key))
            network.append("  docker_network:")
            network.append("    name: " + str(key))
            network.append("    driver: " + str(value["driver"]))
            if "external" in value:
                network.append("    internal: no")
            else:
                network.append("    internal: yes")
            network.append("\n")
        return network

    def create_ansible_config(self):
        config = []
        config.append("[defaults]")
        config.append("host_key_checking = false")
        #config.append("stdout_callback=minimal")
        return config

    def create_inventory(self):
        if not self._config.get_cluster():
            inventory = list()
            inventory.append("localhost")
        elif self._config.get_cluster():
            inventory = list()
            inventory.append("[nodes]")
            id = 0
            for manager in self._config.get_manager():
                inventory.append("manager ansible_host=\"" + manager + "\"")
                id = id + 1
            id = 0
            for worker in self._config.get_worker():
                inventory.append("worker" + str(id) + " ansible_host=\"" + worker + "\"")
                id = id + 1
            id = 0
            inventory.append("[manager]")
            for manager in self._config.get_manager():
                inventory.append("manager ansible_host=\"" + manager + "\"")
                id = id + 1
            id = 0
            inventory.append("[worker]")
            for worker in self._config.get_worker():
                inventory.append("worker" + str(id) + " ansible_host=\"" + worker + "\"")
                id = id + 1
            inventory.append("[all:vars]")
            inventory.append("ansible_connection=ssh")
            inventory.append("ansible_user=" + self._config.get_ssh_user())
            inventory.append("ansible_password=" + self._config.get_ssh_password())
            inventory.append("ansible_sudo_pass=" + self._config.get_ssh_password())
        else:
            inventory = ["localhost"]
        return inventory

    def export_inventory(self, data):
        with open(self._project_path + "/inventory.ini", 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()

    def export_ansible_config(self, data):
        with open(self._project_path + "/ansible.cfg", 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()

    def export_ansible_network(self, data, path):
        with open(path, 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()
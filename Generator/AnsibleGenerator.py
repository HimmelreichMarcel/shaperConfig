import os
import yaml
import io
from shutil import copyfile
import os
from distutils.dir_util import copy_tree

class AnsibleGenerator(object):
    def __init__(self, config, project_path, networks, project_name, file_path):
        self._config = config
        self._project_path = project_path
        self._networks = networks
        self._project_name = project_name
        self._file_path = file_path

    def deploy_swarm(self):
        print()

    def generate(self):
        print("Create Ansible Files...")
        #Create Inventory
        inventory = self.create_inventory()
        self.export_inventory(inventory)

        config = self.create_ansible_config()
        self.export_ansible_config(config)

        if self._config.get_cluster():
            up_path = ""#os.path.dirname(os.getcwd())
            path = self._project_path + "/roles/"
            copyfile(up_path + "./metric.txt", self._project_path + "/metric.txt")
            copyfile(up_path + "./template/ansible/swarm-roles/deploy-stack.yml", self._project_path + "/deploy-stack.yml")
            copyfile(up_path + "./template/ansible/swarm-roles/leave-swarm.yml", self._project_path + "/leave-swarm.yml")
            copyfile(up_path + "./template/ansible/swarm-roles/clear-stack.yml", self._project_path + "/clear-stack.yml")
            copyfile(up_path + "./template/ansible/swarm-roles/install-requirements.yml", self._project_path + "/install-requirements.yml")
            copyfile(up_path + "./template/ansible/swarm-roles/main.yml", self._project_path + "/main.yml")
            copyfile(up_path + "./template/ansible/swarm-roles/benchmark.yml", self._project_path + "/benchmark.yml")

            network = self.create_network()
            self.export_file(network, path + "/create-network/tasks/main.yml")

            stack = self.copy_stack()
            self.export_file(stack, path + "/copy-docker-stack/tasks/main.yml")

            deploy = self.deploy_stack()
            self.export_file(deploy, path + "/deploy-docker-stack/tasks/main.yml")

            metric = self.store_metrics()
            self.export_file(metric, path + "/collect-metrics/tasks/main.yml")

            copy_tree(up_path + "./template/ansible/swarm-roles/install-modules", path + "/install-modules/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-installation", path + "/docker-installation/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-add-manager", path + "/docker-swarm-add-manager/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-add-worker", path + "/docker-swarm-add-worker/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-init", path + "/docker-swarm-init/")
            copy_tree(up_path + "./template/ansible/swarm-roles/install-modules", path + "/install-modules/")
            copy_tree(up_path + "./template/ansible/swarm-roles/docker-swarm-leave", path + "/docker-swarm-leave/")
            copy_tree(up_path + "./template/ansible/swarm-roles/clear-stack", path + "/clear-stack/")
            copy_tree(up_path + "./template/ansible/swarm-roles/init-registry", path + "/init-registry/")
            copy_tree(up_path + "./template/ansible/swarm-roles/generate-certificate", path + "/generate-certificate/")
            copy_tree(up_path + "./template/ansible/swarm-roles/push-image", path + "/push-image/")
            copy_tree(up_path + "./template/ansible/swarm-roles/deploy-docker-requirements", path + "/deploy-docker-requirements/")
            copy_tree(up_path + "./template/ansible/swarm-roles/benchmark", path + "/benchmark/")

            #Generate Nodes Group Vars
            nodes_var = self.create_nodes_vars()
            self.export_file(nodes_var, self._project_path + "/group_vars/nodes.yml")

    def create_nodes_vars(self):
        vars = list()
        vars.append("---")
        vars.append("swarm_name: " + self._config.get_cluster_name())
        vars.append("domain_name: " + self._config.get_domain())
        vars.append("project_path: " + self._project_name)
        vars.append("dockerhub_user: " + self._config.get_docker_user())
        vars.append("dockerhub_password: " + self._config.get_docker_password())
        return vars

    def create_all_config(self, configs, path):
        config = list()
        config.append("---")
        config.append("- name: Install Requirements ")
        config.append("  import_playbook: " + path + "/" + str(configs[0]) + "/install-requirements.yml")
        config.append("\n")
        for config_name in configs:
            config.append("- name: Deploy " + str(config_name))
            config.append("  import_playbook: " + path + "/" + config_name + "/deploy-stack.yml")
            config.append("\n")
            config.append("- name: Benchmark Test " + str(config_name))
            config.append("  import_playbook: " + path + "/" + config_name + "/benchmark.yml")
            config.append("\n")
            config.append("- name: Clear Stack")
            config.append("  import_playbook: " + path + "/" + config_name + "/clear-stack.yml")
            config.append("\n")
            config.append("- name: Leave Swarm" + str(config_name))
            config.append("  import_playbook: " + path + "/" + config_name + "/leave-swarm.yml")
            config.append("\n")
        return config

    def copy_stack(self):
        stack = list()
        stack.append("---")
        stack.append("- name: Create a directory user")
        stack.append("  file:")
        stack.append("    path: /home/" + str(self._config.get_ssh_user()))
        stack.append("    state: directory")
        stack.append("\n")
        stack.append("- name: Create a directory data")
        stack.append("  file:")
        stack.append("    path: /home/" + str(self._config.get_ssh_user()) + "/data")
        stack.append("    state: directory")
        stack.append("\n")
        stack.append("- name: Create a directory deploy folder")
        stack.append("  file:")
        stack.append("    path: /home/" + str(self._config.get_ssh_user()) + "/deploy")
        stack.append("    state: directory")
        stack.append("\n")
        stack.append("- name: Create a directory docker volumes")
        stack.append("  file:")
        stack.append("    path: /opt/docker/volumes")
        stack.append("    state: directory")
        stack.append("\n")
        stack.append("- name: Create a directory docker volumes mysql")
        stack.append("  file:")
        stack.append("    path: /opt/docker/volumes/mysql")
        stack.append("    state: directory")
        stack.append("\n")
        stack.append("- name: Create a NGINX directory")
        stack.append("  file:")
        stack.append("    path: /etc/nginx/")
        stack.append("    state: directory")
        stack.append("\n")
        stack.append("- name: Copy docker stack")
        stack.append("  copy:")
        stack.append("    src: " + str(self._project_path))
        stack.append("    dest: /home/" + str(self._config.get_ssh_user()) + "/deploy")
        stack.append("\n")
        stack.append("- name: Copy Train Data")
        stack.append("  copy:")
        stack.append("    src: " + str(self._file_path))
        stack.append("    dest: /home/" + str(self._config.get_ssh_user()) + "/data")
        stack.append("\n")
        stack.append("- name: Copy daemon json")
        stack.append("  copy:")
        stack.append("    src: " + str(self._project_path) + "/daemon.json")
        stack.append("    dest: /etc/docker/daemon.json")
        stack.append("\n")
        stack.append("- name: Copy Config")
        stack.append("  copy:")
        stack.append("    src: " + str(self._project_path) + "/nginx/nginx.conf")
        stack.append("    dest: /etc/nginx/nginx.conf")
        stack.append("  ignore_errors: true")
        return stack

    def store_metrics(self):
        metrics = []
        metrics.append("- name: Create a metric directory for config ")
        metrics.append("  file:")
        metrics.append("    path: " + self._project_path + "/metric")
        metrics.append("    state: directory")
        metrics.append("\n")
        with open("./metric.txt", "r") as file:
            data = file.read().splitlines()
        for line in data:
            metrics.append("- name: Get Metric " + str(line))
            metrics.append("  uri:")
            metrics.append("    url: http://prometheus.platform.test/api/v1/query?query=" + line +"[1h]")
            metrics.append("    timeout: 600")
            metrics.append("    return_content: yes")
            metrics.append("    body_format: json")
            metrics.append("  register: metric_json_" + str(line))
            metrics.append("  retries: 5")
            metrics.append("\n")
            metrics.append("- name: Save Metric " + str(line))
            metrics.append("  local_action: copy content=\"{{metric_json_" + str(line) + "}}\" dest=\"" + self._project_path + "/metric/metric_json_" + str(line) + ".json\"")
            metrics.append("  ignore_errors: true")
            metrics.append("\n")
        return metrics

    def deploy_stack(self):
        deploy = []
        deploy.append("---")
        deploy.append("- name: Deploy on Swarm")
        deploy.append("  shell: cd /home/" + str(self._config.get_ssh_user()) + "/deploy/" + str(self._project_name) + " && docker stack deploy -c docker-compose.yaml {{ swarm_name }}")
        deploy.append("  register: stack_deploy")
        deploy.append("\n")
        deploy.append("- debug: var={{item}}")
        deploy.append("  with_items: stack_deploy.stdout_lines")
        deploy.append("\n")
        deploy.append("- name: Check list of services")
        deploy.append("  command: docker service ls")
        deploy.append("  register: service_list")
        deploy.append("\n")
        deploy.append("- debug: var={{item}}")
        deploy.append("  with_items: service_list.stdout_lines")
        deploy.append("\n")
        deploy.append("- name: Check list of stack")
        deploy.append("  command: docker stack ps {{ swarm_name }}")
        deploy.append("  register: stack_ps")
        deploy.append("\n")
        deploy.append("- debug: var={{item}}")
        deploy.append("  with_items: stack_ps.stdout_lines")
        return deploy

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
        config.append("timeout = 10")
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
            inventory.append("ansible_python_interpreter=/usr/bin/python3")
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

    def export_file(self, data, path):
        with open(path, 'w') as f:
            for line in data:
                f.write(line + "\n")
        f.close()
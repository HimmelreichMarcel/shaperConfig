

class AnsibleGenerator(object):
    def __init__(self, config, project_path):
        self._config = config
        self._project_path = project_path

    def deploy_swarm(self):
        print()

    def generate(self):
        print()
        #Create Inventory

        #docker installation

        #docker swarm init

        #docker swarm add worker

        #docker create network

        #docker deploy stack

        #Create playbook


    def create_role(self):
        print()

    def create_task(self):
        print()

    def create_site(self):
        print()

    def create_group_vars(self):
        print()

    def create_inventory(self):
        if self._config.get_ssh():
            inventory = list()
            inventory.append("[nodes]")
            for manager in self._config.get_manager():
                inventory.append(manager)
            for worker in self._config.get_worker():
                inventory.append(worker)

            inventory.append("[manager]")
            for manager in self._config.get_manager():
                inventory.append(manager)

            inventory.append("[worker]")
            for worker in self._config.get_worker():
                inventory.append(worker)
        else:
            inventory = ["localhost"]
        return inventory

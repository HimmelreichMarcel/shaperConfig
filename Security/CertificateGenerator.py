import os


class CertificateGenerator(object):
    def __init__(self, email, project_path):
        self._email = email
        self._project_path = project_path

    def create_file(self, services):
        domains = []
        for service in services:
            if service._ssl:
                domains.append(service._domain)
        parent_directory = os.path.dirname(os.getcwd())
        template = open(parent_directory + "/template/letsencrypt_template.sh", 'r')
        cert_file = open(self._project_path + "/certificate.sh", "w")
        cert_file.write("#!/bin/bash")
        cert_file.write("domains=(" + ' '.join(domains) + ")")
        cert_file.write("email=" + self._email)
        for line in template:
            cert_file.write(line)
        cert_file.close()



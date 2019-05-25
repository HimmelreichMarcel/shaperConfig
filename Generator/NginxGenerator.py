"""

"""
import Modules.Service.Service as Service


class NGINX_Generator(object):
    def __init__(self, services=[], ip_list=[], frontend=[]):
        self._services = services
        self._ip_list = ip_list
        self._frontend = frontend

    def create_ssl_path(self, service):
        domain = service._domain
        path = "/etc/letsencrypt/live/" + str(domain) + "/fullchain.pem;"
        return path

    def create_ssl_key_path(self, service):
        domain = service._domain
        path = "/etc/letsencrypt/live/" + str(domain) + "/privkey.pem;"
        return path

    def create_location(self, service):
        start = "location " + str(service._location) + "{"
        metric = "stub_stash;"
        proxy_set_header = "proxy_set_header Host $host;"
        proxy_pass = "proxy_pass http://" + str(service._name).lower() + ":" + service._remote_port + str(
            service._remote_path) + ";"
        proxy_http = "proxy_http_version 1.1;"
        proxy_set_header_connection = "proxy_set_header Connection \"\";"
        proxy_buffering = "proxy_buffering off;"
        end = "}"

        location = []
        location.append(start)
        location.append(metric)
        location.append(proxy_set_header)
        location.append(proxy_pass)
        location.append(proxy_http)
        location.append(proxy_set_header_connection)
        location.append(proxy_buffering)
        location.append(end)
        return location

    def create_server(self, service):
        server = []
        server.append("server {")

        if service._ssl:
            server.append("listen 80;")
            server.append("listen [::]:80 ipv6only=on;")
        else:
            server.append("listen 443;")

        if service._ssl:
            server.append(self.create_ssl_path(service))
            server.append(self.create_ssl_key_path(service))
            server.append("include /etc/letsencrypt/options-ssl-nginx.conf;")
            server.append("ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;")

        if service._location:
            location = self.create_location(service)
            server.extend(location)
        server.append("}")
        return server

    def create_upstream(self, service):
        upstream = []
        start = "upstream " + service._name + "{"
        upstream.append(start)
        if service._ip_hash:
            upstream.append("ip_hash;")
        for x in range(service._size):
            upstream.append(service._name + str(x) + "." + service._domain + ";")
        end = "}"
        upstream.append(end)
        return upstream

    def create_events(self):
        events = []
        events.append("events{")
        events.append("worker_connections 1024;")
        events.append("}")
        return events

    def generate_config(self):
        config = []
        for service in self._frontend:
            config.extend(self.create_upstream(service))

        for service in self._services:
            config.extend(self.create_server(service))
        return config


"""
  upstream webapp {
        ip_hash;
        server 192.168.0.2;
        server 192.168.0.3;
        server 192.168.0.4;
    }
    upstream api {
        server 192.168.0.5;
        server 192.168.0.6;
    }
    server {
        listen 80;
        listen [::]:80 ipv6only=on;
        server_name www.example.com;
        root /usr/share/nginx/html;
        location / {
            proxy_pass http://webapp:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
    server {
        listen 443;
        server_name www.example.com;
        root html;
        index index.html index.htm;
        ssl on;
        ssl_certificate ssl/something.pem;
        ssl_certificate_key ssl/something.key;
        ssl_session_timeout 5m;
        ssl_protocols SSLv3 TLSv1 TLSv1.1 TLSv1.2;
        ssl_ciphers "HIGH:!aNULL:!MD5 or HIGH:!aNULL:!MD5:!3DES";
        ssl_prefer_server_ciphers on;
        root /usr/share/nginx/html;
        location / {
            proxy_pass http://webapp:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
        location /api/ {
            proxy_pass http://api:80;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }

{%- for service_name, service in services.iteritems() %}
upstream {{service_name|lower}} {
    {%- if service.balancing_type %}
    {{service['balancing_type']}};
    {%- endif %}
    {%- for address in service['addresses'] %}
    server {{address}}:{{services[service_name]['port']}};
    {%- endfor %}
}

{% endfor %}

{%- for hostname, host in hosts.iteritems() %}
{%- if host['protocols']['http'] %}

    listen 80;
    server_name {{hostname}};

    {%- if host['error_log'] %}
    error_log {{host['error_log']}} {{host['log_level']}};
    {%- endif %}
    {%- if host['access_log'] %}
    access_log {{host['access_log']}};
    {%- endif %}

    root /usr/share/nginx/html;
    {%- for service_name in host['services'] %}

    # For service: {{service_name}}
    location {{services[service_name]['location']}} {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_pass http://{{service_name|lower}}{{services[service_name]['remote_path']}};
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
    }{% endfor %}
}
{%- endif %}
{%- if host['protocols']['https'] %}
server {
    listen 443;
    server_name {{hostname}};

    {%- if host['error_log'] %}
    error_log {{host['error_log']}} {{host['log_level']}};
    {%- endif %}
    {%- if host['access_log'] %}
    access_log {{host['access_log']}};
    {%- endif %}

    root /usr/share/nginx/html;

    ssl on;
    ssl_certificate {{host['ssl_certificate']}};
    ssl_certificate_key {{host['ssl_certificate_key']}};

    # Diffie-Hellman parameter for DHE ciphersuites, recommended 2048 bits
    ssl_dhparam {{host['ssl_dhparam']}};

    ssl_session_timeout 5m;

    ssl_protocols {{host['ssl_protocols']}};
    ssl_ciphers {{host['ssl_ciphers']}};
    ssl_prefer_server_ciphers on;

    {%- for service_name in host['services'] %}
    # For service: {{service_name}}
    location {{services[service_name]['location']}} {
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_pass http://{{service_name|lower}}{{services[service_name]['remote_path']}};
        proxy_http_version 1.1;
        proxy_set_header Connection "";
        proxy_buffering off;
    }{%- endfor %}
}
{%- endif %}
{%- endfor %}


"""
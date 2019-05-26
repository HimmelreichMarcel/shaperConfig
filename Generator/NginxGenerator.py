"""

"""


class NGINX_Generator(object):
    def __init__(self, domain="", manager_list=[], ip_list=[]):
        self._domain = domain
        self._ip_list = ip_list
        self._manager = manager_list

    def create_ssl_path(self, domain):
        path = "/etc/letsencrypt/live/" + str(domain) + "/fullchain.pem;"
        return path

    def create_ssl_key_path(self, domain):
        path = "/etc/letsencrypt/live/" + str(domain) + "/privkey.pem;"
        return path

    def create_location(self, location, name, port):
        start = "location " + str(location) + "{"
        metric = "stub_stash;"
        proxy_set_header = "proxy_set_header Host $host;"
        proxy_pass = "proxy_pass http://" + str(name).lower() + ":" + str(port) + ";"
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

    def create_server(self, protocol="https"):
        server = []
        server.append("server {")

        if protocol == "https":
            server.append("listen 443;")
            server.append("server_name " + str(self._domain) + ":")
            server.append("ssl on;")
            server.append("ssl_ciphers \"AES128+EECDH:AES128+EDH\";")
            server.append("ssl_protocols TLSv1 TLSv1.1 TLSv1.2;")
            server.append("ssl_prefer_server_ciphers on;")
            server.append("ssl_session_cache shared:SSL:10m;")
            server.append("ssl_certificate" + self.create_ssl_path(self._domain))
            server.append("ssl_certificate_key" + self.create_ssl_key_path(self._domain))
            server.append("include /etc/letsencrypt/options-ssl-nginx.conf;")
        else:
            server.append("listen 80;")
            server.append("listen [::]:80 ipv6only=on;")

        # Create Jupyter
        location = self.create_location("/notebook", "notebook", "8888")
        server.extend(location)
        # Create API
        location = self.create_location("/api", "api", "80")
        server.extend(location)

        # Create Monitoring
        location = self.create_location("/grafana", "grafana", "3333")
        server.extend(location)
        location = self.create_location("/prometheus", "prometheus", "9090")
        server.extend(location)

        server.append("}")
        return server

    def create_upstream(self, name, ip_list, ip_hash=False):
        upstream = []
        upstream.append("upstream " + name + "{")
        if ip_hash:
            upstream.append("ip_hash;")
        for ip in ip_list:
            upstream.append("server " + str(ip) + ":")
        upstream.append("}")
        return upstream

    def create_events(self):
        events = []
        events.append("events{")
        events.append("worker_connections 1024;")
        events.append("}")
        return events

    def generate(self):
        config = []

        config.append("events {")

        config.append(" worker_connections 1024;")

        config.append("}")

        # Jupyter
        config.extend(self.create_upstream("notebook", self._ip_list))
        # API
        config.extend(self.create_upstream("api", self._ip_list))
        # Prometheus
        config.extend(self.create_upstream("prometheus", self._manager))
        # Grafana
        config.extend(self.create_upstream("grafana", self._manager))

        # 80 Server
        config.extend(self.create_server("http"))
        # 443 Server
        config.extend(self.create_server("https"))
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
from gdcmd.helm.values import ValuesYaml
import requests


def deployment_test(path: str, verbose: bool = False):
    def log(msg: str):
        if verbose:
            print(msg)

    def log_error(msg: str):
        print(msg)

    try:
        content = open(path, 'r').read()
        values = ValuesYaml.from_yaml(content)
    except Exception as e:
        log_error(f"Error parsing values file '{path}': \n{e}")
        return

    active_services: list[str] = []

    if values.deploy.link:
        active_services.append(f"http://{values.link.app.host}:{values.link.app.hostPortHttp}")
        if values.appCommon.requireHttps:
            active_services.append(f"https://link-pod:{values.link.app.hostPortHttps}")

    if values.deploy.sync:
        active_services.append(f"http://{values.sync.app.host}:{values.sync.app.hostPortHttp}")
        if values.appCommon.requireHttps:
            active_services.append(f"https://{values.sync.app.host}:{values.sync.app.hostPortHttps}")

    if values.deploy.keycloak:
        active_services.append(f"http://{values.keycloak.host}:{values.keycloak.port}")

    for service in active_services:
        log(f"Checking service {service}...")

        requests_session = requests.Session()
        requests_session.verify = False
        try:
            response = requests_session.get(service, timeout=5)
            if response.status_code != 200:
                log_error(f"Service {service} returned status code {response.status_code}")
            else:
                log(f"Service {service} is up and running.")
        except requests.RequestException as e:
            log_error(f"Error connecting to service {service}: {e}")

    active_metrics: list[str] = []
    if values.metrics.enabled:
        if values.prometheus.nodeExporter:
            active_metrics.append("node-exporter")
        if values.deploy.sync:
            active_metrics.append("sync")
            if values.deploy.db and values.prometheus.databaseExporter:
                active_metrics.append("sync-db")
        if values.deploy.link:
            active_metrics.append("link")
            if values.deploy.db and values.prometheus.databaseExporter:
                active_metrics.append("link-db")

    # TODO: test systemd is working
    # TODO: test promtail is working
    # TODO: test normal logs in containers are working

    # TODO: For db we set memory limits, which can be more than available, test this
    # TODO: Go through the whole helm installation config and check if something is missing
    # TODO: Go through the whole values.yaml and check if something is missing
    print("Deployment successful!")

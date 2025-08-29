from gdcmd.helm.values import ValuesYaml
import requests

VERBOSE = False


def log(msg: str):
    if VERBOSE:
        print(msg)


def log_error(msg: str):
    print(msg)


def deployment_test(path: str, verbose: bool = False):
    global VERBOSE
    VERBOSE = verbose
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

    reseller = values.prometheus.externalLabels.get("reseller", None)

    if not reseller:
        log_error("Prometheus external label 'reseller' is not set, cannot test metrics")
        return

    tenant = values.prometheus.externalLabels.get("tenant", None)
    if not tenant:
        log_error("Prometheus external label 'tenant' is not set, cannot test metrics")
        return

    url = values.prometheus.remoteWrite[0].url
    labels = f'reseller="{reseller}",tenant="{tenant}"'
    u = values.prometheus.remoteWrite[0].username
    p = values.prometheus.remoteWrite[0].password

    if values.metrics.enabled:
        if values.prometheus.nodeExporter:
            test_query_exists(f'node_cpu_seconds_total{{{labels}}}', url, u, p)
        if values.deploy.sync:
            test_query_exists(f'up{{{labels},app="sync"}}', url, u, p)
            if values.deploy.db and values.prometheus.databaseExporter:
                test_query_exists(f'pg_up{{{labels},app="sync"}}', url, u, p)
        if values.deploy.link:
            test_query_exists(f'up{{{labels},app="link"}}', url, u, p)
            if values.deploy.db and values.prometheus.databaseExporter:
                test_query_exists(f'pg_up{{{labels},app="link"}}', url, u, p)

    # TODO: test systemd is working
    # TODO: test promtail is working
    # TODO: test normal logs in containers are working

    # TODO: For db we set memory limits, which can be more than available, test this
    # TODO: Go through the whole helm installation config and check if something is missing
    # TODO: Go through the whole values.yaml and check if something is missing
    print("Deployment successful!")


def test_query_exists(query, remote_write_url, username, password):
    url = remote_write_url.replace("api/prom/push", "api/prom/api/v1/query")
    response = requests.get(url, params={"query": query}, auth=(username, password), timeout=20)

    # Check result
    response.raise_for_status()
    json = response.json()
    if not json.get("data") and not json.get("data").get("result"):
        log_error(f"No result found in the response for user {username} query {query} in {url}")
        log_error(json)
        return

    result = json.get("data", {}).get("result", [])
    if len(result) == 0:
        log_error(f"No results found in the response for user {username} query {query} in {url}")
        log_error(json)
        return

    log(f"Found {len(result)} series for query {query} in {url}")


if __name__ == "__main__":
    VERBOSE = True
    test_query_exists({"query": 'node_cpu_seconds_total{cluster="eg"}'},
                      "https://prometheus-prod-01-eu-west-0.grafana.net/api/prom/push",
                      "772948",
                      "glc_eyJvIjoiNzk0NTA1IiwibiI6InRlc3RpbmctZ2V0dGluZy1tZXRyaWNzLXRlc3QiLCJrIjoiYjEzODgzYTlxZ0NkMFBaNHB4bXhSZDc5IiwibSI6eyJyIjoiZXUifX0="
                      )

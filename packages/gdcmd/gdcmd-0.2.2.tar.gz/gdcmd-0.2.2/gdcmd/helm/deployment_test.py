from gdcmd.helm.values import ValuesYaml


def deployment_test(path: str):
    try:
        content = open(path, 'r').read()
        values = ValuesYaml.from_yaml(content)
    except Exception as e:
        print(f"Error parsing values file '{path}': \n{e}")
        return

    active_services: list[str] = []

    if values.deploy.link:
        active_services.append(f"{values.link.app.host}:{values.link.app.hostPortHttp}")
        if values.appCommon.requireHttps:
            active_services.append(f"link-pod:{values.link.app.hostPortHttps}")

    if values.deploy.sync:
        active_services.append(f"{values.sync.app.host}:{values.sync.app.hostPortHttp}")
        if values.appCommon.requireHttps:
            active_services.append(f"{values.sync.app.host}:{values.sync.app.hostPortHttps}")

    print("Deployment successful!")

from __future__ import annotations
import io
import subprocess
import requests
from requests.auth import HTTPBasicAuth
import yaml
from enum import Enum
from typing import Optional, Annotated
from pydantic import (
    BaseModel,
    Field,
    ValidationError,
    ConfigDict,
    StrictInt, model_validator,
)

from gdcmd.utils.yaml_combiner import YamlCombiner


def list_charts():
    encoded_project = requests.utils.quote("griddot/packages", safe="")
    url = f"https://gitlab.com/api/v4/projects/{encoded_project}/packages/helm/stable/index.yaml"

    # GitLab expects: username = anything (often 'gitlab-ci-token'), password = the token
    auth = HTTPBasicAuth("helm-user", "glpat-mKckaB2sg2vC74xzFWWB")  # or "gitlab-ci-token", token

    response = requests.get(url, auth=auth)
    response.raise_for_status()

    index = yaml.safe_load(response.text)
    charts = list(index.get("entries", {}).keys())
    charts = [f"griddot/{chart}" for chart in charts]
    return charts


def template(deployment: str, values: tuple[str] = None):
    """
    Create a Kubernetes deployment using helm, from the possible deployments in list_helm_charts.
    """
    container_cmd = get_container_command()
    if len(values) > 0:
        values_mount = " ".join([f"-v ./{value}:/{value.split('/')[-1]}" for value in values])
        values_option = "".join([f"-f /{value.split('/')[-1]} " for value in values])
    else:
        values_option = ""
        values_mount = ""

    result = subprocess.run(
        f"{container_cmd} run --rm {values_mount} registry.gitlab.com/griddot/packages/helm:latest helm template {deployment} {values_option}",
        shell=True, check=True, capture_output=True
    )

    return result.stdout.decode('utf-8')


def get_container_command():
    """
    Check if Podman is installed, if not, use Docker.
    Returns the command to use for container operations.
    """
    container_cmd = "podman"
    try:
        subprocess.run("podman --version", shell=True, check=True, capture_output=True)
    except subprocess.CalledProcessError:
        container_cmd = "docker"
    return container_cmd


def lint(deployment: str, values: tuple[str]):
    for value in values:
        try:
            yaml.safe_load(open(value, 'r'))
        except yaml.YAMLError as e:
            raise ValueError(f"YAML parsing error in values file '{value}': {e}")

    combiner = YamlCombiner()
    combiner.set_files(list(values))
    with io.StringIO() as stream:
        combiner.combine(stream)

    combined_values = yaml.safe_load(stream)
    lint_combined_values(combined_values)

    templated_yaml = template(deployment, values)

    try:
        docs = list(yaml.safe_load_all(templated_yaml))
    except yaml.YAMLError as e:
        raise ValueError(f"YAML parsing error: {e}")

    for doc in docs:
        if not isinstance(doc, dict):
            raise ValueError("Each document must be a YAML mapping (dictionary).")
        if 'apiVersion' not in doc or 'kind' not in doc:
            raise ValueError("Each document must contain 'apiVersion' and 'kind' fields.")


def lint_combined_values(y: str):
    class DeployEnv(str, Enum):
        prod = "prod"
        dev = "dev"

    class Region(str, Enum):
        eu = "eu"
        us = "us"
        apac = "apac"

    class ValuesYaml(BaseModel):
        model_config = ConfigDict(extra="forbid")

        name: Annotated[str, Field(min_length=1)]
        replicas: Annotated[StrictInt, Field(ge=1)]
        region: Region
        deploy: bool
        deployEnv: Optional[DeployEnv] = None

        @model_validator(mode="after")
        def additional_checks(self) -> ValuesYaml:
            if self.deploy is True and self.deployEnv is None:
                raise ValueError("deployEnv must be set to 'prod' or 'dev' when deploy is true")
            if self.deploy is False and self.deployEnv is not None:
                raise ValueError("deployEnv must be omitted when deploy is false")
            return self

        @classmethod
        def from_yaml(cls, yaml_str: str) -> ValuesYaml:
            return cls.model_validate(yaml.safe_load(yaml_str))

        def to_yaml(self) -> str:
            return yaml.safe_dump(self.model_dump(mode="json"), sort_keys=False)

    try:
        obj = ValuesYaml.from_yaml(y)

        print(obj.to_yaml())
    except ValidationError as e:
        print(e)


if __name__ == "__main__":
    lint_combined_values("""
            name: web-api
            replicas: 3
            region: eu
            deploy: true
            deployEnv: prod 
        """)

    # This doesnt throw
    lint_combined_values("""
            name: web-api
            replicas: 3
            region: eu
            deploy: true
        """)

    lint_combined_values("""
            name: web-api
            replicas: 3
            region: eu
        """)

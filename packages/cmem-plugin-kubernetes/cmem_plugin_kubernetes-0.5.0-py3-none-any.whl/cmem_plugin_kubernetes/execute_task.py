"""Pod exec workflow task"""

import shlex
from collections.abc import Sequence
from pathlib import Path
from tempfile import NamedTemporaryFile

from cmem_plugin_base.dataintegration.context import ExecutionContext, ExecutionReport
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginAction, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.parameter.code import YamlCode
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import FixedNumberOfInputs, FixedSchemaPort
from cmem_plugin_base.dataintegration.typed_entities.file import FileEntitySchema, LocalFile
from kubernetes.client import CoreV1Api, V1NamespaceList
from kubernetes.config import new_client_from_config
from kubernetes.stream import stream

DEFAULT_CONFIG = YamlCode("")


@Plugin(
    label="Execute a command in a kubernetes pod",
    plugin_id="cmem_plugin_kubernetes-Execute",
    description="Connect to a cluster, execute a command and gather the output.",
    documentation="""
This plugin enables execution of commands inside Kubernetes pods and captures their output.

## Features

- Connects to Kubernetes clusters using kubeconfig
- Executes shell commands in specified pods within namespaces
- Captures both stdout and stderr output
- Returns command output as a file entity for further processing
- Includes namespace listing functionality to verify cluster access

## Output

Command output is captured and returned as a text file entity that can be consumed by
downstream workflow tasks.

## Use Cases

- Running diagnostic commands in production pods
- Executing maintenance scripts
- Gathering system information and logs
- Performing health checks and troubleshooting
    """,
    icon=Icon(package=__package__, file_name="kubernetes.svg"),
    actions=[
        PluginAction(
            name="list_namespaces_action",
            label="List Namespaces",
            description="Check access to the cluster and list namespaces.",
        ),
    ],
    parameters=[
        PluginParameter(
            name="kube_config",
            label="Kube Config",
            description="YAML source code of the kube config.",
        ),
        PluginParameter(
            name="namespace",
            label="Namespace",
            description="Namespaces provide a mechanism for isolating groups of resources.",
        ),
        PluginParameter(
            name="pod",
            label="Pod",
            description="Pods are an abstraction that represent groups of one or more application "
            "containers (such as Docker), and some shared resources for those containers.",
        ),
        PluginParameter(
            name="command",
            label="Command",
            description="The command to execute.",
        ),
    ],
)
class PodExec(WorkflowPlugin):
    """Execute a command in a kubernetes pod"""

    kube_config: str
    namespace: str
    pod: str
    command: str
    output_schema: EntitySchema
    _client: CoreV1Api | None = None

    def __init__(
        self, namespace: str, pod: str, command: str, kube_config: YamlCode = DEFAULT_CONFIG
    ) -> None:
        self.kube_config = kube_config.code
        self.namespace = namespace
        self.pod = pod
        self.command = command
        self.output_schema: FileEntitySchema = FileEntitySchema()
        self.input_ports = FixedNumberOfInputs([])
        self.output_port = FixedSchemaPort(schema=self.output_schema)

    def create_client(self) -> CoreV1Api:
        """Create a kubernetes client"""
        if self.kube_config != "":
            with NamedTemporaryFile() as tmp_file:
                Path(tmp_file.name).write_text(self.kube_config)
                api_client = new_client_from_config(config_file=tmp_file.name)
                return CoreV1Api(api_client=api_client)
        return CoreV1Api()

    @property
    def client(self) -> CoreV1Api:
        """Lazy loaded Kubernetes client"""
        if not self._client:
            self._client = self.create_client()
        return self._client

    def list_namespaces_action(self) -> str:
        """Check access action"""
        namespaces: V1NamespaceList = self.client.list_namespace()
        output = "Client was able to list the following namespaces:\n\n"
        for namespace in namespaces.items:
            output += f"- {namespace.metadata.name}\n"
        return output

    def execute(
        self,
        inputs: Sequence[Entities],  # noqa: ARG002
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        command = shlex.split(self.command)
        self.log.info(f"Execute command {command!s} on pod {self.pod}@{self.namespace}")
        exec_response = stream(
            self.client.connect_get_namespaced_pod_exec,
            name=self.pod,
            namespace=self.namespace,
            command=command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        context.report.update(
            ExecutionReport(
                entity_count=1,
                operation="done",
                operation_desc="command executed",
            )
        )
        with NamedTemporaryFile(mode="w+t", delete=False) as tmp_file:
            tmp_file.write(exec_response)
        file = LocalFile(path=tmp_file.name, mime="text/plain")
        entity = self.output_schema.to_entity(value=file)
        return Entities(
            schema=self.output_schema,
            entities=iter([entity]),
        )

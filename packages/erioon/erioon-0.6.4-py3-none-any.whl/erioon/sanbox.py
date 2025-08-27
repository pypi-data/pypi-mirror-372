# Copyright 2025-present Erioon, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Visit www.erioon.com/dev-docs for more information about the python SDK

import tempfile
import time
from kubernetes import client, config
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
import ast
import time

class Sandbox:
    """
    Erioon sandbox manages running Python code inside an isolated sandbox environment.

    Usage:
    - Call runCode() with Python code to execute inside the sandbox pod.
    - Optionally provide a shell command string to install packages before running the code.

    How it works:
    1. runCode():
       - Checks if the sandbox pod exists and is running:
         - If the sandbox exists but not running, deletes it and waits for deletion.
         - Creates a new pod with the python:3.10-slim image.
       - If package install commands are provided, executes them inside the pod and returns the logs.
       - If code is provided (and no packages or after packages), executes the Python code inside the pod and captures the output.

    Notes:
    - This approach isolates code execution inside ephemeral Kubernetes pods.

    """
    def __init__(self, namespace, sa_name, kubeconfig, sandbox_id, cluster):
        self.namespace = namespace
        self.sa_name = sa_name
        self.kubeconfig = kubeconfig
        self.sandbox_id = sandbox_id
        self.cluster = cluster
        self.console = Console()

        with tempfile.NamedTemporaryFile("w", delete=False) as tmp_kubeconfig:
            tmp_kubeconfig.write(self.kubeconfig)
            self.user_kubeconfig_path = tmp_kubeconfig.name

    def _is_read_only(self):
        return self.cluster == "viewAccess"

    def _read_only_response(self):
        return "[Erioon Error - Sandbox access denied] This user is not allowed to perform any operations in the selected sandbox."

    def _print_header(self, message, style="bold magenta"):
        self.console.print(f"{message}", style=style)

    def runCode(self, code, packages=None):
        if self._is_read_only():
            return self._read_only_response()

        if (not code or code.strip() == "") and (not packages or packages.strip() == ""):
            return ""

        config.load_kube_config(config_file=self.user_kubeconfig_path)
        v1 = client.CoreV1Api()

        pod_exists = False
        pod_running = False

        try:
            pod = v1.read_namespaced_pod(name=self.sandbox_id, namespace=self.namespace)
            pod_exists = True
            if pod.status.phase == "Running":
                pod_running = True
        except ApiException as e:
            if e.status != 404:
                raise

        if not pod_exists or not pod_running:
            if pod_exists:
                v1.delete_namespaced_pod(name=self.sandbox_id, namespace=self.namespace)
                while True:
                    try:
                        v1.read_namespaced_pod(name=self.sandbox_id, namespace=self.namespace)
                        time.sleep(1)
                    except ApiException as e:
                        if e.status == 404:
                            break

            pod_manifest = client.V1Pod(
                metadata=client.V1ObjectMeta(name=self.sandbox_id),
                spec=client.V1PodSpec(
                    containers=[
                        client.V1Container(
                            name="python",
                            image="python:3.10-slim",
                            command=["sh", "-c", "sleep infinity"],
                        )
                    ],
                    restart_policy="Never",
                ),
            )

            v1.create_namespaced_pod(namespace=self.namespace, body=pod_manifest)
            self._print_header(f"Erioon Sandbox '{self.sandbox_id}' is preparing...", style="bold yellow")

            while True:
                pod_status = v1.read_namespaced_pod_status(self.sandbox_id, self.namespace)
                if pod_status.status.phase == "Running":
                    conditions = pod_status.status.conditions or []
                    if any(cond.type == "Ready" and cond.status == "True" for cond in conditions):
                        break
                time.sleep(1)
        else:
            self._print_header(f"Erioon sandbox {self.sandbox_id} is running...", style="bold green")

        if packages and packages.strip() != "":
            self._print_header("Installing user packages...", style="bold cyan")
            self.console.print(packages)
            install_command = ["sh", "-c", packages]
            install_logs = stream(
                v1.connect_get_namespaced_pod_exec,
                self.sandbox_id,
                self.namespace,
                container="python",
                command=install_command,
                stderr=True,
                stdin=False,
                stdout=True,
                tty=False,
            )

            syntax = Syntax(install_logs, "console", theme="monokai", line_numbers=False)
            self.console.print(Panel(syntax, title="Package install logs", expand=True))
            return install_logs

        if not code or code.strip() == "":
            return ""

        exec_command = ["python", "-c", code]
        start_time = time.time()
        resp = stream(
            v1.connect_get_namespaced_pod_exec,
            self.sandbox_id,
            self.namespace,
            container="python",
            command=exec_command,
            stderr=True,
            stdin=False,
            stdout=True,
            tty=False,
        )
        end_time = time.time()
        elapsed = end_time - start_time
        elapsed_str = (
            f"{elapsed:.2f} sec" if elapsed < 60 else f"{elapsed/60:.2f} min"
        )

        self.console.print(f"[bold cyan]Erioon sandbox output ({elapsed_str}):[/bold cyan]")
        result = ast.literal_eval(resp)
        self.console.print(result)
        

        return result

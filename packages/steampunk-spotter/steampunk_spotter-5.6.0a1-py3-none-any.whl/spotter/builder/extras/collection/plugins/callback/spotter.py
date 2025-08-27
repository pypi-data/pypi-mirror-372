# -*- coding: utf-8 -*-
# (C) 2024 Jure Medvesek (jure.medvesek@xlab.si)
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

# pylint: skip-file
# type: ignore
from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
    author: Jure Medvesek (jure.medvesek@xlab.si)
    name: spotter
    type: notification
    requirements: []
    short_description: Sends task to Spotter
    description:
        - This callback sends data to Spotter
        - If Spotter says so executon of playbook is stopped
    options:
      spotter_token:
        description: Token to be used
        env:
          - name: SPOTTER_TOKEN
        ini:
          - section: callback_spotter
            key: spotter_token
        type: str
      spotter_endpoint:
        description: Override the Steampunk Spotter service's API endpoint
        env:
          - name: SPOTTER_ENDPOINT
        ini:
          - section: callback_spotter
            key: spotter_endpoint
        type: str
        default: "https://api.spotter.steampunk.si:443/api"
      spotter_organization:
        description: Organization that scan should be executed on behalf of
        env:
          - name: SPOTTER_ORGANIZATION
        ini:
          - section: callback_spotter
            key: spotter_organization
        type: str
      spotter_project:
        description: Project that scan should be executed into
        env:
          - name: SPOTTER_PROJECT
        ini:
          - section: callback_spotter
            key: spotter_project
        type: str
      spotter_minimal_fail_level:
        description: Threshold for the overall scan result to be considered scan failure. Choices are ["success", "hint", "warning", "error"]
        env:
          - name: SPOTTER_MINIMAL_FAIL_LEVEL
        ini:
          - section: callback_spotter
            key: spotter_minimal_fail_level
        type: str
      spotter_insecure:
        description: Skip server certificate verfication
        env:
          - name: SPOTTER_INSECURE
        ini:
          - section: callback_spotter
            key: spotter_insecure
        type: bool
"""


import enum
import json
import os
import sys
import ssl
import http.client
import uuid

from subprocess import Popen, PIPE
from urllib.parse import urlparse

from ansible.plugins.callback import CallbackBase
from ansible.utils.display import Display
from ansible.template import Templar


def get_result_from_process(command):
    with Popen(command, stdout=PIPE) as process:
        _, _ = process.communicate()
        exit_code = process.wait()
    return exit_code


# needs to have spotter and all its python dependencies installed
def call_spotter(playbook):
    command = ["spotter", "scan", playbook]
    return get_result_from_process(command)


def evaluate(key, value, templar, depth=0):
    implicit_jinja_fields = ["when", "failed_when", "changed_when"]

    # artificial cut to awoid cycles
    if depth > 4:
        return value

    # Also some actions are not evaluated, since we need to know all special cases
    # ansible.builtin.debug:
    #   var: item
    if isinstance(value, str):
        if ("{{" in value) or ("{%" in value) or ("{#" in value):
            return templar.template(value)
        elif depth == 1 and key in implicit_jinja_fields:
            return templar.template("{{ " + value + " }}")
    elif isinstance(value, dict):
        return {k: evaluate(k, v, templar, depth + 1) for k, v in value.items()}
    elif isinstance(value, list):
        return [evaluate(None, v, templar, depth + 1) for v in value]
    return value


class ScanAction(enum.Enum):
    CREATE = "create"
    ATTACH_ITEM = "attach_item"
    COMPLETED = "complete"


scan_levels = {"success": 0, "hint": 1, "warning": 2, "error": 3}


def aap_data_from_env_variables():
    job_id = os.environ.get("JOB_ID")
    inventory_id = os.environ.get("INVENTORY_ID")
    project_revision = os.environ.get("PROJECT_REVISION")
    if not job_id:
        return None
    return {
        "job_id": job_id,
        "inventory_id": inventory_id,
        "project_revision": project_revision,
    }


class SpotterClient:
    def __init__(
        self,
        spotter_api_token,
        spotter_endpoint,
        spotter_organization,
        spotter_project,
        minimal_fail_level,
        spotter_insecure,
    ):
        self.endpoint = f"/api/v2/organizations/{spotter_organization}/projects/{spotter_project}/scan_runtime/"

        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"SPTKN {spotter_api_token}",
        }

        url_parts = urlparse(spotter_endpoint)
        self.host = url_parts.hostname
        self.port = url_parts.port
        self.client = (
            http.client.HTTPSConnection if url_parts.scheme in ["HTTPS", "https"] else http.client.HTTPConnection
        )
        self.minimal_fail_level = minimal_fail_level
        self.spotter_insecure = spotter_insecure
        self.uuid = self.on_playbook_start_callback()

    def http_call(self, payload, action):
        if action == ScanAction.CREATE:
            endpoint = self.endpoint
        elif action == ScanAction.ATTACH_ITEM:
            endpoint = f"{self.endpoint}{self.uuid}/attach_item/"
        elif action == ScanAction.COMPLETED:
            endpoint = f"{self.endpoint}{self.uuid}/completed/"

        body = json.dumps(payload)

        if self.spotter_insecure:
            conn = self.client(self.host, self.port, context=ssl._create_unverified_context())  # nosec
        else:
            conn = self.client(self.host, self.port)

        conn.request("POST", endpoint, body=body, headers=self.headers)
        response = conn.getresponse()
        if response.status not in [200, 201]:
            print(f"SPOTTER request failed: {response.status}")
            print(response.read())
            return None
        return response.read()

    def on_task_callback(self, packed, position, play_uuid) -> bool:
        payload = {
            "tasks": [
                {
                    "task_id": str(uuid.uuid4()),
                    "play_id": play_uuid,
                    "task_args": packed,
                    "spotter_metadata": position,
                    # TODO - obfuscate
                    "spotter_obfuscated": [],
                    # TODO - parsing this part is not trivial
                    "spotter_noqa": [],
                }
            ],
            "playbooks": [],
        }
        response = self.http_call(payload, ScanAction.ATTACH_ITEM)
        if not response:
            return False

        response_data = json.loads(response)
        status = scan_levels[response_data["status"]]
        if status < self.minimal_fail_level:
            return True

        for element in response_data["elements"]:
            if scan_levels[element["level"]] < self.minimal_fail_level:
                continue
            code = (
                f"{element['event_code']}::{element['event_subcode']}"
                if element["event_subcode"]
                else element["event_code"]
            )
            print(
                f"{element['filename']}:{element['line_number']} {element['level'].upper()} {code} {element['message']}"
            )
        return False

    def on_playbook_start_callback(self):
        # TODO: read actual environment - this should happen once per scan anyway
        # maybe we can also install spotter (as python dependency), and then use scan -e export.json
        # functionality, read a file and just send up environment part ...
        payload = {
            "environment": {
                "python_version": sys.version,
                "ansible_version": {
                    # TODO: ansible --version
                    "ansible_core": "2.13.4",
                    "ansible_base": None,
                    "ansible": None,
                },
                # TODO: ansible-galaxy collection list
                "installed_collections": [],
                # TODO: ansible-config dump --only-changed
                "ansible_config": {},
                "galaxy_yml": {},
                # TODO: requirements.yml
                "collection_requirements": {},
                "cli_scan_args": {
                    "parse_values": True,
                    "include_values": True,
                    "include_metadata": True,
                    "rewrite": False,
                    "display_level": "hint",
                    "profile": "default",
                    "skip_checks": [],
                    "enforce_checks": [],
                    "version": "3.1.1",
                    "origin": "ci",
                },
                "aap_data": aap_data_from_env_variables(),
            },
        }
        response = self.http_call(payload, ScanAction.CREATE)
        if not response:
            return None
        response_data = json.loads(response)
        return response_data["uuid"]

    def on_exit(self):
        self.http_call(None, ScanAction.COMPLETED)

    def on_complete(self):
        self.http_call(None, ScanAction.COMPLETED)


class CallbackModule(CallbackBase):
    """Spotter."""

    CALLBACK_VERSION = "1.0"
    CALLBACK_TYPE = "notification"
    CALLBACK_NAME = "xlab.ee.spotter"
    CALLBACK_NEEDS_WHITELIST = False

    DEFAULT_ERROR_EXIT_CODE = 99

    def __init__(self, display: Display = None, options=None):
        super(CallbackModule, self).__init__(display=display)
        self.client = None

    def set_options(self, task_keys=None, var_options=None, direct=None):
        super(CallbackModule, self).set_options(task_keys=task_keys, var_options=var_options, direct=direct)

        spotter_api_token = self.get_option("spotter_token")
        spotter_endpoint = self.get_option("spotter_endpoint")
        spotter_organization = self.get_option("spotter_organization")
        spotter_project = self.get_option("spotter_project")
        spotter_minimal_fail_level = self.get_option("spotter_minimal_fail_level")
        spotter_insecure = self.get_option("spotter_insecure")

        # Validation is here intentionally
        #
        # Default ansible resolution for invalid configuration is to skip callback.
        # Our intent is to stop playbook execution in this case.
        if not spotter_api_token:
            self._display.error(
                "Spotter HTTP collector requires an API"
                "token. The Spotter HTTP collector "
                "API token can be provided using the "
                "`SPOTTER_TOKEN` environment variable or "
                "in the ansible.cfg file."
            )
            sys.exit(self.DEFAULT_ERROR_EXIT_CODE)

        if not spotter_organization:
            self._display.error("Spotter organization must be set.")
            sys.exit(self.DEFAULT_ERROR_EXIT_CODE)

        if not spotter_project:
            self._display.error("Spotter project must be set.")
            sys.exit(self.DEFAULT_ERROR_EXIT_CODE)

        if spotter_minimal_fail_level is not None:
            try:
                minimal_fail_level = scan_levels[spotter_minimal_fail_level]
            except KeyError:
                self._display.error(
                    f"Spotter minimal fail level must be one of: {scan_levels.keys()}. Current value is {spotter_minimal_fail_level}."
                )
                sys.exit(self.DEFAULT_ERROR_EXIT_CODE)
        else:
            minimal_fail_level = scan_levels["error"]

        try:
            self.client = SpotterClient(
                spotter_api_token,
                spotter_endpoint,
                spotter_organization,
                spotter_project,
                minimal_fail_level,
                spotter_insecure,
            )
            if self.client.uuid == None:
                sys.exit(self.DEFAULT_ERROR_EXIT_CODE)
        except Exception as ex:
            # TODO: should we show endpoint, project and organization?
            self._display.error(str(ex))
            self._display.error("Spotter can not reach server.")
            sys.exit(self.DEFAULT_ERROR_EXIT_CODE)
        self._display.display("Spotter runtime checks enabled.")

    def v2_playbook_on_start(self, playbook):
        real_path = os.path.join(playbook._basedir, playbook._file_name)
        self._display.display(f"Scanning playbook with Spotter: { real_path }")

        # TODO: here we can implement preflight checks without tampering EE entrypoint
        # One option is to run "spotter scan -e <playbook folder>" but then spotter is python dependency
        pass

    def v2_playbook_on_play_start(self, play):
        # TODO Report play data up - there are some play checks
        # Problem is execution of scan:
        #  - if attach for each task - play errors will be returned for each task
        #  - if not attach opa tests that test pairwise (task + play) will not have any play data
        pass

    def v2_playbook_on_stats(self, stats):
        self.client.on_complete()

    def v2_runner_on_start(self, host, task):
        """Event used when host begins execution of a task

        .. versionadded:: 2.8
        """

        def test_iteration(self, task, task_vars):
            templar = Templar(loader=task._loader, variables=task_vars)
            evaluated = evaluate(None, task.args, templar, 0)

            # get position
            ansible_pos = task._ds.ansible_pos
            position = {
                "file": os.path.relpath(ansible_pos[0]),
                "line": ansible_pos[1],
                "column": ansible_pos[2],
                "start_mark_index": 0,
                "end_mark_index": 0,
            }

            # get top level attributes
            action = task.action
            name = task.name

            # test with spotter
            packed = {"name": name, action: evaluated}

            play_uuid = task.play._uuid
            result = self.client.on_task_callback(packed, position, play_uuid)
            if not result:
                self._display.error("Gated with Spotter")
                self.client.on_complete()
                sys.exit(self.DEFAULT_ERROR_EXIT_CODE)

        if not task._variable_manager or not hasattr(task, "_ds"):
            return

        # evaluate vars
        task_vars = task._variable_manager.get_vars(task=task, play=task.play, host=host)
        if not task.loop:
            test_iteration(self, task, task_vars)
            return

        for item in task.loop:
            cloned_task_vars = dict(task_vars)
            cloned_task_vars[task.loop_control.loop_var] = item
            test_iteration(self, task, cloned_task_vars)

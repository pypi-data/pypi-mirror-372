"""
  BYOSnap CLI commands
"""
import base64
from binascii import Error as BinasciiError
import json
import os
import re
import time
import subprocess
import platform as sys_platform
from sys import platform
from typing import Union, List
import importlib.resources as pkg_resources
import requests
from requests.exceptions import RequestException
import yaml
from rich.progress import Progress, SpinnerColumn, TextColumn
from snapctl.commands.snapend import Snapend
from snapctl.config.constants import SERVER_CALL_TIMEOUT
from snapctl.config.constants import HTTP_ERROR_SERVICE_VERSION_EXISTS, \
    HTTP_ERROR_TAG_NOT_AVAILABLE, HTTP_ERROR_ADD_ON_NOT_ENABLED, SNAPCTL_INPUT_ERROR, \
    SNAPCTL_BYOSNAP_DEPENDENCY_MISSING, SNAPCTL_BYOSNAP_ECR_LOGIN_ERROR, \
    SNAPCTL_BYOSNAP_BUILD_ERROR, SNAPCTL_BYOSNAP_TAG_ERROR, SNAPCTL_BYOSNAP_PUBLISH_IMAGE_ERROR, \
    SNAPCTL_BYOSNAP_PUBLISH_IMAGE_DUPLICATE_TAG_ERROR, \
    SNAPCTL_BYOSNAP_CREATE_DUPLICATE_NAME_ERROR, SNAPCTL_BYOSNAP_CREATE_PERMISSION_ERROR, \
    SNAPCTL_BYOSNAP_CREATE_ERROR, SNAPCTL_BYOSNAP_PUBLISH_VERSION_DUPLICATE_TAG_ERROR, \
    SNAPCTL_BYOSNAP_PUBLISH_VERSION_ERROR, HTTP_ERROR_SERVICE_IN_USE, \
    SNAPCTL_BYOSNAP_UPDATE_VERSION_ERROR, SNAPCTL_BYOSNAP_UPDATE_VERSION_SERVICE_IN_USE_ERROR, \
    SNAPCTL_BYOSNAP_UPDATE_VERSION_TAG_ERROR, SNAPCTL_BYOSNAP_NOT_FOUND, \
    HTTP_ERROR_RESOURCE_NOT_FOUND, SNAPCTL_BYOSNAP_PUBLISH_ERROR, \
    SNAPCTL_BYOSNAP_GENERATE_PROFILE_ERROR, SNAPCTL_CONFIGURATION_INCORRECT
from snapctl.utils.echo import info, warning, success
from snapctl.utils.helper import get_composite_token, snapctl_error, snapctl_success, \
    check_dockerfile_architecture, check_use_containerd_snapshotter
import snapctl.data.profiles


class ByoSnap:
    """
      CLI commands exposed for a BYOSnap
    """
    ID_PREFIX = 'byosnap-'
    # These are active today
    SUBCOMMANDS = [
        'publish', 'sync', 'upload-docs', 'generate-profile', 'validate-profile',
        'create', 'publish-image', 'publish-version', 'update-version',
    ]
    # These are the real commands that we want to show in the help text
    SHOW_SUBCOMMANDS = ['publish', 'sync', 'upload-docs',
                        'generate-profile', 'validate-profile']
    # These are the commands that we want to deprecate
    TO_DEPRECATE_SUBCOMMANDS = [
        'create', 'publish-image', 'publish-version', 'update-version']
    DEFAULT_PROFILE_NAME_JSON = 'snapser-byosnap-profile.json'
    DEFAULT_PROFILE_NAME_YML = 'snapser-byosnap-profile.yml'
    DEFAULT_PROFILE_NAME_YAML = 'snapser-byosnap-profile.yaml'
    PROFILE_FORMATS = ['json', 'yaml', 'yml']
    PLATFORMS = ['linux/arm64', 'linux/amd64']
    LANGUAGES = ['go', 'node', 'python', 'java', 'csharp', 'cpp', 'rust',
                 'ruby', 'php', 'perl', 'clojure', 'lua', 'ts', 'js', 'kotlin', 'c']
    DEFAULT_BUILD_PLATFORM = 'linux/arm64'
    SID_CHARACTER_LIMIT = 47
    TAG_CHARACTER_LIMIT = 80
    VALID_CPU_MARKS = [100, 250, 500, 750, 1000, 1500, 2000, 3000]
    VALID_MEMORY_MARKS = [0.125, 0.25, 0.5, 1, 2, 3, 4]
    MAX_READINESS_TIMEOUT = 30
    MAX_MIN_REPLICAS = 4
    INTERNAL_PORT_NAME_CHAR_LIMIT = 15

    def __init__(
        self, *, subcommand: str, base_url: str, api_key: Union[str, None], byosnap_id: str,
        name: Union[str, None] = None, desc: Union[str, None] = None,
        platform_type: Union[str, None] = None, language: Union[str, None] = None,
        tag: Union[str, None] = None, path: Union[str, None] = None,
        resources_path: Union[str, None] = None,  docker_filename: Union[str, None] = None,
        version: Union[str, None] = None, skip_build: bool = False,
        snapend_id: Union[str, None] = None, blocking: bool = False,
        profile_filename: Union[str, None] = None,
        out_path: Union[str, None] = None
    ) -> None:
        # Set the BASE variables
        self.subcommand: str = subcommand
        self.base_url: str = base_url
        self.api_key: Union[str, None] = api_key
        self.byosnap_id: str = byosnap_id
        self.tag: Union[str, None] = tag
        # Remote tag is overridden in publish and sync
        self.remote_tag: Union[str, None] = tag
        self.path: Union[str, None] = path
        self.resources_path: Union[str, None] = resources_path
        self.docker_filename: str = docker_filename
        self.docker_path_filename: Union[str, None] = ByoSnap._make_dockerfile_path(
            path, resources_path, docker_filename
        )
        self.profile_filename: Union[str, None] = profile_filename
        self.version: Union[str, None] = version
        self.name: Union[str, None] = name
        self.desc: Union[str, None] = desc
        self.platform_type: Union[str, None] = platform_type
        self.language: Union[str, None] = language
        self.snapend_id: Union[str, None] = snapend_id
        self.skip_build: bool = skip_build
        self.blocking: bool = blocking
        self.out_path: Union[str, None] = out_path
        # Values below will be overridden
        self.token: Union[str, None] = None
        self.token_parts: Union[list, None] = None
        self.profile_path: Union[str, None] = None
        self.profile_data: Union[dict, None] = None
        # These variables are here because of backward compatibility
        # We now takes these inputs from the BYOSnap profile
        self.prefix: Union[str, None] = None
        self.ingress_external_port: Union[dict, None] = None
        self.ingress_internal_ports: Union[list, None] = None
        self.readiness_path: Union[str, None] = None
        self.readiness_delay: Union[str, None] = None
        # Setup and Validate the input
        self.validate_input()

    # Protected methods
    @staticmethod
    def _make_dockerfile_path(path: str, resources_path: str, docker_filename: str) -> Union[str, None]:
        """
        Check for the existence of a Dockerfile in the given `path` and `resources_path`.
        Returns the path where the Dockerfile is found, or an empty string if not found.
        """
        # Check the primary path
        if path and os.path.isfile(os.path.join(path, docker_filename)):
            return os.path.join(path, docker_filename)

        # Check the resources path
        if resources_path and os.path.isfile(os.path.join(resources_path, docker_filename)):
            return os.path.join(resources_path, docker_filename)

        # Return empty string if not found in either location
        return None

    @staticmethod
    def _get_token_values(token: str) -> Union[None, List]:
        """
          Method to break open the token
        """
        try:
            input_token = base64.b64decode(token).decode('ascii')
            parts = input_token.split('|')
            # url|web_app_token|service_id|ecr_repo_url|ecr_repo_username|ecr_repo_token
            # url = self.token_parts[0]
            # web_app_token = self.token_parts[1]
            # service_id = self.token_parts[2]
            # ecr_repo_url = self.token_parts[3]
            # ecr_repo_username = self.token_parts[4]
            # ecr_repo_token = self.token_parts[5]
            # platform = self.token_parts[6]
            if len(parts) >= 3:
                return parts
        except BinasciiError:
            pass
        return None

    @staticmethod
    def _validate_byosnap_profile_data(profile_data) -> None:
        # Check for the parent fields
        for field in ['name', 'description', 'platform', 'language', 'prefix',
                      'readiness_probe_config', 'dev_template', 'stage_template', 'prod_template']:
            if field not in profile_data:
                snapctl_error(
                    message=f'BYOSnap profile requires {field} field. ' +
                    'Please use the following command: ' +
                    '`snapctl byosnap generate-profile --out-path $output_path` ' +
                    'to generate a new profile',
                    code=SNAPCTL_INPUT_ERROR
                )
        # Check for backward compatible fields
        if 'http_port' not in profile_data and 'ingress' not in profile_data:
            snapctl_error(
                message='BYOSnap profile requires an ingress field with external_port and ' +
                'internal_port as children. Note: http_port is going to be deprecated soon. ' +
                'Please use the following command: ' +
                '`snapctl byosnap generate-profile --out-path $output_path` ' +
                'to generate a new profile',
                code=SNAPCTL_INPUT_ERROR
            )
        # Name Check
        if profile_data['name'] is None or profile_data['name'].strip() == '':
            snapctl_error(
                message='BYOSnap profile requires a non empty name value. ' +
                'Please use the following command: ' +
                '`snapctl byosnap generate-profile --out-path $output_path` ' +
                'to generate a new profile',
                code=SNAPCTL_INPUT_ERROR
            )
        # Description Check
        if profile_data['description'] is None or profile_data['description'].strip() == '':
            snapctl_error(
                message='BYOSnap profile requires a non empty description value. ' +
                'Please use the following command: ' +
                '`snapctl byosnap generate-profile --out-path $output_path` ' +
                'to generate a new profile',
                code=SNAPCTL_INPUT_ERROR
            )
        # Platform Check
        if profile_data['platform'] is None or \
                profile_data['platform'].strip() not in ByoSnap.PLATFORMS:
            snapctl_error(
                message='Invalid platform value in BYOSnap profile. Valid values are ' +
                f'{", ".join(map(str, ByoSnap.PLATFORMS))}.',
                code=SNAPCTL_INPUT_ERROR
            )
        # Language Check
        if profile_data['language'] is None or profile_data['language'].strip() == '':
            snapctl_error(
                message='BYOSnap profile requires a non empty language value. ' +
                'Please use the following command: ' +
                '`snapctl byosnap generate-profile --out-path $output_path` ' +
                'to generate a new profile',
                code=SNAPCTL_INPUT_ERROR
            )
        # Prefix Checks
        if profile_data['prefix'] is None or profile_data['prefix'].strip() == '':
            snapctl_error(
                message='BYOSnap profile requires a non empty prefix value. ' +
                'Please use the following command: ' +
                '`snapctl byosnap generate-profile --out-path $output_path` ' +
                'to generate a new profile',
                code=SNAPCTL_INPUT_ERROR
            )
        if not profile_data['prefix'].strip().startswith('/') or \
                profile_data['prefix'].strip().endswith('/') or \
                profile_data['prefix'].strip().count('/') > 1:
            snapctl_error(
                message='Invalid prefix value in BYOSnap profile. ' +
                'Prefix should start with a forward slash (/) and should contain exactly one ' +
                'path segment.',
                code=SNAPCTL_INPUT_ERROR
            )
        # HTTP Port and Ingress Checks
        if 'http_port' in profile_data:
            if profile_data['http_port'] is None or \
                    not isinstance(profile_data['http_port'], int):
                snapctl_error(
                    message='Invalid http_port value in BYOSnap profile. ' +
                    'HTTP port should be a number.',
                    code=SNAPCTL_INPUT_ERROR
                )
            warning('http_port is deprecated. Please use ingress.external_port. ' +
                    'You can generate a new BYOSnap profile via the `generate` command.')
        # Ingress Checks
        if 'ingress' in profile_data:
            if profile_data['ingress'] is None:
                snapctl_error(
                    message='BYOSnap profile requires an ingress field with external_port and ' +
                    'internal_port as children. Please use the following command: ' +
                    '`snapctl byosnap generate-profile --out-path $output_path` ' +
                    'to generate a new profile',
                    code=SNAPCTL_INPUT_ERROR
                )
            if 'external_port' not in profile_data['ingress']:
                snapctl_error(
                    message='BYOSnap profile requires an ingress.external_port field. ' +
                    'Please use the following command: ' +
                    '`snapctl byosnap generate-profile --out-path $output_path` ' +
                    'to generate a new profile',
                    code=SNAPCTL_INPUT_ERROR
                )
            if 'name' not in profile_data['ingress']['external_port'] or \
                    profile_data['ingress']['external_port']['name'] != 'http':
                snapctl_error(
                    message='Invalid Ingress external_port value in BYOSnap profile. ' +
                    'External port should have a name of http and a number port value.',
                    code=SNAPCTL_INPUT_ERROR
                )
            if 'port' not in profile_data['ingress']['external_port'] or \
                profile_data['ingress']['external_port']['port'] is None or \
                    not isinstance(profile_data['ingress']['external_port']['port'], int):
                snapctl_error(
                    message='Invalid Ingress external_port value in BYOSnap profile. ' +
                    'External port should have a name of http and a number port value.',
                    code=SNAPCTL_INPUT_ERROR
                )
            if 'internal_ports' not in profile_data['ingress'] or \
                    not isinstance(profile_data['ingress']['internal_ports'], list):
                snapctl_error(
                    message='Invalid Ingress internal_port value in BYOSnap profile. ' +
                    'Internal port should be an empty list or a list of objects with name and ' +
                    'port values.',
                    code=SNAPCTL_INPUT_ERROR
                )
            duplicate_name = {}
            duplicate_port = {}
            index = 0
            for internal_port_obj in profile_data['ingress']['internal_ports']:
                index += 1
                if 'name' not in internal_port_obj or 'port' not in internal_port_obj:
                    snapctl_error(
                        message='Invalid Ingress internal_port value in BYOSnap profile. ' +
                        'Internal port should be an object with name and port values. ' +
                        f"Check the internal port number #{index}.",
                        code=SNAPCTL_INPUT_ERROR
                    )
                if len(internal_port_obj['name']) > ByoSnap.INTERNAL_PORT_NAME_CHAR_LIMIT:
                    snapctl_error("Internal port name should be less than " +
                                  f"{ByoSnap.INTERNAL_PORT_NAME_CHAR_LIMIT} characters. " +
                                  f"Check internal port number {index}.",
                                  SNAPCTL_INPUT_ERROR)
                if internal_port_obj['name'] is None or internal_port_obj['name'].strip() == '':
                    snapctl_error(
                        message='Invalid Ingress internal_port value in BYOSnap profile. ' +
                        'Internal port name should not be empty. ' +
                        f"Check the internal port number #{index}.",
                        code=SNAPCTL_INPUT_ERROR
                    )
                if internal_port_obj['port'] is None or \
                        not isinstance(internal_port_obj['port'], int):
                    snapctl_error(
                        message='Invalid Ingress internal_port value in BYOSnap profile. ' +
                        'Internal port port should be a number. ' +
                        f"Check the internal port number #{index}.",
                        code=SNAPCTL_INPUT_ERROR
                    )
                # Confirm the name does not collide with the external port
                if internal_port_obj['name'] == profile_data['ingress']['external_port']['name']:
                    snapctl_error("Internal port name should not be the same as " +
                                  "the external port name. " +
                                  f"Check the internal port number #{index}.",
                                  SNAPCTL_INPUT_ERROR)
                if internal_port_obj['port'] == profile_data['ingress']['external_port']['port']:
                    snapctl_error("Internal port number should not be the same as " +
                                  "the external port number. " +
                                  f"Check the internal port number #{index}.",
                                  SNAPCTL_INPUT_ERROR)
                if internal_port_obj['name'] in duplicate_name:
                    snapctl_error("Duplicate internal port name. " +
                                  f"Check the internal port number #{index}.",
                                  SNAPCTL_INPUT_ERROR)
                if internal_port_obj['port'] in duplicate_port:
                    snapctl_error("Duplicate internal port number. " +
                                  f"Check the internal port number #{index}.",
                                  SNAPCTL_INPUT_ERROR)
                duplicate_name[internal_port_obj['name']] = True
                duplicate_port[internal_port_obj['port']] = True
        # Readiness Probe Checks
        if 'readiness_probe_config' not in profile_data:
            snapctl_error(
                message='BYOSnap profile requires a readiness_probe_config field. ' +
                'Please use the following command: ' +
                '`snapctl byosnap generate-profile --out-path $output_path` ' +
                'to generate a new profile',
                code=SNAPCTL_INPUT_ERROR
            )
        if 'initial_delay_seconds' not in profile_data['readiness_probe_config'] or \
                'path' not in profile_data['readiness_probe_config']:
            snapctl_error(
                message='Invalid readiness_probe_config value in BYOSnap profile. ' +
                'Readiness probe config should have an initial_delay_seconds and path value. ' +
                'Set both to null if not required.',
                code=SNAPCTL_INPUT_ERROR
            )
        if (profile_data['readiness_probe_config']['initial_delay_seconds'] is None and
            profile_data['readiness_probe_config']['path'] is not None) or \
                (profile_data['readiness_probe_config']['initial_delay_seconds'] is not None and
                 profile_data['readiness_probe_config']['path'] is None):
            snapctl_error(
                message='Invalid readiness_probe_config value in BYOSnap profile. ' +
                'Readiness probe config should have both initial_delay_seconds and path values. ' +
                'One of them cannot be null. However, set both to null if not required.',
                code=SNAPCTL_INPUT_ERROR
            )
        if profile_data['readiness_probe_config']['path'] is not None is not None:
            if profile_data['readiness_probe_config']['path'].strip() == '':
                snapctl_error(
                    "Invalid readiness_probe_config.path value. Readiness path cannot be empty",
                    SNAPCTL_INPUT_ERROR)
            if not profile_data['readiness_probe_config']['path'].strip().startswith('/'):
                snapctl_error(
                    "Invalid readiness_probe_config.path value. Readiness path has to start with /",
                    SNAPCTL_INPUT_ERROR)
        if profile_data['readiness_probe_config']['initial_delay_seconds'] is not None:
            if not isinstance(profile_data['readiness_probe_config']['initial_delay_seconds'], int) or \
               profile_data['readiness_probe_config']['initial_delay_seconds'] < 0 or \
               profile_data['readiness_probe_config']['initial_delay_seconds'] > ByoSnap.MAX_READINESS_TIMEOUT:
                snapctl_error(
                    "Invalid readiness_probe_config.path value. " +
                    "Readiness delay should be between 0 " +
                    f"and {ByoSnap.MAX_READINESS_TIMEOUT}", SNAPCTL_INPUT_ERROR)
        # Template Object Checks
        if 'dev_template' not in profile_data or \
            'stage_template' not in profile_data or \
                'prod_template' not in profile_data:
            snapctl_error(
                message='Invalid BYOSnap profile JSON. Please check the JSON structure',
                code=SNAPCTL_INPUT_ERROR
            )
        for profile in ['dev_template', 'stage_template', 'prod_template']:
            # IMPORTANT: Not checking for in min_replicas for backward compatibility
            for field in ['cpu', 'memory', 'cmd', 'args', 'env_params']:
                if field not in profile_data[profile]:
                    snapctl_error(
                        message='Invalid BYOSnap profile JSON. ' +
                        f'{profile} requires cpu, memory, min_replicas, cmd, args, and ' +
                        'env_params fields.',
                        code=SNAPCTL_INPUT_ERROR
                    )
            if profile_data[profile]['cpu'] is None or \
                    profile_data[profile]['cpu'] not in ByoSnap.VALID_CPU_MARKS:
                snapctl_error(
                    message='Invalid CPU value in BYOSnap profile. Valid values are' +
                    f'{", ".join(map(str, ByoSnap.VALID_CPU_MARKS))}.',
                    code=SNAPCTL_INPUT_ERROR
                )
            if profile_data[profile]['memory'] is None or \
                    profile_data[profile]['memory'] not in ByoSnap.VALID_MEMORY_MARKS:
                snapctl_error(
                    message='Invalid Memory value in BYOSnap profile. Valid values are ' +
                    f'{", ".join(map(str, ByoSnap.VALID_MEMORY_MARKS))}.',
                    code=SNAPCTL_INPUT_ERROR
                )
            if 'min_replicas' in profile_data[profile] and \
                profile_data[profile]['min_replicas'] is not None and \
                (not isinstance(profile_data[profile]['min_replicas'], int) or
                    profile_data[profile]['min_replicas'] < 0 or
                 profile_data[profile]['min_replicas'] > ByoSnap.MAX_MIN_REPLICAS):
                snapctl_error(
                    message='Invalid Min Replicas value in BYOSnap profile. ' +
                    'Minimum replicas should be between 0 and ' +
                    f'{ByoSnap.MAX_MIN_REPLICAS}',
                    code=SNAPCTL_INPUT_ERROR
                )
            if 'min_replicas' in profile_data[profile] and \
                profile_data[profile]['min_replicas'] is not None and \
                isinstance(profile_data[profile]['min_replicas'], int) and \
                profile_data[profile]['min_replicas'] > 1 and \
                    (profile == 'dev_template' or profile == 'stage_template'):
                snapctl_error(
                    message='Invalid Min Replicas value in BYOSnap profile. ' +
                    'Minimum replicas should be 1 for dev and stage templates.',
                    code=SNAPCTL_INPUT_ERROR
                )

            if profile_data[profile]['cmd'] is None:
                snapctl_error(
                    message='Invalid CMD value in BYOSnap profile. CMD should not be an ' +
                    'empty string or the command you want to run in the container.',
                    code=SNAPCTL_INPUT_ERROR
                )
            if profile_data[profile]['args'] is None or \
                    not isinstance(profile_data[profile]['args'], list):
                snapctl_error(
                    message='Invalid ARGS value in BYOSnap profile. ARGS should be a ' +
                    'list of arguments or an empty list if no arguments are required.',
                    code=SNAPCTL_INPUT_ERROR
                )
            if profile_data[profile]['env_params'] is None or \
                    not isinstance(profile_data[profile]['env_params'], list):
                snapctl_error(
                    message='Invalid env_params value in BYOSnap profile. env_params should be a ' +
                    'list of environment variables as a dict with key and value attribute. ' +
                    'It can be  an empty list if no environment variables are required.',
                    code=SNAPCTL_INPUT_ERROR
                )
            env_index = 0
            for env_param in profile_data[profile]['env_params']:
                env_index += 1
                if 'key' not in env_param or 'value' not in env_param:
                    snapctl_error(
                        message='Invalid env_params value in BYOSnap profile. env_params should ' +
                        'be a list of environment variables as a dict with key and value ' +
                        'attribute. It can be an empty list if no environment variables ' +
                        'are required. ' +
                        f"Check the entry {profile}.env_params #{env_index}.",
                        code=SNAPCTL_INPUT_ERROR
                    )
                if env_param['key'] is None or env_param['key'].strip() == '':
                    snapctl_error(
                        message='Invalid env_params value in BYOSnap profile. env_params key ' +
                        'should not be empty. ' +
                        f"Check the key entry at {profile}.env_params #{env_index}.",
                        code=SNAPCTL_INPUT_ERROR
                    )
                if env_param['value'] is None or env_param['value'].strip() == '':
                    snapctl_error(
                        message='Invalid env_params value in BYOSnap profile. env_params value ' +
                        'should not be empty. ' +
                        f"Check the value entry at {profile}.env_params #{env_index}.",
                        code=SNAPCTL_INPUT_ERROR
                    )
        return profile_data

    @staticmethod
    def _validate_byosnap_id(byosnap_id: str) -> None:
        if not byosnap_id.startswith(ByoSnap.ID_PREFIX):
            snapctl_error(
                message="Invalid Snap ID. Valid Snap IDs start with " +
                f"{ByoSnap.ID_PREFIX}.",
                code=SNAPCTL_INPUT_ERROR
            )
        if len(byosnap_id) > ByoSnap.SID_CHARACTER_LIMIT:
            snapctl_error(
                message="Invalid Snap ID. Snap ID should be less than " +
                f"{ByoSnap.SID_CHARACTER_LIMIT} characters",
                code=SNAPCTL_INPUT_ERROR
            )

    @staticmethod
    def _handle_output_file(resource_filename: str, output_filepath: str) -> bool:
        try:
            with pkg_resources.open_text(snapctl.data.profiles, resource_filename) as in_file, open(output_filepath, 'w') as outfile:
                for line in in_file:
                    outfile.write(line)
            return True
        except FileNotFoundError:
            warning(
                f"[ERROR] Could not find profile file: {resource_filename}")
            return False

    @staticmethod
    def _docker_supports_buildkit():
        try:
            version = subprocess.check_output(
                ["docker", "version", "--format", "{{.Server.Version}}"])
            major, minor = map(int, version.decode().split(".")[:2])
            return (major > 18) or (major == 18 and minor >= 9)
        except Exception:
            return False

    def _get_profile_contents(self) -> dict:
        """
          Get the BYOSNap profile contents
          based on if the user has a YAML or JSON file
        """
        profile_contents = {}
        with open(self.profile_path, 'rb') as file:
            try:
                if self.profile_filename.endswith('.yaml') or\
                        self.profile_filename.endswith('.yml'):
                    yaml_content = yaml.safe_load(file)
                    file_contents = json.dumps(yaml_content)
                    profile_contents = json.loads(file_contents)
                else:
                    profile_contents = json.load(file)
            except json.JSONDecodeError:
                pass
        return profile_contents

    def _setup_token_and_token_parts(self, base_url, api_key, byosnap_id) -> None:
        '''
        Setup the token and token parts for publishing and syncing
        '''
        self.token: Union[str, None] = get_composite_token(
            base_url, api_key,
            'byosnap', {'service_id': byosnap_id}
        )
        self.token_parts: Union[list, None] = ByoSnap._get_token_values(
            self.token) if self.token is not None else None

    def _setup_and_validate_byosnap_profile_data(self) -> None:
        """
          Pre-Override Validator
        """
        # Check dependencies
        if self.path is None and self.resources_path is None:
            snapctl_error(
                message='Either the path or resources path is required ' +
                'to import the BYOSnap profile.',
                code=SNAPCTL_INPUT_ERROR
            )
        base_path = self.resources_path if self.resources_path else self.path
        # Publish and Publish version
        if not self.profile_filename:
            self.profile_filename = ByoSnap.DEFAULT_PROFILE_NAME_JSON
        else:
            if not self.profile_filename.endswith('.json') and \
                not self.profile_filename.endswith('.yaml') and \
                    not self.profile_filename.endswith('.yml'):
                snapctl_error(
                    message='Invalid BYOSnap profile file. Please check the file extension' +
                    ' and ensure it is either .json, .yaml, or .yml',
                    code=SNAPCTL_INPUT_ERROR
                )
        self.profile_path = os.path.join(
            base_path, self.profile_filename)
        if not os.path.isfile(self.profile_path):
            snapctl_error(
                "Unable to find " +
                f"{self.profile_filename} at path {base_path}",
                SNAPCTL_INPUT_ERROR)
        profile_data_obj = self._get_profile_contents()
        if not profile_data_obj:
            snapctl_error(
                message='Invalid BYOSnap profile JSON. Please check the JSON structure',
                code=SNAPCTL_INPUT_ERROR
            )
        # IMPORTANT: This is where the profile data is set and validated
        #
        # Update: June 2, 2025 -  We removed the line that updated the self.platform_type
        # self.platform_type = profile_data_obj['platform']
        self.profile_data = profile_data_obj
        ByoSnap._validate_byosnap_profile_data(self.profile_data)
        # End: IMPORTANT: This is where the profile data is set
        # Now apply the overrides
        self.name = self.profile_data['name']
        self.desc = self.profile_data['description']
        self.language = self.profile_data['language']
        self.prefix = self.profile_data['prefix']
        # Setup the final ingress external port
        final_ingress_external_port = {
            'name': 'http',
            'port': None
        }
        if 'http_port' in self.profile_data:
            final_ingress_external_port = {
                'name': 'http',
                'port': self.profile_data['http_port']
            }
        elif 'ingress' in self.profile_data and 'external_port' in self.profile_data['ingress']:
            final_ingress_external_port = self.profile_data['ingress']['external_port']
        self.ingress_external_port = final_ingress_external_port
        # Setup the final ingress internal ports
        final_ingress_internal_ports = []
        if 'ingress' in self.profile_data and 'internal_ports' in self.profile_data['ingress']:
            final_ingress_internal_ports = self.profile_data['ingress']['internal_ports']
        self.ingress_internal_ports = final_ingress_internal_ports
        self.readiness_path = self.profile_data['readiness_probe_config']['path']
        self.readiness_delay = \
            self.profile_data['readiness_probe_config']['initial_delay_seconds']

    def _check_dependencies(self) -> None:
        """
          Check application dependencies
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Checking dependencies...', total=None)
        try:
            # Check dependencies
            result = subprocess.run([
                "docker", "info"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False)
            if not result.returncode:
                return snapctl_success(
                    message='BYOSnap dependencies verified',
                    progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOSNAP_DEPENDENCY_MISSING, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='Docker not running. Please start docker.',
            code=SNAPCTL_BYOSNAP_DEPENDENCY_MISSING, progress=progress)

    def _docker_login(self) -> None:
        """
          Docker Login
        """
        ecr_repo_url = self.token_parts[0]
        ecr_repo_username = self.token_parts[1]
        ecr_repo_token = self.token_parts[2]
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Logging into Snapser Image Registry...', total=None)
        try:
            # Login to Snapser Registry
            if platform == 'win32':
                # Start: Hack for Windows
                data = {
                    "auths": {
                        "https://index.docker.io/v1/": {}
                    }
                }

                # Path to the Docker config file, adjust the path as necessary
                docker_config_path = os.path.expanduser(
                    '~\\.docker\\config.json')

                # Ensure the directory exists
                os.makedirs(os.path.dirname(docker_config_path), exist_ok=True)

                # Write the data to the file
                with open(docker_config_path, 'w', encoding='utf-8') as file:
                    json.dump(data, file)
                info("Updated the docker config for docker login")
                # End: Hack for Windows
                response = subprocess.run([
                    'docker', 'login', '--username', ecr_repo_username,
                    '--password', ecr_repo_token, ecr_repo_url
                ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False)
            else:
                response = subprocess.run([
                    f'echo "{ecr_repo_token}" | docker login ' +
                    f'--username {ecr_repo_username} --password-stdin {ecr_repo_url}'
                ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False)
            if not response.returncode:
                return snapctl_success(
                    message='BYOSnap ECR login successful',
                    progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOSNAP_ECR_LOGIN_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOSnap ECR login failure',
            code=SNAPCTL_BYOSNAP_ECR_LOGIN_ERROR, progress=progress)

    def _docker_build(self) -> None:
        # Get the data
        # image_tag = f'{self.byosnap_id}.{self.tag}'
        build_platform = ByoSnap.DEFAULT_BUILD_PLATFORM
        if len(self.token_parts) == 4:
            build_platform = self.token_parts[3]
        if self.platform_type is not None:
            build_platform = self.platform_type
        # if len(self.token_parts) == 4:
        #     build_platform = self.token_parts[3]
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Building your snap...', total=None)
        try:
            env = os.environ.copy()
            if ByoSnap._docker_supports_buildkit():
                info('Docker BuildKit is supported. Enabling it.')
                env["DOCKER_BUILDKIT"] = "1"
            # Warning check for architecture specific commands
            info(f'Building on system architecture {sys_platform.machine()}')
            check_response = check_dockerfile_architecture(
                self.docker_path_filename, sys_platform.machine())
            if check_response['error']:
                warning(check_response['message'])
            # Build the image
            if platform == "win32":
                response = subprocess.run([
                    # f"docker build --no-cache -t {remote_tag} {path}"
                    'docker', 'build', '--platform', build_platform, '-t', self.remote_tag,
                    '-f', self.docker_path_filename,  self.path
                ], shell=True, check=False, env=env)
                # stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            else:
                response = subprocess.run([
                    # f"docker build --no-cache -t {remote_tag} {path}"
                    "docker build --platform " +
                    f"{build_platform} -t {self.remote_tag} " +
                    f"-f {self.docker_path_filename} {self.path}"
                ], shell=True, check=False, env=env)
                # stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if not response.returncode:
                return snapctl_success(
                    message='BYOSnap build successful', progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOSNAP_BUILD_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOSnap build failure',
            code=SNAPCTL_BYOSNAP_BUILD_ERROR, progress=progress)

    def _docker_tag(self) -> None:
        # Get the data
        ecr_repo_url = self.token_parts[0]
        image_tag = f'{self.byosnap_id}.{self.remote_tag}'
        full_ecr_repo_url = f'{ecr_repo_url}:{image_tag}'
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Tagging your snap...', total=None)
        try:
            # Tag the repo
            if platform == "win32":
                response = subprocess.run([
                    'docker', 'tag', self.tag, full_ecr_repo_url
                ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False)
            else:
                response = subprocess.run([
                    f"docker tag {self.tag} {full_ecr_repo_url}"
                ], shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False)
            if not response.returncode:
                return snapctl_success(
                    message='BYOSnap tag successful', progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOSNAP_TAG_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOSnap tag failure',
            code=SNAPCTL_BYOSNAP_TAG_ERROR, progress=progress)

    def _docker_push(self) -> bool:
        """
          Push the Snap image
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(description='Pushing your snap...', total=None)
        try:
            # Push the image
            ecr_repo_url = self.token_parts[0]
            image_tag = f'{self.byosnap_id}.{self.tag}'
            full_ecr_repo_url = f'{ecr_repo_url}:{image_tag}'
            if platform == "win32":
                response = subprocess.run([
                    'docker', 'push', full_ecr_repo_url
                ], shell=True, check=False)
                # stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            else:
                response = subprocess.run([
                    f"docker push {full_ecr_repo_url}"
                ], shell=True, check=False)
                # stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if not response.returncode:
                return snapctl_success(
                    message='BYOSnap upload successful', progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOSNAP_PUBLISH_IMAGE_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOSnap upload failure. Duplicate image error.',
            code=SNAPCTL_BYOSNAP_PUBLISH_IMAGE_DUPLICATE_TAG_ERROR, progress=progress)

    def _clean_slate(self) -> None:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Cleaning cache and initializing...', total=None)
        try:
            # Specific ECR repository URL to check against
            ecr_domain = self.token_parts[0].split('/')[0]
            # Perform the Docker logout
            if platform == "win32":
                logout_response = subprocess.run(['docker', 'logout', ecr_domain],
                                                 shell=True, check=False)
            else:
                logout_response = subprocess.run([
                    f"docker logout {ecr_domain}"
                ], shell=True, check=False)
            if not logout_response.returncode:
                return snapctl_success(
                    message='Cleanup complete.', progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            warning('Unable to initialize with a clean slate.')
        finally:
            progress.stop()

    # Public methods

    # Validate
    def validate_input(self) -> None:
        """
          Validator
        """
        # Check API Key and Base URL
        if not self.api_key or self.base_url == '':
            snapctl_error(
                message="Missing API Key.", code=SNAPCTL_INPUT_ERROR)
        # Check subcommand
        if not self.subcommand in ByoSnap.SUBCOMMANDS:
            snapctl_error(
                message="Invalid command. Valid commands are " +
                f"{', '.join(ByoSnap.SUBCOMMANDS)}.",
                code=SNAPCTL_INPUT_ERROR
            )
        # Validation for subcommands
        if self.subcommand == 'create':
            # Validator
            ByoSnap._validate_byosnap_id(self.byosnap_id)
            if self.name == '':
                snapctl_error(message="Missing name", code=SNAPCTL_INPUT_ERROR)
            if not self.language:
                snapctl_error(message="Missing language",
                              code=SNAPCTL_INPUT_ERROR)
            if self.language not in ByoSnap.LANGUAGES:
                snapctl_error(
                    message="Invalid language. Valid languages are " +
                    f"{', '.join(ByoSnap.LANGUAGES)}.",
                    code=SNAPCTL_INPUT_ERROR
                )
            if self.platform_type not in ByoSnap.PLATFORMS:
                snapctl_error(
                    message="Invalid platform. Valid platforms are " +
                    f"{', '.join(ByoSnap.PLATFORMS)}.",
                    code=SNAPCTL_INPUT_ERROR
                )
        elif self.subcommand == 'publish-image':
            # Setup
            self._setup_token_and_token_parts(
                self.base_url, self.api_key, self.byosnap_id)
            # Validator
            if self.token_parts is None:
                snapctl_error('Invalid token. Please reach out to your support team.',
                              SNAPCTL_INPUT_ERROR)
            ByoSnap._validate_byosnap_id(self.byosnap_id)
            if not self.tag:
                snapctl_error(
                    "Missing required parameter: tag", SNAPCTL_INPUT_ERROR)
            if len(self.tag.split()) > 1 or \
                    len(self.tag) > ByoSnap.TAG_CHARACTER_LIMIT:
                snapctl_error(
                    "Tag should be a single word with maximum of " +
                    f"{ByoSnap.TAG_CHARACTER_LIMIT} characters",
                    SNAPCTL_INPUT_ERROR
                )
            if ':' in self.tag:
                snapctl_error("Tag should not contain `:` ",
                              SNAPCTL_INPUT_ERROR)
            if not self.skip_build and not self.path:
                snapctl_error("Missing required parameter: path",
                              SNAPCTL_INPUT_ERROR)
            # Check docker file path
            if not self.skip_build and not self.docker_path_filename:
                snapctl_error(
                    f"Unable to find {self.docker_path_filename}", SNAPCTL_INPUT_ERROR)
        elif self.subcommand == 'upload-docs':
            # Setup
            self._setup_token_and_token_parts(
                self.base_url, self.api_key, self.byosnap_id)
            # Validator
            ByoSnap._validate_byosnap_id(self.byosnap_id)
            if self.token_parts is None:
                snapctl_error('Invalid token. Please reach out to your support team.',
                              SNAPCTL_INPUT_ERROR)
            if self.path is None and self.resources_path is None:
                snapctl_error(
                    "Missing one of: path or resources-path parameter", SNAPCTL_INPUT_ERROR)
            if not self.tag and not self.version:
                snapctl_error("Missing tag or version", SNAPCTL_INPUT_ERROR)
            if self.tag:
                if len(self.tag.split()) > 1 or \
                        len(self.tag) > ByoSnap.TAG_CHARACTER_LIMIT:
                    snapctl_error(
                        "Tag should be a single word with maximum of " +
                        f"{ByoSnap.TAG_CHARACTER_LIMIT} characters",
                        SNAPCTL_INPUT_ERROR
                    )
            if self.version:
                pattern = r'^v\d+\.\d+\.\d+$'
                if not re.match(pattern, self.version):
                    snapctl_error(message="Version should be in the format vX.X.X",
                                  code=SNAPCTL_INPUT_ERROR)
        elif self.subcommand == 'publish-version':
            # Setup
            self._setup_token_and_token_parts(
                self.base_url, self.api_key, self.byosnap_id)
            # Setup the profile data
            self._setup_and_validate_byosnap_profile_data()
            # Validator
            ByoSnap._validate_byosnap_id(self.byosnap_id)
            if self.token_parts is None:
                snapctl_error('Invalid token. Please reach out to your support team.',
                              SNAPCTL_INPUT_ERROR)
            if not self.tag:
                snapctl_error(
                    "Missing required parameter: tag", SNAPCTL_INPUT_ERROR)
            if len(self.tag.split()) > 1 or \
                    len(self.tag) > ByoSnap.TAG_CHARACTER_LIMIT:
                snapctl_error(
                    "Tag should be a single word with maximum of " +
                    f"{ByoSnap.TAG_CHARACTER_LIMIT} characters",
                    SNAPCTL_INPUT_ERROR
                )
            if not self.version:
                snapctl_error("Missing version", SNAPCTL_INPUT_ERROR)
                pattern = r'^v\d+\.\d+\.\d+$'
            if not re.match(r'^v\d+\.\d+\.\d+$', self.version):
                snapctl_error("Version should be in the format vX.X.X",
                              SNAPCTL_INPUT_ERROR)
        elif self.subcommand == 'update-version':
            # Setup
            self._setup_token_and_token_parts(
                self.base_url, self.api_key, self.byosnap_id)
            # Setup the profile data
            self._setup_and_validate_byosnap_profile_data()
            # Validator
            ByoSnap._validate_byosnap_id(self.byosnap_id)
            if self.token_parts is None:
                snapctl_error('Invalid token. Please reach out to your support team.',
                              SNAPCTL_INPUT_ERROR)
            if not self.version:
                snapctl_error(message="Missing version",
                              code=SNAPCTL_INPUT_ERROR)
            pattern = r'^v\d+\.\d+\.\d+$'
            if not re.match(pattern, self.version):
                snapctl_error(
                    message="Version should be in the format vX.X.X",
                    code=SNAPCTL_INPUT_ERROR)
            if not self.tag:
                snapctl_error(
                    message="Missing required parameter: tag", code=SNAPCTL_INPUT_ERROR)
            if len(self.tag.split()) > 1 or \
                    len(self.tag) > ByoSnap.TAG_CHARACTER_LIMIT:
                snapctl_error(
                    message="Tag should be a single word with maximum of " +
                    f"{ByoSnap.TAG_CHARACTER_LIMIT} characters",
                    code=SNAPCTL_INPUT_ERROR
                )
        elif self.subcommand == 'sync':
            # Setup
            self._setup_token_and_token_parts(
                self.base_url, self.api_key, self.byosnap_id)
            # Setup the profile data
            self._setup_and_validate_byosnap_profile_data()
            # Validator
            ByoSnap._validate_byosnap_id(self.byosnap_id)
            if self.token_parts is None:
                snapctl_error('Invalid token. Please reach out to your support team.',
                              SNAPCTL_INPUT_ERROR)
            if not self.version:
                snapctl_error(message="Missing version. Version should be in the format vX.X.X",
                              code=SNAPCTL_INPUT_ERROR)
            pattern = r'^v\d+\.\d+\.\d+$'
            if not re.match(pattern, self.version):
                snapctl_error(message="Version should be in the format vX.X.X",
                              code=SNAPCTL_INPUT_ERROR)
            if not self.skip_build and not self.path:
                snapctl_error(
                    message="Missing required parameter: path",
                    code=SNAPCTL_INPUT_ERROR)
            # Check docker file path
            if not self.skip_build and not self.docker_path_filename:
                snapctl_error(
                    f"Unable to find {self.docker_path_filename}", SNAPCTL_INPUT_ERROR)
            if not self.snapend_id:
                snapctl_error(
                    message="Missing required parameter: snapend-id",
                    code=SNAPCTL_INPUT_ERROR)
        elif self.subcommand == 'publish':
            # Setup the profile data
            self._setup_and_validate_byosnap_profile_data()
            # Validator
            ByoSnap._validate_byosnap_id(self.byosnap_id)
            if not self.version:
                snapctl_error(message="Missing version. Version should be in the format vX.X.X",
                              code=SNAPCTL_INPUT_ERROR)
            if not re.match(r'^v\d+\.\d+\.\d+$', self.version):
                snapctl_error(message="Version should be in the format vX.X.X",
                              code=SNAPCTL_INPUT_ERROR)
            if not self.skip_build and not self.path:
                snapctl_error(
                    message="Missing required parameter: path", code=SNAPCTL_INPUT_ERROR)
            if not self.skip_build and not self.docker_path_filename:
                snapctl_error(
                    f"Unable to find {self.docker_path_filename}", SNAPCTL_INPUT_ERROR)
                # Run the overrides
        elif self.subcommand == 'generate-profile':
            # Setup
            # self._setup_token_and_token_parts(
            #     self.base_url, self.api_key, self.byosnap_id)
            # Validator
            if not self.out_path:
                snapctl_error(
                    message='Missing required parameter: out-path. ' +
                    'Path is required for profile generation',
                    code=SNAPCTL_INPUT_ERROR)
            if not os.path.isdir(self.out_path):
                snapctl_error(
                    message='Invalid out-path. ' +
                    'Path should be a directory',
                    code=SNAPCTL_INPUT_ERROR)
            if self.profile_filename is not None:
                if not self.profile_filename.endswith('.json') and \
                    not self.profile_filename.endswith('.yaml') and \
                        not self.profile_filename.endswith('.yml'):
                    snapctl_error(
                        message='Invalid BYOSnap profile file. Please check the file extension' +
                        ' and ensure it is either .json, .yaml, or .yml',
                        code=SNAPCTL_INPUT_ERROR
                    )
        elif self.subcommand == 'validate-profile':
            # # Setup
            # self._setup_token_and_token_parts(
            #     self.base_url, self.api_key, self.byosnap_id)
            # Setup the profile data
            self._setup_and_validate_byosnap_profile_data()

    # Basic methods

    def build(self) -> None:
        """
          Build the image
          1. Check Dependencies
          2. Login to Snapser Registry
          3. Build your snap
        """
        self._check_dependencies()
        self._docker_build()

    def push(self) -> bool:
        """
          Tag the image
          1. Check Dependencies
          2. Login to Snapser Registry
          3. Tag the snap
          4. Push your snap
        """
        self._check_dependencies()
        self._docker_tag()
        self._clean_slate()
        self._docker_login()
        self._docker_push()

    # Crud methods
    def upload_docs(self, no_exit: bool = False) -> None:
        '''
        Note this step is optional hence we do not raise a typer.Exit
        '''
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Uploading your BYOSnap Docs...', total=None)
        try:
            upload_tag = self.tag
            if not upload_tag:
                upload_tag = self.version
            if self.resources_path:
                base_dir = self.resources_path
            else:
                base_dir = self.path

            swagger_file = os.path.join(base_dir, 'swagger.json')
            readme_file = os.path.join(base_dir, 'README.md')
            # Upload swagger.json
            if os.path.isfile(swagger_file):
                try:
                    with open(swagger_file, "rb") as attachment_file:
                        info(f'Uploading swagger.json at {swagger_file}')
                        url = (
                            f"{self.base_url}/v1/snapser-api/byosnaps/"
                            f"{self.byosnap_id}/docs/{upload_tag}/openapispec"
                        )
                        test_res = requests.post(
                            url, files={"attachment": attachment_file},
                            headers={'api-key': self.api_key},
                            timeout=SERVER_CALL_TIMEOUT
                        )
                        if test_res.ok:
                            snapctl_success(
                                message='Uploaded swagger.json', progress=None, no_exit=True)
                        else:
                            static_message = 'Snapser enforces a strict schema for the swagger.json ' + \
                                'file. It needs to be a valid OpenAPI 3.0 spec. In addition, ever API ' + \
                                'needs an operationId. a summary and a non-empty description. This allows ' + \
                                'Snapser to generate your SDK and power the API explorer. If you do not ' + \
                                'wish to leverage this feature, just remove the swagger.json file.'
                            warning(static_message)
                            response_json = test_res.json()
                            if 'details' in response_json:
                                error_msg = f"Swagger upload error: {response_json['details']}"
                            else:
                                error_msg = 'Swagger upload error: In-compatible swagger.json file.'
                            warning(error_msg)
                except RequestException as e:
                    info(
                        'Exception: Unable to find swagger.json at ' +
                        f'{base_dir} {e}'
                    )
            else:
                info(
                    'No swagger.json found at' +
                    f'{base_dir}. Skipping swagger.json upload'
                )

            # Upload README.md
            if os.path.isfile(readme_file):
                try:
                    with open(readme_file, "rb") as attachment_file:
                        url = (
                            f"{self.base_url}/v1/snapser-api/byosnaps/"
                            f"{self.byosnap_id}/docs/{upload_tag}/markdown"
                        )
                        test_res = requests.post(
                            url, files={"attachment": attachment_file},
                            headers={'api-key': self.api_key},
                            timeout=SERVER_CALL_TIMEOUT
                        )
                        if test_res.ok:
                            snapctl_success(
                                message='Uploaded README.md', progress=None, no_exit=True)
                        else:
                            info('Unable to upload your README.md')
                except RequestException as e:
                    info(
                        'Exception: Unable to find README.md at ' +
                        f'{base_dir} {str(e)}'
                    )
            else:
                info(
                    'No README.md found at ' +
                    f'{base_dir}. Skipping README.md upload'
                )

            # Upload any snapser-tool-*.json files
            for file_name in os.listdir(base_dir):
                if file_name.startswith("snapser-tool-") and file_name.endswith(".json"):
                    file_path = os.path.join(base_dir, file_name)
                    if os.path.isfile(file_path):
                        try:
                            with open(file_path, "rb") as attachment_file:
                                url = (
                                    f"{self.base_url}/v1/snapser-api/byosnaps/"
                                    f"{self.byosnap_id}/docs/{upload_tag}/tools"
                                )
                                test_res = requests.post(
                                    url, files={"attachment": attachment_file},
                                    headers={'api-key': self.api_key},
                                    timeout=SERVER_CALL_TIMEOUT
                                )
                                if test_res.ok:
                                    snapctl_success(
                                        message=f'Uploaded tool {file_name}',
                                        progress=None, no_exit=True)
                                else:
                                    info(f'Unable to upload tool {file_name}')
                        except RequestException as e:
                            info('Exception: Unable to upload tool ' +
                                 f'{file_name} {str(e)}')

            # Show success message
            snapctl_success(
                message='Completed the docs uploading process', progress=progress, no_exit=no_exit)
        except RequestException as e:
            info(f'Exception: Unable to upload your API Json {str(e)}')
        finally:
            progress.stop()

    def create(self, no_exit: bool = False) -> None:
        """
          Creating a new snap
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(description='Creating your snap...', total=None)
        try:
            payload = {
                "service_id": self.byosnap_id,
                "name": self.name,
                "description": self.desc,
                "platform": self.platform_type,
                "language": self.language,
            }
            res = requests.post(
                f"{self.base_url}/v1/snapser-api/byosnaps",
                json=payload, headers={'api-key': self.api_key},
                timeout=SERVER_CALL_TIMEOUT
            )
            if res.ok:
                return snapctl_success(
                    message='BYOSNAP create successful', progress=progress, no_exit=no_exit)
            response_json = res.json()
            if "api_error_code" in response_json and "message" in response_json:
                if response_json['api_error_code'] == HTTP_ERROR_RESOURCE_NOT_FOUND:
                    snapctl_error(
                        message='BYOSnap not found.',
                        code=SNAPCTL_BYOSNAP_NOT_FOUND, progress=progress
                    )
                if response_json['api_error_code'] == HTTP_ERROR_SERVICE_VERSION_EXISTS:
                    snapctl_error(
                        message=f'BYOSnap {self.name} already exists. ' +
                        'Please use a different name',
                        code=SNAPCTL_BYOSNAP_CREATE_DUPLICATE_NAME_ERROR,
                        progress=progress
                    )
                # elif response_json['api_error_code'] == HTTP_ERROR_TAG_NOT_AVAILABLE:
                #     error('Invalid tag. Please use the correct tag')
                if response_json['api_error_code'] == HTTP_ERROR_ADD_ON_NOT_ENABLED:
                    snapctl_error(
                        message='Missing Add-on. Please enable the add-on via the Snapser Web app.',
                        code=SNAPCTL_BYOSNAP_CREATE_PERMISSION_ERROR,
                        progress=progress
                    )
            snapctl_error(
                message=f'Server error: {json.dumps(response_json, indent=2)}',
                code=SNAPCTL_BYOSNAP_CREATE_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message=f"Exception: Unable to create your snap {e}",
                code=SNAPCTL_BYOSNAP_CREATE_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='Failed to create snap',
            code=SNAPCTL_BYOSNAP_CREATE_ERROR, progress=progress)

    def publish_image(self, no_exit: bool = False) -> None:
        """
          Publish the image
          1. Check Dependencies
          2. Login to Snapser Registry
          3. Build your snap
          4. Tag the repo
          5. Push the image
          6. Upload swagger.json
        """
        if check_use_containerd_snapshotter():
            msg = 'Containerd is active. Please disable it from your Docker Desktop settings.'
            snapctl_error(
                message=msg,
                code=SNAPCTL_CONFIGURATION_INCORRECT
            )
        self._check_dependencies()
        if not self.skip_build:
            self._docker_build()
        else:
            info('--skip-build set. Skipping the build step.')
        self._docker_tag()
        self._clean_slate()
        self._docker_login()
        self._docker_push()
        if self.path is not None or self.resources_path is not None:
            self.upload_docs(no_exit=True)
        snapctl_success(
            message='BYOSNAP publish successful', no_exit=no_exit)

    def publish_version(self, no_exit: bool = False) -> None:
        """
          Publish the version
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Publishing your snap...', total=None)
        try:
            profile_data = self._get_profile_contents()
            dev_template = None
            if 'dev_template' in profile_data:
                dev_template = profile_data['dev_template']
            stage_template = None
            if 'stage_template' in profile_data:
                stage_template = profile_data['stage_template']
            prod_template = None
            if 'prod_template' in profile_data:
                prod_template = profile_data['prod_template']
            payload = {
                "version": self.version,
                "image_tag": self.tag,
                "base_url": f"{self.prefix}/{self.byosnap_id}",
                "ingress": {
                    "external_port": self.ingress_external_port,
                    "internal_ports": self.ingress_internal_ports
                },
                "readiness_probe_config": {
                    "path": self.readiness_path,
                    "initial_delay_seconds": self.readiness_delay
                },
                "dev_template": dev_template,
                "stage_template": stage_template,
                "prod_template": prod_template,
                # Currently not supported so we are just hardcoding an empty list
                "egress": {"ports": []},
                # Platform override
            }
            if self.platform_type is not None:
                payload['platform_override'] = self.platform_type

            res = requests.post(
                f"{self.base_url}/v1/snapser-api/byosnaps/{self.byosnap_id}/versions",
                json=payload, headers={'api-key': self.api_key},
                timeout=SERVER_CALL_TIMEOUT
            )
            if res.ok:
                return snapctl_success(
                    message='BYOSNAP publish version successful',
                    progress=progress, no_exit=no_exit)
            response_json = res.json()
            if "api_error_code" in response_json:
                if response_json['api_error_code'] == HTTP_ERROR_RESOURCE_NOT_FOUND:
                    snapctl_error(
                        message='BYOSnap not found.',
                        code=SNAPCTL_BYOSNAP_NOT_FOUND, progress=progress
                    )
                if response_json['api_error_code'] == HTTP_ERROR_SERVICE_VERSION_EXISTS:
                    snapctl_error(
                        message='Version already exists. Please update your version and try again',
                        code=SNAPCTL_BYOSNAP_PUBLISH_IMAGE_DUPLICATE_TAG_ERROR,
                        progress=progress
                    )
                if response_json['api_error_code'] == HTTP_ERROR_TAG_NOT_AVAILABLE:
                    snapctl_error(
                        message='Invalid tag. Please use the correct tag.',
                        code=SNAPCTL_BYOSNAP_PUBLISH_VERSION_DUPLICATE_TAG_ERROR,
                        progress=progress)
            snapctl_error(
                message=f'Server error: {json.dumps(response_json, indent=2)}',
                code=SNAPCTL_BYOSNAP_PUBLISH_VERSION_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message='Exception: Unable to publish a ' +
                f'version for your snap. Exception: {e}',
                code=SNAPCTL_BYOSNAP_PUBLISH_VERSION_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='Failed to publish version',
            code=SNAPCTL_BYOSNAP_PUBLISH_VERSION_ERROR, progress=progress)

    def update_version(self, no_exit: bool = False) -> None:
        """
          Update the byosnap version
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Updating your Byosnap...', total=None)
        try:
            profile_data = self._get_profile_contents()
            dev_template = None
            if 'dev_template' in profile_data:
                dev_template = profile_data['dev_template']
            stage_template = None
            if 'stage_template' in profile_data:
                stage_template = profile_data['stage_template']
            prod_template = None
            if 'prod_template' in profile_data:
                prod_template = profile_data['prod_template']
            payload = {
                "image_tag": self.tag,
                "base_url": f"{self.prefix}/{self.byosnap_id}",
                "ingress": {
                    "external_port": self.ingress_external_port,
                    "internal_ports": self.ingress_internal_ports
                },
                "readiness_probe_config": {
                    "path": self.readiness_path,
                    "initial_delay_seconds": self.readiness_delay
                },
                "dev_template": dev_template,
                "stage_template": stage_template,
                "prod_template": prod_template,
                # Currently not supported so we are just hardcoding an empty list
                "egress": {"ports": []},
            }
            if self.platform_type is not None:
                payload['platform_override'] = self.platform_type
            res = requests.patch(
                f"{self.base_url}/v1/snapser-api/byosnaps/{self.byosnap_id}/versions/{self.version}",
                json=payload, headers={'api-key': self.api_key},
                timeout=SERVER_CALL_TIMEOUT
            )
            if res.ok:
                return snapctl_success(
                    message='BYOSNAP update version successful',
                    progress=progress, no_exit=no_exit)
            response_json = res.json()
            if "api_error_code" in response_json:
                if response_json['api_error_code'] == HTTP_ERROR_RESOURCE_NOT_FOUND:
                    snapctl_error(
                        message='BYOSnap not found.',
                        code=SNAPCTL_BYOSNAP_NOT_FOUND, progress=progress
                    )
                if response_json['api_error_code'] == HTTP_ERROR_SERVICE_IN_USE:
                    snapctl_error(
                        message='Version already in use in a staging or production snapend. ' +
                        'Please publish an unused version and start using that instead.',
                        code=SNAPCTL_BYOSNAP_UPDATE_VERSION_SERVICE_IN_USE_ERROR,
                        progress=progress
                    )
                if response_json['api_error_code'] == HTTP_ERROR_TAG_NOT_AVAILABLE:
                    snapctl_error(
                        message='Invalid tag. Please use the correct tag.',
                        code=SNAPCTL_BYOSNAP_UPDATE_VERSION_TAG_ERROR, progress=progress)
            snapctl_error(
                message=f'Server error: {json.dumps(response_json, indent=2)}',
                code=SNAPCTL_BYOSNAP_UPDATE_VERSION_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message='Exception: Unable to update a ' +
                f'version for your snap. Exception: {e}',
                code=SNAPCTL_BYOSNAP_UPDATE_VERSION_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='Failed to update version',
            code=SNAPCTL_BYOSNAP_UPDATE_VERSION_ERROR, progress=progress)

    # Upper echelon methods
    def publish(self) -> None:
        '''
        Sync the snap
        '''
        try:
            # Attempt to create a BYOSnap but no worries if it fails
            payload = {
                "service_id": self.byosnap_id,
                "name": self.name,
                "description": self.desc,
                "platform": self.profile_data['platform'],
                "language": self.language,
            }
            res = requests.post(
                f"{self.base_url}/v1/snapser-api/byosnaps",
                json=payload, headers={'api-key': self.api_key},
                timeout=SERVER_CALL_TIMEOUT
            )
            if res.ok:
                success('BYOSnap created successfully')
            else:
                response_json = res.json()
                if "api_error_code" in response_json and "message" in response_json:
                    if response_json['api_error_code'] == HTTP_ERROR_SERVICE_VERSION_EXISTS:
                        info(
                            msg=f'BYOSnap {self.name} present. ' +
                            'Lets proceed',
                        )
            # Setup the token and token parts
            # Make the remote tag same as version if user is not passing the tag
            if self.tag is None:
                self.tag = self.version
                self.remote_tag = self.version
            self._setup_token_and_token_parts(
                self.base_url, self.api_key, self.byosnap_id)
            # Now publish the image
            self.publish_image(no_exit=True)
            # Now publish the version
            self.publish_version(no_exit=True)
            return snapctl_success(message='BYOSNAP published successfully')
        except RequestException as e:
            snapctl_error(
                message='Exception: Unable to publish a ' +
                f' version for your Byosnap. Exception: {e}',
                code=SNAPCTL_BYOSNAP_PUBLISH_ERROR)

    def sync(self) -> None:
        '''
        Sync the snap
        '''
        try:
            # Make the remote tag same as version if user is not passing the tag
            if self.tag is None:
                time_string = str(int(time.time()))
                self.tag = f'{self.version}-{time_string}'
                self.remote_tag = f'{self.version}-{time_string}'
            self.publish_image(no_exit=True)
            self.update_version(no_exit=True)
            byosnap_list: str = f"{self.byosnap_id}:{self.version}"
            snapend = Snapend(
                subcommand='update', base_url=self.base_url, api_key=self.api_key,
                snapend_id=self.snapend_id, byosnaps=byosnap_list, blocking=self.blocking
            )
            snapend.update(no_exit=True)
            return snapctl_success(message='BYOSNAP sync successful')
        except RequestException as e:
            snapctl_error(
                message='Exception: Unable to update a ' +
                f' version for your snap. Exception: {e}',
                code=SNAPCTL_BYOSNAP_UPDATE_VERSION_ERROR)

    def generate_profile(self, no_exit: bool = False) -> None:
        """
            Generate snapser-byosnap-profile.json
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Generating BYOSnap profile...', total=None)
        try:
            if self.out_path is not None:
                file_save_path = os.path.join(
                    self.out_path, self.profile_filename)
            else:
                file_save_path = os.path.join(
                    os.getcwd(), self.profile_filename)
            extension = self.profile_filename.split('.')[-1]
            resource_filename = f"snapser-byosnap-profile.{extension}"
            file_written = ByoSnap._handle_output_file(
                resource_filename, file_save_path)
            if file_written:
                snapctl_success(
                    message="BYOSNAP Profile generation successful. " +
                    f"{self.profile_filename} saved at {file_save_path}",
                    progress=progress,
                    no_exit=no_exit
                )
                return
        except (IOError, OSError) as file_error:
            snapctl_error(
                message=f"File error: {file_error}",
                code=SNAPCTL_BYOSNAP_GENERATE_PROFILE_ERROR, progress=progress)
        snapctl_error(
            message="Failed to generate BYOSNAP Profile",
            code=SNAPCTL_BYOSNAP_GENERATE_PROFILE_ERROR,
            progress=progress
        )

    def validate_profile(self) -> None:
        '''
        Validate the profile
        '''
        # Note all the validation is already happening in the constructor
        return snapctl_success(message='BYOSNAP profile validated.')

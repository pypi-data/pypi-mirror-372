"""
    BYOGS CLI commands
"""
import base64
from binascii import Error as BinasciiError
import os
import json
import subprocess
import time
import platform as sys_platform
from sys import platform
from typing import Union, List

from rich.progress import Progress, SpinnerColumn, TextColumn
from snapctl.commands.snapend import Snapend
from snapctl.config.constants import SNAPCTL_BYOGS_DEPENDENCY_MISSING, \
    SNAPCTL_BYOGS_ECR_LOGIN_ERROR, SNAPCTL_BYOGS_BUILD_ERROR, \
    SNAPCTL_BYOGS_TAG_ERROR, SNAPCTL_BYOGS_PUBLISH_ERROR, \
    SNAPCTL_BYOGS_PUBLISH_DUPLICATE_TAG_ERROR, SNAPCTL_INPUT_ERROR, \
    SNAPCTL_CONFIGURATION_INCORRECT
from snapctl.utils.helper import get_composite_token, snapctl_error, snapctl_success, \
    check_dockerfile_architecture, check_use_containerd_snapshotter
from snapctl.utils.echo import info, warning


class ByoGs:
    """
        BYOGS CLI commands
    """
    SID = 'byogs'
    SUBCOMMANDS = ['publish', 'sync']
    PLATFORMS = ['linux/amd64']
    LANGUAGES = ['go', 'python', 'ruby', 'c#', 'c++', 'rust', 'java', 'node']
    DEFAULT_BUILD_PLATFORM = 'linux/amd64'
    SID_CHARACTER_LIMIT = 47
    TAG_CHARACTER_LIMIT = 80

    def __init__(
        self, *, subcommand: str, base_url: str, api_key: Union[str, None],
        tag: Union[str, None] = None, path: Union[str, None] = None,
        resources_path: Union[str, None] = None, docker_filename: Union[str, None] = None,
        skip_build: bool = False, snapend_id: Union[str, None] = None,
        fleet_names: Union[str, None] = None, blocking: bool = False
    ) -> None:
        self.subcommand: str = subcommand
        self.base_url: str = base_url
        self.api_key: Union[str, None] = api_key
        self.tag: Union[str, None] = tag
        self.path: Union[str, None] = path
        self.resources_path: Union[str, None] = resources_path
        self.docker_filename: str = docker_filename
        self.docker_path_filename: Union[str, None] = ByoGs._make_dockerfile_path(
            path, resources_path, docker_filename
        )
        self.skip_build: bool = skip_build
        self.snapend_id: Union[str, None] = snapend_id
        self.fleet_names: Union[str, None] = fleet_names
        self.blocking: bool = blocking
        # Values below are derived values
        self.token: Union[str, None] = get_composite_token(
            base_url, api_key, 'byogs', {'service_id': ByoGs.SID}
        )
        self.token_parts: Union[List, None] = ByoGs._get_token_values(
            self.token) if self.token is not None else None
        # Validate input
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
            Get the token values
        """
        try:
            input_token = base64.b64decode(token).decode('ascii')
            token_parts = input_token.split('|')
            # url|web_app_token|service_id|ecr_repo_url|ecr_repo_username|ecr_repo_token
            # url = self.token_parts[0]
            # web_app_token = self.token_parts[1]
            # service_id = self.token_parts[2]
            # ecr_repo_url = self.token_parts[3]
            # ecr_repo_username = self.token_parts[4]
            # ecr_repo_token = self.token_parts[5]
            # platform = self.token_parts[6]
            if len(token_parts) >= 3:
                return token_parts
        except BinasciiError:
            pass
        return None

    @staticmethod
    def _docker_supports_buildkit():
        try:
            version = subprocess.check_output(
                ["docker", "version", "--format", "{{.Server.Version}}"])
            major, minor = map(int, version.decode().split(".")[:2])
            return (major > 18) or (major == 18 and minor >= 9)
        except Exception:
            return False

    def _check_dependencies(self) -> None:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Checking dependencies...', total=None
        )
        try:
            # Check dependencies
            result = subprocess.run([
                "docker", "info"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, check=False)
            if not result.returncode:
                return snapctl_success(
                    message='BYOGS dependencies verified',
                    progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error('Snapctl Exception',
                          SNAPCTL_BYOGS_DEPENDENCY_MISSING, progress)
        finally:
            progress.stop()
        snapctl_error('Docker not running. Please start docker.',
                      SNAPCTL_BYOGS_DEPENDENCY_MISSING, progress)

    def _docker_login(self) -> None:
        # Get the data
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
                    message='BYOGS ECR login successful', progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOGS_ECR_LOGIN_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOGS ECR login failure',
            code=SNAPCTL_BYOGS_ECR_LOGIN_ERROR, progress=progress)

    def _docker_build(self) -> None:
        # Get the data
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
            if ByoGs._docker_supports_buildkit():
                info('Docker BuildKit is supported. Enabling it.')
                env["DOCKER_BUILDKIT"] = "1"
            # image_tag = f'{ByoGs.SID}.{self.tag}'
            build_platform = ByoGs.DEFAULT_BUILD_PLATFORM
            if len(self.token_parts) == 4:
                build_platform = self.token_parts[3]

            # Warning check for architecture specific commands
            info(f'Building on system architecture {sys_platform.machine()}')
            check_response = check_dockerfile_architecture(
                self.docker_path_filename, sys_platform.machine())
            if check_response['error']:
                warning(check_response['message'])
            # Build the image
            if platform == "win32":
                response = subprocess.run([
                    # f"docker build --no-cache -t {tag} {path}"
                    'docker', 'build', '--platform', build_platform, '-t', self.tag,
                    '-f', self.docker_path_filename,  self.path
                ], shell=True, check=False, env=env)
                # stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            else:
                response = subprocess.run([
                    # f"docker build --no-cache -t {tag} {path}"
                    "docker build --platform " +
                    f"{build_platform} -t {self.tag} " +
                    f"-f {self.docker_path_filename} {self.path}"
                ], shell=True, check=False, env=env)
                # stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT)
            if not response.returncode:
                return snapctl_success(
                    message='BYOGS build successful',
                    progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOGS_BUILD_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOGS build failure',
            code=SNAPCTL_BYOGS_BUILD_ERROR, progress=progress)

    def _docker_tag(self) -> None:
        # Get the data
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Tagging your snap...', total=None)
        try:
            ecr_repo_url = self.token_parts[0]
            image_tag = f'{ByoGs.SID}.{self.tag}'
            full_ecr_repo_url = f'{ecr_repo_url}:{image_tag}'
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
                    message='BYOGS tag successful', progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOGS_TAG_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOGS tag failure', code=SNAPCTL_BYOGS_TAG_ERROR, progress=progress)

    def _docker_push(self) -> None:
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Pushing your snap...', total=None)
        try:
            ecr_repo_url = self.token_parts[0]
            image_tag = f'{ByoGs.SID}.{self.tag}'
            full_ecr_repo_url = f'{ecr_repo_url}:{image_tag}'
            # Push the image
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
                    message='BYOGS upload successful',
                    progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            snapctl_error(
                message='Snapctl Exception',
                code=SNAPCTL_BYOGS_PUBLISH_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='BYOGS upload failure. Duplicate image error.',
            code=SNAPCTL_BYOGS_PUBLISH_DUPLICATE_TAG_ERROR, progress=progress)

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
            ecr_repo_url = self.token_parts[0]
            if platform == "win32":
                # Perform the Docker logout
                logout_response = subprocess.run(
                    ['docker', 'logout', ecr_repo_url],
                    shell=True, check=False)
            else:
                # Perform the Docker logout
                logout_response = subprocess.run([
                    f"docker logout {ecr_repo_url}"
                ], shell=True, check=False)
            if not logout_response.returncode:
                return snapctl_success(
                    message='Cleanup complete',
                    progress=progress, no_exit=True)
        except subprocess.CalledProcessError:
            warning('Unable to initialize with a clean slate.')
        finally:
            progress.stop()

    # Public methods

    # Validator
    def validate_input(self) -> None:
        """
          Validator
        """
        # Check API Key and Base URL
        if not self.api_key or self.base_url == '':
            snapctl_error(
                message="Missing API Key.", code=SNAPCTL_INPUT_ERROR)
        # Check subcommand
        if not self.subcommand in ByoGs.SUBCOMMANDS:
            snapctl_error(
                message="Invalid command. Valid commands are " +
                f"{', '.join(ByoGs.SUBCOMMANDS)}.",
                code=SNAPCTL_INPUT_ERROR)
        # Validation for subcommands
        if self.token_parts is None:
            snapctl_error(
                message='Invalid token. Please reach out to your support team',
                code=SNAPCTL_INPUT_ERROR)
        # Check tag
        if self.tag is None:
            snapctl_error(
                message="Missing required parameter:  tag",
                code=SNAPCTL_INPUT_ERROR)
        if len(self.tag.split()) > 1 or len(self.tag) > ByoGs.TAG_CHARACTER_LIMIT:
            snapctl_error(
                message="Tag should be a single word with maximum of " +
                f"{ByoGs.TAG_CHARACTER_LIMIT} characters",
                code=SNAPCTL_INPUT_ERROR
            )
        if self.subcommand in ['build', 'publish']:
            # Check path
            if not self.skip_build and not self.path:
                snapctl_error(
                    message="Missing required parameter:  path",
                    code=SNAPCTL_INPUT_ERROR)
            # Check docker file path
            if not self.skip_build and not self.docker_path_filename:
                snapctl_error(
                    f"Unable to find {self.docker_path_filename}", SNAPCTL_INPUT_ERROR)
        elif self.subcommand == 'sync':
            # Check path
            if not self.skip_build and not self.path:
                snapctl_error(
                    message="Missing required parameter:  path",
                    code=SNAPCTL_INPUT_ERROR)
            # Check docker file path
            if not self.skip_build and not self.docker_path_filename:
                snapctl_error(
                    f"Unable to find {self.docker_path_filename}", SNAPCTL_INPUT_ERROR)
            if not self.snapend_id:
                snapctl_error(
                    message="Missing required parameter: snapend_id",
                    code=SNAPCTL_INPUT_ERROR)
            if not self.fleet_names:
                snapctl_error(
                    message="Missing required parameter: fleet_names",
                    code=SNAPCTL_INPUT_ERROR)

    # CRUD methods
    def build(self) -> None:
        """
          Build the image
          1. Check Dependencies
          2. Login to Snapser Registry
          3. Build your snap
        """
        self._check_dependencies()
        self._docker_build()

    def push(self) -> None:
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

    # Upper echelon commands
    def publish(self, no_exit: bool = False) -> None:
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
        snapctl_success(
            message='BYOGS publish successful', no_exit=no_exit)

    def sync(self) -> None:
        """
          Sync the image
          1. Check Dependencies
          2. Login to Snapser Registry
          3. Build your snap
          4. Tag the repo
          5. Push the image
          6. Upload swagger.json
        """
        self.tag = f'{self.tag}-{int(time.time())}'
        self.publish(no_exit=True)
        fleet_list: List[str] = self.fleet_names.split(',')
        byogs_list: List[str] = []
        for fleet in fleet_list:
            byogs_list.append(f"{fleet.strip()}:{self.tag}")
        snapend = Snapend(
            subcommand='update', base_url=self.base_url, api_key=self.api_key,
            snapend_id=self.snapend_id, byogs=", ".join(map(str, byogs_list)),
            blocking=self.blocking
        )
        snapend.update(no_exit=True)
        return snapctl_success(message='BYOGs sync successful')

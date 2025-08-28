"""
  Snapend CLI commands
"""
from typing import Dict, Union

import os
import json
import time
import requests
from requests.exceptions import RequestException

import typer
from rich.progress import Progress, SpinnerColumn, TextColumn
from snapctl.config.constants import SERVER_CALL_TIMEOUT, SNAPCTL_INPUT_ERROR, \
    SNAPCTL_SNAPEND_ENUMERATE_ERROR, SNAPCTL_SNAPEND_CLONE_SERVER_ERROR, \
    SNAPCTL_SNAPEND_CLONE_TIMEOUT_ERROR, SNAPCTL_SNAPEND_CLONE_ERROR, \
    SNAPCTL_SNAPEND_APPLY_SERVER_ERROR, SNAPCTL_SNAPEND_APPLY_TIMEOUT_ERROR, \
    SNAPCTL_SNAPEND_APPLY_ERROR, SNAPCTL_SNAPEND_PROMOTE_SERVER_ERROR, \
    SNAPCTL_SNAPEND_PROMOTE_TIMEOUT_ERROR, SNAPCTL_SNAPEND_PROMOTE_ERROR, \
    SNAPCTL_SNAPEND_DOWNLOAD_ERROR, SNAPCTL_SNAPEND_UPDATE_TIMEOUT_ERROR, \
    SNAPCTL_SNAPEND_UPDATE_ERROR, SNAPCTL_SNAPEND_STATE_ERROR, HTTP_ERROR_SNAPEND_MANIFEST_MISMATCH, \
    SNAPCTL_SNAPEND_APPLY_MANIFEST_MISMATCH_ERROR
from snapctl.config.hashes import PROTOS_TYPES, CLIENT_SDK_TYPES, SERVER_SDK_TYPES, \
    SNAPEND_MANIFEST_TYPES, SDK_TYPES, SDK_ACCESS_AUTH_TYPE_LOOKUP
from snapctl.utils.echo import error, success, info
from snapctl.utils.helper import snapctl_error, snapctl_success


class Snapend:
    """
      CLI commands exposed for a Snapend
    """
    SUBCOMMANDS = [
        'enumerate', 'clone', 'apply',
        'download', 'update', 'state'
    ]
    DOWNLOAD_CATEGORY = [
        'sdk', 'protos', 'snapend-manifest'
    ]
    CATEGORY_TYPE_SDK = [
        # 'omni',
        'user', 'api-key', 'internal', 'app']
    CATEGORY_TYPE_PROTOS = ['messages', 'services']
    # CATEGORY_TYPE_HTTP_LIB_FORMATS = ['unity', 'web-ts', 'ts']

    DOWNLOAD_TYPE_NOT_REQUIRED = ['admin-settings']
    # ACCESS_TYPES = ['external', 'internal']
    # AUTH_TYPES = ['user', 'app']
    ENV_TYPES = ['DEVELOPMENT', 'STAGING']
    BLOCKING_CALL_SLEEP = 5
    MAX_BLOCKING_RETRIES = 120

    def __init__(
        self, *, subcommand: str, base_url: str, api_key: Union[str, None],
        snapend_id: Union[str, None] = None,
        # Enumerate, Clone
        game_id: Union[str, None] = None,
        # Clone
        name: Union[str, None] = None,
        env: Union[str, None] = None,
        # Clone, Apply, Promote
        manifest_path_filename: Union[str, None] = None,
        force: bool = False,
        # Download
        category: Union[str, None] = None,
        category_format: Union[str, None] = None,
        category_type: Union[str, None] = None,
        category_http_lib: Union[str, None] = None,
        snaps: Union[str, None] = None,
        # Clone, Apply, Promote, Download
        out_path: Union[str, None] = None,
        # Update
        byosnaps: Union[str, None] = None,
        byogs: Union[str, None] = None,
        blocking: bool = False
    ) -> None:
        self.subcommand: str = subcommand
        self.base_url: str = base_url
        self.api_key: str = api_key
        self.snapend_id: str = snapend_id
        self.game_id: Union[str, None] = game_id
        self.name: str = name
        self.env: str = env
        self.manifest_path_filename: Union[str, None] = manifest_path_filename
        self.force: bool = force
        self.category: str = category
        self.category_format: str = category_format
        self.portal_category: Union[str, None] = Snapend._make_portal_category(
            category, category_format)
        self.category_type: Union[str, None] = category_type
        self.category_http_lib: Union[str, None] = category_http_lib
        self.download_types: Union[
            Dict[str, Dict[str, str]], None
        ] = Snapend._make_download_type(category)
        self.out_path: Union[str, None] = out_path
        self.snaps: Union[str, None] = snaps
        # Values below are derived values
        self.manifest_file_name: Union[str, None] = Snapend._get_manifest_file_name(
            manifest_path_filename
        )
        self.byosnap_list: Union[list, None] = Snapend._make_byosnap_list(
            byosnaps) if byosnaps else None
        self.byogs_list: Union[str, None] = Snapend._make_byogs_list(
            byogs) if byogs else None
        self.blocking: bool = blocking
        # Validate input
        self.validate_input()

    # Helpers
    @staticmethod
    def _get_manifest_file_name(manifest_path: str) -> Union[str, None]:
        if manifest_path and manifest_path != '' and os.path.isfile(manifest_path):
            file_name = os.path.basename(manifest_path)
            if file_name.endswith('.json') or file_name.endswith('.yml') or \
                    file_name.endswith('.yaml'):
                return file_name
        return None

    @staticmethod
    def _make_portal_category(category: str, category_format: str):
        '''
            We have simplified the input for the user to only take the category as sdk
            The portal server however expects us to pass client-sdk or server-sdk
            Hence we need to do this
        '''
        if category == 'sdk' and category_format in CLIENT_SDK_TYPES:
            return 'client-sdk'
        if category == 'sdk' and category_format in SERVER_SDK_TYPES:
            return 'server-sdk'
        if category == 'protos' and category_format in PROTOS_TYPES:
            return 'protos'
        if category == 'snapend-manifest' and category_format in SNAPEND_MANIFEST_TYPES:
            return 'snapend-manifest'
        return None

    @staticmethod
    def _make_download_type(category: str):
        if category == 'sdk':
            return SDK_TYPES
        if category == 'protos':
            return PROTOS_TYPES
        if category == 'snapend-manifest':
            return SNAPEND_MANIFEST_TYPES
        return None

    @staticmethod
    def _make_byosnap_list(byosnaps: str) -> list:
        byosnap_list = []
        for byosnap in byosnaps.split(','):
            byosnap = byosnap.strip()
            if len(byosnap.split(':')) != 2:
                return []
            byosnap_list.append({
                'service_id': byosnap.split(':')[0],
                'service_version': byosnap.split(':')[1]
            })
        return byosnap_list

    @staticmethod
    def _make_byogs_list(byogs: str) -> list:
        byogs_list = []
        for byog in byogs.split(','):
            byog = byog.strip()
            if len(byog.split(':')) != 2:
                return []
            byogs_list.append({
                'fleet_name': byog.split(':')[0],
                'image_tag': byog.split(':')[1],
            })
        return byogs_list

    def _get_snapend_state(self) -> str:
        try:
            url = f"{self.base_url}/v1/snapser-api/snapends/{self.snapend_id}"
            res = requests.get(
                url, headers={'api-key': self.api_key}, timeout=SERVER_CALL_TIMEOUT
            )
            cluster_object = res.json()
            if 'cluster' in cluster_object and 'id' in cluster_object['cluster'] and \
                    cluster_object['cluster']['id'] == self.snapend_id and \
                    'state' in cluster_object['cluster']:
                return cluster_object['cluster']['state']
        except RequestException as e:
            info(f"Exception: Unable to get Snapend state {e}")
        return 'INVALID'

    def _blocking_get_status(self) -> bool:
        total_tries = 0
        while True:
            total_tries += 1
            if total_tries > Snapend.MAX_BLOCKING_RETRIES:
                error("Going past maximum tries. Exiting...")
                return False
            current_state = self._get_snapend_state()
            if current_state != 'IN_PROGRESS':
                if current_state == 'LIVE':
                    success('Updated your snapend. Your snapend is Live.')
                    return True
                info(
                    f"Update not completed successfully. Your Snapend status is {current_state}.")
                return False
            info(f'Current snapend state is {current_state}')
            info(f"Retrying in {Snapend.BLOCKING_CALL_SLEEP} seconds...")
            time.sleep(Snapend.BLOCKING_CALL_SLEEP)

    def _assign_snapend_id(self, snapend_id: str) -> None:
        self.snapend_id = snapend_id

    def _setup_for_download(self, category_format: str) -> bool:
        '''
            Called by subcommands that want to initiate a download of the new manifest post update
        '''
        download_category: str = 'snapend-manifest'
        self.category = download_category
        self.category_format = category_format
        self.download_types: Union[
            Dict[str, Dict[str, str]], None
        ] = Snapend._make_download_type(download_category)

    def _execute_download(self) -> bool:
        try:
            url = (
                f"{self.base_url}/v1/snapser-api/snapends/{self.snapend_id}/"
                f"download?category={self.portal_category}"
            )
            if self.category not in Snapend.DOWNLOAD_TYPE_NOT_REQUIRED:
                url += "&type=" + \
                    f"{self.download_types[self.category_format]['type']}"
            # If Protos, add protos category
            if self.category == 'protos':
                url += f"&subtype={self.category_type}"
            # If client or server SDK, add sub type and auth type
            if self.category == 'sdk':
                url += "&subtype=" + \
                    f"{self.download_types[self.category_format]['subtype']}"
                url += f"&access_type={SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type]['access_type']}"
                if 'auth_type' in SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type] and \
                        SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type]['auth_type'] != '':
                    url += f"&auth_type={SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type]['auth_type']}"
                if self.category_http_lib:
                    # First check if the format supports http-lib
                    if self.category_format in Snapend.get_formats_supporting_http_lib():
                        url += f"&http_lib={self.category_http_lib}"
            # Customize snaps
            if self.snaps:
                url += f"&snaps={self.snaps}"
            res = requests.get(
                url, headers={'api-key': self.api_key}, timeout=SERVER_CALL_TIMEOUT
            )
            fn: str = ''
            if self.category == 'admin-settings':
                fn = f"snapser-{self.snapend_id}-admin-settings.json"
            elif self.category == 'snapend-manifest':
                fn = f"snapser-{self.snapend_id}-manifest." + \
                    f"{self.download_types[self.category_format]['type']}"
            elif self.category == 'protos':
                fn = f"snapser-{self.snapend_id}-{self.category}" + \
                    f"-{self.category_format}-{self.category_type}.zip"
            else:
                fn = f"snapser-{self.snapend_id}-{self.category}" + \
                    f"-{self.category_format}" + \
                    f"-{SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type]['access_type']}"
                if 'auth_type' in SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type] and \
                        SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type]['auth_type'] != '':
                    fn += f"-{SDK_ACCESS_AUTH_TYPE_LOOKUP[self.category_type]['auth_type']}"
                if self.category_http_lib:
                    # First check if the format supports http-lib
                    if self.category_format in Snapend.get_formats_supporting_http_lib():
                        fn += f"-{self.category_http_lib}"
                fn += ".zip"
            if self.out_path is not None:
                file_save_path = os.path.join(self.out_path, fn)
            else:
                file_save_path = os.path.join(os.getcwd(), fn)
            if res.ok:
                content: bytes = res.content
                with open(file_save_path, "wb") as file:
                    if self.category in ['admin-settings']:
                        content = json.loads(res.content)
                        json.dump(content, file, indent=4)
                    else:
                        file.write(res.content)
                return True
        except RequestException as e:
            info(
                f"Exception: Unable to download {self.category}. Reason: {e}"
            )
        return False

    @staticmethod
    def get_formats_supporting_http_lib() -> list:
        '''
            Get the list of formats that support http-lib
        '''
        format_list = []
        for key, value in SDK_TYPES.items():
            if 'http-lib' in value and len(value['http-lib']) > 0:
                format_list.append(key)
        return format_list

    @staticmethod
    def get_http_formats_str() -> str:
        '''
            Get the list of formats that support http-lib as a string
        '''
        format_str = ""
        for key, value in SDK_TYPES.items():
            if 'http-lib' in value and len(value['http-lib']) > 0:
                format_str += f"{key}({', '.join(value['http-lib'])}) | "
        if format_str != "":
            format_str = format_str[:-2]
        return format_str

    # Validate input
    def validate_input(self) -> None:
        """
          Validator
        """
        # Check API Key and Base URL
        if not self.api_key or self.base_url == '':
            snapctl_error(
                message="Missing API Key.", code=SNAPCTL_INPUT_ERROR)
        # Check subcommand
        if not self.subcommand in Snapend.SUBCOMMANDS:
            snapctl_error(
                message="Invalid command. Valid commands are " +
                f"{', '.join(Snapend.SUBCOMMANDS)}.",
                code=SNAPCTL_INPUT_ERROR
            )
        if self.subcommand == 'enumerate':
            if not self.game_id:
                snapctl_error(
                    message="Missing required parameter: game_id",
                    code=SNAPCTL_INPUT_ERROR)
        elif self.subcommand == 'clone':
            if not self.game_id:
                snapctl_error(
                    message="Missing required parameter: game_id",
                    code=SNAPCTL_INPUT_ERROR)
            if not self.name:
                snapctl_error(
                    message="Missing required parameter: name",
                    code=SNAPCTL_INPUT_ERROR)
            if not self.env:
                snapctl_error(
                    message="Missing required parameter: env", code=SNAPCTL_INPUT_ERROR)
            if self.env.upper() not in Snapend.ENV_TYPES:
                snapctl_error(
                    message="Invalid environment. Valid environments are " +
                    f"{', '.join(Snapend.ENV_TYPES)}.",
                    code=SNAPCTL_INPUT_ERROR
                )
            if not self.manifest_path_filename:
                snapctl_error(
                    message="Missing required parameter: manifest_path_filename",
                    code=SNAPCTL_INPUT_ERROR)
            if not os.path.isfile(self.manifest_path_filename):
                snapctl_error(
                    message=f"Invalid path {self.manifest_path_filename}. " +
                    "Please enter a valid path to the manifest file",
                    code=SNAPCTL_INPUT_ERROR
                )
        elif self.subcommand == 'apply':
            if not self.manifest_path_filename:
                snapctl_error(
                    message="Missing required parameter: manifest_path_filename",
                    code=SNAPCTL_INPUT_ERROR)
                raise typer.Exit(code=SNAPCTL_INPUT_ERROR)
            if not os.path.isfile(self.manifest_path_filename):
                snapctl_error(
                    message=f"Invalid path {self.manifest_path_filename}. " +
                    "Please enter a valid path to the manifest file",
                    code=SNAPCTL_INPUT_ERROR
                )
            if not self.manifest_file_name:
                snapctl_error(
                    message="Invalid manifest file. Supported formats are .json, .yml, .yaml",
                    code=SNAPCTL_INPUT_ERROR)
        elif self.subcommand == 'download':
            if not self.snapend_id:
                snapctl_error(
                    message="Missing required parameter: snapend_id", code=SNAPCTL_INPUT_ERROR)
            if not self.category:
                snapctl_error(
                    message="Missing required parameter: category", code=SNAPCTL_INPUT_ERROR)
            if self.category not in Snapend.DOWNLOAD_CATEGORY:
                snapctl_error(
                    message="Invalid SDK category. Valid categories are " +
                    f"{', '.join(Snapend.DOWNLOAD_CATEGORY)}.",
                    code=SNAPCTL_INPUT_ERROR
                )
            if not self.category_format:
                snapctl_error(
                    message="Missing required parameter: --format",
                    code=SNAPCTL_INPUT_ERROR)
            if self.category not in Snapend.DOWNLOAD_TYPE_NOT_REQUIRED and \
               (self.download_types is None or self.category_format not in self.download_types):
                snapctl_error(
                    message="Invalid Download format.", code=SNAPCTL_INPUT_ERROR)
            # Check the Protos category
            if self.category == 'protos' and self.category_type not in Snapend.CATEGORY_TYPE_PROTOS:
                snapctl_error(
                    message="Invalid Protos Type. Valid type are " +
                    f"{', '.join(Snapend.CATEGORY_TYPE_PROTOS)}.",
                    code=SNAPCTL_INPUT_ERROR
                )
            # Check the auth type
            if self.category == 'sdk':
                if not self.category_type:
                    snapctl_error(
                        message="Missing required parameter: --type",
                        code=SNAPCTL_INPUT_ERROR)
                if self.category_type not in Snapend.CATEGORY_TYPE_SDK:
                    snapctl_error(
                        message="Invalid SDK Type. Valid type are " +
                        f"{', '.join(Snapend.CATEGORY_TYPE_SDK)}.",
                        code=SNAPCTL_INPUT_ERROR
                    )
                # Special cases for client SDKs
                if self.category_format in CLIENT_SDK_TYPES:
                    if self.category_type in ['api-key', 'app', 'internal']:
                        snapctl_error(
                            message="Invalid combination of format and type. " +
                            ", ".join(CLIENT_SDK_TYPES.keys()) +
                            # " SDKs are only available for --type=omni or --type=user",
                            " SDKs are only available for --type=user",
                            code=SNAPCTL_INPUT_ERROR
                        )
                    # if self.category_type == 'internal':
                    #     snapctl_error(
                    #         message="Internal access type is not supported for " +
                    #         ", ".join(CLIENT_SDK_TYPES.keys()) + " SDKs.",
                    #         code=SNAPCTL_INPUT_ERROR
                    #     )
                if self.category_http_lib:
                    # First check if the format supports http-lib
                    if self.category_format in Snapend.get_formats_supporting_http_lib():
                        # Check if the http-lib is supported for the format
                        valid_http_libs = SDK_TYPES[self.category_format]['http-lib']
                        if self.category_http_lib not in valid_http_libs:
                            snapctl_error(
                                message="Invalid HTTP Library. Valid libraries are " +
                                Snapend.get_http_formats_str(),
                                code=SNAPCTL_INPUT_ERROR
                            )

                    # Check file path
            if not self.out_path:
                snapctl_error(
                    message="Missing required parameter: out-path",
                    code=SNAPCTL_INPUT_ERROR)
            if self.out_path and not os.path.isdir(f"{self.out_path}"):
                snapctl_error(
                    message=f"Invalid path {self.out_path}. " +
                    "Please enter a valid path to save your output file",
                    code=SNAPCTL_INPUT_ERROR
                )
        elif self.subcommand == 'promote':
            if not self.snapend_id:
                snapctl_error(
                    message="Missing required parameter: snapend_id",
                    code=SNAPCTL_INPUT_ERROR)
        # Check update commands
        elif self.subcommand == 'update':
            if not self.snapend_id:
                snapctl_error(
                    message="Missing required parameter: snapend_id",
                    code=SNAPCTL_INPUT_ERROR)
            byosnap_present = True
            if self.byosnap_list is None or len(self.byosnap_list) == 0:
                byosnap_present = False
            byogs_present = True
            if self.byogs_list is None or len(self.byogs_list) == 0:
                byogs_present = False
            if not byosnap_present and not byogs_present:
                snapctl_error(
                    message="The update command needs one of byosnaps or byogs",
                    code=SNAPCTL_INPUT_ERROR)

    ## Subcommands ##
    def enumerate(self) -> None:
        """
          List Snapends
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Enumerating all your game snapends...', total=None)
        try:
            url = f"{self.base_url}/v1/snapser-api/snapends?game_id={self.game_id}"
            res = requests.get(
                url, headers={'api-key': self.api_key},
                timeout=SERVER_CALL_TIMEOUT
            )
            response_json = res.json()
            if res.ok and 'clusters' in response_json:
                snapctl_success(
                    message=response_json['clusters'],
                    progress=progress)
        except RequestException:
            snapctl_error(
                message="Snapctl Exception. Unable to enumerate snapends.",
                code=SNAPCTL_SNAPEND_ENUMERATE_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message="Unable to enumerate snapends.",
            code=SNAPCTL_SNAPEND_ENUMERATE_ERROR, progress=progress)

    def clone(self) -> None:
        """
          Create a Snapend from a manifest
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Cloning your snapend from the manifest...', total=None)
        try:
            with open(self.manifest_path_filename, 'rb') as file:
                files = {'snapend-manifest': file}
                payload = {
                    'game_id': self.game_id,
                    'name': self.name,
                    'env': self.env.upper(),
                    'ext': self.manifest_file_name.split('.')[-1]
                }
                url = f"{self.base_url}/v1/snapser-api/snapends/snapend-manifest"
                res = requests.post(
                    url, headers={'api-key': self.api_key},
                    files=files, data=payload, timeout=SERVER_CALL_TIMEOUT
                )
                if res.ok:
                    # extract the cluster ID
                    response = res.json()
                    if 'cluster' not in response or 'id' not in response['cluster']:
                        snapctl_error(
                            message='Server Error. Unable to get a Snapend ID. ' +
                            'Please try again in sometime.',
                            code=SNAPCTL_SNAPEND_CLONE_SERVER_ERROR,
                            progress=progress
                        )
                    self._assign_snapend_id(response['cluster']['id'])
                    info(f"Cluster ID assigned: {response['cluster']['id']}")
                    if self.blocking:
                        snapctl_success(
                            message='Snapend clone initiated.',
                            progress=progress,
                            no_exit=True
                        )
                        status = self._blocking_get_status()
                        # Fetch the new manifest
                        if status is True:
                            # TODO: Uncomment this if we want to do an auto download
                            # self._setup_for_download(
                            #     self.manifest_file_name.split('.')[-1])
                            # self._execute_download()
                            snapctl_success(
                                message='Snapend clone successful. Do not forget to download the latest manifest.',
                                progress=progress)
                        snapctl_error(
                            message='Snapend clone has been initiated but the Snapend is not up yet.' +
                            'Please try checking the status of the Snapend in some time',
                            code=SNAPCTL_SNAPEND_CLONE_TIMEOUT_ERROR,
                            progress=progress
                        )
                    snapctl_success(
                        message="Snapend clone has been initiated. " +
                        "You can check the status using " +
                        "`snapctl snapend state --snapend-id" +
                        f"{response['cluster']['id']}`",
                        progress=progress
                    )
        except RequestException as e:
            snapctl_error(
                message=f"Unable to apply the manifest snapend. {e}",
                code=SNAPCTL_SNAPEND_CLONE_ERROR, progress=progress
            )
        finally:
            progress.stop()
        snapctl_error(
            message='Unable to apply the manifest.',
            code=SNAPCTL_SNAPEND_CLONE_ERROR, progress=progress)

    def apply(self) -> None:
        """
          Apply a manifest
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Applying your manifest...', total=None)
        try:
            with open(self.manifest_path_filename, 'rb') as file:
                files = {'snapend-manifest': file}
                payload = {
                    'ext': self.manifest_file_name.split('.')[-1]
                }
                if self.force is True:
                    info('Force flag is set. Ignoring manifest diff.')
                    payload['ignore_diff'] = 'true'
                url = f"{self.base_url}/v1/snapser-api/snapends/snapend-manifest"
                res = requests.put(
                    url, headers={'api-key': self.api_key},
                    files=files, data=payload, timeout=SERVER_CALL_TIMEOUT
                )
                response = res.json()
                if res.ok:
                    # extract the cluster ID
                    if 'cluster' not in response or 'id' not in response['cluster']:
                        snapctl_error(
                            message='Server Error. Unable to get a Snapend ID. '
                            'Please try again in sometime.',
                            code=SNAPCTL_SNAPEND_APPLY_SERVER_ERROR,
                            progress=progress
                        )
                    self._assign_snapend_id(response['cluster']['id'])
                    if self.blocking:
                        snapctl_success(
                            message='Snapend apply has been initiated.',
                            progress=progress,
                            no_exit=True
                        )
                        status = self._blocking_get_status()
                        # Fetch the new manifest
                        if status is True:
                            # TODO: Uncomment this if we want to do an auto download
                            # self._setup_for_download(
                            #     self.manifest_file_name.split('.')[-1])
                            # self._execute_download()
                            snapctl_success(
                                message='Snapend apply successful. Do not forget to download ' +
                                'the latest manifest.',
                                progress=progress)
                        snapctl_error(
                            message='Snapend apply has been initiated but the Snapend is ' +
                            'not up yet. Please try checking the status of the Snapend in some time',
                            code=SNAPCTL_SNAPEND_APPLY_TIMEOUT_ERROR, progress=progress
                        )
                    snapctl_success(
                        message="Snapend apply has been initiated. " +
                        "You can check the status using " +
                        "`snapctl snapend state --snapend-id" +
                        f"{response['cluster']['id']}`",
                        progress=progress
                    )
                else:
                    if "api_error_code" in response and "message" in response:
                        if response['api_error_code'] == HTTP_ERROR_SNAPEND_MANIFEST_MISMATCH:
                            snapctl_error(
                                message='Remote manifest does not match the manifest in the applied_configuration field.',
                                code=SNAPCTL_SNAPEND_APPLY_MANIFEST_MISMATCH_ERROR, progress=progress
                            )
        except RequestException as e:
            snapctl_error(
                message=f"Unable to apply the manifest snapend. {e}",
                code=SNAPCTL_SNAPEND_APPLY_ERROR, progress=progress
            )
        finally:
            progress.stop()
        snapctl_error(
            message='Unable to apply the manifest.', code=SNAPCTL_SNAPEND_APPLY_ERROR, progress=progress)

    def promote(self) -> None:
        """
          Promote a staging manifest to production
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Promoting your staging snapend...', total=None)
        try:
            with open(self.manifest_path_filename, 'rb') as file:
                payload = {
                    'snapend_id': self.snapend_id
                }
                url = f"{self.base_url}/v1/snapser-api/snapends/promote"
                res = requests.put(
                    url, headers={'api-key': self.api_key},
                    json=payload, timeout=SERVER_CALL_TIMEOUT
                )
                if res.ok:
                    # extract the cluster ID
                    response = res.json()
                    if 'cluster' not in response or 'id' not in response['cluster']:
                        snapctl_error(
                            message='Server Error. Unable to get a Snapend ID. '
                            'Please try again in sometime.',
                            code=SNAPCTL_SNAPEND_PROMOTE_SERVER_ERROR,
                            progress=progress
                        )
                    self._assign_snapend_id(response['cluster']['id'])
                    if self.blocking:
                        snapctl_success(
                            message='Snapend promotion has been initiated.',
                            progress=progress,
                            no_exit=True
                        )
                        status = self._blocking_get_status()
                        if status is True:
                            # TODO: Uncomment this if we want to do an auto download
                            # self._setup_for_download(
                            #     self.manifest_file_name.split('.')[-1])
                            # self._execute_download()
                            # Fetch the new manifest
                            snapctl_success(
                                message='Snapend promote successful. Do not forget to ' +
                                'download the latest manifest.',
                                progress=progress
                            )
                        snapctl_error(
                            message='Snapend apply has been initiated but the Snapend is not up yet.' +
                            'Please try checking the status of the Snapend in some time',
                            code=SNAPCTL_SNAPEND_PROMOTE_TIMEOUT_ERROR,
                            progress=progress
                        )
                    snapctl_success(
                        message="Snapend apply has been initiated. " +
                        "You can check the status using " +
                        "`snapctl snapend state --snapend-id" +
                        f"{response['cluster']['id']}`",
                        progress=progress
                    )
                snapctl_error(
                    message='Unable to promote the manifest. Reason: ' +
                    f'{res.text}',
                    code=SNAPCTL_SNAPEND_PROMOTE_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message=f"Unable to promote the snapend. {e}",
                code=SNAPCTL_SNAPEND_PROMOTE_ERROR, progress=progress
            )
        finally:
            progress.stop()
        snapctl_error(
            message="Unable to promote the snapend.",
            code=SNAPCTL_SNAPEND_PROMOTE_ERROR, progress=progress)

    def download(self) -> None:
        """
          Download SDKs, Protos, Admin Settings and Configuration
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description=f'Downloading your Custom {self.category}...', total=None)
        try:
            if self._execute_download():
                snapctl_success(
                    message="Snapend download successful. " +
                    f"{self.category} saved at {self.out_path}",
                    progress=progress
                )
        except RequestException as e:
            snapctl_error(
                message=f"Unable to download {self.category}. Reason: {e}",
                code=SNAPCTL_SNAPEND_DOWNLOAD_ERROR, progress=progress
            )
        finally:
            progress.stop()
        snapctl_error(
            message=f"Unable to download {self.category}",
            code=SNAPCTL_SNAPEND_DOWNLOAD_ERROR, progress=progress)

    def update(self, no_exit: bool = False) -> None:
        """
          Update a Snapend
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Updating your Snapend...', total=None)
        try:
            payload = {
                'byosnap_updates': self.byosnap_list,
                'byogs_updates': self.byogs_list
            }
            url = f"{self.base_url}/v1/snapser-api/snapends/{self.snapend_id}"
            res = requests.patch(
                url, json=payload, headers={'api-key': self.api_key},
                timeout=SERVER_CALL_TIMEOUT
            )
            if res.ok:
                if self.blocking:
                    snapctl_success(
                        message='Snapend update has been initiated.',
                        progress=progress,
                        no_exit=True
                    )
                    status = self._blocking_get_status()
                    # Fetch the new manifest
                    if status is True:
                        # TODO: Uncomment this if we want to do an auto download
                        # self._setup_for_download(
                        #     self.manifest_file_name.split('.')[-1])
                        # self._execute_download()
                        return snapctl_success(
                            message='Snapend update successful. Do not forget to ' +
                            'download the latest manifest.',
                            progress=progress,
                            no_exit=no_exit
                        )
                    snapctl_error(
                        message='Snapend update has been initiated. ' +
                        'You can check the status using `snapctl snapend state`',
                        code=SNAPCTL_SNAPEND_UPDATE_TIMEOUT_ERROR,
                        progress=progress
                    )
                return snapctl_success(
                    message="Snapend update has been initiated. " +
                    "You can check the status using " +
                    f"`snapctl snapend state --snapend-id {self.snapend_id}`",
                    progress=progress,
                    no_exit=no_exit
                )
            snapctl_error(
                message=f"Unable to update the snapend. Reason: {res.text}",
                code=SNAPCTL_SNAPEND_UPDATE_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message=f"Unable to update the snapend {e}",
                code=SNAPCTL_SNAPEND_UPDATE_ERROR, progress=progress
            )
        finally:
            progress.stop()
        snapctl_error(
            message="Unable to update the snapend.",
            code=SNAPCTL_SNAPEND_UPDATE_ERROR, progress=progress)

    def state(self) -> None:
        """
          Get the state of a Snapend
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Getting your Snapend state...', total=None)
        try:
            current_state = self._get_snapend_state()
            if current_state != 'INVALID':
                snapctl_success(
                    message='Snapend get state successful. Current snapend state is: ' +
                    f'{current_state}',
                    progress=progress)
            snapctl_error(
                message="Unable to get the snapend state.",
                code=SNAPCTL_SNAPEND_STATE_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message=f"Unable to get your snapend state {e}",
                code=SNAPCTL_SNAPEND_STATE_ERROR, progress=progress
            )
        finally:
            progress.stop()
        snapctl_error(
            message="Unable to get the snapend state.",
            code=SNAPCTL_SNAPEND_STATE_ERROR, progress=progress)

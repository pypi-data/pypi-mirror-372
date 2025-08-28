"""
Helper functions for snapctl
"""
from typing import Union, Dict
from pathlib import Path
import re
import platform
import os
import json
import requests
import typer
from requests.exceptions import RequestException
from rich.progress import Progress
from snapctl.config.constants import HTTP_NOT_FOUND, HTTP_FORBIDDEN, HTTP_UNAUTHORIZED, \
    SERVER_CALL_TIMEOUT, SNAPCTL_CONFIGURATION_ERROR, SNAPCTL_SUCCESS
from snapctl.config.hashes import ARCHITECTURE_MAPPING
from snapctl.utils.echo import error, success
from snapctl.config.app import APP_CONFIG


def validate_api_key(base_url: str, api_key: Union[str, None]) -> bool:
    """
    This function validates the API Key
    """
    try:
        url = f"{base_url}/v1/snapser-api/validate"
        res = requests.post(
            url, json={'api_key': api_key},
            timeout=SERVER_CALL_TIMEOUT
        )
        if res.ok:
            success('API Key validated')
            return True
        if res.status_code == HTTP_UNAUTHORIZED:
            error(
                'API Key verification failed. Your API Key is either invalid or may have expired. ',
                SNAPCTL_CONFIGURATION_ERROR
            )
        elif res.status_code == HTTP_FORBIDDEN:
            error(
                'Permission denied. Your role has been revoked. Please contact your administrator.',
                SNAPCTL_CONFIGURATION_ERROR
            )
        else:
            error('Failed to validate API Key. Error:',
                  SNAPCTL_CONFIGURATION_ERROR)
    except RequestException as e:
        error(f"Exception: Unable to update your snapend {e}")
    raise typer.Exit(code=SNAPCTL_CONFIGURATION_ERROR)


def get_composite_token(base_url: str, api_key: Union[str, None], action: str, params: object) -> str:
    """
    This function exchanges the api_key for a composite token.
    """
    if not api_key or base_url == '':
        return ''
    # Exchange the api_key for a token
    payload: object = {
        'action': action,
        'params': params
    }
    res = requests.post(f"{base_url}/v1/snapser-api/composite-token",
                        headers={'api-key': api_key}, json=payload, timeout=SERVER_CALL_TIMEOUT)
    if not res.ok:
        if res.status_code == HTTP_NOT_FOUND:
            error('Service ID is invalid.')
        elif res.status_code == HTTP_UNAUTHORIZED:
            error(
                'API Key verification failed. Your API Key is either invalid or may have expired. '
            )
        elif res.status_code == HTTP_FORBIDDEN:
            error(
                'Permission denied. Your role has been revoked. Please contact your administrator.'
            )
        else:
            error(f'Failed to validate API Key. Error: {res.text}')
        raise typer.Exit(code=SNAPCTL_CONFIGURATION_ERROR)
    success('Generate snapctl transaction token')
    return res.json()['token']


def check_dockerfile_architecture(dockerfile_path: str, system_arch: str) -> Dict[str, object]:
    """
    Check the Dockerfile for architecture specific commands
    """
    response = {
        'error': False,
        'message': ''
    }
    # Normalize system architecture
    system_arch = ARCHITECTURE_MAPPING.get(system_arch, system_arch)
    try:
        lines = []
        with open(dockerfile_path, 'r') as file:
            lines = file.readlines()
        for line_number, line in enumerate(lines, 1):
            if line.startswith('#'):
                continue
            # Checking various build and run commands for architecture specifics
            patterns = [
                # FROM with platform
                r'FROM --platform=linux/(\w+)',
                # dotnet runtime
                r'-r linux-(\w+)',
                # Build args specifying arch
                r'--build-arg ARCH=(\w+)',
                # Environment variables setting arch
                r'ENV ARCH=(\w+)',
                # cmake specifying arch
                r'cmake.*?-DARCH=(\w+)',
                # make specifying arch
                r'make.*?ARCH=(\w+)'
            ]

            for pattern in patterns:
                match = re.search(pattern, line)
                if match and ARCHITECTURE_MAPPING.get(match.group(1)) != system_arch:
                    response['error'] = True
                    response['message'] = '[Architecture Mismatch] Line ' + \
                        f'{line_number}: "{line.strip()}" ' + \
                        f'of Dockerfile {dockerfile_path} ' + \
                        f'specifies architecture {match.group(1)}, which does not match the ' + \
                        f'systems ({system_arch}).'
                    return response
    except FileNotFoundError:
        response['error'] = True
        response['message'] = f'Dockerfile not found at {dockerfile_path}'
        return response
    except Exception as e:
        response['error'] = True
        response['message'] = f'Exception {e}'
        return response
    return response


def snapctl_success(message: str, progress: Union[Progress, None] = None, no_exit: bool = False):
    """
    This function exits the snapctl
    """
    if progress:
        progress.stop()
    success(message)
    if not no_exit:
        raise typer.Exit(code=SNAPCTL_SUCCESS)


def snapctl_error(message: str, code: int, progress: Union[Progress, None] = None):
    """
    This function exits the snapctl
    """
    if progress:
        progress.stop()
    error(message, code)
    raise typer.Exit(code=code)


def check_use_containerd_snapshotter() -> bool:
    '''
    This function checks the value of the UseContainerdSnapshotter in the Docker Desktop
    settings-store.json
    '''
    # Determine the OS
    os_name = platform.system()

    # Determine the correct path based on the OS
    if os_name == 'Darwin':
        path = os.path.expanduser(
            '~/Library/Group Containers/group.com.docker/settings-store.json')
    elif os_name == 'Windows':
        username = os.getlogin()  # Get the current logged-in username
        path = f"C:\\Users\\{username}\\AppData\\Roaming\\Docker\\settings-store.json"
    elif os_name == 'Linux':
        path = os.path.expanduser('~/.docker/desktop/settings-store.json')
    else:
        return False

    # Try to read the file and extract the UseContainerdSnapshotter value
    try:
        with open(path, 'r') as file:
            settings = json.load(file)
            # Access the specific key in the JSON data
            return settings.get('UseContainerdSnapshotter', False)
    except FileNotFoundError:
        return False
    except Exception:
        return False


def get_dot_snapser_dir() -> Path:
    """
    Returns the .snapser configuration directory, creating it if necessary.
    """
    config_dir = Path.home() / ".snapser"
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir


def get_config_value(environment: str, key: str) -> str:
    """
    Returns the config value based on the environment.
    """
    if environment == '' or environment not in APP_CONFIG or key not in APP_CONFIG[environment]:
        return ''
    return APP_CONFIG[environment][key]

"""
  Snapend CLI commands
"""
from typing import Union
import requests
from requests.exceptions import RequestException
from rich.progress import Progress, SpinnerColumn, TextColumn
from snapctl.config.constants import SERVER_CALL_TIMEOUT, SNAPCTL_INPUT_ERROR, \
    SNAPCTL_GAME_CREATE_ERROR, SNAPCTL_GAME_ENUMERATE_ERROR, \
    HTTP_ERROR_DUPLICATE_GAME_NAME, SNAPCTL_GAME_CREATE_DUPLICATE_NAME_ERROR, \
    HTTP_ERROR_GAME_LIMIT_REACHED, SNAPCTL_GAME_CREATE_LIMIT_ERROR
from snapctl.utils.helper import snapctl_error, snapctl_success


class Game:
    """
      CLI commands exposed for a Game
    """
    SUBCOMMANDS = ['create', 'enumerate']

    def __init__(
            self, *, subcommand: str, base_url: str, api_key: Union[str, None],
            name: Union[str, None] = None
    ) -> None:
        self.subcommand: str = subcommand
        self.base_url: str = base_url
        self.api_key: Union[str, None] = api_key
        self.name: Union[str, None] = name
        # Validate input
        self.validate_input()

    def validate_input(self) -> None:
        """
          Validator
        """
        # Check API Key and Base URL
        if not self.api_key or self.base_url == '':
            snapctl_error(
                message="Missing API Key.", code=SNAPCTL_INPUT_ERROR)
        # Check subcommand
        if not self.subcommand in Game.SUBCOMMANDS:
            snapctl_error(
                message="Invalid command. Valid commands are " +
                f"{', '.join(Game.SUBCOMMANDS)}.",
                code=SNAPCTL_INPUT_ERROR)
        # Check sdk-download commands
        if self.subcommand == 'create':
            if self.name is None or self.name == '':
                snapctl_error(
                    message="Missing game name.",
                    code=SNAPCTL_INPUT_ERROR)

    def create(self, no_exit: bool = False) -> bool:
        """
          Create a game
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Creating a new game on Snapser...', total=None)
        try:
            url = f"{self.base_url}/v1/snapser-api/games"
            payload = {
                'name': self.name
            }
            res = requests.post(
                url, headers={'api-key': self.api_key},
                json=payload, timeout=SERVER_CALL_TIMEOUT
            )
            if res.ok:
                snapctl_success(
                    message=f"Game {self.name} create successful",
                    progress=progress, no_exit=no_exit)
                return
            response_json = res.json()
            if "api_error_code" in response_json and "message" in response_json:
                if response_json['api_error_code'] == HTTP_ERROR_GAME_LIMIT_REACHED:
                    snapctl_error(
                        message=f"Game {self.name} already exists.",
                        code=SNAPCTL_GAME_CREATE_LIMIT_ERROR, progress=progress)
                if response_json['api_error_code'] == HTTP_ERROR_DUPLICATE_GAME_NAME:
                    snapctl_error(
                        message=f"Game {self.name} already exists.",
                        code=SNAPCTL_GAME_CREATE_DUPLICATE_NAME_ERROR, progress=progress)
            snapctl_error(
                message=f'Server error: {response_json}',
                code=SNAPCTL_GAME_CREATE_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message=f"Exception: Unable to download the SDK {e}",
                code=SNAPCTL_GAME_CREATE_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='Failed to create game.',
            code=SNAPCTL_GAME_CREATE_ERROR, progress=progress)

    def enumerate(self) -> bool:
        """
          Enumerate all games
        """
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            transient=True,
        )
        progress.start()
        progress.add_task(
            description='Enumerating all your games...', total=None)
        try:
            url = f"{self.base_url}/v1/snapser-api/games"
            res = requests.get(
                url, headers={'api-key': self.api_key},
                timeout=SERVER_CALL_TIMEOUT
            )
            response_json = res.json()
            if res.ok and 'games' in response_json:
                snapctl_success(
                    message=response_json['games'], progress=progress)
            snapctl_error(
                message='Unable to enumerate games.',
                code=SNAPCTL_GAME_ENUMERATE_ERROR, progress=progress)
        except RequestException as e:
            snapctl_error(
                message=f"Exception: Unable to update your snapend {e}",
                code=SNAPCTL_GAME_ENUMERATE_ERROR, progress=progress)
        finally:
            progress.stop()
        snapctl_error(
            message='Failed to enumerate games.',
            code=SNAPCTL_GAME_ENUMERATE_ERROR, progress=progress)

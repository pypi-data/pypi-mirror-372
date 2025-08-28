"""
    SnapCTL entrypoint
"""
import configparser
import os
from sys import platform
from typing import Union
import typer
import pyfiglet

from snapctl.commands.byosnap import ByoSnap
from snapctl.commands.byogs import ByoGs
from snapctl.commands.game import Game
from snapctl.commands.generate import Generate
from snapctl.commands.snapend import Snapend
from snapctl.commands.byows import Byows
from snapctl.commands.release_notes import ReleaseNotes
from snapctl.config.constants import COMPANY_NAME, API_KEY, URL_KEY, CONFIG_FILE_MAC, \
    CONFIG_FILE_WIN, DEFAULT_PROFILE, VERSION, SNAPCTL_SUCCESS, CONFIG_PATH_KEY, \
    SNAPCTL_CONFIGURATION_INCORRECT, VERSION_PREFIX
from snapctl.config.endpoints import END_POINTS, GATEWAY_END_POINTS
from snapctl.config.hashes import PROTOS_TYPES, SERVICE_IDS, \
    SNAPEND_MANIFEST_TYPES, SDK_TYPES
from snapctl.utils.echo import error, success, info
from snapctl.utils.helper import validate_api_key
from snapctl.utils.telemetry import telemetry

######### Globals #########


def draw_ascii_text():
    """
      Draws the ascii text for Snapser
    """
    ascii_text = pyfiglet.figlet_format(COMPANY_NAME)
    typer.echo(ascii_text)


app = typer.Typer(
    help=draw_ascii_text(),
    context_settings={
        "help_option_names": ["-h", "--help"]
    }
)


######### HELPER METHODS #########


def extract_config(extract_key: str, profile: Union[str, None] = None) -> object:
    """
      Extracts the API Key from the environment variable and if not present from the config file
    """
    result = {
        'location': '',
        'value': None
    }
    # Option 1 - Get the API Key from the environment variable
    env_api_key = os.getenv(extract_key)
    if env_api_key is not None:
        result['location'] = 'environment-variable'
        result['value'] = env_api_key
        return result
    encoding: Union[str, None] = "utf-8-sig" if platform == 'win32' else None
    # Option 2 - Get the API Key from CONFIG PATH environment variable
    config_file_path: Union[str, None] = os.getenv(CONFIG_PATH_KEY)
    # Option 3 - Get the API Key from the hardcoded config file we look for
    if config_file_path is None:
        if platform == 'win32':
            config_file_path = os.path.expandvars(CONFIG_FILE_WIN)
        else:
            config_file_path = os.path.expanduser(CONFIG_FILE_MAC)
    result['location'] = f'{config_file_path}'
    if os.path.isfile(config_file_path):
        config = configparser.ConfigParser()
        config.read(config_file_path, encoding=encoding)
        config_profile: str = DEFAULT_PROFILE
        if profile is not None and profile != '' and profile != DEFAULT_PROFILE:
            result['location'] = f'"{config_file_path}:profile {profile}"'
            config_profile = f'profile {profile}'
            info(
                'Trying to extract API KEY from ' +
                f'{config_file_path}:profile {profile}"'
            )
        result['value'] = config.get(
            config_profile, extract_key, fallback=None, raw=True
        )
    else:
        info(
            f'Config file on platform {platform} not found at {config_file_path}')
    return result


def get_environment(api_key_value: Union[str, None]) -> str:
    """
        Returns the environment based on the api_key
    """
    if api_key_value is None:
        return 'UNKNOWN'
    if api_key_value.startswith('dev_'):
        return 'DEV'
    if api_key_value.startswith('devtwo_'):
        return 'DEV_TWO'
    if api_key_value.startswith('playtest_'):
        return 'PLAYTEST'
    return 'PROD'


def get_base_url(api_key: Union[str, None]) -> str:
    """
        Returns the base url based on the api_key
    """
    # Check if the user has a URL override
    url_key_obj = extract_config(URL_KEY, None)
    if url_key_obj['value'] is not None:
        return url_key_obj['value']
    # If there was no override then we use the default
    if api_key is None:
        return ''
    if api_key.startswith('dev_'):
        return END_POINTS['DEV']
    if api_key.startswith('devtwo_'):
        return END_POINTS['DEV_TWO']
    if api_key.startswith('playtest_'):
        return END_POINTS['PLAYTEST']
    return END_POINTS['PROD']


def get_base_snapend_url(api_key: Union[str, None]) -> str:
    """
        Returns the base url for snapend based on the api_key
    """
    if api_key is None:
        return ''
    if api_key.startswith('dev_'):
        return GATEWAY_END_POINTS['SANDBOX']
    if api_key.startswith('devtwo_'):
        return GATEWAY_END_POINTS['SANDBOX']
    if api_key.startswith('playtest_'):
        return GATEWAY_END_POINTS['SANDBOX']
    return GATEWAY_END_POINTS['LIVE']


def validate_command_context(
        ctx: typer.Context,
):
    """
      Validator to confirm if the context has been set properly
    """
    if ctx.obj['api_key'] is None or ctx.obj['base_url'] == '':
        error("Snapctl Configuration Incorrect. Unable to extract API Key",
              SNAPCTL_CONFIGURATION_INCORRECT)
        raise typer.Exit(code=SNAPCTL_CONFIGURATION_INCORRECT)

######### CALLBACKS #########


def default_context_callback(ctx: typer.Context):
    """
      Common Callback to set the main app context
      This gets called on every command right at the start
    """
    # info("In default callback")
    # Ensure ctx object is instantiated
    ctx.ensure_object(dict)
    # Extract the api_key
    api_key_obj = extract_config(API_KEY, None)
    ctx.obj['version'] = VERSION
    ctx.obj['api_key'] = api_key_obj['value']
    ctx.obj['api_key_location'] = api_key_obj['location']
    ctx.obj['profile'] = DEFAULT_PROFILE
    ctx.obj['environment'] = get_environment(api_key_obj['value'])
    ctx.obj['base_url'] = get_base_url(api_key_obj['value'])
    ctx.obj['base_snapend_url'] = get_base_snapend_url(api_key_obj['value'])


def api_key_context_callback(
        ctx: typer.Context,
        api_key: Union[str, None] = None
):
    """
      Callback to set the context for the api_key
      This gets called only if the user has added a --api-key override
    """
    if api_key is None:
        return None
    # info("In API Key callback")
    # Ensure ctx object is instantiated
    ctx.ensure_object(dict)
    ctx.obj['version'] = VERSION
    ctx.obj['api_key'] = api_key
    ctx.obj['api_key_location'] = 'command-line-argument'
    ctx.obj['environment'] = get_environment(api_key)
    ctx.obj['base_url'] = get_base_url(api_key)


def profile_context_callback(
        ctx: typer.Context,
        profile: Union[str, None] = None
):
    """
      Callback to set the context for the profile
      This gets called only if the user has added a --profile override
    """
    # Its important to early return if user has already entered API Key via command line
    if profile is None or ctx.obj['api_key_location'] == 'command-line-argument':
        return None
    # info("In Profile Callback")
    # Ensure ctx object is instantiated
    ctx.ensure_object(dict)
    api_key_obj = extract_config(API_KEY, profile)
    # if api_key_obj['value'] is None and profile is not None and profile != '':
    #     conf_file = ''
    #     if platform == 'win32':
    #         conf_file = os.path.expandvars(CONFIG_FILE_WIN)
    #     else:
    #         conf_file = os.path.expanduser(CONFIG_FILE_MAC)
    #     error(
    #         f'Invalid profile input {profile}. '
    #         f'Please check your snap config file at {conf_file}'
    #     )
    ctx.obj['version'] = VERSION
    ctx.obj['api_key'] = api_key_obj['value']
    ctx.obj['api_key_location'] = api_key_obj['location']
    ctx.obj['profile'] = profile if profile else DEFAULT_PROFILE
    ctx.obj['environment'] = get_environment(api_key_obj['value'])
    ctx.obj['base_url'] = get_base_url(api_key_obj['value'])


# Presently in typer this is the only way we can expose the `--version`
def version_callback(value: bool = True):
    """
        Prints the version and exits
    """
    if value:
        success(f"Snapctl version: {VERSION}")
        raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.callback()
def common(
    ctx: typer.Context,
    version: bool = typer.Option(
        None, "--version", "-v",
        help="Get the Snapctl version.",
        callback=version_callback
    ),
):
    """
    Snapser CLI Tool
    """
    default_context_callback(ctx)

######### TYPER COMMANDS #########


@app.command()
@telemetry("validate", subcommand_arg="subcommand")
def validate(
    ctx: typer.Context,
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
    Validate your Snapctl setup
    """
    validate_command_context(ctx)
    validate_api_key(ctx.obj['base_url'], ctx.obj['api_key'])
    success("Setup is valid")
    raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.command()
@telemetry("release_notes", subcommand_arg="subcommand")
def release_notes(
    ctx: typer.Context,
    subcommand: str = typer.Argument(
        ..., help="Release Notes Subcommands: " + ", ".join(ReleaseNotes.SUBCOMMANDS) + "."
    ),
    version: str = typer.Option(
        VERSION_PREFIX + VERSION, help="(optional: show-version) If not passed will show the latest version."
    ),
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
    Release notes for Snapctl
    """
    validate_command_context(ctx)
    release_notes_obj: ReleaseNotes = ReleaseNotes(
        subcommand=subcommand,
        version=version
    )
    getattr(release_notes_obj, subcommand.replace('-', '_'))()
    raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.command()
@telemetry("byogs", subcommand_arg="subcommand")
def byogs(
    ctx: typer.Context,
    # Required fields
    subcommand: str = typer.Argument(
        ..., help="BYOGs Subcommands: " + ", ".join(ByoGs.SUBCOMMANDS) + "."
    ),
    tag: str = typer.Option(
        None, "--tag",
        help="(req: build, push, publish) Tag for your snap"
    ),
    # publish and publish-image
    path: Union[str, None] = typer.Option(
        None, "--path", help="(req: build, publish) Path to your snap code"
    ),
    resources_path: Union[str, None] = typer.Option(
        None, "--resources-path", help="(optional: publish) Path to resources such as your Dockerfile, swagger.json or README.md"
    ),
    docker_filename: str = typer.Option(
        "Dockerfile", help="(optional: publish) Dockerfile name to use"
    ),
    skip_build: bool = typer.Option(
        False, "--skip-build", help="(optional: publish) Skip the build step. You have to pass the image tag you used during the build step."
    ),
    snapend_id: str = typer.Option(
        None, "--snapend-id",
        help=("(req: sync) Snapend Id.")
    ),
    fleet_names: str = typer.Option(
        None, "--fleet-names",
        help=("(req: sync) Comma separated fleet names.")
    ),
    blocking: bool = typer.Option(
        False, "--blocking",
        help=(
            "(optional: update) Set to true if you want to wait for the update to complete "
            "before returning."
        )
    ),
    # overrides
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
      Bring your own game server commands
    """
    validate_command_context(ctx)
    byogs_obj: ByoGs = ByoGs(
        subcommand=subcommand,
        base_url=ctx.obj['base_url'],
        api_key=ctx.obj['api_key'],
        tag=tag,
        path=path,
        resources_path=resources_path,
        docker_filename=docker_filename,
        skip_build=skip_build,
        snapend_id=snapend_id,
        fleet_names=fleet_names,
        blocking=blocking
    )
    getattr(byogs_obj, subcommand.replace('-', '_'))()
    success(f"BYOGs {subcommand} complete")
    raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.command()
@telemetry("byosnap", subcommand_arg="subcommand")
def byosnap(
    ctx: typer.Context,
    # Required fields
    subcommand: str = typer.Argument(
        ..., help="BYOSnap Subcommands: " + ", ".join(ByoSnap.SHOW_SUBCOMMANDS) + ". Commands to be deprecated soon: " + ", ".join(ByoSnap.TO_DEPRECATE_SUBCOMMANDS) + "."
    ),
    byosnap_id: Union[str, None] = typer.Option(
        None, "--byosnap-id", help="(req: 'publish', 'sync', 'upload-docs', 'create', 'publish-image', 'publish-version', 'update-version') BYOSnap Id. Should start with byosnap-"
    ),
    # publish
    path: Union[str, None] = typer.Option(
        None, "--path", help="(req: publish, sync, publish-image, publish-version) Path to your snap code"
    ),
    resources_path: Union[str, None] = typer.Option(
        None, "--resources-path", help="(optional: publish, sync, publish-image, publish-version; req: upload-docs) Path to resources such as your Dockerfile, snapser-byosnap-profile.json, snapser-tool-*.json, swagger.json or README.md"
    ),
    # publish, sync and publish-version
    version: Union[str, None] = typer.Option(
        None, "--version",
        help="(req: publish, sync, publish-version) Snap version. Should start with v. Example vX.X.X"
    ),
    # sync
    snapend_id: str = typer.Option(
        None, "--snapend-id",
        help=("(req: sync) Snapend Id. NOTE: Development Snapends only.")
    ),
    blocking: bool = typer.Option(
        False, "--blocking",
        help=(
            "(optional: sync) Set to true if you want to wait for the update to complete "
            "before returning."
        )
    ),
    # create
    name: str = typer.Option(
        None, "--name", help="(req: create) Name for your snap."
    ),
    desc: str = typer.Option(
        None, "--desc", help="(req: create) Description for your snap"
    ),
    platform_type: str = typer.Option(
        None, "--platform",
        help="(req: create) Platform for your snap - " +
        ", ".join(ByoSnap.PLATFORMS) + "."
    ),
    language: str = typer.Option(
        None, "--language",
        help="(req: create) Language of your snap - " +
        ", ".join(ByoSnap.LANGUAGES) + "."
    ),
    # publish-image, publish-version, publish, sync, upload-docs
    tag: str = typer.Option(
        None, "--tag", help=(
            "(req: publish-image, publish-version, upload-docs) (optional: publish, sync) Tag for your snap"
        )
    ),
    # overrides
    skip_build: bool = typer.Option(
        False, "--skip-build", help="(optional: publish-image, publish, sync) Skip the build step. You have to pass the image tag you used during the build step."
    ),
    docker_filename: str = typer.Option(
        "Dockerfile", help="(optional override: publish, sync) Dockerfile name to use"
    ),
    profile_filename: str = typer.Option(
        "snapser-byosnap-profile.json", "--profile-filename", help="(req: generate-profile, validate-profile) (optional override: publish, publish-version) BYOSnap Profile is picked up via the --path or the --resources-path. This allows you to override the default profile filename."
    ),
    out_path: Union[str, None] = typer.Option(
        None, "--out-path", help=(
            "(req: generate-profile) Path to output the byosnap profile"
        )
    ),
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="(optional override) API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="(optional override) Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
      Bring your own snap commands
    """
    validate_command_context(ctx)
    byosnap_obj: ByoSnap = ByoSnap(
        subcommand=subcommand,
        base_url=ctx.obj['base_url'],
        api_key=ctx.obj['api_key'],
        byosnap_id=byosnap_id,
        name=name,
        desc=desc,
        platform_type=platform_type,
        language=language,
        tag=tag,
        path=path,
        resources_path=resources_path,
        docker_filename=docker_filename,
        version=version,
        skip_build=skip_build,
        snapend_id=snapend_id,
        blocking=blocking,
        profile_filename=profile_filename,
        out_path=out_path
    )
    getattr(byosnap_obj, subcommand.replace('-', '_'))()
    success(f"BYOSnap {subcommand} complete")
    raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.command()
@telemetry("game", subcommand_arg="subcommand")
def game(
    ctx: typer.Context,
    # Required fields
    subcommand: str = typer.Argument(
        ..., help="Game Subcommands: " + ", ".join(Game.SUBCOMMANDS) + "."
    ),
    # name
    name: str = typer.Option(
        None, "--name",
        help=("(req: create) Name of your game: ")
    ),
    # overrides
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
      Game commands
    """
    validate_command_context(ctx)
    game_obj: Game = Game(
        subcommand=subcommand,
        base_url=ctx.obj['base_url'],
        api_key=ctx.obj['api_key'],
        name=name
    )
    getattr(game_obj, subcommand.replace('-', '_'))()
    success(f"Game {subcommand} complete")
    raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.command()
@telemetry("generate", subcommand_arg="subcommand")
def generate(
    ctx: typer.Context,
    # Required fields
    subcommand: str = typer.Argument(
        ..., help=(
            "Generate Subcommands: " +
            ", ".join(Generate.SUBCOMMANDS) + "."
        )
    ),
    category: Union[str, None] = typer.Option(
        None, "--category",
        help=(
            "(req: token) (token: " +
              ", ".join(Generate.CATEGORIES['credentials']) + ')'
        )
    ),
    out_path: Union[str, None] = typer.Option(
        None, "--out-path", help=(
            "(req: token) Path to output the byosnap profile"
        )
    ),
    # overrides
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
      Generate files to be used by other commands
    """
    validate_command_context(ctx)
    generate_obj: Generate = Generate(
        subcommand=subcommand,
        base_url=ctx.obj['base_url'],
        api_key=ctx.obj['api_key'],
        category=category,
        out_path=out_path
    )
    getattr(generate_obj, subcommand.replace('-', '_'))()
    success(f"Generate {subcommand} complete")
    raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.command()
@telemetry("snapend", subcommand_arg="subcommand")
def snapend(
    ctx: typer.Context,
    # Required fields
    subcommand: str = typer.Argument(
        ..., help="Snapend Subcommands: " + ", ".join(Snapend.SUBCOMMANDS) + "."
    ),
    # snapend_id: str = typer.Argument(..., help="Snapend Id"),
    snapend_id: str = typer.Option(
        None, "--snapend-id",
        help=("(req: state, update, download) Snapend Id")
    ),
    # enumerate
    game_id: str = typer.Option(
        None, "--game-id",
        help="(req: enumerate, clone) Game Id"
    ),
    # apply, clone
    manifest_path_filename: str = typer.Option(
        None, "--manifest-path-filename",
        help="(req: apply|clone) Full Path to the manifest file including the filename."
    ),
    force: bool = typer.Option(
        False, "--force",
        help="(optional: apply) If true, Snapser will ignore the configuration diff validation and allow to force apply the manifest."
    ),
    # download
    category: str = typer.Option(
        None, "--category",
        help=(
            "(req: download) Category of the Download: " +
            ", ".join(Snapend.DOWNLOAD_CATEGORY) + "."
        )
    ),
    category_format: str = typer.Option(
        None, "--format",
        help=(
            "(req: --category sdk|protos|snapend-manifest --format  "
            "sdk(" + ", ".join(SDK_TYPES.keys()) +
            ") | protos(" + ", ".join(PROTOS_TYPES.keys()) + ")" +
            ") | snapend-manifest(" +
            ", ".join(SNAPEND_MANIFEST_TYPES.keys()) + ")"
        )
    ),
    category_type: str = typer.Option(
        None, "--type",
        help=(
            "(optional: download) Only applicable for --category sdk|protos --type "
            "sdk(" + ", ".join(Snapend.CATEGORY_TYPE_SDK) + ")"
            " | protos(" + ", ".join(Snapend.CATEGORY_TYPE_PROTOS) + ")"
        )
    ),
    category_http_lib: str = typer.Option(
        None, "--http-lib",
        help=(
            "(optional: download) Only applicable for --category sdk "
            "--format " + '|'.join(Snapend.get_formats_supporting_http_lib()) + ' ' +
            "--type user|server|internal|app "
            "--http-lib " + Snapend.get_http_formats_str()
        )
    ),
    snaps: Union[str, None] = typer.Option(
        None, "--snaps",
        help=(
            "(optional: download) Comma separated list of snap ids to customize the "
              "SDKs, protos or admin settings. "
              "snaps(" + ", ".join(SERVICE_IDS)
        )
    ),
    # Clone
    name: Union[str, None] = typer.Option(
        None, "--name", help="(req: clone) Snapend name"),
    env: Union[str, None] = typer.Option(
        None, "--env", help=(
            "(req: clone) Snapend environment"
            "Environments: (" + ", ".join(Snapend.ENV_TYPES) + ")"
        )),
    # Download, Apply, Clone
    out_path: Union[str, None] = typer.Option(
        None, "--out-path", help="(optional: download|apply|clone) Path to save the output file"),
    # update
    byosnaps_list: str = typer.Option(
        None, "--byosnaps",
        help=(
            "(optional: update) Comma separated list of BYOSnap ids and versions. "
            "Eg: service-1:v1.0.0,service-2:v1.0.0"
        )
    ),
    byogs_list: str = typer.Option(
        None, "--byogs",
        help=(
            "(optional: update) Comma separated list of BYOGs fleet_name:tag. "
            "Eg: fleet-1:v1.0.0,fleet-2:v1.0.0"
        )
    ),
    # create, update, promote, apply, clone
    blocking: bool = typer.Option(
        False, "--blocking",
        help=(
            "(optional: update) Set to true if you want to wait for the update to complete "
            "before returning."
        )
    ),
    # overrides
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
      Snapend commands
    """
    validate_command_context(ctx)
    snapend_obj: Snapend = Snapend(
        subcommand=subcommand,
        base_url=ctx.obj['base_url'],
        api_key=ctx.obj['api_key'],
        snapend_id=snapend_id,
        # Enumerate, Clone
        game_id=game_id,
        # Clone
        name=name, env=env,
        # Apply, Clone
        manifest_path_filename=manifest_path_filename,
        force=force,
        # Download
        category=category,
        category_format=category_format,
        category_type=category_type,
        category_http_lib=category_http_lib,
        snaps=snaps,
        # Download, Apply and Clone
        out_path=out_path,
        # Update
        byosnaps=byosnaps_list, byogs=byogs_list, blocking=blocking
    )
    getattr(snapend_obj, subcommand.replace('-', '_'))()
    success(f"Snapend {subcommand} complete")
    raise typer.Exit(code=SNAPCTL_SUCCESS)


@app.command()
@telemetry("byows", subcommand_arg="subcommand")
def byows(
    ctx: typer.Context,
    # Required fields
    subcommand: str = typer.Argument(
        ..., help="Byows Subcommands: " + ", ".join(Byows.SUBCOMMANDS) + "."
    ),
    # attach
    snapend_id: str = typer.Option(
        None, "--snapend-id",
        help=("(req: attach, reset) Your Snapend Id")
    ),
    byosnap_id: str = typer.Option(
        None, "--byosnap-id",
        help=("(req: attach) Your BYOSnap Id")
    ),
    http_port: str = typer.Option(
        None, "--http-port",
        help=("(oneof: attach) HTTP port of your local server. One of --http-port or --grpc-port is required.")
    ),
    grpc_port: str = typer.Option(
        None, "--grpc-port",
        help=("(oneof: attach) gRPC port of your local server. One of --http-port or --grpc-port is required.")
    ),
    # overrides
    api_key: Union[str, None] = typer.Option(
        None, "--api-key", help="API Key override.", callback=api_key_context_callback
    ),
    profile: Union[str, None] = typer.Option(
        None, "--profile", help="Profile from the Snapser config to use.", callback=profile_context_callback
    ),
) -> None:
    """
      Bring your own workstation commands
    """
    validate_command_context(ctx)
    byows_obj: Byows = Byows(
        subcommand=subcommand,
        base_url=ctx.obj['base_url'],
        base_snapend_url=ctx.obj['base_snapend_url'],
        api_key=ctx.obj['api_key'],
        snapend_id=snapend_id,
        byosnap_id=byosnap_id,
        http_port=http_port,
        grpc_port=grpc_port,
    )
    getattr(byows_obj, subcommand.replace('-', '_'))()
    success(f"BYOWs {subcommand} complete")
    raise typer.Exit(code=SNAPCTL_SUCCESS)

'''
Telemetry utilities for snapctl
'''
from __future__ import annotations
from typing import Any, Dict, Optional
import functools
import platform
import uuid
import hashlib
import requests
import typer
from snapctl.config.constants import AMPLITUDE_HTTP_US, AMPLITUDE_HTTP_EU
from snapctl.utils.helper import get_config_value
from snapctl.utils.echo import info


def _ctx(ctx: Optional[typer.Context]) -> dict:
    try:
        return ctx.obj or {}
    except Exception:
        return {}


def _base_props(ctx: Optional[typer.Context]) -> Dict[str, Any]:
    c = _ctx(ctx)
    return {
        "source": "snapctl",
        "cli_version": c.get("version"),
        "os": platform.system(),
    }


def _device_id_from_ctx(ctx: Optional[typer.Context]) -> str:
    """
    Amplitude requires either user_id or device_id.
    We derive a non-reversible device_id from the API key (if present).
    """
    c = _ctx(ctx)
    api_key = c.get("api_key") or ""
    if api_key:
        # hash + truncate to keep it compact but stable
        h = hashlib.sha256(f"snapctl|{api_key}".encode("utf-8")).hexdigest()
        return f"dev-{h[:32]}"
    # fallback: hostname or a random-ish node id
    return f"host-{platform.node() or uuid.getnode()}"


def _endpoint_from_env(ctx: Optional[typer.Context]) -> str:
    """
    Returns the Amplitude endpoint based on environment config.
    """
    c = _ctx(ctx)
    env = c.get("environment")
    region = (get_config_value(env, "AMPLITUDE_REGION") or "US").upper()
    return AMPLITUDE_HTTP_EU if region == "EU" else AMPLITUDE_HTTP_US


def _is_active(ctx: Optional[typer.Context]) -> tuple[bool, bool, Optional[str]]:
    """
    Returns (telemetry_active, dry_run, api_key)
    """
    c = _ctx(ctx)
    env = c.get("environment")
    api_key = get_config_value(env, "AMPLITUDE_API_KEY")
    if not api_key or api_key == '':
        return (False, False, None)
    telemetry_active = get_config_value(env, "TELEMETRY_ACTIVE") == "true"
    dry_run = get_config_value(env, "TELEMETRY_DRY_RUN") == "true"
    return (telemetry_active, dry_run, api_key)


def _post_event(payload: dict, endpoint: str, timeout_s: float) -> None:
    """
    Post the event to Amplitude.
    """
    try:
        requests.post(endpoint, json=payload, timeout=timeout_s)
    except Exception:
        # Never break the CLI
        pass


def track_simple(
    ctx: Optional[typer.Context],
    *,
    command: str,
    sub: str,
    result: str,
    count: int = 1,
    timeout_s: float = 2.0,
) -> None:
    """
    Minimal Amplitude event:
      event_type = action
      event_properties = { category, label, count, ...tiny base props }
    """
    category = 'cli'
    active, dry_run, api_key = _is_active(ctx)
    if not active or not api_key:
        return

    action = f"{command}_{sub}" if sub else command
    props = {**_base_props(ctx)}
    if dry_run:
        info(
            f"[telemetry:DRY-RUN] category={category} action={action} label={result} "
            f"count={count} props={props}")
        return

    payload = {
        "api_key": api_key,
        "events": [{
            "event_type": action,
            "device_id": _device_id_from_ctx(ctx),
            "event_properties": props,
        }]
    }
    _post_event(payload, _endpoint_from_env(ctx), timeout_s)

# -------- Decorator to auto-track per-command result --------


def telemetry(command_name: str, subcommand_arg: Optional[str] = None):
    """
    Decorator to track telemetry for a command function.
    """
    def deco(fn):
        @functools.wraps(fn)
        def wrapper(*args, **kwargs):
            ctx: Optional[typer.Context] = kwargs.get("ctx")
            sub = (kwargs.get(subcommand_arg) if subcommand_arg else None)
            label = "success"  # default unless we see a failure
            should_track_run = True
            try:
                result = fn(*args, **kwargs)
                return result
            except typer.Exit as e:
                code = getattr(e, "exit_code", None)
                # treat Exit(0/None) as success, anything else as failure
                label = "success" if (code == 0 or code is None) else "failure"
                # Now we only want to track if it was a success
                #   typer.Exit is called by us on user failure.
                #   If we start tracking this, bad actors can spam our telemetry.
                should_track_run = not label == 'failure'
                raise
            except SystemExit as e:
                # print('#1')
                code = getattr(e, "code", None)
                label = "success" if (code == 0 or code is None) else "failure"
                raise
            except Exception:
                # print('#2')
                label = "failure"
                raise
            finally:
                if should_track_run:
                    track_simple(ctx, command=command_name,
                                 sub=sub, result=label, count=1)
        return wrapper
    return deco

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable

import importlib_metadata as md

if TYPE_CHECKING:
    from ..api import Env


def oenv2config_compatibility(curr_env: Env) -> Env:
    """ """
    return curr_env + {
        "PROXY_MODE": curr_env.gets("PROXY_MODE", "PROXY_ENABLE"),
        "ADMIN_PASSWORD": curr_env.gets("ADMIN_PASSWORD", "ADMIN_PASSWD"),
        "WORKER_HTTP": curr_env.gets("WORKER_HTTP", "WORKERS"),
        "WORKER_CRON": curr_env.gets("WORKER_CRON", "CRON_THREAD", "MAX_CRON_THREADS"),
        "HTTP_INTERFACE": curr_env.gets("HTTP_INTERFACE", "XMLRPC_INTERFACE"),
        "HTTP_PORT": curr_env.gets("HTTP_PORT", "XMLRPC_PORT"),
        "HTTP_ENABLE": curr_env.gets("HTTP_ENABLE", "XMLRPC_ENABLE"),
        "GEVENT_PORT": curr_env.gets("GEVENT_PORT", "LONGPOLLING_PORT"),
        "SERVER_WIDE_MODULES": curr_env.gets("SERVER_WIDE_MODULES", "LOAD"),
        "GEOIP_CITY_DB": curr_env.gets("GEOIP_CITY_DB", "GEOIP_DB"),
        "TRANSIENT_AGE_LIMIT": curr_env.gets("TRANSIENT_AGE_LIMIT", "OSV_MEMORY_AGE_LIMIT"),
        "TRANSIENT_COUNT_LIMIT": curr_env.gets("TRANSIENT_COUNT_LIMIT", "OSV_MEMORY_COUNT_LIMIT"),
    }


def apply_mapper(env: Env) -> Env:
    """
    Apply the MAPPER on `env` and return a new `api.Env` without mutate `env`
    Args:
        env: The env to map

    Returns:
        A new `api.Env` with all MAPPER applied on.
    """
    curr_env = oenv2config_compatibility(env.copy())
    for mapper in load_mappers():
        curr_env = mapper(curr_env.copy())
    for mapper in load_post_mappers():
        curr_env = mapper(curr_env.copy())
    return curr_env


def load_mappers() -> list[Callable[[Env], Env]]:
    exclude_mappers = set(k.strip() for k in os.getenv("ODOO_ENV2CONFIG_EXCLUDE_MAPPERS", "").split(",") if k)
    mappers: list[Callable[[Env], Env]] = []
    eps = md.entry_points()
    for entry_point in eps.select(group="environ_odoo_config.mapper"):
        # If no distro is specified, use first to come up.
        if entry_point.name in exclude_mappers:
            continue
        mappers.append(entry_point.load())
    return mappers


def load_post_mappers() -> list[Callable[[Env], Env]]:
    exclude_mappers = set(k.strip() for k in os.getenv("ODOO_ENV2CONFIG_EXCLUDE_MAPPERS", "").split(",") if k)
    mappers: list[Callable[[Env], Env]] = []
    eps = md.entry_points()
    for entry_point in eps.select(group="environ_odoo_config.post_mapper"):
        # If no distro is specified, use first to come up.
        if entry_point.name in exclude_mappers:
            continue
        mappers.append(entry_point.load())
    return mappers

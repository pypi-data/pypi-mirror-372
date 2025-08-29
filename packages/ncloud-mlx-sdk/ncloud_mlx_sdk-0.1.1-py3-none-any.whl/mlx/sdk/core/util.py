#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import os
from urllib.request import getproxies

PROJECT_NAMESPACE_PREFIX = "p-"
MLX_APPNAME = "mlxp"


def project_name_to_namespace(project_name: str) -> str:
    return f"{PROJECT_NAMESPACE_PREFIX}{project_name}" if project_name else "default"


def namespace_to_project_name(namespace: str) -> str:
    if not namespace.startswith(PROJECT_NAMESPACE_PREFIX):
        return ""
    return namespace.removeprefix(PROJECT_NAMESPACE_PREFIX)


def config_dir(app_name: str = MLX_APPNAME) -> str:
    if not app_name:
        raise RuntimeError("app_name required")

    path = f"~/.config/{app_name}"
    path = os.path.abspath(os.path.expanduser(path))
    if not os.path.isdir(path):
        os.makedirs(path)
    return path


def config_path(app_name: str = MLX_APPNAME, file_name: str = "conf.yaml") -> str:
    return os.path.join(config_dir(app_name), file_name)


def proxy_url(debug=False):
    proxies = getproxies()
    try:
        url = proxies["https"]
        if debug:
            print(f"Uses proxy env variable https_proxy == '{url}'")
        return url
    except KeyError:
        pass

    return None


def redact(s: str, no_redact: bool) -> str:
    if no_redact:
        return s
    return "*" * 32

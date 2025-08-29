#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

import os
import os.path
import sys
from collections import OrderedDict
from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Optional
from typing import OrderedDict as OrderedDictType

import yaml

# cluster 관련 import 제거됨
from mlx.sdk.core.errors import (
    ContextAlreadyExistError,
    EmptyCurrentContextError,
    EmptyCurrentProjectError,
    EmptyCurrentWorkspaceError,
    InvalidContextNameError,
)
from mlx.sdk.core.util import project_name_to_namespace

from .util import config_path


class TokenType(Enum):
    MLX_API_KEY = "MLX_API_KEY"
    KEYCLOAK = "KEYCLOAK"
    K8S_SA = "K8S_SA"


DEFAULT_CONTEXT_NAME = "default"


@dataclass
class ConfigContext:
    name: str = None
    endpoint_url: Optional[str] = None
    workspace: Optional[str] = None
    project: Optional[str] = None
    apikey: Optional[str] = None

    def __post_init__(self):
        if self.name is None:
            self.name = self.default_name

    @property
    def default_name(self):
        return "default"


@dataclass
class Config:
    current_context: Optional[str] = f"{DEFAULT_CONTEXT_NAME}"
    contexts: OrderedDictType[str, ConfigContext] = field(
        default_factory=lambda: OrderedDict({DEFAULT_CONTEXT_NAME: ConfigContext()})
    )

    def __post_init__(self):
        contexts_map = OrderedDict()
        contexts = (
            self.contexts.values()
            if isinstance(self.contexts, OrderedDict)
            else self.contexts
        )
        for c in contexts:
            if isinstance(c, dict):
                c.pop("user", None)

            context = ConfigContext(**c) if isinstance(c, dict) else c
            contexts_map[context.name] = context
        self.contexts = contexts_map

    def get_context(self, name: str) -> ConfigContext:
        return self.contexts.get(name)

    def set_current_context(self, name: str):
        if name == "":
            self.current_context = name
            return

        _ = self.get_context(name)
        self.current_context = name

    def add_context(self, context: ConfigContext):
        if context.name in self.contexts:
            raise ContextAlreadyExistError(f"{context.name} context already exists")
        self.contexts[context.name] = context

    def delete_context(self, name: str):
        if self.current_context == name:
            self.current_context = ""

        self.contexts.pop(name)


class ConfigFile:
    def __init__(self, config: Optional[Config] = None):
        if config:
            self._config = config
            return

        self._config_path = self.config_file_path()

        data = None
        if os.path.isfile(self._config_path):
            with open(self._config_path) as f:
                data = yaml.safe_load(f)

        if data:
            self._config = Config(**data)
        else:
            self._config = Config()

    @staticmethod
    def config_file_path() -> str:
        return config_path()

    def dump(self, stream=sys.stdout):
        config_dict = asdict(self._config)
        # convert contexts OrderedDict -> list
        config_dict["contexts"] = [ctx for ctx in config_dict["contexts"].values()]
        # NOTE: behavior default dumper was wierd. result output adds extra space to each key.
        # change Dumper as yaml.CDumper fixed the issue.
        yaml.dump(config_dict, stream, default_flow_style=False, Dumper=yaml.CDumper)

    def save(self):
        with open(self._config_path, "w+") as f:
            self.dump(f)

    @property
    def current_context(self) -> Optional[str]:
        return os.environ.get("MLX_CONTEXT", self._config.current_context)

    @property
    def current_context_object(self) -> ConfigContext:
        if not self.current_context:
            raise EmptyCurrentContextError("current context is empty")
        return self.context_object_by_name(self.current_context)

    def context_object_by_name(self, name: str) -> ConfigContext:
        try:
            return self._config.contexts[name]
        except KeyError:
            raise InvalidContextNameError(f"Not found context for name {name}")

    @current_context.setter
    def current_context(self, name: str):
        self._config.set_current_context(name)
        self.save()

    @property
    def endpoint_url(self) -> Optional[str]:
        """
        Get endpoint URL from environment or config file.

        Priority order:
        1. Environment variable: MLX_ENDPOINT_URL
        2. Config file setting

        To set endpoint URL:
        - Environment: export MLX_ENDPOINT_URL='https://your-api-server.com'
        - CLI command: mlx configure
        - Programmatically: config.endpoint_url = 'https://your-api-server.com'

        :return: Endpoint URL string or None if not found.
        """
        return os.environ.get(
            "MLX_ENDPOINT_URL",
            self.current_context_object.endpoint_url,
        )

    @endpoint_url.setter
    def endpoint_url(self, url: str):
        """Set endpoint URL."""
        self.current_context_object.endpoint_url = url
        self.save()

    @property
    def workspace(self) -> Optional[str]:
        return os.environ.get(
            "MLX_WORKSPACE",
            self.current_context_object.workspace,
        )

    @workspace.setter
    def workspace(self, name: str):
        self.current_context_object.workspace = name
        self.save()

    @property
    def project(self) -> Optional[str]:
        return os.environ.get(
            "MLX_PROJECT",
            self.current_context_object.project,
        )

    @project.setter
    def project(self, name: str):
        self.current_context_object.project = name
        self.save()

    @property
    def apikey(self) -> Optional[str]:
        return os.environ.get(
            "MLX_APIKEY",
            self.current_context_object.apikey,
        )

    @apikey.setter
    def apikey(self, key: str):
        """Set apikey for internal use."""
        self.current_context_object.apikey = key
        self.save()

    def add_context(self, context: ConfigContext):
        self._config.add_context(context)
        self.save()

    def delete_context(self, name: str):
        if self.current_context == name:
            self.current_context = ""

        for c in self._config.contexts.values():
            if c.name == name:
                self._config.contexts.pop(name)
                self.save()
                return

        raise InvalidContextNameError(f"{name} context not found")

    def clear(self, auth_only: bool = True):
        self.apikey = None

        if not auth_only:
            self.project = None
            self.workspace = None

    def clear_global_attrs(self, attr_name: str, attr_value: str):
        for ctx in self._config.contexts.values():
            if getattr(ctx, attr_name, None) == attr_value:
                setattr(ctx, attr_name, None)

                # clear project from context also if workspace cleared
                if attr_name == "workspace":
                    setattr(ctx, "project", None)

        self.save()


class GlobalContext:
    """Global context to be shared to cli, extensions based on ConfigFile."""

    def __init__(self, verbose=False, debug=False):
        self._config_file = ConfigFile()
        self.verbose = verbose
        self.debug = debug

    @property
    def current_context(self) -> Optional[str]:
        return self._config_file.current_context

    @property
    def endpoint_url(self) -> Optional[str]:
        """
        Get endpoint URL from global context.

        :return: Endpoint URL string or None if not found.
        """
        return self._config_file.endpoint_url

    @property
    def current_workspace(self) -> str:
        workspace = self._config_file.workspace
        if not workspace:
            raise EmptyCurrentWorkspaceError
        return workspace

    @property
    def safe_current_workspace(self) -> Optional[str]:
        try:
            return self.current_workspace
        except Exception:
            return None

    @property
    def current_project(self) -> str:
        project_name = self._config_file.project
        if not project_name:
            raise EmptyCurrentProjectError
        return project_name

    @property
    def safe_current_project(self) -> Optional[str]:
        try:
            return self.current_project
        except Exception:
            return None

    @property
    def namespace(self) -> str:
        return project_name_to_namespace(self.current_project)

    @property
    def apikey(self) -> Optional[str]:
        return self._config_file.apikey

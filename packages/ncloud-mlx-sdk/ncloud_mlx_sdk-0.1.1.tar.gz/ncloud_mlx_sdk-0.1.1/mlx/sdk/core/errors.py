#
# ML expert Platform
# Copyright (c) 2025-present NAVER Cloud Corp.
# Apache-2.0
#

class Error(Exception):
    """Base Error of mlx"""

    pass


empty_error_msg_template = (
    "{0} is not set. Please run the '{1}' command to set your {0}."
)


class InvalidTokenError(Error):
    """Raised when token string is invalid"""

    def __init__(
        self,
        message="Invalid token. Try to login again.",
    ):
        self.message = message
        super().__init__(self.message)


class NotImplementedFeatureError(Error):
    """Raised when the feature is not implemented"""

    def __init__(self, message="This feature is not implemented yet. "):
        self.message = message
        super().__init__(self.message)


class TokenRefreshError(Error):
    """Raised when token refresh is failed"""

    def __init__(self, message="Token refresh failed. Try to login again."):
        self.message = message
        super().__init__(self.message)


class WorkspaceNotFoundError(Error):
    """Raised when there is no workspace available"""

    def __init__(
        self,
        message="You have no workspace. "
        "Try to create one with : 'mlx workspace create <WorkspaceName>'",
    ):
        self.message = message
        super().__init__(self.message)


class ProjectNotFoundError(Error):
    """Raised when there is no project available"""

    def __init__(
        self,
        message="You have no project. "
        "Try to create one with : 'mlx project create <ProjectName>'",
    ):
        self.message = message
        super().__init__(self.message)


class EmptyCurrentWorkspaceError(Error):
    """Raised when current workspace context is empty"""

    def __init__(
        self,
        message=empty_error_msg_template.format("Workspace", "mlx workspace set"),
    ):
        self.message = message
        super().__init__(self.message)


class EmptyCurrentProjectError(Error):
    """Raised when current project context is empty"""

    def __init__(
        self, message=empty_error_msg_template.format("Project", "mlx project set")
    ):
        self.message = message
        super().__init__(self.message)


class EmptyCurrentRegionError(Error):
    """Raised when current region context is empty"""

    def __init__(
        self,
        message=empty_error_msg_template.format("Region", "mlx context region set"),
    ):
        self.message = message
        super().__init__(self.message)


class EmptyAccessTokenError(Error):
    """Raised when access token is empty"""

    def __init__(
        self,
        message="You have no authentication available. "
        "Please run the 'mlx auth login' command to initialize authentication.",
    ):
        self.message = message
        super().__init__(self.message)


class EmptyApiKeyError(Error):
    """Raised when access token is empty"""

    def __init__(
        self,
        message="ApiKey is not set in current context. "
        "Please run the 'mlx apikey set' command to set ApiKey.",
    ):
        self.message = message
        super().__init__(self.message)


class EmptyResourceNameError(Error):
    """Raised when required resource name is empty"""

    pass


class InvalidCredentialNameError(Error):
    pass


class EmptyCurrentContextError(Error):
    """Raised when current context is empty"""

    pass


class InvalidContextNameError(Error):
    """Raised when not found context information by name"""

    pass


class InvalidWorkspaceNameError(Error):
    """Raised when workspace name is invalid"""

    def __init__(
        self,
        workspace_name=None,
        message="Invalid workspace name. Please run 'mlx workspace "
        "list' to get valid workspace names.",
    ):
        if workspace_name:
            message = (
                f"`{workspace_name} is not exist in available workspaces`. "
                f"try - `mlx workspace list`"
            )

        self.message = message
        super().__init__(self.message)


class InvalidProjectNameError(Error):
    """Raised when project name is invalid"""

    def __init__(
        self,
        project_name=None,
        message="Invalid project name. Please run 'mlx project list' to get valid "
        "project names.",
    ):
        if project_name:
            message = (
                f"`{project_name} is not exist in available projects`. "
                f"try - 'mlx project list'."
            )

        self.message = message
        super().__init__(self.message)


class ContextAlreadyExistError(Error):
    """Raised when the context name to add already exists"""

    pass


class MetricNotFoundError(Error):
    """Raised when givin metric type is not available."""

    def __init__(self, metric_type, project_name, message="Metric not found."):
        self.message = f"Metric {metric_type} for project {project_name} is not available. {message}"
        super().__init__(self.message)


class MetricOpenFailureError(Error):
    """Raised when port forwarding is failed."""

    pass

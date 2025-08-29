from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkspaceSettings(BaseSettings):

    model_config = SettingsConfigDict(
        case_sensitive=False,
        extra="allow",
    )

    data_root: Path = Field(
        default=Path("/mnt/ssd1/repos/docparser_trainer/data")
    )  # DATA_ROOT 环境变量

    @property
    def batch_root(self) -> Path:
        return self.data_root.joinpath("batches")

    @property
    def task_root(self) -> Path:
        return self.data_root.joinpath("tasks")

    @property
    def workspace_root(self) -> Path:
        return self.data_root.joinpath("workspaces")


workspace_settings = WorkspaceSettings()

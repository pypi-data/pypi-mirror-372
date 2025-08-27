from typing import Optional, List, Dict, Any
from sqlmodel import SQLModel, Field
from datetime import datetime
from enum import Enum
from sqlalchemy import Column
from sqlalchemy import JSON as SA_JSON
from sqlalchemy.dialects.postgresql import JSONB
from pydantic import BaseModel
from pydantic import field_validator

from .enums import TaskStatusEnum, ProjectStatusEnum, ProjectDataSourceType
from .minio import MinioClientConfig

JSON_PORTABLE = SA_JSON().with_variant(JSONB, "postgresql")


class Project(SQLModel, table=True):
    """
    标注项目（场景）表：一个项目对应一个完整的多帧数据序列
    """

    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True, unique=True)  # 项目名称，唯一
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # 项目标注状态
    status: ProjectStatusEnum = Field(default=ProjectStatusEnum.unstarted)

    # minio client config
    # 入库为 JSON（dict），ORM 能识别
    minio_client_config: Optional[Dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON_PORTABLE, nullable=True),
        description="MinIO 客户端配置,JSON 形式存储",
    )

    # --- 输入端兼容：允许直接传 MinioClientConfig 或 dict ---
    @field_validator("minio_client_config", mode="before")
    @classmethod
    def _coerce_minio_config(cls, v):
        if v is None:
            return None
        if isinstance(v, MinioClientConfig):
            # 通过你在 MinioClientConfig 里定义的 after-validator 做规范化
            return v.model_dump()
        if isinstance(v, dict):
            # 也走一次 Pydantic 校验 + 规范化再转回 dict，确保数据入库一致
            return MinioClientConfig.model_validate(v).model_dump()
        # 其他类型一律拒绝
        raise TypeError("minio_client_config must be MinioClientConfig or dict")

    # --- 便捷方法：读取时拿到 Pydantic 模型 ---
    def get_minio_client_config(self) -> Optional[MinioClientConfig]:
        if self.minio_client_config is None:
            return None
        return MinioClientConfig.model_validate(self.minio_client_config)


# Projects Model
class ProjectCreateRequest(BaseModel):
    """创建项目请求模型"""

    project_name: str
    data_source_type: ProjectDataSourceType = ProjectDataSourceType.NEXTPOINTS
    description: Optional[str] = None

    # minio client config
    minio_client_config: MinioClientConfig

    main_channel: str = "lidar-fusion"
    time_interval: float = 0.5  # 时间间隔，单位为秒


class ProjectCreateResponse(BaseModel):
    """项目响应模型"""

    project_name: str
    status: TaskStatusEnum
    message: Optional[str]


class ProjectResponse(BaseModel):
    """项目响应模型"""

    id: Optional[int]
    name: str
    description: Optional[str]
    status: ProjectStatusEnum
    created_at: str


class ProjectStatusUpdateRequest(BaseModel):
    """项目状态更新请求模型"""

    project_name: str
    status: ProjectStatusEnum

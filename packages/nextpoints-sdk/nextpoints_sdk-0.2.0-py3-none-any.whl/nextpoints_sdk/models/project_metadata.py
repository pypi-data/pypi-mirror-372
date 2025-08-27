from typing import Optional, List, Dict, Set
from pydantic import BaseModel, model_validator


from .annotation import AnnotationItem
from .pose import Pose
from .calibration import CalibrationMetadata, SensorType
from .project import ProjectResponse

import json
import math
from decimal import Decimal, ROUND_HALF_UP, InvalidOperation
import hashlib


class FrameMetadata(BaseModel):
    """帧元数据响应模型"""

    id: int
    timestamp_ns: str
    prev_timestamp_ns: str
    next_timestamp_ns: str
    lidars: Dict[str, str]  # 必须有点云数据
    images: Optional[Dict[str, str]] = None
    pose: Optional[Pose] = None
    annotation: Optional[List[AnnotationItem]] = None


class ProjectMetadataResponse(BaseModel):
    """项目完整元数据响应模型"""

    project: ProjectResponse

    # 摘要信息
    frame_count: int
    start_timestamp_ns: str
    end_timestamp_ns: str
    duration_seconds: float
    main_channel: str

    # 标定信息（字典结构）
    calibration: Dict[str, CalibrationMetadata]

    # 帧列表（有序且包含上下文链接）
    frames: List[FrameMetadata]

    @model_validator(mode="after")
    def validate_frames_and_calibration(self):
        # —— 0) 基础校验：必须有帧
        if not self.frames:
            raise ValueError("frames 不能为空")

        # —— 1) 以第一帧作为基准，提取 lidars / images 的 key 模板
        first = self.frames[0]
        # lidars 必须非空
        if not first.lidars or len(first.lidars) == 0:
            raise ValueError(f"frame id={first.id} 的 lidars 不能为空")
        lidar_keys_ref: Set[str] = set(first.lidars.keys())

        # images 允许为空；若第一帧为 None，则参考集合为空集
        image_keys_ref: Set[str] = set(first.images.keys()) if first.images else set()

        # —— 2) 遍历所有帧，检查 key 集合一致性
        for idx, f in enumerate(self.frames):
            # 2.1 lidars 一致性（必有）
            if not f.lidars or len(f.lidars) == 0:
                raise ValueError(f"frame idx={idx}, id={f.id} 的 lidars 不能为空")
            lks = set(f.lidars.keys())
            if lks != lidar_keys_ref:
                missing = lidar_keys_ref - lks
                extra = lks - lidar_keys_ref
                raise ValueError(
                    f"lidars key 不一致 at frame idx={idx}, id={f.id}；"
                    f"缺失: {sorted(missing)}，多出: {sorted(extra)}；"
                    f"参考: {sorted(lidar_keys_ref)}"
                )

            # 2.2 images 一致性（允许整体都为空；但一旦有，则所有帧都必须有且 key 相同）
            iks = set(f.images.keys()) if f.images else set()
            if iks != image_keys_ref:
                # 若参考为空，但当前帧有 images，或参考非空但当前帧缺失/不同，均不允许
                missing = image_keys_ref - iks
                extra = iks - image_keys_ref
                raise ValueError(
                    f"images key 不一致 at frame idx={idx}, id={f.id}；"
                    f"缺失: {sorted(missing)}，多出: {sorted(extra)}；"
                    f"参考: {sorted(image_keys_ref)}"
                )

        # —— 3) 由帧统计得到的传感器 key 集合
        frames_lidar_keys = set(lidar_keys_ref)
        frames_camera_keys = set(image_keys_ref)

        # —— 4) 从 calibration 中按 sensor_type 分类统计
        calib_lidar_keys = {
            name
            for name, calib in self.calibration.items()
            if calib.sensor_type == SensorType.LIDAR
        }
        calib_camera_keys = {
            name
            for name, calib in self.calibration.items()
            if calib.sensor_type == SensorType.CAMERA
        }

        # —— 5) 一一对应关系检查（集合必须相等）
        if calib_lidar_keys != frames_lidar_keys:
            missing = frames_lidar_keys - calib_lidar_keys
            extra = calib_lidar_keys - frames_lidar_keys
            raise ValueError(
                "calibration(LIDAR) 与 frames 中的 lidar key 不一致；"
                f"calibration 缺失: {sorted(missing)}，calibration 多出: {sorted(extra)}；"
                f"frames.lidars: {sorted(frames_lidar_keys)}"
            )

        if calib_camera_keys != frames_camera_keys:
            missing = frames_camera_keys - calib_camera_keys
            extra = calib_camera_keys - frames_camera_keys
            raise ValueError(
                "calibration(CAMERA) 与 frames 中的 camera key 不一致；"
                f"calibration 缺失: {sorted(missing)}，calibration 多出: {sorted(extra)}；"
                f"frames.images: {sorted(frames_camera_keys)}"
            )

        # 通过校验
        return self

    # ------------------------------
    # 内容哈希（项目名 + calibration + 每帧 timestamp/pose/annotation）
    # ------------------------------
    def compute_content_hash(self) -> str:
        """计算项目元数据的内容哈希。

        参与字段：
        - project.name
        - calibration: 全部字段，按 key 排序
        - frames: 按 timestamp_ns 数值升序；每帧取 timestamp_ns, pose, annotation
          * pose: 保留 None；浮点量化 6 位
          * annotation: 保留 None vs [] 区分；按 obj_id 升序；全部字段；浮点量化 6 位
        排除：frame id / prev/next ts / lidars / images / 其他摘要统计
        """

        def to_decimal_str(val: float) -> str:
            # 使用 Decimal 精确量化到 6 位小数
            try:
                d = Decimal(str(val))
            except (InvalidOperation, ValueError):
                raise ValueError(f"无法转换为 Decimal: {val}")
            if d.is_nan() or d.is_infinite():
                raise ValueError(f"非法浮点值 (NaN/Inf): {val}")
            quantized = d.quantize(Decimal("0.000001"), rounding=ROUND_HALF_UP)
            # 固定显示 6 位小数
            return f"{quantized:.6f}"

        def normalize_scalar(x):
            if isinstance(x, float):
                return to_decimal_str(x)
            return x

        def normalize(obj):
            # 递归规范化：BaseModel -> dict；dict -> 排序；list -> 顺序保留；浮点 -> 量化
            if obj is None:
                return None
            if isinstance(obj, BaseModel):
                data = obj.model_dump(exclude_none=False)
                return normalize(data)
            if isinstance(obj, dict):
                norm_items = []
                for k in sorted(obj.keys()):
                    norm_items.append((k, normalize(obj[k])))
                return {k: v for k, v in norm_items}
            if isinstance(obj, (list, tuple)):
                return [normalize(v) for v in obj]
            if isinstance(obj, float):
                return to_decimal_str(obj)
            return obj

        # 1) calibration 规范化
        calib_norm = {}
        for key in sorted(self.calibration.keys()):
            calib_norm[key] = normalize(self.calibration[key])

        # 2) frames 规范化（按 timestamp_ns 数值排序）
        seen_ts = set()
        frames_sorted = sorted(self.frames, key=lambda f: int(f.timestamp_ns))
        frames_norm = []
        for f in frames_sorted:
            # timestamp 唯一性
            if f.timestamp_ns in seen_ts:
                raise ValueError(f"重复的 timestamp_ns: {f.timestamp_ns}")
            seen_ts.add(f.timestamp_ns)

            # pose
            pose_norm = normalize(f.pose) if f.pose is not None else None

            # annotation
            if f.annotation is None:
                ann_norm = None
            else:
                # 按 obj_id 排序
                try:
                    ann_sorted = sorted(f.annotation, key=lambda a: a.obj_id)
                except AttributeError:
                    raise ValueError("AnnotationItem 缺少 obj_id 字段")
                ann_norm = [normalize(a) for a in ann_sorted]

            frames_norm.append(
                {
                    "timestamp_ns": f.timestamp_ns,
                    "pose": pose_norm,
                    "annotation": ann_norm,
                }
            )

        canonical = {
            "project_name": self.project.name,
            "calibration": calib_norm,
            "frames": frames_norm,
        }

        raw = json.dumps(
            canonical, ensure_ascii=False, sort_keys=True, separators=(",", ":")
        )
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

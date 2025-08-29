"""
3D 几何相关工具
"""

from typing import NamedTuple
import numpy as np
from scipy.spatial.transform import Rotation as R


class SElement(NamedTuple):
    """3D元素
    包含平移和旋转

    Args:
        translation: 平移向量
        rotation: 旋转四元数
    """

    translation: np.ndarray
    rotation: np.ndarray


def init_element(translation: np.ndarray, rotation: np.ndarray) -> SElement:
    """初始化3D元素

    Args:
        translation: 平移向量
        rotation: 旋转四元数
    """
    return SElement(translation=translation, rotation=rotation)


def init_default_element() -> SElement:
    """初始化默认3D元素"""
    return init_element(
        translation=np.array([0.0, 0.0, 0.0]), rotation=np.array([0.0, 0.0, 0.0, 1.0])
    )


def extract_rotation_matrix(element: SElement) -> np.ndarray:
    """提取旋转矩阵"""
    return R.from_quat(element.rotation).as_matrix()


def to_homogeneous_matrix(element: SElement) -> np.ndarray:
    """将3D元素转换为齐次矩阵"""
    matrix = np.eye(4)
    matrix[:3, :3] = R.from_quat(element.rotation).as_matrix()
    matrix[:3, 3] = element.translation
    return matrix

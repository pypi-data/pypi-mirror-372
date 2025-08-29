"""
点云相关工具
"""

from pathlib import Path
import re
from typing import NamedTuple
from returns.io import impure_safe
from returns.result import Result, Success, Failure
import numpy as np


class PcdHeaderMeta(NamedTuple):
    data_start: int
    header_bytes: bytes


@impure_safe
def read_head_bytes(file: Path, num_bytes: int) -> bytes:
    """读取文件前num_bytes字节"""
    with file.open("rb") as f:
        return f.read(num_bytes)


@impure_safe
def get_pcd_head_meta(file: Path, start_bytes) -> PcdHeaderMeta:
    """
    取 PCD 头元信息

    支持的 DATA 格式：
        DATA ascii
        DATA binary
        DATA binary_compressed

    Args:
        file: PCD 文件路径
        cat_bytes: 读取头部的最大字节数

    Returns:
        PcdHeaderMeta
    """
    # 读取头部字节（解包 Result -> bytes）
    origin_head_bytes = read_head_bytes(file, start_bytes).unwrap()

    # 正则匹配 DATA 行
    data_pattern = rb"DATA\s+(ascii|binary|binary_compressed)\s*\n"
    match = re.search(data_pattern, origin_head_bytes)
    if not match:
        raise ValueError("PCD ERROR: DATA line not found or invalid format")

    # 数据起始位置（换行后一个字节）
    data_start = match.end()

    return PcdHeaderMeta(
        data_start=data_start, header_bytes=origin_head_bytes[:data_start]
    )


class PcdHeader(NamedTuple):
    """PCD 头结构"""

    VERSION: str
    FIELDS: list[str]
    SIZE: list[int]
    TYPE: list[str]
    COUNT: list[int]
    WIDTH: int
    HEIGHT: int
    VIEWPOINT: list[int]
    POINTS: int
    DATA: str


def create_pcd_header(
    version: str,
    fields: list[str],
    size: list[int],
    type_: list[str],
    count: list[int],
    width: int,
    height: int,
    viewpoint: list[int],
    points: int,
    data: str,
) -> PcdHeader:
    """创建PCD头结构"""
    return PcdHeader(
        VERSION=version,
        FIELDS=fields,
        SIZE=size,
        TYPE=type_,
        COUNT=count,
        WIDTH=width,
        HEIGHT=height,
        VIEWPOINT=viewpoint,
        POINTS=points,
        DATA=data,
    )


def convert_pcd_header_to_str(pcd_header: PcdHeader) -> str:
    return (
        "# .PCD v0.7 - Point Cloud Data file format\n"
        f"VERSION {pcd_header.VERSION}\n"
        + f"FIELDS {' '.join(pcd_header.FIELDS)}\n"
        + f"SIZE {' '.join(map(str, pcd_header.SIZE))}\n"
        + f"TYPE {' '.join(pcd_header.TYPE)}\n"
        + f"COUNT {' '.join(map(str, pcd_header.COUNT))}\n"
        + f"WIDTH {pcd_header.WIDTH}\n"
        + f"HEIGHT {pcd_header.HEIGHT}\n"
        + f"VIEWPOINT {' '.join(map(str, pcd_header.VIEWPOINT))}\n"
        + f"POINTS {pcd_header.POINTS}\n"
        + f"DATA {pcd_header.DATA}\n"
    )


def convert_str_to_pcd_header(header_str: str) -> Result[PcdHeader, ValueError]:
    HEADER_PATTERN = re.compile(
        r"^(VERSION|FIELDS|SIZE|TYPE|COUNT|WIDTH|HEIGHT|VIEWPOINT|POINTS|DATA)"
    )
    """将字符串转换为pcd头"""
    header_lines = header_str.split("\n")
    header = {}
    for line in header_lines[1:]:
        match = HEADER_PATTERN.match(line)
        if not match:
            return Failure(ValueError(f"Invalid header line: {line}"))
        parts = line.strip().split()
        key = match.group(0)
        header[key] = parts[1:] if len(parts) > 2 else parts[1]
    header["POINTS"] = int(header["POINTS"])
    header["WIDTH"] = int(header["WIDTH"])
    header["HEIGHT"] = int(header["HEIGHT"])
    return Success(create_pcd_header(**header))


def parse_pcd_header(meta: PcdHeaderMeta) -> Result[PcdHeader, ValueError]:
    """解析pcd头"""
    header_str = meta.header_bytes.decode(encoding="utf-8")
    return convert_str_to_pcd_header(header_str)


def build_dtype(
    fields: list, types: list, sizes: list, counts: list
) -> Result[np.dtype, ValueError]:
    """构建pcd numpy结构
    Args:
        fields (list): 字段名
        types (list): 类型
        sizes (list): 大小
        counts (list): 数量
    Raises:
        ValueError: 不支持的类型
    Returns:
        np.dtype: numpy结构
    """
    TYPE_MAP = {
        ("U", 1): np.uint8,
        ("U", 2): np.uint16,
        ("U", 4): np.uint32,
        ("U", 8): np.uint64,
        ("I", 1): np.int8,
        ("I", 2): np.int16,
        ("I", 4): np.int32,
        ("I", 8): np.int64,
        ("F", 4): np.float32,
        ("F", 8): np.float64,
    }
    dtype = []
    for field, type_char, size, count in zip(fields, types, sizes, counts):
        np_type = TYPE_MAP.get((type_char.upper(), int(size)), None)
        if np_type is None:
            return Failure(ValueError(f"Unsupported type: {type_char}{size}"))

        count = int(count)
        if count > 1:
            dtype.extend([(f"{field}_{i}", np_type) for i in range(count)])
        else:
            dtype.append((field, np_type))
    return Success(np.dtype(dtype))


@impure_safe
def read_pcd(
    pcd_file: Path, start_bytes: int = 1024
) -> Result[tuple[np.ndarray, PcdHeader], ValueError]:
    """读取pcd文件
    Args:
        pcd_file: pcd文件路径
        start_bytes: 读取头部的最大字节数
    Returns:
        tuple[np.ndarray, PcdHeader]
    """
    meta = get_pcd_head_meta(pcd_file, start_bytes).unwrap()
    header: Result[PcdHeader, ValueError] = parse_pcd_header(meta)
    dtype = build_dtype(header.FIELDS, header.TYPE, header.SIZE, header.COUNT)
    return Success(
        (_read_pcd_binary(pcd_file, dtype.unwrap(), meta.data_start), header)
    )


def _read_pcd_binary(file_path: Path, dtype: np.dtype, data_start: int) -> np.ndarray:
    return np.fromfile(file=file_path, dtype=dtype, offset=data_start)

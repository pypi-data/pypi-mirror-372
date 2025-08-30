"""
点云相关工具
"""

import re
from pathlib import Path
from typing import Generator, NamedTuple

import numpy as np
from returns.io import impure_safe
from returns.result import Failure, Result, Success, safe


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
    origin_head_bytes = read_head_bytes(file, start_bytes).unwrap()._inner_value

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


def __convert_str_to_pcd_header(header_str: str) -> PcdHeader:
    HEADER_PATTERN = re.compile(
        r"^(VERSION|FIELDS|SIZE|TYPE|COUNT|WIDTH|HEIGHT|VIEWPOINT|POINTS|DATA)"
    )
    """将字符串转换为pcd头"""
    header_lines = [line.strip() for line in header_str.split("\n") if line.strip()]
    header = {}
    for line in header_lines[1:]:
        match = HEADER_PATTERN.match(line)
        if not match:
            raise ValueError(f"Invalid header line: {line}")
        parts = line.split()
        key = match.group(0)
        header[key] = parts[1:] if len(parts) > 2 else parts[1]
    header["POINTS"] = int(header["POINTS"])
    header["WIDTH"] = int(header["WIDTH"])
    header["HEIGHT"] = int(header["HEIGHT"])
    return PcdHeader(**header)


@safe
def parse_pcd_header(meta: PcdHeaderMeta) -> PcdHeader:
    """解析pcd头"""
    header_str = meta.header_bytes.decode(encoding="utf-8")
    return __convert_str_to_pcd_header(header_str)


@safe
def build_dtype(
    fields: list[str], types: list[str], sizes: list[int], counts: list[int]
) -> np.dtype:
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
            raise ValueError(f"Unsupported type: {type_char}{size}")
        count = int(count)
        if count > 1:
            dtype.extend([(f"{field}_{i}", np_type) for i in range(count)])
        else:
            dtype.append((field, np_type))
    return np.dtype(dtype)


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
    meta = get_pcd_head_meta(pcd_file, start_bytes).unwrap()._inner_value
    header = parse_pcd_header(meta).unwrap()
    dtype = build_dtype(header.FIELDS, header.TYPE, header.SIZE, header.COUNT).unwrap()
    return __read_pcd_binary(pcd_file, dtype, meta.data_start), header


def __read_pcd_binary(file_path: Path, dtype: np.dtype, data_start: int) -> np.ndarray:
    return np.fromfile(file=file_path, dtype=dtype, offset=data_start)


def __write_pcd_binary(
    file: Path, header: PcdHeader
) -> Generator[None, np.ndarray, None]:
    """流式写入二进制PCD文件的生成器
    Args:
        file: PCD文件路径
        header: PCD头信息，包含字段定义

    Yields:
        None: 每次yield后等待接收点云数据
    """
    # 根据头部信息构建dtype
    dtype = build_dtype(header.FIELDS, header.TYPE, header.SIZE, header.COUNT).unwrap()

    with file.open("wb") as f:
        header_data = convert_pcd_header_to_str(header).encode("utf-8")
        f.write(header_data)

        while True:
            pc_data: np.ndarray = yield
            if pc_data is None:
                break

            if pc_data.dtype != dtype:
                pc_data = pc_data.astype(dtype)

            f.write(pc_data.tobytes())


def get_pcd_writer(file: Path, header: PcdHeader):
    """获取已初始化的PCD写入器

    Args:
        file: PCD文件路径
        header: PCD头信息

    Returns:
        已初始化的写入器生成器，可直接使用send()方法写入数据
    """
    data_type = header.DATA.lower()
    match data_type:
        case "binary":
            writer = __write_pcd_binary(file, header)
            next(writer)  # 初始化写入器，写入头部信息
            return writer
        case _:
            raise ValueError(f"Unsupported data type: {data_type}")

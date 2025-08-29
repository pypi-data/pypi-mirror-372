from typing import NamedTuple
from returns.maybe import Maybe

from fyuneru.geometry3d import SElement


class Item(NamedTuple):
    uid: str
    batch_uid: str
    labels: list
    frames: list


class Label(NamedTuple):
    uid: str
    id: int
    draw_type: str
    hash: str
    label: str
    frame_index: int
    lens_index: Maybe[int]
    points: Maybe[list]
    attributes: Maybe[dict]


class Frame(NamedTuple):
    idx: int
    url: str
    imgUrls: Maybe[list[str]]
    locations: Maybe[SElement]


def extract_frames(item: dict) -> list[Frame]:
    info = item["info"]["info"]
    image_urls = info.get("url") or info["imgUrls"]
    urls = info.get("pcdUrls") or info["urls"]
    # locations = info["locations"]
    locations = info.get("locations", [])
    if locations:
        ...
    elif urls:
        ...
    elif image_urls:
        ...
    return []


def extract_label(label: dict) -> Label: ...


def extract_labels(item: dict) -> list[Label]:
    return [extract_label(label=label) for label in item["labels"]]


def parse_task_config(task: dict) -> dict:
    return task


def parse_export_config(config: dict) -> dict:
    return config


def parse_item(item: dict) -> Item:
    uid = item["_id"]
    batch_uid = item["item"]["batchId"]
    labels = extract_labels(item)
    frames = extract_frames(item)

    return Item(uid=uid, batch_uid=batch_uid, labels=labels, frames=frames)


def parse_items(items: list[dict]) -> list[Item]:
    return [parse_item(item) for item in items]


class ExportTask(NamedTuple):
    task_config: dict
    export_config: dict
    items: list[Item]


def parse_origin(origin: dict) -> ExportTask:
    task = origin.get("task")
    config = origin.get("config")
    data = origin.get("data")

    export_config = parse_export_config(config)
    task_config = parse_task_config(task)
    items = parse_items(data)

    return ExportTask(task_config=task_config, export_config=export_config, items=items)

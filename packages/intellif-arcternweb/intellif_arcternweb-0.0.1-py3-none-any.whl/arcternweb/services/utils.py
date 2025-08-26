# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""通用模块

主要提供了一些通用函数接口

- **其它通用函数接口**
"""

import json
import os
from ..utils.http import http_download_file


class Utils:
    """通用类，用来封装一些跟arcternweb有关的函数"""

    def __init__(self):
        pass

    @staticmethod
    def download_file(s3_path: str, result_file: str) -> bool:
        """根据 s3 上的存储文件的 path 下载文件到本地磁盘指定路径下，如果 result_file 已经存在，将会被删除之后再下载

        Args:
            s3_path: s3 上的存储文件的的路径
            result_file: 本地磁盘文件路径
        Returns:
            bool: true 成功，false失败
        """
        if os.path.exists(result_file):
            os.remove(result_file)
        s3_path = "http://storage.ifai:5080/arcternweb/" + s3_path
        http_download_file(s3_path, result_file)
        return os.path.exists(result_file)

    @staticmethod
    def parse_images_from_result_file(result_file: str) -> dict | None:
        """
        ```
        从 arcternweb 上的推理任务结果文件中解析图片信息，包括图片，框，或其他

        Args:
            result_file: 推理任务的结果文件, 其内容为例:
                {
                    "Images": [
                        {
                            "MinioKey": "dataset/798/face-type_JPG/images/91483.jpg",
                            "Rect": [ 0, 0, 66, 66],
                            ...
                        },
                        {
                            "MinioKey": "dataset/798/face-type_JPG/images/294993.jpg",
                            "Rect": [ 56, 32, 120, 120],
                            ...
                        },
                        ...
                    ]
                }
        Returns:
            dict: 返回图片列表 和 框列表组成的 字典，例:
                {
                    "Images": ["dataset/798/face-type_JPG/images/91483.jpg", "dataset/798/face-type_JPG/images/294993.jpg", ...],
                    "Rects":  [[ 0, 0, 66, 66],       [ 56, 32, 120, 120],   ...],
                }
        ```
        """
        # 1. 读取 JSON 文件
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

        # 2. 获取 'Images' 数据
        items = data.get("Images")
        if not isinstance(items, list) or not items:
            return None

        # 3. 遍历提取 MinioKey 和 Rect
        images = []
        rects = []
        for item in items:
            if not isinstance(item, dict):
                return None
            minio_key = item.get("MinioKey")
            rect = item.get("Rect")

            if not isinstance(minio_key, str) or not isinstance(rect, list):
                return None

            images.append(minio_key)
            rects.append(rect)

        # 4. 返回结果
        return {"Images": images, "Rects": rects}

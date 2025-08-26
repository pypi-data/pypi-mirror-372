# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""分类器模块

主要提供了一些分类器通用函数接口

- **解析arcternweb上的推理任务的结果文件**
"""

import json
from typing import Union, List, Dict, Any
from pathlib import Path


class ClassifierUtils:
    """分类器通用类，用来封装一些跟分类有关的函数"""

    def __init__(self):
        pass

    @staticmethod
    def parse_labels_from_result_file(result_file: Union[str, bytes], label: list) -> list | None:
        """
        ```
        解析 推理任务结果文件中的 "Labels"，仅属性类模型可以调用

        Args:
            result_file: 推理任务结果文件, 其内容为例:

                {
                    "Images | Videos": [
                        {
                            ...
                            "Labels": [
                                {
                                    "color": "red"
                                },
                                {
                                    "shape": "circle"
                                }
                            ],
                            ...
                        },
                        {
                            ...
                            "Labels": [
                                {
                                    "color": "green"
                                },
                                {
                                    "shape": "circle"
                                }
                            ],
                            ...
                        },
                    ]
                }
            label: 推理结果中的下标索引所代表的具体属性, 例:
                [
                    {
                        "color": ["red", "green", "blue"]
                    },
                    {
                        "shape": ["rectangle", "triangle", "circle"]
                    },
                    ...
                ]
        Returns:
            list: 推理结果中的 "Lables" 中的属性的下标索引列表， 例:
            [
                [0, 1, ...], # 其中 0 代表 red, 1 代表 green, 2 代表 blue
                [2, 2, ...], # 其中 1 代表 rectangle, 1 代表 triangle, 2 代表 circle
                ...
            ]
        ```
        """

        # 1. 检查 label 格式
        if not isinstance(label, list) or not all(isinstance(d, dict) for d in label):
            raise TypeError("label 必须是 list[dict] 类型")

        # 2. 读取 JSON
        if isinstance(result_file, str):
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif isinstance(result_file, bytes):
            data = json.loads(result_file.decode("utf-8"))
        else:
            raise TypeError("result_file 必须是 str 或 bytes 类型")

        # 3. 获取 'Images | Videos' 数据
        items = data.get("Images", None)
        if not items:
            items = data.get("Videos", None)
        if not isinstance(items, list):
            raise TypeError("Images | Videos 必须是个 list")

        # 4. 初始化结果数组，每个属性一个空列表（按 label 顺序）
        results = [[] for _ in label]

        # 5. 遍历每个 item
        for item in items:
            labels = item.get("Labels", [])
            if not isinstance(labels, list):
                raise TypeError("必须包含 Labels 字段")

            # 按 label 定义的顺序依次找
            for idx, attr_dict in enumerate(label):
                # attr_dict 是 {属性名: 值列表}
                attr_name, attr_values = next(iter(attr_dict.items()))
                # 找到该 item 对应的属性值
                matched_value = None
                for ld in labels:
                    if isinstance(ld, dict) and attr_name in ld:
                        matched_value = ld[attr_name]
                        break
                if matched_value is None:
                    raise TypeError("找不到对应的属性{}".format(attr_name))

                # 映射到下标
                try:
                    value_index = attr_values.index(matched_value)
                except ValueError:
                    raise TypeError("找不到对应的下标值")
                results[idx].append(value_index)

        return results

    @staticmethod
    def parse_infers_from_result_file(result_file: Union[str, bytes]) -> list | None:
        """
        ```
        解析 推理任务结果文件中的 "Infers"，仅属性类模型可以调用

        Args:
            result_file: 推理任务结果文件, 其内容为例:
                {
                    "Images": [
                        {
                            ...
                            "Infers": [
                                {
                                    "Confidence": 0.998107,
                                    "Idx": 0
                                },
                                {
                                    "Confidence": 0.964285,
                                    "Idx": 2
                                }
                            ],
                            ...
                        },
                        {
                            ...
                            "Infers": [
                                {
                                    "Confidence": 0.891485,
                                    "Idx": 1
                                },
                                {
                                    "Confidence": 0.999154,
                                    "Idx": 2
                                }
                            ],
                            ...
                        },
                        ...
                    ]
                }
        Returns:
            list: 按照属性划分，输出 "Idx" 的列表， 例:
                [
                    [0, 1, ...],
                    [2, 2, ...],
                    ...
                ]
        ```
        """
        # 1. 读取 JSON
        if isinstance(result_file, str):
            with open(result_file, "r", encoding="utf-8") as f:
                data = json.load(f)
        elif isinstance(result_file, bytes):
            data = json.loads(result_file.decode("utf-8"))
        else:
            raise TypeError("result_file 必须是 str 或 bytes 类型")

        # 2. 获取 'Images' 数据
        items = data.get("Images", None)
        if not items:
            items = data.get("Videos", None)
        if not isinstance(items, list) or not items:
            return None

        # 3. 检查第一个样本的 Infers 数量，建立结果结构
        first_infers = items[0].get("Infers")
        if not isinstance(first_infers, list) or not first_infers:
            return None
        num_attrs = len(first_infers)
        results = [[] for _ in range(num_attrs)]

        # 4. 遍历每个样本
        for item in items:
            infers = item.get("Infers")
            if not isinstance(infers, list) or len(infers) != num_attrs:
                return None  # 数量不一致直接返回 None
            for idx, infer in enumerate(infers):
                if not isinstance(infer, dict) or "Idx" not in infer:
                    return None
                results[idx].append(infer["Idx"])

        return results

    @staticmethod
    def to_COCO(arcternweb_result_file: str, label: list, coco_dataset_file: str, coco_predict_file: str) -> bool:
        """
        ```
        把 arcternweb 上的结果转成 coco 格式的数据集 和 预测结果集

        Args:
            arcternweb_result_file: arcternweb 上的推理任务的结果文件 (/path/result.json)， 内容可能为:
                {
                    "Images": [
                        {
                            "MinioKey": "dataset/798/face-type_JPG/images/294993.jpg",
                            "ImageHeight": 145,
                            "ImageWidth": 256,
                            "Labels": [
                                {
                                    "color": "red"
                                },
                                {
                                    "shape": "circle"
                                }
                            ],
                            "Infers": [
                                {
                                    "Confidence": 0.998107,
                                    "Idx": 0
                                },
                                {
                                    "Confidence": 0.964285,
                                    "Idx": 1
                                }
                            ],
                            "Rect": [
                                30,
                                21,
                                101,
                                100
                            ]
                            ...
                        },
                        ...
                    ]
                }
            label: 推理结果中的下标索引所代表的具体属性列表, 例:
                [
                    {
                        "color": ["red", "green", "blue"]
                    },
                    {
                        "shape": ["rectangle", "triangle", "circle"]
                    },
                    ...
                ]
            coco_dataset_file: coco 数据集的保存文件（/path/coco_gt.json）, 对应 arcternweb_result_file 中的 "Labels" 字段, 内容可能为:
                {
                    "images":[
                        {
                            "id": 1,
                            "file_name": "dataset/798/face-type_JPG/images/294993.jpg",
                            "width": 256,
                            "height": 145
                        },
                        ...
                    ],
                    "annotations": [
                        {
                            "id": 1,
                            "image_id": 1,
                            "category_id": 1,
                            "bbox": [30, 21, 101, 100],
                            "area": 10100,
                            "iscrowd": 0,
                            "segmentation": [[30,21, 131,21, 131,121, 30,121]]
                        },
                        {
                            "id": 2,
                            "image_id": 1,
                            "category_id": 6,
                            "bbox": [30, 21, 101, 100],
                            "area": 10100,
                            "iscrowd": 0,
                            "segmentation": [[30,21, 131,21, 131,121, 30,121]]
                        },
                        ...
                    ],
                    "categories":[
                        {"id": 1, "name": "red", "supercategory": "color"},
                        {"id": 2, "name": "green", "supercategory": "color"},
                        {"id": 3, "name": "blue", "supercategory": "color"},
                        "
                        {"id": 4, "name": "rectangle", "supercategory": "shape"},
                        {"id": 5, "name": "triangle", "supercategory": "shape"},
                        {"id": 6, "name": "circle", "supercategory": "shape"},
                        ...
                    ]
                }
            coco_predict_file: 符合 coco 数据集格式的预测结果文件（/path/coco_dt.json), 对应 arcternweb_result_file 中的 "Infers" 字段，内容可能为:
                [
                    {
                        "image_id": 1,
                        "category_id": 1,
                        "bbox": [30, 21, 101, 100],
                        "score":  0.998107,
                    },
                    {
                        "image_id": 1,
                        "category_id": 5,
                        "bbox": [30, 21, 101, 100],
                        "score":  0.998107,
                    },
                    ...
                ]
        Returns:
            bool: true 成功，false失败
        ```
        """
        try:
            # 1. 读取输入文件
            with open(arcternweb_result_file, "r", encoding="utf-8") as f:
                result_data: Dict[str, Any] = json.load(f)

            # with open(label, "r", encoding="utf-8") as f:
            label_data: List[Dict[str, List[str]]] = label

            # 2. 构建 category_id 映射表
            supercats = []
            cats = []

            categories = []
            cat2id = {}
            cat_id = 1
            for group in label_data:
                for supercat, names in group.items():
                    supercats.append(supercat)
                    cats.append(names)
                    for name in names:
                        categories.append({"id": cat_id, "name": name, "supercategory": supercat})
                        cat2id[(supercat, name)] = cat_id
                        cat_id += 1

            # 3. 转换 images 和 annotations
            images = []
            annotations = []
            predictions = []
            ann_id = 1
            img_id = 1

            json_images = result_data.get("Images", None)
            if not json_images:
                json_images = result_data.get("Videos", None)
            for img in result_data.get("Images", []):
                images.append(
                    {
                        "id": img_id,
                        "file_name": img["MinioKey"],
                        "width": img["ImageWidth"],
                        "height": img["ImageHeight"],
                    }
                )

                x, y, w, h = img["Rect"]
                bbox = [x, y, w, h]
                area = w * h
                segmentation = [[x, y, x + w, y, x + w, y + h, x, y + h]]

                # Ground truth labels
                for lab in img.get("Labels", []):
                    for supercat, name in lab.items():
                        category_id = cat2id[(supercat, name)]
                        annotations.append(
                            {
                                "id": ann_id,
                                "image_id": img_id,
                                "category_id": category_id,
                                "bbox": bbox,
                                "area": area,
                                "iscrowd": 0,
                                "segmentation": segmentation,
                            }
                        )
                        ann_id += 1

                # Predictions
                for row_idx, infer in enumerate(img.get("Infers", [])):
                    idx = infer["Idx"]
                    score = infer["Confidence"]

                    if idx < len(cats[row_idx]) and row_idx < len(supercats):
                        supercat, name = supercats[row_idx], cats[row_idx][idx]
                        category_id = cat2id[(supercat, name)]
                        predictions.append(
                            {"image_id": img_id, "category_id": category_id, "bbox": bbox, "score": score}
                        )

                img_id += 1

            # 4. 写 COCO 数据集文件
            coco_dataset = {"info": {}, "images": images, "annotations": annotations, "categories": categories}
            Path(coco_dataset_file).write_text(json.dumps(coco_dataset, indent=2), encoding="utf-8")

            # 5. 写预测文件
            Path(coco_predict_file).write_text(json.dumps(predictions, indent=2), encoding="utf-8")

            return True
        except Exception as e:
            print(f"转换失败: {e}")
            return False

from __future__ import annotations

import os
import sys

import httpx
from loguru import logger

from .exceptions import APIError
from .services import utils
from .services.infer_task import InferTaskService
from .services.model_group import ModelGroupService
from .services.classifier import ClassifierUtils
from .services.utils import Utils


class Client:
    """ArcternWeb python SDK 客户端

    Attributes:
        infer_task_server (InferTaskService): 推理任务服务
        model_group_server (ModelGroupService): 模型组服务
        classifier_utils (ClassifierUtils): 通用分类器
        utils (Utils): 通用接口
    """

    infer_task_server: InferTaskService = None
    model_group_server: ModelGroupService = None
    classifier_utils: ClassifierUtils = None
    utils: Utils = None

    def __init__(
        self,
        *,
        base_url: str,
        token: str | None = None,
        timeout: float = 60.0,
        log_level: str = "INFO",
    ):
        """ArcternWeb python SDK 客户端

        Args:
            base_url (str): 服务地址
            token (str): 密钥，显式传入，或在环境变量 ARCTERNWEB_TOKEN 中设置

        Examples:
            >>> from arcternweb.client import Client
            >>> client = Client(base_url="xxx", token="xxxx")

        """
        logger.remove()
        logger.add(
            sys.stdout,
            colorize=True,
            format="<green>{time}</green> <level>{message}</level>",
            level=log_level,
        )
        logger.info(f"ArcternWeb Python SDK initialized with log level: {log_level}")

        if not base_url:
            raise ValueError("base_url必须填写")

        token = os.getenv("ARCTERNWEB_TOKEN") or token
        if not token:
            raise ValueError("缺少token：请显式传入，或在环境变量 ARCTERNWEB_TOKEN 中设置")

        self._http = httpx.Client(
            base_url=base_url.rstrip("/"),
            timeout=timeout,
            headers={"Authorization": f"Bearer {token}", "User-Agent": "arcternweb_sdk"},
            # event_hooks={"response": [self._raise_for_status]},
        )
        self.infer_task_server = InferTaskService(self._http)
        self.model_group_server = ModelGroupService(self._http)
        self.classifier_utils = ClassifierUtils()
        self.utils = Utils()

    @staticmethod
    def _raise_for_status(r: httpx.Response):
        try:
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            raise APIError(f"{e.response.status_code}: {e.response.text}") from e

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self._http.close()

# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""推理任务服务模块

主要提供了 推理任务 的相关接口

- **根据推理任务ID查询推理任务详情**
"""
import httpx
import json
import os
from ..exceptions import APIError
from ..models.common import APIWrapper
from ..models.infer_task import InferTask


_INFER_TASK_BASE = "/api/infertask/v5/normal-infer-tasks"


class InferTaskService:
    """推理任务"""

    def __init__(self, http: httpx.Client):
        self._http = http

    def get(self, infer_task_id: int) -> InferTask | None:
        """根据 arcternweb 上的推理任务 id 获取此次推理的详细信息

        Args:
            infer_task_id: 推理任务 id

        Returns:
            InferTask: 推理的详细信息
        """
        params = {"InferTaskID": infer_task_id}
        resp = self._http.get(f"{_INFER_TASK_BASE}/{infer_task_id}", params=params)
        wrapper = APIWrapper[InferTask].model_validate(resp.json())
        if wrapper.Code != 0:
            raise APIError(f"backend code {wrapper.Code}: {wrapper.Msg}")
        return wrapper.Data

# !/usr/bin/env python
# -*- coding:utf-8 -*-
"""模型组服务模块

主要提供了 模型组 的相关接口

- **根据模型组ID查询模型组详情**
"""
import httpx
import json
import os
from ..exceptions import APIError
from ..models.common import APIWrapper
from ..models.model_group import ModelGroup


_MODEL_GROUP_BASE = "/api/model/v5/modelgroup"


class ModelGroupService:
    """模型组"""

    def __init__(self, http: httpx.Client):
        self._http = http

    def get(self, model_group_id: int) -> ModelGroup | None:
        """根据 arcternweb 上的模型组 id 获取模型组的详细信息

        Args:
            model_group_id: 模型组 id

        Returns:
            ModelGroup: 模型组的详细信息
        """
        params = {"ModelGroupID": model_group_id}
        resp = self._http.get(f"{_MODEL_GROUP_BASE}/{model_group_id}", params=params)
        wrapper = APIWrapper[ModelGroup].model_validate(resp.json())
        if wrapper.Code != 0:
            raise APIError(f"backend code {wrapper.Code}: {wrapper.Msg}")
        return wrapper.Data

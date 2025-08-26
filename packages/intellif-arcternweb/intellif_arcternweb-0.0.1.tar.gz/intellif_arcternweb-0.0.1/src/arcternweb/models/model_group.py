# !/usr/bin/env python
# -*-coding:utf-8 -*-

from pydantic import BaseModel, Field
from enum import IntEnum


class ModelGroupType(IntEnum):
    """模型组类型：1-图片；2-视频；3-多模态"""

    IMAGES = 1
    VIDEOS = 2
    MM = 3


class ModelGroup(BaseModel):
    """模型组信息"""

    m_model_group_id: int = Field(alias="ModelGroupID", description="模型组ID")
    m_model_group_name: str = Field(alias="ModelGroupName", description="模型组名称")
    m_model_input_dims: int = Field(4, alias="ModelInputDims", description="模型的输出维度数，4维模型，5维模型等")
    m_model_group_type: ModelGroupType = Field(ModelGroupType.IMAGES, alias="ModelGroupType", description="模型组类型")

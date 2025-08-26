# !/usr/bin/env python
# -*-coding:utf-8 -*-

from pydantic import BaseModel, Field


class InferTask(BaseModel):
    """推理任务信息"""

    infer_task_id: int = Field(alias="InferTaskID", description="推理任务ID")
    task_name: str = Field(alias="TaskName", description="推理任务名称")
    model_group_id: int = Field(alias="ModelGroupID", description="模型组ID")
    dataset_id: int = Field(alias="DatasetID", description="数据集ID")
    dataset_name: str = Field(alias="DatasetName", description="数据集名称")
    device_id: int = Field(alias="DeviceID", description="设备ID")
    device_name: str = Field(alias="DeviceName", description="设备名称")
    result_path: str = Field(alias="ResultKey", description="推理任务结果文件在S3上的路径")
    label: str = Field(alias="Label", description="推理结果中的下标索引的具体含义")

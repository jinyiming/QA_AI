from typing import Literal

from fastapi import APIRouter, Body

from file_rag.server.types.server.response.base import BaseResponse
from file_rag.settings import Settings
from file_rag.server.utils import get_prompt_template, get_server_configs

server_router = APIRouter(prefix="/login", tags=["Login State"])

# 服务器相关接口
server_router.post(
    "/login",
    summary="登录",
)(get_server_configs)


@server_router.post("/get_prompt_template", summary="获取服务区配置的 prompt 模板", response_model=BaseResponse)
def get_server_prompt_template(
        type: str = Body(
            "llm_model", description="模板类型，可选值：{available_template_types}"
        ),
        name: str = Body("default", description="模板名称"),
):
    prompt_template = get_prompt_template(type=type, name=name)
    if prompt_template is None:
        return BaseResponse.error("Prompt template not found")
    return BaseResponse.success(prompt_template)
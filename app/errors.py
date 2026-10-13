"""Chinese messages at the HTTP boundary; keep status codes and English API behavior."""

import os

from fastapi import Request
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException

TEXT = {
    "Not Found": "未找到请求的内容。",
    "Method Not Allowed": "此接口不支持该操作。",
    "profile not found": "未找到用户档案。",
    "AI analysis is not configured (set MISCALE_AI_API_KEY)": "尚未配置 AI 分析，请设置 MISCALE_AI_API_KEY。",
    "no weigh-in in the last 7 days": "最近 7 天没有称重记录，暂时无法分析。",
    "an analysis for this profile is already being written": "正在生成该用户的分析，请稍后再试。",
    "send a JPEG, PNG or WebP image": "请上传 JPEG、PNG 或 WebP 格式的图片。",
    "empty photo or larger than 8 MB": "图片为空或超过 8 MB，请换一张图片。",
}
FIELDS = {
    "name": "姓名", "height_cm": "身高", "birth": "出生日期", "male": "性别",
    "ref_weight": "参考体重", "unit": "体重单位", "tolerance_kg": "识别体重的允许偏差",
    "profile_id": "用户", "weight": "体重", "impedance": "阻抗",
}


def chinese(request: Request) -> bool:
    language = request.headers.get("accept-language", os.environ.get("MISCALE_LANG", "zh-CN"))
    return language.lower().startswith("zh")


async def http_error(request: Request, exc: HTTPException):
    if not chinese(request):
        return await http_exception_handler(request, exc)
    detail = TEXT.get(str(exc.detail))
    if detail is None:
        detail = "AI 服务暂时无法生成分析，请检查配置后重试。" if exc.status_code == 502 else "请求失败，请检查输入后重试。"
    return JSONResponse(status_code=exc.status_code, content={"detail": detail}, headers=exc.headers)


async def validation_error(request: Request, exc: RequestValidationError):
    if not chinese(request):
        return await request_validation_exception_handler(request, exc)
    details = []
    for error in exc.errors():
        field = FIELDS.get(str(error["loc"][-1]), "输入内容")
        context = error.get("ctx") or {}
        kind = error["type"]
        if kind == "greater_than":
            reason = f"必须大于 {context['gt']}"
        elif kind == "less_than":
            reason = f"必须小于 {context['lt']}"
        elif kind == "string_too_short":
            reason = f"至少填写 {context['min_length']} 个字符"
        elif kind == "string_too_long":
            reason = f"最多填写 {context['max_length']} 个字符"
        elif kind == "missing":
            reason = "请填写此项"
        elif kind == "literal_error":
            reason = "请选择有效选项"
        else:
            reason = "格式不正确，请检查后重试"
        details.append({"loc": list(error["loc"]), "msg": f"{field}：{reason}。", "type": kind})
    return JSONResponse(status_code=422, content={"detail": details})

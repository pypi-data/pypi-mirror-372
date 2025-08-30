#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : generations
# @Time         : 2025/6/11 17:06
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 统一收口

from meutils.pipe import *
from meutils.llm.clients import AsyncClient
from meutils.llm.openai_utils import to_openai_params

from meutils.schemas.image_types import ImageRequest, RecraftImageRequest

from meutils.apis.fal.images import generate as fal_generate

from meutils.apis.gitee.image_to_3d import generate as image_to_3d_generate
from meutils.apis.gitee.openai_images import generate as gitee_images_generate
from meutils.apis.volcengine_apis.images import generate as volc_generate
from meutils.apis.images.recraft import generate as recraft_generate
from meutils.apis.jimeng.images import generate as jimeng_generate
# from meutils.apis.google.images import generate as google_generate

from meutils.apis.qwen.chat import Completions as QwenCompletions
from meutils.apis.google.chat import Completions as GoogleCompletions
from meutils.apis.google.images import generate as google_generate


async def generate(
        request: ImageRequest,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
):
    logger.debug(request)

    if request.model.startswith("fal-ai"):  # 主要 request.image
        return await fal_generate(request, api_key)

    if request.model.startswith(("recraft",)):
        request = RecraftImageRequest(**request.model_dump(exclude_none=True))
        return await recraft_generate(request)

    if request.model.startswith(("seed", "seededit_v3.0", "byteedit_v2.0", "i2i_portrait_photo")):  # seededit seedream
        return await volc_generate(request, api_key)

    if request.model.startswith(("jimeng")):  # 即梦
        return await jimeng_generate(request)

    if request.model in {"Hunyuan3D-2", "Hi3DGen", "Step1X-3D"}:
        return await image_to_3d_generate(request, api_key)

    if request.model in {"Qwen-Image", "FLUX_1-Krea-dev"} and request.model.endswith(("lora",)):
        return await gitee_images_generate(request, api_key)

    if request.model.startswith("qwen-image"):  # 仅支持单图
        if request.image and isinstance(request.image, list):
            request.image = request.image[-1]
        return await QwenCompletions(api_key=api_key).generate(request)

    if request.model.startswith(("gemini",)):
        return await GoogleCompletions(base_url=base_url, api_key=api_key).generate(request)

    if request.model.startswith(("google/gemini",)):  # openrouter
        return await google_generate(request, base_url=base_url, api_key=api_key)

    # 其他
    data = {
        **request.model_dump(exclude_none=True, exclude={"extra_fields", "aspect_ratio"}),
        **(request.extra_fields or {})
    }
    request = ImageRequest(**data)
    if request.model.startswith("doubao"):
        request.watermark = False
        if request.image and isinstance(request.image, list):
            request.image = request.image[0]

    data = to_openai_params(request)
    client = AsyncClient(api_key=api_key, base_url=base_url)
    return await client.images.generate(**data)


# "flux.1-krea-dev"

if __name__ == '__main__':
    # arun(generate(ImageRequest(model="flux", prompt="笑起来")))
    # arun(generate(ImageRequest(model="FLUX_1-Krea-dev", prompt="笑起来")))

    token = f"""{os.getenv("VOLC_ACCESSKEY")}|{os.getenv("VOLC_SECRETKEY")}"""
    arun(generate(ImageRequest(model="seed", prompt="笑起来"), api_key=token))

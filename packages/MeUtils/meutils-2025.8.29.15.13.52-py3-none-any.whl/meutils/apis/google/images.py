#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : images
# @Time         : 2025/4/7 13:07
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : D3 生图、编辑图
"""
# {
    #     "index": 0,
    #     "type": "image_url",
    #     "image_url": {
    #         "url": "b64"
    #     }
    #
    # }

"""

from meutils.pipe import *
from meutils.io.files_utils import to_url
from meutils.llm.clients import AsyncOpenAI
from meutils.apis.images.edits import edit_image, ImageProcess

from meutils.schemas.image_types import ImageRequest, ImagesResponse
from meutils.schemas.openai_types import CompletionRequest


async def generate(request: ImageRequest, api_key: Optional[str] = None, base_url: Optional[str] = None):
    is_hd = False
    if request.model.endswith("-hd"):
        is_hd = True
        request.model = request.model.removesuffix("-hd")

    image_urls = request.image_urls
    image_urls = await to_url(image_urls, content_type="image/png")
    image_urls = [
        {
            "type": "image_url",
            "image_url": {
                "url": image_url
            }
        }
        for image_url in image_urls or []
    ]

    request = CompletionRequest(
        model=request.model,
        stream=False,
        max_tokens=None,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": request.prompt
                    },
                    *image_urls
                ]
            }
        ],
    )

    data = request.model_dump(exclude_none=True)

    client = AsyncOpenAI(
        base_url=base_url,
        api_key=api_key
        # base_url="https://openrouter.ai/api/v1",
        # base_url="https://all.chatfire.cn/openrouter/v1",
        # api_key=api_key or os.getenv("OPENROUTER_API_KEY"),

    )

    completion = await client.chat.completions.create(**data)
    logger.debug(completion)
    if (
            completion
            and completion.choices
            and hasattr(completion.choices[0].message, "images")
            and (images := completion.choices[0].message.images)
    ):
        image_urls = [image['image_url']['url'] for image in images]
        logger.debug(image_urls)

        # if is_hd:
        #     tasks = [edit_image(ImageProcess(model="clarity", image=image_url)) for image_url in image_urls]
        #     responses = await asyncio.gather(*tasks)
        #
        #     logger.debug(responses)
        #
        #     image_urls = [response.data[0]["url"] for response in responses if response.data]
        #
        # else:
        image_urls = await to_url(image_urls, content_type="image/png")

        return ImagesResponse(image=image_urls)


if __name__ == '__main__':
    base_url = "https://api.huandutech.com/v1"
    api_key = "sk-qOpbMHesasoVgX75ZoeEeBEf1R9dmsUZVAPcu5KkvLFhElrn"
    request = ImageRequest(
        # model="google/gemini-2.5-flash-image-preview:free",
        model="gemini-2.5-flash-image-preview",
        # model="gemini-2.5-flash-image-preview-hd",

        prompt="带个墨镜",
        # image=["https://oss.ffire.cc/files/kling_watermark.png"],
    )

    r = arun(
        generate(
            request, base_url=base_url, api_key=api_key
        )
    )

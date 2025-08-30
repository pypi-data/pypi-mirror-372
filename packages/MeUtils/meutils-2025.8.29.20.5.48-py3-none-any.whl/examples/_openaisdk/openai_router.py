#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Project      : AI.  @by PyCharm
# @File         : open_router
# @Time         : 2024/10/14 19:04
# @Author       : betterme
# @WeChat       : meutils
# @Software     : PyCharm
# @Description  : 

from meutils.pipe import *
from openai import OpenAI
from os import getenv
from meutils.io.files_utils import to_url

# gets API Key from environment variable OPENAI_API_KEY
client = OpenAI(
    # base_url="https://openrouter.ai/api/v1",
    # base_url="https://all.chatfire.cn/openrouter/v1",
    # api_key=os.getenv("OPENROUTER_API_KEY"),
    #
    # base_url="http://38.46.219.252:9001/v1",
    #
    # api_key="sk-Azgp1thTIonR7IdIEqlJU51tpDYNIYYpxHvAZwFeJiOdVWiz"

    base_url="https://api.huandutech.com/v1",
api_key = "sk-qOpbMHesasoVgX75ZoeEeBEf1R9dmsUZVAPcu5KkvLFhElrn"
)

completion = client.chat.completions.create(
    # extra_headers={
    #   "HTTP-Referer": $YOUR_SITE_URL, # Optional, for including your app on openrouter.ai rankings.
    #   "X-Title": $YOUR_APP_NAME, # Optional. Shows in rankings on openrouter.ai.
    # },
    # model="meta-llama/llama-3.2-11b-vision-instruct:free",
    # model="openai/o1",
    # model="deepseek/deepseek-r1-0528-qwen3-8b:free",
    # model="google/gemini-2.5-flash-image-preview:free",
    model="gemini-2.5-flash-image-preview",
    # model="gemini-2.0-flash-exp-image-generation",
    # max_tokens=10,

    messages=[
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "带个墨镜"
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": "https://oss.ffire.cc/files/kling_watermark.png"
                    }
                }
            ]
        }
    ]
)
# print(completion.choices[0].message.content)
# arun(to_url(completion.choices[0].message.images[0]['image_url']['url'], content_type="image/png"))


# arun(to_url(completion.choices[0].message.images[0]['image_url']['url'], content_type="image/png"))

# print(dict(completion.choices[0].message).keys())

# {
#     "index": 0,
#     "type": "image_url",
#     "image_url": {
#         "url": "b64"
#     }
#
# }

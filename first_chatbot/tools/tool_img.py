import json
import openai
import utils
import time
import base64
import gradio as gr

client = utils.get_openai_client()


def tool_img(param, request: gr.Request):
    image_response = client.images.generate(
        prompt=json.loads(param)["desc"],
        model="dall-e-2",
        n=1,
        quality="standard",
        response_format="b64_json",
        size="1024x1024",
        style="natural"
    )

    file_path = utils.save_file_by_content(
        "firt_chatbot", str(time.time())+".png", base64.b64decode(image_response.data[0].b64_json))

    return {
        "url": f'''<img src="{file_path}" />''',
    }


def desc_tool_img():
    return {
        "type": "function",
        "function": {
            "name": "tool_img",
            "description": "通过描述生成图片",
            "parameters": {
                "type": "object",
                "properties": {
                    # 参数定义
                    "desc": {
                        "type": "string",
                        "description": "图片的描述",
                    },
                },
                # 规定哪些参数是必须的
                "required": ["desc"],
            },
        }
    }

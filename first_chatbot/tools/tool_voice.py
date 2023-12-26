import json
import openai
import utils
import time
import gradio as gr

client = utils.get_openai_client()


def tool_voice(param, request: gr.Request):
    voice = client.audio.speech.create(
        model="tts-1",
        input=json.loads(param)["text"],
        voice="alloy",
        response_format="mp3",
        speed=1.0
    )

    file_path = utils.save_file_by_content(
        "firt_chatbot", str(time.time())+".mp3", voice.content)

    print(file_path)

    return {
        "url": f'''<audio src="{file_path}" controls />''',
    }


def desc_tool_voice():
    return {
        "type": "function",
        "function": {
            "name": "tool_voice",
            "description": "通过文本生成语音",
            "parameters": {
                "type": "object",
                "properties": {
                    # 参数定义
                    "text": {
                        "type": "string",
                        "description": "要生成语音的文本",
                    },
                },
                # 规定哪些参数是必须的
                "required": ["text"],
            },
        }
    }

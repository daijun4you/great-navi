import time
from gradio import Request
import openai


def gradio_history_to_openai_messages(history, system_role):
    openai_messages = [{
        "role": "system",
        "content": system_role
    }]

    for one in history:
        openai_messages.append({
            "role": "user",
            "content": one[0],
        })

        openai_messages.append({
            "role": "assistant",
            "content": one[1],
        })

    return openai_messages


def get_gpt_chunk_tool_calls(chunk):
    return chunk.choices[0].delta.tool_calls


def save_file_by_content(chatbot_name, file_name, content):
    file_path = f"/static/{chatbot_name}_{file_name}"
    with open("."+file_path, 'wb') as file:
        file.write(content)

    return file_path


def create_file_url_path(req: Request, file_path: str):
    return req.request.base_url._url[:-1] + file_path


def get_openai_client():
    return openai.OpenAI(
        api_key="sk-6V2exWFBSa2lmuZ7C0D773D1BaEd4fB7A1B6A0A265D550C6",
        base_url="https://key.wenwen-ai.com/v1"
    )

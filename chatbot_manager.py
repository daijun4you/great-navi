import gradio as gr
from dotenv import load_dotenv
import sys
import importlib
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os


class ChatBotManager:
    def __init__(self):
        load_dotenv()
        self.app = FastAPI()
        self._init_download_folder()
        self._init_gradio()

    def start(self):
        import uvicorn
        uvicorn.run(self.app, host="0.0.0.0", port=8123)

    def _init_download_folder(self):
        self.app.mount(
            "/static", StaticFiles(directory="static"), name="static")

    def _init_gradio(self):
        chatbot = self._get_chatbot_by_cmd()

        self.gr_service = gr.ChatInterface(
            # 消息处理的函数
            chatbot.handle_msg,

            # 聊天框大小 & 加载消息
            chatbot=gr.Chatbot(height=500),
            # 提问框里的提示
            textbox=gr.Textbox(placeholder="输入你的问题...",
                               container=False, scale=7),
            title=chatbot.name,
            description=chatbot.desc,
            theme="soft",

            # --------- 一些功能按钮定义 ---------------
            retry_btn="重试",
            undo_btn=None,
            submit_btn="提问",
            clear_btn=" 清空",
        ).queue()

        gr.mount_gradio_app(self.app, self.gr_service, path="/")

    def _get_chatbot_by_cmd(self):
        chatbot_name = "first_chatbot"
        if len(sys.argv) > 1:
            bot_name = sys.argv[1]
        chatbot_module = importlib.import_module(f"{chatbot_name}.chatbot")
        chatbot = chatbot_module.Chatbot()
        return chatbot


if __name__ == "__main__":
    chatbot_manager = ChatBotManager()
    chatbot_manager.start()

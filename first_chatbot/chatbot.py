import openai
import os
import utils
import json
from first_chatbot.tools import tool_img
from first_chatbot.tools import tool_voice
import gradio as gr


class Chatbot:
    def __init__(self):
        self.name = "菠菜的Chatbot"
        self.desc = "菠菜的第一个聊天机器人"
        self.gpt_model = "gpt-3.5-turbo"
        self.client = utils.get_openai_client()
        self.tools = {
            "tool_img": [tool_img.tool_img, tool_img.desc_tool_img],
            "tool_voice": [tool_voice.tool_voice, tool_voice.desc_tool_voice],
        }

    def handle_msg(self, user_msg, history, request: gr.Request, *arg):
        # 构建GPT的上下文
        messages = utils.gradio_history_to_openai_messages(
            history, self.get_system_role())
        messages.append({
            "role": "user",
            "content": user_msg
        })

        # 请求GPT，获取结果
        chat_completion_chunks = self.client.chat.completions.create(
            messages=messages,
            model=self.gpt_model,
            stream=True,
            top_p=0.2,
            tools=self.get_tools_define(),
            tool_choice="auto",
        )

        # 通过第一个chunk判断是tool call，还是正常的消息答复
        first_chunk = next(chat_completion_chunks)
        tool_calls = utils.get_gpt_chunk_tool_calls(first_chunk)
        if first_chunk is None:
            yield "empty"

        # tool call
        elif tool_calls is not None:
            # 等待tool_call的function的args输出完成
            for rs in self._handle_tool_call_msg(
                    first_chunk, chat_completion_chunks, messages, request):
                yield rs

        # 处理正常的消息
        else:
            for rs in self._handle_normal_msg(chat_completion_chunks):
                yield rs

    def _handle_normal_msg(self, chat_completion_chunks):
        msg = ""
        for one in chat_completion_chunks:
            chunk = one.choices[0].delta
            if chunk.content is not None:
                msg += chunk.content
                yield msg

    def _handle_tool_call_msg(
            self, first_chunk, other_chunks, messages, request):

        tool_calls = utils.get_gpt_chunk_tool_calls(first_chunk)
        tool_calls_args = [
            "" for _ in range(len(tool_calls))
        ]

        for chunk in other_chunks:
            chunk_tool_calls = utils.get_gpt_chunk_tool_calls(chunk)
            if chunk_tool_calls is None:
                break

            for i, chunk_tool_call in enumerate(chunk_tool_calls):
                tool_calls_args[i] += chunk_tool_call.function.arguments

        # 完成调用tool的过程
        messages.append(first_chunk.choices[0].delta)

        yield self.call_tool(tool_calls, tool_calls_args, messages, request)

    def get_tools_define(self):
        tools = []
        for tool in self.tools.values():
            tools.append(tool[1]())

        return tools

    def call_tool(self, tool_calls, tool_calls_args, messages, request):
        for tool_call, tool_call_args in zip(tool_calls, tool_calls_args):
            # 获取tool的名称
            tool_name = tool_call.function.name
            # 获取tool的参数

            tool = self.tools.get(tool_name)
            if tool is None:
                continue

            result = tool[0](tool_call_args, request)

            # 将tool_call的结果加入上下文
            messages.append({
                "role": "tool",
                "content": json.dumps(result),
                "tool_call_id": tool_call.id
            })

        tool_chat_completion = self.client.chat.completions.create(
            messages=messages,
            model=self.gpt_model,
            top_p=0.2,
            stream=False,
            tools=self.get_tools_define(),
            tool_choice="auto"
        )

        messages.append(tool_chat_completion.choices[0].message)

        return tool_chat_completion.choices[0].message.content

    def get_system_role(self):
        return '''
# role: 菠菜的智能机器人
## rule
- 对于用户生成图片请直接在会话框里展示而不是需要用户点击跳转
- 对于语音、音频等文件的展示，可以使用可以使用"<audio>"标签
## init
作为<role>，请严格遵守<rule>
        '''

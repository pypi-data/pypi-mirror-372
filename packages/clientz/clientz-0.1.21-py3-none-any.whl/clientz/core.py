
""" core 需要修改"""
import re
from typing import Dict, Any
from llmada.core import BianXieAdapter
from clientz.utils import FileChangeTrigger

from .log import Log
logger = Log.logger

LLM_INFO = {
"query_persist_dir": "/Users/zhaoxuefeng/GitHub/test1/obsidian_kb/my_obsidian_notes",
"WORK_CANVAS_PATH": [
"/工程系统级设计/能力级别/人体训练设计/人体训练设计.canvas"
],
"ModelCards": [
    "cus-gpt-5",
    "cus-gpt-5-mini-2025-08-07",
    "cus-gemini-2.5-flash-preview-04-17-nothinking",
    "cus-gemini-2.5-flash-preview-05-20-nothinking",
    "cus-deepseek-v3-250324",
],
"Custom": [
            "Z_LongMemory",
        ]
}

def extract_last_user_input(dialogue_text):
    """
    从多轮对话文本中提取最后一个 user 的输入内容。

    Args:
        dialogue_text: 包含多轮对话的字符串。

    Returns:
        最后一个 user 的输入内容字符串，如果未找到则返回 None。
    """
    pattern = r"(?s).*user:\s*(.*?)(?=user:|$)"

    match = re.search(pattern, dialogue_text)

    if match:
        # group(1) 捕获的是最后一个 user: 到下一个 user: 或字符串末尾的内容
        return match.group(1).strip()
    else:
        return None

class YamlTrigger(FileChangeTrigger):
    def _trigger_action(self):
        print('hello world')

class ChatBox():
    """ chatbox """
    def __init__(self) -> None:
        self.bx = BianXieAdapter()
        self.dicts = LLM_INFO
        self.query_persist_dir = self.dicts.get('query_persist_dir')
        self.model_pool = self.dicts.get("ModelCards")
        self.init_lazy_parameter()
        self.trigger = YamlTrigger(file_path = 'clientz/config.yaml')
        self.update_llm()

    def init_lazy_parameter(self):
        """ 一个懒加载的初始化头部 """
        self.chat_with_agent_notes_object = None

    def update_llm(self):
        for model in self.model_pool:
            self.bx.model_pool.append(model[4:])

    def product(self,prompt_with_history: str, model: str) -> str:
        """ 同步生成, 搁置 """
        prompt_no_history = extract_last_user_input(prompt_with_history)
        logger.debug(f"# prompt_no_history : {prompt_no_history}")
        logger.debug(f"# prompt_with_history : {prompt_with_history}")
        prompt_with_history, model
        return 'product 还没有拓展'

    async def astream_product(self,prompt_with_history: str, model: str) -> Any:
        """
        # 只需要修改这里
        """
        self.trigger.check_and_trigger()
        prompt_no_history = extract_last_user_input(prompt_with_history)
        logger.debug(f"# prompt_no_history : {prompt_no_history}")
        logger.debug(f"# prompt_with_history : {prompt_with_history}")


        ## __init__ ##
        if model in self.model_pool:
            logger.info(f"running {model}")
            self.bx.set_model(model[4:])
            # for word in self.bx.product_stream(prompt_with_history):
            #     yield word

            async for word in self.bx.aproduct_stream(prompt_with_history):
                yield word



        elif model == 'Z_LongMemory':
            logger.info(f"running {model}")
            # build

            # chat
            prompt_with_history, prompt_no_history

            yield "TODO"

        else:
            yield 'pass'

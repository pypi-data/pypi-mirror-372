
import os
from abc import ABC, abstractmethod

class FileChangeTrigger(ABC):
    # 文件修改后的触发器
    def __init__(self,file_path) -> None:
        self.file_path = file_path
        self._last_modified_time = None
        self._update_last_modified_time()
    
    def _update_last_modified_time(self):
        """更新存储的最后修改时间"""
        try:
            self._last_modified_time = os.path.getmtime(self.file_path)
        except FileNotFoundError:
            self._last_modified_time = None # 文件不存在时设为None

    def check_and_trigger(self):
        """检查文件是否变化，如果变化则触发动作"""
        try:
            current_modified_time = os.path.getmtime(self.file_path)
            if current_modified_time != self._last_modified_time:
                print(f"文件 '{self.file_path}' 已发生变化。")
                self._trigger_action()
                self._last_modified_time = current_modified_time # 更新存储的时间
            else:
                print(f"文件 '{self.file_path}' 未发生变化。")
        except FileNotFoundError:
            print(f"文件 '{self.file_path}' 不存在。")
            self._last_modified_time = None # 文件不存在时重置状态
        except Exception as e:
            print(f"检查文件时发生错误: {e}")

    @abstractmethod
    def _trigger_action(self):
        """当文件发生变化时触发的动作
            添加到服务中
        """


import re
import os
import time
from contextlib import contextmanager
import importlib.resources
from typing import Dict, Any
import yaml


@contextmanager
def check_time(title:str,logger):
    """ try catch"""
    time1 = time.time()
    yield
    time2 = time.time()
    logger.debug(f"{title}: {time2-time1}")

    

def extra_docs(inputs:str)->dict:
    """ docs """
    pattern1 = r'<context>(.*?)<\/context>'
    pattern2 = r'<source id="(\d+)">(.*?)<\/source>'

    match = re.search(pattern1, inputs,re.DOTALL)

    if match:
        sources = match.group(1).strip()
        matches = re.findall(pattern2, sources)

    result = {int(id): content for id, content in matches}
    return result



def load_config():
    """ load config """
    with importlib.resources.open_text('clientz', 'config.yaml') as f:
        return yaml.safe_load(f)

def format_node_for_chat(node_data: Dict[str, Any]) -> str:
    """
    解析节点数据，生成适合聊天窗口显示的格式化字符串。

    Args:
        node_data: 包含节点信息的字典结构。

    Returns:
        一个格式化的字符串，包含分数和节点文本内容。
        如果结构异常，返回错误提示。
    """
    node = node_data.get('node')
    score = node_data.get('score')

    if not node:
        return "Error: Could not find 'node' information."

    text_content = node.get('text')
    if not text_content:
        return "Error: 'text' content not found in node."

    # 移除 text 开头的 "topic:  content: \n\n\n" 或类似的元数据前缀
    # 根据你提供的样本，可能是固定的前缀，或者需要更灵活的处理
    # 这里简单移除已知的开头
    prefix_to_remove = "topic:  content: \n\n\n"
    if text_content.startswith(prefix_to_remove):
        text_content = text_content[len(prefix_to_remove):].strip()
    else:
        text_content = text_content.strip() # 或者只移除首尾空白

    # 构建输出字符串
    output = ""
    if score is not None:
        # 格式化分数，例如保留两位小数
        output += f"**Relevant Information (Score: {score:.2f})**:\n\n"
    else:
        output += "**Relevant Information:**\n\n"

    # 直接添加处理后的文本内容
    # 假设聊天窗口支持 Markdown，会渲染 #, ##, **, -, []() 等
    output += text_content

    # 你可以进一步处理 links，例如将它们提取出来单独列在末尾
    # link_pattern = re.compile(r'\[([^\]]+)\]\(([^\)]+)\)')
    # links_found = link_pattern.findall(text_content)
    # if links_found:
    #     output += "\n\n---\n*Links mentioned:*\n"
    #     for link_text, link_url in links_found:
    #         output += f"- [{link_text}]({link_url})\n" # 或其他格式

    return output

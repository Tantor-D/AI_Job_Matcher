from abc import ABC, abstractmethod
from typing import Dict, Any
import re

class AIModel(ABC):
    """AI模型的抽象基类"""
    
    @abstractmethod
    def judge(self, user_requirements: str, job_description: str) -> Dict[str, Any]:
        """
        判断用户需求和职位描述的匹配程度
        
        Args:
            user_requirements: 用户需求文本
            job_description: 职位描述文本
            
        Returns:
            包含判断结果的字典，可能包含以下字段：
            - decision: 是否推荐（布尔值）
            - score: 匹配度分数（0-1之间的浮点数）
            - reason: 推荐原因或不推荐原因
        """
        pass


    def _extract_code_blocks(self, text: str) -> list:
        """
        提取由 ``` 包裹的内容的代码块。

        Args:
            text (str): 输入字符串。

        Returns:
            list: 一个包含所有代码块内容的列表。
        """
        # 使用正则表达式匹配 ``` 包裹的内容
        pattern = r"```(.*?)```"
        matches = re.findall(pattern, text, re.DOTALL)

        # 如果没有匹配到代码块，则返回原始字符串
        if not matches:
            return text

        return matches
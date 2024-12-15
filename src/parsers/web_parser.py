from abc import ABC, abstractmethod
from typing import Dict, Any


class WebParser(ABC):
    """网页解析的抽象基类"""
    
    @abstractmethod
    def parse(self, url: str) -> Dict[str, Any]:
        """
        解析给定URL的招聘信息
        
        Args:
            url: 招聘信息网页的URL
            
        Returns:
            包含招聘信息的字典，应该包含以下字段：
            - title: 职位名称
            - company: 公司名称
            - location: 工作地点
            - salary: 薪资范围
            - description: 职位描述
            - requirements: 职位要求
        """
        pass 
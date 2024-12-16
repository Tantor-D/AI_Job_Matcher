from abc import ABC, abstractmethod
from typing import Dict, Any, List


class WebParser(ABC):
    """网页解析的抽象基类"""

    @abstractmethod
    def parse(self, url: str) -> List[Dict[str, Any]]:
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

    @abstractmethod
    def format_job_description_str(self, job_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        将职位信息转换为文本

        Args:
            job_info: 包含招聘信息的字典

        Returns:
            包含职位信息的文本
        """
        pass

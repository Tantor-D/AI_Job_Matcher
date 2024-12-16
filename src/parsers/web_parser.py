from abc import ABC, abstractmethod
from typing import Dict, Any, List


class WebParser(ABC):
    """网页解析的抽象基类"""

    @abstractmethod
    def parse(self, url: str, max_num: int) -> List[Dict[str, Any]]:
        """
        解析给定URL的招聘信息，注意这里的URL是搜索结果页，不是具体的招聘信息页，所以返回的是多个招聘信息
        
        Args:
            url: 招聘信息网页的URL
            max_num: 最多解析的招聘信息数量，-1表示不限制
            
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

    @abstractmethod
    def format_all_job_descriptions(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """
        格式化多个职位信息为字符串

        Args:
            jobs: 包含多个职位信息的列表

        Returns:
            包含多个格式化职位描述字符串的列表
        """
        pass

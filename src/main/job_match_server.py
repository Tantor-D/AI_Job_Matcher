from typing import Dict, Any
import yaml
from ..parsers.web_parser import WebParser
from ..ai.ai_judger import AIJudger

class JobMatchServer:
    """求职匹配系统主类"""
    
    def __init__(self, parser: WebParser, judger: AIJudger):
        self.parser = parser
        self.judger = judger
        
    def process_job(self, user_requirements: str, job_url: str) -> Dict[str, Any]:
        """
        处理单个职位匹配
        """
        try:
            # 解析职位信息
            job_info = self.parser.parse(job_url)
            
            # 将职位信息转换为文本
            job_description = self._format_job_info(job_info)
            
            # 进行匹配判断
            result = self.judger.judge_single(user_requirements, job_description)
            
            # 添加职位基本信息到结果中
            result.update({
                'job_title': job_info['title'],
                'company': job_info['company'],
                'location': job_info['location'],
                'salary': job_info['salary']
            })
            
            return result
            
        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }
    
    def _format_job_info(self, job_info: Dict[str, Any]) -> str:
        """
        将职位信息格式化为文本
        """
        return f"""
        职位：{job_info['title']}
        公司：{job_info['company']}
        地点：{job_info['location']}
        薪资：{job_info['salary']}
        描述：{job_info['description']}
        要求：{job_info['requirements']}
        """ 
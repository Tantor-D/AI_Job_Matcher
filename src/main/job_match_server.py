from typing import Dict, Any
import yaml
from parsers import WebParser, LinkedInParser
from ai import AIJudger, QwenModel


class JobMatchServer:
    """求职匹配系统主类"""

    def __init__(self, parser: WebParser, judger: AIJudger):
        self.parser = parser
        self.judger = judger

    def process_job(self, job_url: str, max_num: int = -1, user_requirements: str = "") -> Dict[str, Any]:
        """
        处理一次linkedin职位检索结果 的匹配请求
        """
        try:
            # 解析职位信息
            job_info_list = self.parser.parse(job_url, max_num)
            job_str_description_list = self.parser.format_all_job_descriptions(job_info_list)
            result = self.judger.judge_batch(job_str_description_list, job_info_list, user_requirements)[0]
            return result

        except Exception as e:
            return {
                'error': str(e),
                'status': 'failed'
            }


if __name__ == '__main__':
    # 加载配置
    with open('../../config/config.yaml', 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 初始化parser
    parser = LinkedInParser()

    # 初始化AI模型
    ai_model = QwenModel(**config['ai_model']['qwen'])
    judger = AIJudger(
        ai_model,
        user_requirements=config['user_requirements'],
    )

    # 初始化主服务
    server = JobMatchServer(parser, judger)

    # 测试
    test_url = "https://www.linkedin.com/jobs/search/?currentJobId=4077875677&geoId=101008859&keywords=student%20software&origin=JOB_SEARCH_PAGE_SEARCH_BUTTON&refresh=true"
    result = server.process_job(test_url, max_num=2)
    print(result)

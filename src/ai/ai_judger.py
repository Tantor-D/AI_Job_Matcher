from typing import Dict, Any, List
from .ai_model import AIModel


class AIJudger:
    """AI判断协调器"""

    def __init__(self, ai_model: AIModel, user_requirements, threshold: float = 0.7):
        # todo 后期优化的话这里应该是可以传入AIModel的config的，然后直接初始化AIModel
        self.ai_model = ai_model
        self.threshold = threshold
        self.user_requirements = user_requirements

    def judge_single(self, job_description: str, job_info: Dict = None, user_requirements: str = "") -> Dict[str, Any]:
        """
        判断单个职位是否匹配需求
        """
        if not user_requirements:
            user_requirements = self.user_requirements
        result = self.ai_model.judge(user_requirements, job_description)
        result = self._post_process(result, job_info)
        return result

    def judge_batch(self, job_descriptions: List[str], job_info_list: List = None, user_requirements: str = "") -> List[
        Dict[str, Any]]:
        """
        批量判断多个职位

        todo, 优化为并行处理
        """
        if not user_requirements:
            user_requirements = self.user_requirements
        results = []
        for idx in range(len(job_descriptions)):
            job_info = job_info_list[idx] if job_info_list else None
            results.append(self.judge_single(job_descriptions[idx], job_info, user_requirements))
        return results

    def _post_process(self, result: Dict[str, Any], job_info: Dict) -> Dict[str, Any]:
        """
        对得到的result进行后处理，例如没有reason字段时自动生成，只有score没有decision时自动判断
        """
        # 如果提供了职位信息，将职位信息添加到结果中
        if job_info:
            result['job_info'] = job_info

        # 处理失败了，不进行任何处理
        if "success" in result and not result["success"]:
            return result

        # 如果模型只返回分数，补充决策和原因
        if 'score' in result and 'decision' not in result:
            score = result['score']
            result['decision'] = score >= self.threshold
            if 'reason' not in result or not result['reason']:
                result['reason'] = self._generate_default_reason(score)

        # todo: other post processing
        return result

    def _generate_default_reason(self, score: float) -> str:
        """
        生成推荐或不推荐的理由
        """
        if score >= self.threshold:
            return f"匹配度达到{score:.2%}，建议考虑此职位"
        else:
            return f"匹配度仅为{score:.2%}，建议继续寻找更合适的职位"

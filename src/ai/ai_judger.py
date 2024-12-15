from typing import Dict, Any, List
from .ai_model import AIModel


class AIJudger:
    """AI判断协调器"""

    def __init__(self, ai_model: AIModel, threshold: float = 0.7):
        self.ai_model = ai_model
        self.threshold = threshold

    def judge_single(self, user_requirements: str, job_description: str) -> Dict[str, Any]:
        """
        判断单个职位是否匹配需求
        """
        result = self.ai_model.judge(user_requirements, job_description)
        result = self._post_process(result)
        return result

    def judge_batch(self, user_requirements: str, job_descriptions: List[str]) -> List[Dict[str, Any]]:
        """
        批量判断多个职位

        todo, 优化为并行处理
        """
        return [self.judge_single(user_requirements, desc) for desc in job_descriptions]

    def _post_process(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        对得到的result进行后处理，例如没有reason字段时自动生成，只有score没有decision时自动判断
        """

        # 处理失败了，不进行任何处理
        if "success" in result and not result["success"]:
            return result

        # 如果模型只返回分数，补充决策和原因
        if 'score' in result and 'decision' not in result:
            score = result['score']
            result['decision'] = score >= self.threshold
            if 'reason' not in result or not result['reason']:
                result['reason'] = self._generate_reason(score)

        # todo: other post processing
        return result

    def _generate_reason(self, score: float) -> str:
        """
        生成推荐或不推荐的理由
        """
        if score >= self.threshold:
            return f"匹配度达到{score:.2%}，建议考虑此职位"
        else:
            return f"匹配度仅为{score:.2%}，建议继续寻找更合适的职位"

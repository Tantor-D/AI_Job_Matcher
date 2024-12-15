from typing import Dict, Any, List
from .ai_model import AIModel

class AIJudger:
    """AI判断协调器"""
    
    def __init__(self, model: AIModel, threshold: float = 0.7):
        self.model = model
        self.threshold = threshold
    
    def judge_single(self, user_requirements: str, job_description: str) -> Dict[str, Any]:
        """
        判断单个职位
        """
        result = self.model.judge(user_requirements, job_description)
        
        # 如果模型只返回分数，补充决策和原因
        if 'score' in result and 'decision' not in result:
            score = result['score']
            result['decision'] = score >= self.threshold
            result['reason'] = self._generate_reason(score)
        
        return result
    
    def judge_batch(self, user_requirements: str, job_descriptions: List[str]) -> List[Dict[str, Any]]:
        """
        批量判断多个职位
        """
        return [self.judge_single(user_requirements, desc) for desc in job_descriptions]
    
    def _generate_reason(self, score: float) -> str:
        """
        根据分数生��推荐理由
        """
        if score >= self.threshold:
            return f"匹配度达到{score:.2%}，建议考虑此职位"
        else:
            return f"匹配度仅为{score:.2%}，建议继续寻找更合适的职位" 
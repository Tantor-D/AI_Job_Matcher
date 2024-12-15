import openai
from typing import Dict, Any
from .ai_model import AIModel


DEFAULT_PROMPT_TEMPLATE = """
请分析以下求职者的需求和职位描述的匹配程度：

求职者需求：
{user_requirements}

职位描述：
{job_description}

请给出：
1. 匹配度评分（0-1之间）
2. 是否推荐（true/false）
3. 详细的推荐理由或不推荐理由

请用JSON格式回答，包含score、decision和reason三个字段。
"""


class ChatGPTModel(AIModel):
    """基于ChatGPT的文本匹配模型"""

    def __init__(self,
                 api_key: str,
                 model: str = "gpt-3.5-turbo",
                 prompt_template: str = None):

        openai.api_key = api_key
        self.model = model
        self.prompt_template = prompt_template if prompt_template else DEFAULT_PROMPT_TEMPLATE

    def judge(self, user_requirements: str, job_description: str) -> Dict[str, Any]:
        prompt = self.prompt_template.format(
            user_requirements=user_requirements, job_description=job_description)

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )

            # 解析ChatGPT的JSON响应
            result = eval(response.choices[0].message.content)
            return result

        except Exception as e:
            raise Exception(f"ChatGPT API调用失败: {str(e)}")

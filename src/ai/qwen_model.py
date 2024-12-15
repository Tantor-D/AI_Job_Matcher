from typing import Dict, Any
from .ai_model import AIModel
import json

import os
from openai import OpenAI


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

请用JSON格式回答，包含score、decision和reason三个字段，注意你只需要给我一个JSON格式的内容就好了，且reason字段请尽可能的精简，整个JSON 请使用```前后包裹。
"""


class QwenModel(AIModel):
    """基于Qwen的文本匹配模型"""

    def __init__(self,
                 api_key: str,
                 base_url: str = "https://dashscope.aliyuncs.com/compatible-mode/v1",
                 model: str = "qwen-plus",
                 prompt_template: str = None):
        self.api_key = api_key
        self.model = model
        self.prompt_template = prompt_template if prompt_template else DEFAULT_PROMPT_TEMPLATE

        self.client = OpenAI(
            api_key=self.api_key,
            base_url=base_url,
        )
        
    def judge(self, user_requirements: str, job_description: str) -> Dict[str, Any]:
        prompt = self.prompt_template.format(
            user_requirements=user_requirements, job_description=job_description)
        messages = [{'role': 'system', 'content': 'You are a helpful assistant.'},
                    {'role': 'user', 'content': prompt}]

        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=True,
                stream_options={"include_usage": True}
            )

            chunks_content = []
            for chunk in completion:
                print(chunk.model_dump_json())
                chunks_content.append(chunk.choices[0].delta.content if len(chunk.choices) > 0 else "")

            response = "".join(chunks_content)
            ret_json = self.extract_code_blocks(response)
            ret_json = json.loads(ret_json[0])
            return ret_json

        except Exception as e:
            raise Exception(f"ChatGPT API调用失败: {str(e)}")
        
        


# 流式输出的JSON格式：
# {
#     "id":"chatcmpl-ecd76cbd-ec86-9546-880f-556fd2bb44b5",
#     "choices":[
#         {
#             "delta":{"content":"","function_call":null,"refusal":null,"role":null,"tool_calls":null},
#             "finish_reason":"stop","index":0,"logprobs":null}
#         ],
#     "created":1724916712,
#     "model":"qwen-turbo",
#     "object":"chat.completion.chunk",
#     "service_tier":null,
#     "system_fingerprint":null,
#     "usage":nul
# }


"""
JobMatch - 一个智能的求职匹配系统
"""

from .parsers.web_parser import WebParser
from .parsers.linkedin_parser import LinkedInParser
from .ai.ai_model import AIModel
from .ai.bert_model import BERTModel
from .ai.chatgpt_model import ChatGPTModel
from .ai.ai_judger import AIJudger
from .main.job_match import JobMatch

__version__ = "0.1.0"

__all__ = [
    "WebParser",
    "LinkedInParser",
    "AIModel",
    "BERTModel",
    "ChatGPTModel",
    "AIJudger",
    "JobMatch",
] 
from typing import Dict, Any
import torch
from transformers import BertModel, BertTokenizer
from .ai_model import AIModel

class BERTModel(AIModel):
    """基于BERT的文本匹配模型"""
    
    def __init__(self, model_name: str = 'bert-base-uncased'):
        self.tokenizer = BertTokenizer.from_pretrained(model_name)
        self.model = BertModel.from_pretrained(model_name)
        self.model.eval()
    
    def judge(self, user_requirements: str, job_description: str) -> Dict[str, Any]:
        # 对文本进行编码
        inputs1 = self.tokenizer(user_requirements, return_tensors="pt", padding=True, truncation=True)
        inputs2 = self.tokenizer(job_description, return_tensors="pt", padding=True, truncation=True)
        
        with torch.no_grad():
            # 获取CLS token的输出向量
            outputs1 = self.model(**inputs1)
            outputs2 = self.model(**inputs2)
            
            # 获取[CLS]标记的最后隐藏状态
            cls1 = outputs1.last_hidden_state[:, 0, :]
            cls2 = outputs2.last_hidden_state[:, 0, :]
            
            # 计算余弦相似度
            similarity = torch.cosine_similarity(cls1, cls2)
            score = similarity.item()
        
        return {
            'score': score
        } 
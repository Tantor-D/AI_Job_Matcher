import os
import yaml
from pathlib import Path

from ai.qwen_model import QwenModel

def load_config():
    """加载配置文件"""
    config_path = Path(__file__).parent.parent / "config" / "config.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def test_qwen_model_judge():
    """测试 QWENModel 的 judge 方法"""
    # 加载配置
    config = load_config()
    qwen_config = config["ai_model"]["qwen"]
    
    # 实例化 QWENModel
    model = QwenModel(
        model=qwen_config["model"],
        api_key=qwen_config["api_key"],
        base_url=qwen_config["base_url"]
    )
    
    # 测试用例
    user_requirements = """
    我想找一份Python开发工作，主要做后端开发。
    薪资要求25k-35k，最好在上海。
    我有3年工作经验，熟悉Django和Flask框架，
    对数据库和微服务架构都有实践经验。
    希望是一家技术氛围好的公司，能有技术成长。
    """
    
    job_description = """
    职位：Python后端开发工程师
    公司：某科技有限公司
    地点：上海市浦东新区
    薪资：25k-40k
    职责：
    1. 负责公司核心业务系统的后端开发
    2. 参与系统架构设计和优化
    3. 编写技术文档，参与代码审查
    要求：
    1. 3年以上Python开发经验
    2. 精通Django或Flask框架
    3. 熟悉MySQL、Redis等数据库
    4. 有微服务架构经验优先
    """
    
    # 调用judge方法
    result = model.judge(user_requirements, job_description)
    
    # 验证返回结果
    assert isinstance(result, dict), "返回结果应该是字典类型"
    assert "score" in result, "返回结果应包含score字段"
    assert "decision" in result, "返回结果应包含decision字段"
    assert "reason" in result, "返回结果应包含reason字段"
    
    # 打印结果供人工检查
    print("\n测试结果:")
    print(f"匹配度: {result['score']}")
    print(f"决策: {'接受' if result['decision'] else '拒绝'}")
    print(f"原因: {result['reason']}")


if __name__ == "__main__":
    test_qwen_model_judge() 
# JobMatch



## 简述

本项目用于实现一个简单的求职匹配系统。用户输入一段描述自己求职需求的文本（包括期望工作地点、薪资范围、工作内容等），系统会分析用户的需求。当用户提供招聘信息网页链接时，系统会自动解析招聘信息，并根据用户的需求给出匹配度评分和推荐建议。



## 功能特点

- 自动解析多个招聘网站的职位信息，给出网址即可
- 智能分析用户需求和职位要求
- 提供匹配度评分和详细的匹配原因


## 项目结构

项目源代码主要包含以下几个部分：

#### 网页解析模块
- `WebParser`（抽象类）
  - 定义网页解析的基本接口
  - 提供通用的解析方法
- `LinkedInParser`（实现类）
  - 专门用于解析LinkedIn网站的招聘信息
  - 继承自WebParser

#### AI判断模块
- `AIJudger`
  - 负责协调AI模型进行匹配度判断，AIModel会给出初步的判断结果，AIJudger会根据AIModel的结果给出最终的判断结果，比如AIModel给出的是一个分数，AIJudger会根据分数给出是否接受工作的决策。
  - 输入：用户需求文本和职位描述文本，支持批处理，输入为列表，输出为列表
  - 输出：包含decision（决策）、score（分数）、reason（原因）等信息的字典
- `AIModel`（抽象类）
  - 定义`judge`方法接口
  - 输入：用户需求文本和职位描述文本
  - 输出：包含decision（决策）、score（分数）、reason（原因）等信息的字典
- `BERTModel`（实现类）
  - 基于BERT的文本匹配模型实现
  - 使用transformers库中的BERT模型进行文本匹配，比较CLS token的输出向量和职位描述的CLS token的输出向量，计算余弦相似度，返回一个仅仅包含 score（分数）这一项信息的字典
  - 继承自AIModel
- `ChatGPTModel`（实现类）
  - 调用ChatGPT API进行匹配度判断，解析ChatGPT的返回结果，返回一个字典，包含decision（决策）、score（分数）、reason（原因）等信息的字典
  - 继承自AIModel

#### 主程序
- `JobMatchServer`
  - 系统入口类
  - 协调各模块工作
  - 类似于服务器的形式，等待用户输出请求，输入一个处理一个，处理完之后返回结果

#### 架构

```sh
JobMatch/
├── src/
│   ├── parsers/                   # 网页解析模块
│   │   ├── __init__.py
│   │   ├── web_parser.py          # WebParser 抽象类
│   │   ├── linkedin_parser.py     # LinkedInParser 实现类
│   │   └── ...                    # 其他网站解析实现类
│   ├── ai/                        # AI判断模块
│   │   ├── __init__.py
│   │   ├── ai_judger.py           # AIJudger 类
│   │   ├── ai_model.py            # AIModel 抽象类
│   │   ├── bert_model.py          # BERTModel 实现类
│   │   ├── chatgpt_model.py       # ChatGPTModel 实现类
│   ├── main/                      # 主程序模块
│   │   ├── __init__.py
│   │   ├── job_match_server.py     # JobMatchServer 类
│   │   └── utils.py               # 辅助工具类，比如日志、格式化处理
├── config/                       
│   ├── config1.yaml               # 配置信息（用什么模型，API密钥等）
├── tests/                         # 单元测试和集成测试
│   ├── test_parsers.py            # 网页解析模块测试
│   ├── test_ai.py                 # AI判断模块测试
│   ├── test_job_match.py          # 主程序测试
├── requirements.txt               # 项目依赖包
├── README.md                      # 项目说明文档
└── .env                           # 配置文件（如API密钥）
```



## 使用方法

[待补充]

## 开发环境

[待补充]

## 安装说明

[待补充]


# AI-Powered Cold Outreach Tool

一个基于AI的智能冷邮件生成工具，能够从职位页面提取信息，解析简历，并生成个性化的冷邮件。

## 功能特性

- 🔍 **智能职位信息提取**: 从公司招聘页面自动提取职位详情
- 📄 **简历解析**: 支持PDF和Word格式简历，自动提取技能和项目经验
- 🤖 **AI驱动邮件生成**: 使用RAG技术生成个性化冷邮件
- 🎯 **精准匹配**: 将简历技能与职位要求智能匹配
- 💼 **专业模板**: 生成简洁、专业的冷邮件内容

## 技术架构

- **前端**: Streamlit Web应用
- **AI模型**: OpenAI GPT-4 (通过LangChain)
- **RAG系统**: FAISS向量数据库 + LangChain检索
- **文档处理**: PyPDF2, python-docx
- **网页抓取**: BeautifulSoup4

## 安装说明

### 1. 克隆项目
```bash
git clone <your-repo-url>
cd Cold_email
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 环境配置
创建 `.env` 文件并添加你的OpenAI API密钥：
```
OPENAI_API_KEY=your_openai_api_key_here
```

### 4. 运行应用
```bash
streamlit run app.py
```

## 使用指南

1. **输入职位URL**: 粘贴目标公司的招聘页面链接
2. **上传简历**: 选择PDF或Word格式的简历文件
3. **提取信息**: 系统自动提取职位详情和简历信息
4. **生成邮件**: 点击生成按钮，获得个性化冷邮件

## 项目结构

```
Cold_email/
├── app.py                 # 主应用文件
├── job_extractor.py       # 职位信息提取模块
├── resume_parser.py       # 简历解析模块
├── email_generator.py     # 邮件生成模块
├── rag_system.py         # RAG系统
├── utils.py              # 工具函数
├── requirements.txt      # 项目依赖
├── .env                  # 环境变量
└── README.md            # 项目说明
```

## 核心模块说明

### Job Extractor
- 使用BeautifulSoup4抓取网页内容
- 智能提取职位标题、描述、要求等信息
- 支持多种招聘网站格式

### Resume Parser
- 支持PDF和Word文档解析
- 提取技能、工作经验、教育背景
- 智能识别关键信息

### RAG System
- 使用FAISS进行向量检索
- 结合职位信息和简历内容
- 提供上下文相关的信息增强

### Email Generator
- 基于GPT-4的邮件生成
- 个性化提示工程
- 确保邮件简洁专业

## 评估标准

- ✅ **个性化程度**: 邮件与职位的高度匹配
- ✅ **RAG效果**: 有效的信息检索和整合
- ✅ **提示工程**: 优化的AI提示设计
- ✅ **用户体验**: 流畅的Web界面
- ✅ **代码质量**: 清晰、可维护的代码结构

## 注意事项

- 确保有有效的OpenAI API密钥
- 简历文件大小建议不超过10MB
- 支持主流招聘网站（LinkedIn, Indeed等）
- 生成的邮件仅供参考，建议人工审核

## 许可证

MIT License

## 贡献

欢迎提交Issue和Pull Request来改进这个项目！ 
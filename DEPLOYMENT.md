# 部署指南

## 本地部署

### 1. 环境准备

确保你的系统已安装：
- Python 3.8+
- pip

### 2. 克隆项目

```bash
git clone <your-repo-url>
cd Cold_email
```

### 3. 安装依赖

```bash
pip install -r requirements.txt
```

### 4. 配置环境变量

复制环境变量示例文件：
```bash
cp env_example.txt .env
```

编辑 `.env` 文件，添加你的OpenAI API密钥：
```
OPENAI_API_KEY=your_actual_openai_api_key_here
```

### 5. 运行应用

```bash
streamlit run app.py
```

应用将在 `http://localhost:8501` 启动。

## 云部署

### Streamlit Cloud 部署

1. **准备代码**
   - 确保所有文件都已提交到GitHub
   - 检查 `requirements.txt` 是否完整

2. **部署步骤**
   - 访问 [share.streamlit.io](https://share.streamlit.io)
   - 使用GitHub账号登录
   - 选择你的仓库
   - 设置部署配置：
     - Main file path: `app.py`
     - Python version: 3.8+
   - 添加环境变量：
     - `OPENAI_API_KEY`: 你的OpenAI API密钥

3. **部署完成**
   - 应用将获得一个公开的URL
   - 可以分享给其他人使用

### Heroku 部署

1. **创建 Procfile**
   ```
   web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0
   ```

2. **创建 runtime.txt**
   ```
   python-3.9.16
   ```

3. **部署命令**
   ```bash
   heroku create your-app-name
   heroku config:set OPENAI_API_KEY=your_api_key
   git push heroku main
   ```

### Docker 部署

1. **创建 Dockerfile**
   ```dockerfile
   FROM python:3.9-slim
   
   WORKDIR /app
   
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   
   COPY . .
   
   EXPOSE 8501
   
   CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
   ```

2. **构建和运行**
   ```bash
   docker build -t cold-email-app .
   docker run -p 8501:8501 -e OPENAI_API_KEY=your_key cold-email-app
   ```

## 环境变量配置

### 必需变量

- `OPENAI_API_KEY`: OpenAI API密钥

### 可选变量

- `STREAMLIT_SERVER_PORT`: 服务器端口（默认8501）
- `STREAMLIT_SERVER_ADDRESS`: 服务器地址（默认localhost）

## 故障排除

### 常见问题

1. **OpenAI API密钥错误**
   - 确保API密钥正确
   - 检查账户余额是否充足

2. **依赖安装失败**
   - 尝试升级pip: `pip install --upgrade pip`
   - 使用虚拟环境: `python -m venv venv`

3. **端口被占用**
   - 更改端口: `streamlit run app.py --server.port=8502`

4. **内存不足**
   - 减少并发用户数
   - 优化代码性能

### 性能优化

1. **缓存优化**
   - 使用Streamlit缓存装饰器
   - 避免重复计算

2. **API调用优化**
   - 批量处理请求
   - 实现请求限流

3. **资源管理**
   - 定期清理临时文件
   - 监控内存使用

## 安全注意事项

1. **API密钥安全**
   - 不要在代码中硬编码API密钥
   - 使用环境变量或密钥管理服务

2. **文件上传安全**
   - 验证文件类型和大小
   - 扫描恶意文件

3. **数据隐私**
   - 不存储用户敏感信息
   - 实现数据清理机制

## 监控和维护

1. **日志记录**
   - 记录错误和异常
   - 监控API调用次数

2. **性能监控**
   - 监控响应时间
   - 跟踪资源使用

3. **定期更新**
   - 更新依赖包
   - 检查安全漏洞 
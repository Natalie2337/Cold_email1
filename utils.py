"""
工具函数模块
包含通用的辅助函数和常量
"""

import re
import os
from typing import List, Dict, Any
from urllib.parse import urlparse
import streamlit as st

# 常量定义
SUPPORTED_FILE_TYPES = ['.pdf', '.docx', '.doc']
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

def validate_url(url: str) -> bool:
    """
    验证URL格式是否有效
    
    Args:
        url: 要验证的URL字符串
        
    Returns:
        bool: URL是否有效
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

def clean_text(text: str) -> str:
    """
    清理文本内容，移除多余的空白字符
    
    Args:
        text: 原始文本
        
    Returns:
        str: 清理后的文本
    """
    if not text:
        return ""
    
    # 移除多余的空白字符
    text = re.sub(r'\s+', ' ', text)
    # 移除特殊字符
    text = re.sub(r'[^\w\s\.\,\!\?\:\;\-\(\)]', '', text)
    return text.strip()

def extract_skills_from_text(text: str) -> List[str]:
    """
    从文本中提取技能关键词
    
    Args:
        text: 输入文本
        
    Returns:
        List[str]: 提取的技能列表
    """
    # 常见技能关键词
    skill_keywords = [
        'python', 'java', 'javascript', 'react', 'angular', 'vue', 'node.js',
        'sql', 'mongodb', 'postgresql', 'mysql', 'aws', 'azure', 'gcp',
        'docker', 'kubernetes', 'git', 'machine learning', 'ai', 'deep learning',
        'tensorflow', 'pytorch', 'scikit-learn', 'pandas', 'numpy', 'matplotlib',
        'html', 'css', 'bootstrap', 'jquery', 'django', 'flask', 'fastapi',
        'spring', 'hibernate', 'maven', 'gradle', 'jenkins', 'ci/cd',
        'agile', 'scrum', 'jira', 'confluence', 'rest api', 'graphql',
        'microservices', 'serverless', 'lambda', 's3', 'ec2', 'rds'
    ]
    
    text_lower = text.lower()
    found_skills = []
    
    for skill in skill_keywords:
        if skill in text_lower:
            found_skills.append(skill)
    
    return list(set(found_skills))

def format_experience_years(text: str) -> str:
    """
    格式化工作经验年限
    
    Args:
        text: 包含年限信息的文本
        
    Returns:
        str: 格式化的年限信息
    """
    # 匹配年限模式
    patterns = [
        r'(\d+)\+?\s*years?',
        r'(\d+)\+?\s*yr',
        r'(\d+)\+?\s*年'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            years = match.group(1)
            return f"{years} years"
    
    return "Not specified"

def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件扩展名（小写）
    """
    return os.path.splitext(filename)[1].lower()

def validate_file_upload(uploaded_file) -> Dict[str, Any]:
    """
    验证上传的文件
    
    Args:
        uploaded_file: Streamlit上传的文件对象
        
    Returns:
        Dict[str, Any]: 验证结果
    """
    if uploaded_file is None:
        return {"valid": False, "error": "请选择文件"}
    
    # 检查文件类型
    file_extension = get_file_extension(uploaded_file.name)
    if file_extension not in SUPPORTED_FILE_TYPES:
        return {
            "valid": False, 
            "error": f"不支持的文件类型。支持的类型: {', '.join(SUPPORTED_FILE_TYPES)}"
        }
    
    # 检查文件大小
    if uploaded_file.size > MAX_FILE_SIZE:
        return {
            "valid": False, 
            "error": f"文件大小超过限制。最大允许: {MAX_FILE_SIZE // (1024*1024)}MB"
        }
    
    return {"valid": True, "error": None}

def create_session_state():
    """
    初始化Streamlit会话状态
    """
    if 'job_data' not in st.session_state:
        st.session_state.job_data = None
    if 'resume_data' not in st.session_state:
        st.session_state.resume_data = None
    if 'generated_email' not in st.session_state:
        st.session_state.generated_email = None

def display_error(error_message: str):
    """
    显示错误信息
    
    Args:
        error_message: 错误信息
    """
    st.error(f"❌ {error_message}")

def display_success(message: str):
    """
    显示成功信息
    
    Args:
        message: 成功信息
    """
    st.success(f"✅ {message}")

def display_info(message: str):
    """
    显示信息
    
    Args:
        message: 信息内容
    """
    st.info(f"ℹ️ {message}")

def truncate_text(text: str, max_length: int = 200) -> str:
    """
    截断文本到指定长度
    
    Args:
        text: 原始文本
        max_length: 最大长度
        
    Returns:
        str: 截断后的文本
    """
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def extract_company_name_from_url(url: str) -> str:
    """
    从URL中提取公司名称
    
    Args:
        url: 公司网站URL
        
    Returns:
        str: 公司名称
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # 移除常见的前缀和后缀
        domain = domain.replace('www.', '').replace('.com', '').replace('.org', '')
        
        # 处理常见的招聘网站
        if 'linkedin.com' in domain:
            return "LinkedIn"
        elif 'indeed.com' in domain:
            return "Indeed"
        elif 'glassdoor.com' in domain:
            return "Glassdoor"
        else:
            # 提取主域名作为公司名
            return domain.split('.')[0].title()
    except:
        return "Unknown Company" 
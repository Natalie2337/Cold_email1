"""
测试脚本
用于验证各个模块的功能
"""

import os
from dotenv import load_dotenv
from job_extractor import JobExtractor
from resume_parser import ResumeParser
from email_generator import EmailGenerator
from utils import validate_url, clean_text

# 加载环境变量
load_dotenv()

def test_job_extractor():
    """测试职位信息提取"""
    print("🧪 测试职位信息提取...")
    
    extractor = JobExtractor()
    
    # 测试URL验证
    test_urls = [
        "https://www.linkedin.com/jobs/view/123456",
        "https://indeed.com/viewjob?jk=123456",
        "invalid-url",
        ""
    ]
    
    for url in test_urls:
        is_valid = validate_url(url)
        print(f"URL: {url} -> Valid: {is_valid}")
    
    print("✅ 职位信息提取测试完成\n")

def test_resume_parser():
    """测试简历解析"""
    print("🧪 测试简历解析...")
    
    parser = ResumeParser()
    
    # 测试文本清理
    test_texts = [
        "  Hello   World  ",
        "Python, Java, JavaScript",
        "Software Engineer with 5+ years experience",
        ""
    ]
    
    for text in test_texts:
        cleaned = clean_text(text)
        print(f"Original: '{text}' -> Cleaned: '{cleaned}'")
    
    print("✅ 简历解析测试完成\n")

def test_email_generator():
    """测试邮件生成"""
    print("🧪 测试邮件生成...")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("⚠️ 未找到OpenAI API密钥，跳过邮件生成测试")
        return
    
    generator = EmailGenerator(api_key)
    
    # 模拟数据
    job_data = {
        'title': 'Software Engineer',
        'company': 'Tech Corp',
        'location': 'San Francisco, CA',
        'description': 'We are looking for a skilled software engineer...',
        'requirements': 'Python, JavaScript, 3+ years experience',
        'skills': ['python', 'javascript', 'react', 'sql'],
        'experience_level': 'Mid',
        'employment_type': 'Full-time'
    }
    
    resume_data = {
        'name': 'John Doe',
        'email': 'john.doe@email.com',
        'summary': 'Experienced software engineer with 4 years of experience',
        'skills': ['python', 'javascript', 'react', 'node.js', 'mongodb'],
        'experience': [
            {
                'title': 'Software Engineer',
                'company': 'Previous Corp',
                'period': '2020-2023',
                'description': 'Developed web applications using React and Node.js'
            }
        ]
    }
    
    try:
        # 测试技能匹配
        skill_matches = generator.rag_system.get_skill_matches(
            job_data['skills'], resume_data['skills']
        )
        print(f"技能匹配结果: {skill_matches}")
        
        print("✅ 邮件生成测试完成\n")
        
    except Exception as e:
        print(f"❌ 邮件生成测试失败: {str(e)}\n")

def test_utils():
    """测试工具函数"""
    print("🧪 测试工具函数...")
    
    # 测试技能提取
    test_text = "I have experience with Python, JavaScript, React, and SQL databases"
    from utils import extract_skills_from_text
    skills = extract_skills_from_text(test_text)
    print(f"提取的技能: {skills}")
    
    # 测试经验年限格式化
    from utils import format_experience_years
    test_experience = "5+ years of experience"
    formatted = format_experience_years(test_experience)
    print(f"经验年限: {formatted}")
    
    print("✅ 工具函数测试完成\n")

def main():
    """主测试函数"""
    print("🚀 开始运行测试...\n")
    
    test_utils()
    test_job_extractor()
    test_resume_parser()
    test_email_generator()
    
    print("🎉 所有测试完成！")

if __name__ == "__main__":
    main() 
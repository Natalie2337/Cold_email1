"""
AI驱动的冷邮件生成工具
主应用文件
"""

import streamlit as st
import os
from dotenv import load_dotenv
from job_extractor import JobExtractor
from resume_parser import ResumeParser
from email_generator import EmailGenerator
from utils import (
    validate_url, validate_file_upload, create_session_state,
    display_error, display_success, display_info, truncate_text
)

# 加载环境变量
load_dotenv()

# 页面配置
st.set_page_config(
    page_title="AI冷邮件生成器",
    page_icon="📧",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS样式
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #2c3e50;
        margin-bottom: 1rem;
    }
    .info-box {
        background-color: #f8f9fa;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    """主函数"""
    # 初始化会话状态
    create_session_state()
    
    # 页面标题
    st.markdown('<h1 class="main-header">🤖 AI驱动的冷邮件生成器</h1>', unsafe_allow_html=True)
    
    # 侧边栏配置
    with st.sidebar:
        st.header("⚙️ 配置")
        
        # API密钥输入
        api_key = st.text_input(
            "OpenAI API密钥",
            type="password",
            help="请输入你的OpenAI API密钥"
        )
        
        if not api_key:
            api_key = os.getenv("OPENAI_API_KEY")
        
        if not api_key:
            st.error("⚠️ 请提供OpenAI API密钥")
            st.info("💡 你可以在.env文件中设置OPENAI_API_KEY，或在侧边栏输入")
            return
        
        # 邮件风格选择
        email_style = st.selectbox(
            "邮件风格",
            ["professional", "casual", "enthusiastic"],
            format_func=lambda x: {
                "professional": "专业正式",
                "casual": "友好轻松",
                "enthusiastic": "充满激情"
            }[x]
        )
        
        # 生成多个版本选项
        generate_multiple = st.checkbox("生成多个版本", value=False)
        
        st.markdown("---")
        st.markdown("### 📊 使用统计")
        if 'generated_emails' not in st.session_state:
            st.session_state.generated_emails = 0
        st.metric("已生成邮件", st.session_state.generated_emails)
    
    # 主界面
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown('<h2 class="sub-header">📋 输入信息</h2>', unsafe_allow_html=True)
        
        # 职位URL输入
        job_url = st.text_input(
            "职位页面URL",
            placeholder="https://www.linkedin.com/jobs/view/...",
            help="请输入招聘页面的完整URL"
        )
        
        # 简历上传
        uploaded_resume = st.file_uploader(
            "上传简历",
            type=['pdf', 'docx', 'doc'],
            help="支持PDF和Word格式，最大10MB"
        )
        
        # 处理按钮
        if st.button("🚀 开始处理", type="primary", use_container_width=True):
            if not job_url or not uploaded_resume:
                display_error("请提供职位URL和简历文件")
                return
            
            if not validate_url(job_url):
                display_error("请输入有效的URL")
                return
            
            # 验证文件
            file_validation = validate_file_upload(uploaded_resume)
            if not file_validation["valid"]:
                display_error(file_validation["error"])
                return
            
            # 开始处理
            with st.spinner("正在处理..."):
                try:
                    # 提取职位信息
                    job_extractor = JobExtractor()
                    job_data = job_extractor.extract_job_info(job_url)
                    st.session_state.job_data = job_data
                    
                    # 解析简历
                    resume_parser = ResumeParser()
                    resume_data = resume_parser.parse_resume(uploaded_resume)
                    st.session_state.resume_data = resume_data
                    
                    display_success("信息提取完成！")
                    
                except Exception as e:
                    display_error(f"处理失败: {str(e)}")
                    return
    
    with col2:
        st.markdown('<h2 class="sub-header">📊 提取结果</h2>', unsafe_allow_html=True)
        
        # 显示职位信息
        if st.session_state.job_data:
            with st.expander("📋 职位信息", expanded=True):
                job_data = st.session_state.job_data
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("职位", job_data.get('title', 'N/A'))
                    st.metric("公司", job_data.get('company', 'N/A'))
                    st.metric("地点", job_data.get('location', 'N/A'))
                
                with col_b:
                    st.metric("经验要求", job_data.get('experience_level', 'N/A'))
                    st.metric("雇佣类型", job_data.get('employment_type', 'N/A'))
                    st.metric("技能数量", len(job_data.get('skills', [])))
                
                if job_data.get('skills'):
                    st.write("**所需技能:**")
                    st.write(", ".join(job_data['skills'][:10]))
        
        # 显示简历信息
        if st.session_state.resume_data:
            with st.expander("👤 简历信息", expanded=True):
                resume_data = st.session_state.resume_data
                
                col_a, col_b = st.columns(2)
                with col_a:
                    st.metric("姓名", resume_data.get('name', 'N/A'))
                    st.metric("邮箱", resume_data.get('email', 'N/A'))
                    st.metric("工作经验", len(resume_data.get('experience', [])))
                
                with col_b:
                    st.metric("教育背景", len(resume_data.get('education', [])))
                    st.metric("项目经验", len(resume_data.get('projects', [])))
                    st.metric("技能数量", len(resume_data.get('skills', [])))
                
                if resume_data.get('skills'):
                    st.write("**技能:**")
                    st.write(", ".join(resume_data['skills'][:10]))
    
    # 邮件生成部分
    if st.session_state.job_data and st.session_state.resume_data:
        st.markdown("---")
        st.markdown('<h2 class="sub-header">📧 生成邮件</h2>', unsafe_allow_html=True)
        
        # 技能匹配分析
        if st.session_state.job_data.get('skills') and st.session_state.resume_data.get('skills'):
            job_skills = st.session_state.job_data['skills']
            resume_skills = st.session_state.resume_data['skills']
            
            # 计算匹配度
            matched_skills = set(job_skills) & set(resume_skills)
            match_percentage = (len(matched_skills) / len(job_skills)) * 100 if job_skills else 0
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("技能匹配度", f"{match_percentage:.1f}%")
            with col2:
                st.metric("匹配技能", len(matched_skills))
            with col3:
                st.metric("缺失技能", len(job_skills) - len(matched_skills))
            
            if matched_skills:
                st.info(f"✅ 匹配技能: {', '.join(list(matched_skills)[:5])}")
        
        # 生成邮件按钮
        if st.button("✨ 生成个性化邮件", type="primary", use_container_width=True):
            with st.spinner("正在生成邮件..."):
                try:
                    email_generator = EmailGenerator(api_key)
                    
                    if generate_multiple:
                        # 生成多个版本
                        email_versions = email_generator.generate_multiple_versions(
                            st.session_state.job_data,
                            st.session_state.resume_data
                        )
                        st.session_state.generated_email = email_versions
                    else:
                        # 生成单个版本
                        email_result = email_generator.generate_cold_email(
                            st.session_state.job_data,
                            st.session_state.resume_data,
                            email_style
                        )
                        st.session_state.generated_email = [email_result]
                    
                    st.session_state.generated_emails += 1
                    display_success("邮件生成完成！")
                    
                except Exception as e:
                    display_error(f"邮件生成失败: {str(e)}")
        
        # 显示生成的邮件
        if st.session_state.generated_email:
            st.markdown("---")
            st.markdown('<h2 class="sub-header">📨 生成的邮件</h2>', unsafe_allow_html=True)
            
            for i, email_data in enumerate(st.session_state.generated_email):
                with st.expander(f"邮件版本 {i+1} ({email_data.get('style_name', email_style)})", expanded=True):
                    # 邮件主题
                    st.markdown(f"**主题:** {email_data['subject']}")
                    
                    # 邮件内容
                    st.markdown("**内容:**")
                    st.text_area(
                        "邮件正文",
                        value=email_data['content'],
                        height=300,
                        key=f"email_content_{i}"
                    )
                    
                    # 复制按钮
                    if st.button(f"📋 复制邮件 {i+1}", key=f"copy_{i}"):
                        st.write("邮件已复制到剪贴板")
                    
                    # 上下文信息
                    if email_data.get('context_info'):
                        with st.expander("📊 匹配详情"):
                            context = email_data['context_info']
                            if context.get('skill_matches'):
                                matches = context['skill_matches']
                                st.metric("技能匹配度", f"{matches['match_percentage']}%")
                                if matches['matched_skills']:
                                    st.write("**匹配技能:**", ", ".join(matches['matched_skills']))
                                if matches['missing_skills']:
                                    st.write("**缺失技能:**", ", ".join(matches['missing_skills']))
    
    # 页脚
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🤖 AI驱动的冷邮件生成器 | 让求职更智能</p>
        <p>💡 提示：生成的邮件仅供参考，建议根据实际情况进行调整</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 
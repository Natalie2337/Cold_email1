"""
简历解析模块
支持PDF和Word格式的简历解析
"""

import PyPDF2
from docx import Document
import re
from typing import Dict, Any, List
from utils import clean_text, extract_skills_from_text, get_file_extension

class ResumeParser:
    """简历解析器"""
    
    def __init__(self):
        self.section_keywords = {
            'education': ['education', 'academic', 'degree', 'university', 'college', 'school'],
            'experience': ['experience', 'work history', 'employment', 'career', 'job'],
            'skills': ['skills', 'technical skills', 'competencies', 'technologies'],
            'projects': ['projects', 'portfolio', 'achievements', 'accomplishments'],
            'contact': ['contact', 'email', 'phone', 'address', 'linkedin']
        }
    
    def parse_resume(self, uploaded_file) -> Dict[str, Any]:
        """
        解析简历文件
        
        Args:
            uploaded_file: Streamlit上传的文件对象
            
        Returns:
            Dict[str, Any]: 解析后的简历信息
        """
        try:
            file_extension = get_file_extension(uploaded_file.name)
            
            if file_extension == '.pdf':
                text = self._extract_text_from_pdf(uploaded_file)
            elif file_extension in ['.docx', '.doc']:
                text = self._extract_text_from_docx(uploaded_file)
            else:
                raise ValueError(f"不支持的文件格式: {file_extension}")
            
            # 解析简历内容
            resume_data = self._parse_resume_text(text)
            resume_data['filename'] = uploaded_file.name
            resume_data['file_size'] = uploaded_file.size
            
            return resume_data
            
        except Exception as e:
            raise Exception(f"解析简历失败: {str(e)}")
    
    def _extract_text_from_pdf(self, uploaded_file) -> str:
        """从PDF文件提取文本"""
        try:
            pdf_reader = PyPDF2.PdfReader(uploaded_file)
            text = ""
            
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"PDF文本提取失败: {str(e)}")
    
    def _extract_text_from_docx(self, uploaded_file) -> str:
        """从Word文档提取文本"""
        try:
            doc = Document(uploaded_file)
            text = ""
            
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            
            return text
        except Exception as e:
            raise Exception(f"Word文档文本提取失败: {str(e)}")
    
    def _parse_resume_text(self, text: str) -> Dict[str, Any]:
        """
        解析简历文本内容
        
        Args:
            text: 简历文本内容
            
        Returns:
            Dict[str, Any]: 解析后的简历信息
        """
        # 清理文本
        text = clean_text(text)
        
        # 提取各个部分
        sections = self._extract_sections(text)
        
        # 构建简历数据结构
        resume_data = {
            'name': self._extract_name(text),
            'email': self._extract_email(text),
            'phone': self._extract_phone(text),
            'linkedin': self._extract_linkedin(text),
            'summary': self._extract_summary(text),
            'education': self._extract_education(sections.get('education', '')),
            'experience': self._extract_experience(sections.get('experience', '')),
            'skills': self._extract_skills(text),
            'projects': self._extract_projects(sections.get('projects', '')),
            'raw_text': text
        }
        
        return resume_data
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """提取简历的各个部分"""
        sections = {}
        lines = text.split('\n')
        
        current_section = 'general'
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的部分标题
            section_found = False
            for section_name, keywords in self.section_keywords.items():
                if any(keyword.lower() in line.lower() for keyword in keywords):
                    if current_section != 'general':
                        sections[current_section] = '\n'.join(current_content)
                    current_section = section_name
                    current_content = []
                    section_found = True
                    break
            
            if not section_found:
                current_content.append(line)
        
        # 添加最后一个部分
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def _extract_name(self, text: str) -> str:
        """提取姓名"""
        # 查找常见的姓名模式
        lines = text.split('\n')
        for line in lines[:5]:  # 通常姓名在前几行
            line = line.strip()
            if len(line) > 2 and len(line) < 50:
                # 检查是否包含常见的姓名模式
                if re.match(r'^[A-Z][a-z]+ [A-Z][a-z]+', line):
                    return line
                elif re.match(r'^[A-Z][a-z]+', line) and ' ' in line:
                    return line
        
        return "姓名未找到"
    
    def _extract_email(self, text: str) -> str:
        """提取邮箱地址"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return emails[0] if emails else "邮箱未找到"
    
    def _extract_phone(self, text: str) -> str:
        """提取电话号码"""
        phone_patterns = [
            r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',  # 美国格式
            r'\b\d{4}[-.]?\d{4}[-.]?\d{4}\b',  # 中国格式
            r'\+\d{1,3}[-.]?\d{1,4}[-.]?\d{1,4}[-.]?\d{1,4}\b'  # 国际格式
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                return phones[0]
        
        return "电话未找到"
    
    def _extract_linkedin(self, text: str) -> str:
        """提取LinkedIn链接"""
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+'
        linkedin_urls = re.findall(linkedin_pattern, text)
        return linkedin_urls[0] if linkedin_urls else "LinkedIn未找到"
    
    def _extract_summary(self, text: str) -> str:
        """提取个人总结"""
        # 查找常见的总结关键词
        summary_keywords = ['summary', 'objective', 'profile', 'about']
        lines = text.split('\n')
        
        for i, line in enumerate(lines):
            line_lower = line.lower()
            if any(keyword in line_lower for keyword in summary_keywords):
                # 提取接下来的几行作为总结
                summary_lines = []
                for j in range(i + 1, min(i + 5, len(lines))):
                    if lines[j].strip() and len(lines[j].strip()) > 10:
                        summary_lines.append(lines[j].strip())
                    else:
                        break
                if summary_lines:
                    return ' '.join(summary_lines)
        
        return "个人总结未找到"
    
    def _extract_education(self, education_text: str) -> List[Dict[str, str]]:
        """提取教育背景"""
        if not education_text:
            return []
        
        education_list = []
        lines = education_text.split('\n')
        
        current_education = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的教育条目
            if re.search(r'\b(University|College|School|Institute|Academy)\b', line, re.IGNORECASE):
                if current_education:
                    education_list.append(current_education)
                current_education = {'institution': line}
            elif 'degree' in line.lower() or 'bachelor' in line.lower() or 'master' in line.lower():
                current_education['degree'] = line
            elif re.search(r'\b(20\d{2}|19\d{2})\b', line):  # 年份
                current_education['year'] = line
            elif 'gpa' in line.lower():
                current_education['gpa'] = line
        
        if current_education:
            education_list.append(current_education)
        
        return education_list
    
    def _extract_experience(self, experience_text: str) -> List[Dict[str, str]]:
        """提取工作经验"""
        if not experience_text:
            return []
        
        experience_list = []
        lines = experience_text.split('\n')
        
        current_experience = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的工作条目
            if re.search(r'\b(20\d{2}|19\d{2})\b.*\b(20\d{2}|19\d{2}|Present|Current)\b', line):
                if current_experience:
                    experience_list.append(current_experience)
                current_experience = {'period': line}
            elif any(keyword in line.lower() for keyword in ['engineer', 'developer', 'manager', 'analyst', 'specialist']):
                if 'title' not in current_experience:
                    current_experience['title'] = line
            elif '@' in line or 'www.' in line:
                if 'company' not in current_experience:
                    current_experience['company'] = line
            elif len(line) > 20 and not re.search(r'\b(20\d{2}|19\d{2})\b', line):
                if 'description' not in current_experience:
                    current_experience['description'] = line
                else:
                    current_experience['description'] += ' ' + line
        
        if current_experience:
            experience_list.append(current_experience)
        
        return experience_list
    
    def _extract_skills(self, text: str) -> List[str]:
        """提取技能"""
        return extract_skills_from_text(text)
    
    def _extract_projects(self, projects_text: str) -> List[Dict[str, str]]:
        """提取项目经验"""
        if not projects_text:
            return []
        
        projects_list = []
        lines = projects_text.split('\n')
        
        current_project = {}
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 检查是否是新的项目条目
            if re.search(r'\b(Project|App|System|Platform|Tool)\b', line, re.IGNORECASE):
                if current_project:
                    projects_list.append(current_project)
                current_project = {'name': line}
            elif 'github.com' in line or 'gitlab.com' in line:
                current_project['repository'] = line
            elif len(line) > 20:
                if 'description' not in current_project:
                    current_project['description'] = line
                else:
                    current_project['description'] += ' ' + line
        
        if current_project:
            projects_list.append(current_project)
        
        return projects_list
    
    def get_resume_summary(self, resume_data: Dict[str, Any]) -> str:
        """
        生成简历摘要
        
        Args:
            resume_data: 简历数据字典
            
        Returns:
            str: 简历摘要
        """
        summary_parts = []
        
        if resume_data['name']:
            summary_parts.append(f"姓名: {resume_data['name']}")
        
        if resume_data['email']:
            summary_parts.append(f"邮箱: {resume_data['email']}")
        
        if resume_data['skills']:
            summary_parts.append(f"技能: {', '.join(resume_data['skills'][:5])}")
        
        if resume_data['experience']:
            summary_parts.append(f"工作经验: {len(resume_data['experience'])} 项")
        
        if resume_data['education']:
            summary_parts.append(f"教育背景: {len(resume_data['education'])} 项")
        
        return " | ".join(summary_parts) 
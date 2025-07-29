"""
RAG系统模块
用于信息检索和增强生成
"""

import os
from typing import List, Dict, Any
import tiktoken
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.schema import Document
from langchain.chains import RetrievalQA
from langchain_community.llms import OpenAI
import numpy as np

class RAGSystem:
    """RAG系统类"""
    
    def __init__(self, openai_api_key: str):
        """
        初始化RAG系统
        
        Args:
            openai_api_key: OpenAI API密钥
        """
        self.openai_api_key = openai_api_key
        os.environ["OPENAI_API_KEY"] = openai_api_key
        
        # 初始化组件
        self.embeddings = OpenAIEmbeddings()
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
        )
        self.vector_store = None
        
    def create_knowledge_base(self, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> None:
        """
        创建知识库
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
        """
        # 准备文档
        documents = self._prepare_documents(job_data, resume_data)
        
        # 分割文档
        texts = self.text_splitter.split_documents(documents)
        
        # 创建向量存储
        self.vector_store = FAISS.from_documents(texts, self.embeddings)
        
    def _prepare_documents(self, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> List[Document]:
        """
        准备文档数据
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            
        Returns:
            List[Document]: 文档列表
        """
        documents = []
        
        # 职位信息文档
        job_content = self._format_job_content(job_data)
        documents.append(Document(
            page_content=job_content,
            metadata={"source": "job_posting", "type": "job"}
        ))
        
        # 简历信息文档
        resume_content = self._format_resume_content(resume_data)
        documents.append(Document(
            page_content=resume_content,
            metadata={"source": "resume", "type": "candidate"}
        ))
        
        return documents
    
    def _format_job_content(self, job_data: Dict[str, Any]) -> str:
        """
        格式化职位内容
        
        Args:
            job_data: 职位信息
            
        Returns:
            str: 格式化的职位内容
        """
        content_parts = []
        
        if job_data.get('title'):
            content_parts.append(f"Job Title: {job_data['title']}")
        
        if job_data.get('company'):
            content_parts.append(f"Company: {job_data['company']}")
        
        if job_data.get('location'):
            content_parts.append(f"Location: {job_data['location']}")
        
        if job_data.get('description'):
            content_parts.append(f"Job Description: {job_data['description']}")
        
        if job_data.get('requirements'):
            content_parts.append(f"Requirements: {job_data['requirements']}")
        
        if job_data.get('responsibilities'):
            content_parts.append(f"Responsibilities: {job_data['responsibilities']}")
        
        if job_data.get('skills'):
            content_parts.append(f"Required Skills: {', '.join(job_data['skills'])}")
        
        if job_data.get('experience_level'):
            content_parts.append(f"Experience Level: {job_data['experience_level']}")
        
        if job_data.get('employment_type'):
            content_parts.append(f"Employment Type: {job_data['employment_type']}")
        
        return "\n\n".join(content_parts)
    
    def _format_resume_content(self, resume_data: Dict[str, Any]) -> str:
        """
        格式化简历内容
        
        Args:
            resume_data: 简历信息
            
        Returns:
            str: 格式化的简历内容
        """
        content_parts = []
        
        if resume_data.get('name'):
            content_parts.append(f"Candidate Name: {resume_data['name']}")
        
        if resume_data.get('summary'):
            content_parts.append(f"Professional Summary: {resume_data['summary']}")
        
        if resume_data.get('skills'):
            content_parts.append(f"Skills: {', '.join(resume_data['skills'])}")
        
        if resume_data.get('experience'):
            content_parts.append("Work Experience:")
            for exp in resume_data['experience']:
                exp_text = []
                if exp.get('title'):
                    exp_text.append(f"Title: {exp['title']}")
                if exp.get('company'):
                    exp_text.append(f"Company: {exp['company']}")
                if exp.get('period'):
                    exp_text.append(f"Period: {exp['period']}")
                if exp.get('description'):
                    exp_text.append(f"Description: {exp['description']}")
                content_parts.append(" - ".join(exp_text))
        
        if resume_data.get('education'):
            content_parts.append("Education:")
            for edu in resume_data['education']:
                edu_text = []
                if edu.get('institution'):
                    edu_text.append(f"Institution: {edu['institution']}")
                if edu.get('degree'):
                    edu_text.append(f"Degree: {edu['degree']}")
                if edu.get('year'):
                    edu_text.append(f"Year: {edu['year']}")
                content_parts.append(" - ".join(edu_text))
        
        if resume_data.get('projects'):
            content_parts.append("Projects:")
            for project in resume_data['projects']:
                proj_text = []
                if project.get('name'):
                    proj_text.append(f"Name: {project['name']}")
                if project.get('description'):
                    proj_text.append(f"Description: {project['description']}")
                if project.get('repository'):
                    proj_text.append(f"Repository: {project['repository']}")
                content_parts.append(" - ".join(proj_text))
        
        return "\n\n".join(content_parts)
    
    def retrieve_relevant_info(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        """
        检索相关信息
        
        Args:
            query: 查询内容
            k: 返回的文档数量
            
        Returns:
            List[Dict[str, Any]]: 相关文档列表
        """
        if not self.vector_store:
            return []
        
        # 执行相似性搜索
        docs = self.vector_store.similarity_search(query, k=k)
        
        # 格式化结果
        results = []
        for doc in docs:
            results.append({
                'content': doc.page_content,
                'metadata': doc.metadata,
                'score': self._calculate_relevance_score(query, doc.page_content)
            })
        
        return results
    
    def _calculate_relevance_score(self, query: str, content: str) -> float:
        """
        计算相关性分数
        
        Args:
            query: 查询内容
            content: 文档内容
            
        Returns:
            float: 相关性分数
        """
        # 简单的关键词匹配分数
        query_words = set(query.lower().split())
        content_words = set(content.lower().split())
        
        if not query_words:
            return 0.0
        
        intersection = query_words.intersection(content_words)
        return len(intersection) / len(query_words)
    
    def get_skill_matches(self, job_skills: List[str], resume_skills: List[str]) -> Dict[str, Any]:
        """
        获取技能匹配信息
        
        Args:
            job_skills: 职位要求的技能
            resume_skills: 简历中的技能
            
        Returns:
            Dict[str, Any]: 技能匹配信息
        """
        if not job_skills:
            return {
                'matched_skills': [],
                'missing_skills': [],
                'match_percentage': 0.0
            }
        
        # 标准化技能名称
        job_skills_normalized = [skill.lower().strip() for skill in job_skills]
        resume_skills_normalized = [skill.lower().strip() for skill in resume_skills]
        
        # 找到匹配的技能
        matched_skills = []
        for job_skill in job_skills_normalized:
            for resume_skill in resume_skills_normalized:
                if job_skill in resume_skill or resume_skill in job_skill:
                    matched_skills.append(job_skill)
                    break
        
        # 找到缺失的技能
        missing_skills = [skill for skill in job_skills_normalized if skill not in matched_skills]
        
        # 计算匹配百分比
        match_percentage = (len(matched_skills) / len(job_skills_normalized)) * 100
        
        return {
            'matched_skills': matched_skills,
            'missing_skills': missing_skills,
            'match_percentage': round(match_percentage, 2)
        }
    
    def generate_context_summary(self, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> str:
        """
        生成上下文摘要
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            
        Returns:
            str: 上下文摘要
        """
        summary_parts = []
        
        # 职位摘要
        if job_data.get('title') and job_data.get('company'):
            summary_parts.append(f"Position: {job_data['title']} at {job_data['company']}")
        
        if job_data.get('location'):
            summary_parts.append(f"Location: {job_data['location']}")
        
        if job_data.get('experience_level'):
            summary_parts.append(f"Experience Level: {job_data['experience_level']}")
        
        # 技能匹配信息
        job_skills = job_data.get('skills', [])
        resume_skills = resume_data.get('skills', [])
        skill_matches = self.get_skill_matches(job_skills, resume_skills)
        
        if skill_matches['matched_skills']:
            summary_parts.append(f"Matched Skills: {', '.join(skill_matches['matched_skills'])}")
        
        if skill_matches['match_percentage'] > 0:
            summary_parts.append(f"Skill Match: {skill_matches['match_percentage']}%")
        
        # 候选人信息
        if resume_data.get('name'):
            summary_parts.append(f"Candidate: {resume_data['name']}")
        
        if resume_data.get('experience'):
            summary_parts.append(f"Work Experience: {len(resume_data['experience'])} positions")
        
        return " | ".join(summary_parts)
    
    def get_relevant_experience(self, job_requirements: str, resume_experience: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        获取相关工作经验
        
        Args:
            job_requirements: 职位要求
            resume_experience: 简历中的工作经验
            
        Returns:
            List[Dict[str, str]]: 相关工作经验
        """
        if not resume_experience:
            return []
        
        relevant_experience = []
        requirements_lower = job_requirements.lower()
        
        for exp in resume_experience:
            relevance_score = 0
            
            # 检查职位标题相关性
            if exp.get('title'):
                title_lower = exp['title'].lower()
                if any(keyword in title_lower for keyword in requirements_lower.split()):
                    relevance_score += 2
            
            # 检查描述相关性
            if exp.get('description'):
                desc_lower = exp['description'].lower()
                if any(keyword in desc_lower for keyword in requirements_lower.split()):
                    relevance_score += 1
            
            # 如果相关性分数大于0，添加到相关经验
            if relevance_score > 0:
                exp['relevance_score'] = relevance_score
                relevant_experience.append(exp)
        
        # 按相关性分数排序
        relevant_experience.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        return relevant_experience[:3]  # 返回前3个最相关的经验 
"""
职位信息提取模块
从招聘页面URL中提取职位详情
"""

import requests
from bs4 import BeautifulSoup
import re
from typing import Dict, Any, Optional
from urllib.parse import urljoin
import time
from utils import clean_text, extract_skills_from_text, format_experience_years

class JobExtractor:
    """职位信息提取器"""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
    
    def extract_job_info(self, url: str) -> Dict[str, Any]:
        """
        从URL提取职位信息
        
        Args:
            url: 招聘页面URL
            
        Returns:
            Dict[str, Any]: 提取的职位信息
        """
        try:
            # 获取页面内容
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # 解析HTML
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # 提取职位信息
            job_info = {
                'title': self._extract_job_title(soup),
                'company': self._extract_company_name(soup, url),
                'location': self._extract_location(soup),
                'description': self._extract_description(soup),
                'requirements': self._extract_requirements(soup),
                'responsibilities': self._extract_responsibilities(soup),
                'skills': [],
                'experience_level': '',
                'employment_type': '',
                'salary_range': '',
                'url': url
            }
            
            # 提取技能和职位类型
            job_info['skills'] = self._extract_job_skills(job_info['description'] + ' ' + job_info['requirements'])
            job_info['experience_level'] = self._extract_experience_level(job_info['description'] + ' ' + job_info['requirements'])
            job_info['employment_type'] = self._extract_employment_type(job_info['description'])
            
            return job_info
            
        except Exception as e:
            raise Exception(f"提取职位信息失败: {str(e)}")
    
    def _extract_job_title(self, soup: BeautifulSoup) -> str:
        """提取职位标题"""
        # 常见的职位标题选择器
        title_selectors = [
            'h1[class*="title"]',
            'h1[class*="job"]',
            'h1[class*="position"]',
            '.job-title',
            '.position-title',
            'h1',
            'title'
        ]
        
        for selector in title_selectors:
            element = soup.select_one(selector)
            if element:
                title = clean_text(element.get_text())
                if title and len(title) > 3:
                    return title
        
        # 从页面标题提取
        title_tag = soup.find('title')
        if title_tag:
            title = clean_text(title_tag.get_text())
            # 移除常见的后缀
            title = re.sub(r'\s*[-|]\s*(Indeed|LinkedIn|Glassdoor|.*\.com).*', '', title)
            return title
        
        return "职位标题未找到"
    
    def _extract_company_name(self, soup: BeautifulSoup, url: str) -> str:
        """提取公司名称"""
        # 从页面元素提取
        company_selectors = [
            '[class*="company"]',
            '[class*="employer"]',
            '.company-name',
            '.employer-name'
        ]
        
        for selector in company_selectors:
            element = soup.select_one(selector)
            if element:
                company = clean_text(element.get_text())
                if company and len(company) > 2:
                    return company
        
        # 从URL提取
        from utils import extract_company_name_from_url
        return extract_company_name_from_url(url)
    
    def _extract_location(self, soup: BeautifulSoup) -> str:
        """提取工作地点"""
        location_selectors = [
            '[class*="location"]',
            '[class*="address"]',
            '.job-location',
            '.location'
        ]
        
        for selector in location_selectors:
            element = soup.select_one(selector)
            if element:
                location = clean_text(element.get_text())
                if location and len(location) > 2:
                    return location
        
        return "地点未指定"
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """提取职位描述"""
        description_selectors = [
            '[class*="description"]',
            '[class*="summary"]',
            '.job-description',
            '.position-description',
            '[id*="description"]'
        ]
        
        for selector in description_selectors:
            element = soup.select_one(selector)
            if element:
                description = clean_text(element.get_text())
                if description and len(description) > 50:
                    return description
        
        # 如果没有找到专门的描述区域，尝试从主要内容区域提取
        main_content = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
        if main_content:
            description = clean_text(main_content.get_text())
            if len(description) > 100:
                return description[:1000]  # 限制长度
        
        return "职位描述未找到"
    
    def _extract_requirements(self, soup: BeautifulSoup) -> str:
        """提取职位要求"""
        requirement_selectors = [
            '[class*="requirement"]',
            '[class*="qualification"]',
            '.job-requirements',
            '.qualifications',
            '[id*="requirement"]'
        ]
        
        for selector in requirement_selectors:
            element = soup.select_one(selector)
            if element:
                requirements = clean_text(element.get_text())
                if requirements and len(requirements) > 20:
                    return requirements
        
        return "职位要求未找到"
    
    def _extract_responsibilities(self, soup: BeautifulSoup) -> str:
        """提取工作职责"""
        responsibility_selectors = [
            '[class*="responsibility"]',
            '[class*="duty"]',
            '.job-responsibilities',
            '.responsibilities'
        ]
        
        for selector in responsibility_selectors:
            element = soup.select_one(selector)
            if element:
                responsibilities = clean_text(element.get_text())
                if responsibilities and len(responsibilities) > 20:
                    return responsibilities
        
        return "工作职责未找到"
    
    def _extract_job_skills(self, text: str) -> list:
        """从职位描述和要求中提取技能"""
        return extract_skills_from_text(text)
    
    def _extract_experience_level(self, text: str) -> str:
        """提取经验要求"""
        text_lower = text.lower()
        
        # 经验级别关键词
        levels = {
            'entry': ['entry level', 'junior', '0-1 years', '1 year'],
            'mid': ['mid level', 'intermediate', '2-4 years', '3 years', '4 years'],
            'senior': ['senior', 'lead', '5+ years', '5 years', '6 years', '7 years'],
            'expert': ['expert', 'principal', 'architect', '10+ years']
        }
        
        for level, keywords in levels.items():
            for keyword in keywords:
                if keyword in text_lower:
                    return level.title()
        
        return "Not specified"
    
    def _extract_employment_type(self, text: str) -> str:
        """提取雇佣类型"""
        text_lower = text.lower()
        
        if any(word in text_lower for word in ['full time', 'full-time', 'fulltime']):
            return "Full-time"
        elif any(word in text_lower for word in ['part time', 'part-time', 'parttime']):
            return "Part-time"
        elif any(word in text_lower for word in ['contract', 'contractor']):
            return "Contract"
        elif any(word in text_lower for word in ['intern', 'internship']):
            return "Internship"
        elif any(word in text_lower for word in ['remote', 'work from home']):
            return "Remote"
        
        return "Not specified"
    
    def get_job_summary(self, job_info: Dict[str, Any]) -> str:
        """
        生成职位摘要
        
        Args:
            job_info: 职位信息字典
            
        Returns:
            str: 职位摘要
        """
        summary_parts = []
        
        if job_info['title']:
            summary_parts.append(f"职位: {job_info['title']}")
        
        if job_info['company']:
            summary_parts.append(f"公司: {job_info['company']}")
        
        if job_info['location']:
            summary_parts.append(f"地点: {job_info['location']}")
        
        if job_info['experience_level']:
            summary_parts.append(f"经验要求: {job_info['experience_level']}")
        
        if job_info['employment_type']:
            summary_parts.append(f"雇佣类型: {job_info['employment_type']}")
        
        if job_info['skills']:
            summary_parts.append(f"技能要求: {', '.join(job_info['skills'][:5])}")
        
        return " | ".join(summary_parts) 
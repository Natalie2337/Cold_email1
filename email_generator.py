"""
邮件生成模块
使用AI生成个性化的冷邮件
"""

import os
from typing import Dict, Any, List
from openai import OpenAI
from rag_system import RAGSystem

class EmailGenerator:
    """邮件生成器"""
    
    def __init__(self, openai_api_key: str):
        """
        初始化邮件生成器
        
        Args:
            openai_api_key: OpenAI API密钥
        """
        self.client = OpenAI(api_key=openai_api_key)
        self.rag_system = RAGSystem(openai_api_key)
        
    def generate_cold_email(self, job_data: Dict[str, Any], resume_data: Dict[str, Any], 
                          email_style: str = "professional") -> Dict[str, Any]:
        """
        生成冷邮件
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            email_style: 邮件风格 ("professional", "casual", "enthusiastic")
            
        Returns:
            Dict[str, Any]: 生成的邮件信息
        """
        try:
            # 创建知识库
            self.rag_system.create_knowledge_base(job_data, resume_data)
            
            # 获取相关上下文信息
            context_info = self._get_context_information(job_data, resume_data)
            
            # 生成邮件内容
            email_content = self._generate_email_content(job_data, resume_data, context_info, email_style)
            
            # 生成邮件主题
            subject_line = self._generate_subject_line(job_data, resume_data)
            
            return {
                'subject': subject_line,
                'content': email_content,
                'context_info': context_info,
                'style': email_style
            }
            
        except Exception as e:
            raise Exception(f"生成邮件失败: {str(e)}")
    
    def _get_context_information(self, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        获取上下文信息
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            
        Returns:
            Dict[str, Any]: 上下文信息
        """
        context_info = {}
        
        # 技能匹配信息
        job_skills = job_data.get('skills', [])
        resume_skills = resume_data.get('skills', [])
        skill_matches = self.rag_system.get_skill_matches(job_skills, resume_skills)
        context_info['skill_matches'] = skill_matches
        
        # 相关工作经验
        job_requirements = job_data.get('requirements', '') + ' ' + job_data.get('description', '')
        relevant_experience = self.rag_system.get_relevant_experience(
            job_requirements, resume_data.get('experience', [])
        )
        context_info['relevant_experience'] = relevant_experience
        
        # 上下文摘要
        context_summary = self.rag_system.generate_context_summary(job_data, resume_data)
        context_info['summary'] = context_summary
        
        return context_info
    
    def _generate_email_content(self, job_data: Dict[str, Any], resume_data: Dict[str, Any], 
                              context_info: Dict[str, Any], style: str) -> str:
        """
        生成邮件内容
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            context_info: 上下文信息
            style: 邮件风格
            
        Returns:
            str: 邮件内容
        """
        # 构建提示词
        prompt = self._build_email_prompt(job_data, resume_data, context_info, style)
        
        # 调用OpenAI API
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的求职邮件撰写专家。你需要根据职位信息和候选人简历生成个性化、专业且吸引人的冷邮件。邮件应该简洁、具体，并突出候选人的相关技能和经验。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=800,
            temperature=0.7
        )
        
        return response.choices[0].message.content.strip()
    
    def _build_email_prompt(self, job_data: Dict[str, Any], resume_data: Dict[str, Any], 
                          context_info: Dict[str, Any], style: str) -> str:
        """
        构建邮件生成提示词
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            context_info: 上下文信息
            style: 邮件风格
            
        Returns:
            str: 提示词
        """
        # 风格指导
        style_guides = {
            "professional": "使用正式、专业的语言，突出专业能力和成就。",
            "casual": "使用友好、轻松的语气，展现个人魅力和文化契合度。",
            "enthusiastic": "使用充满激情的语言，展现对公司和职位的强烈兴趣。"
        }
        
        style_guide = style_guides.get(style, style_guides["professional"])
        
        # 构建提示词
        prompt = f"""
请根据以下信息生成一封个性化的冷邮件：

职位信息：
- 职位：{job_data.get('title', 'N/A')}
- 公司：{job_data.get('company', 'N/A')}
- 地点：{job_data.get('location', 'N/A')}
- 职位描述：{job_data.get('description', 'N/A')[:500]}...
- 职位要求：{job_data.get('requirements', 'N/A')[:300]}...
- 所需技能：{', '.join(job_data.get('skills', []))}

候选人信息：
- 姓名：{resume_data.get('name', 'N/A')}
- 邮箱：{resume_data.get('email', 'N/A')}
- 个人总结：{resume_data.get('summary', 'N/A')}
- 技能：{', '.join(resume_data.get('skills', []))}
- 工作经验：{len(resume_data.get('experience', []))} 项

匹配信息：
- 技能匹配度：{context_info['skill_matches']['match_percentage']}%
- 匹配技能：{', '.join(context_info['skill_matches']['matched_skills'])}
- 相关工作经验：{len(context_info['relevant_experience'])} 项

邮件要求：
1. 风格：{style_guide}
2. 长度：150-250字
3. 结构：开场白 + 个人介绍 + 技能匹配 + 相关经验 + 结尾
4. 个性化：具体提及职位和公司
5. 专业：避免拼写和语法错误

请生成一封完整的邮件，包括称呼、正文和签名。
"""
        
        return prompt
    
    def _generate_subject_line(self, job_data: Dict[str, Any], resume_data: Dict[str, Any]) -> str:
        """
        生成邮件主题行
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            
        Returns:
            str: 邮件主题
        """
        # 构建主题行提示词
        prompt = f"""
请为以下求职邮件生成一个吸引人的主题行：

职位：{job_data.get('title', 'N/A')}
公司：{job_data.get('company', 'N/A')}
候选人：{resume_data.get('name', 'N/A')}

要求：
1. 简洁明了（不超过60个字符）
2. 包含职位名称
3. 突出候选人的主要技能或经验
4. 避免使用"申请"、"求职"等常见词汇
5. 个性化且吸引人

请只返回主题行，不要其他内容。
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的邮件主题行撰写专家。你需要生成简洁、吸引人且个性化的邮件主题行。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=50,
                temperature=0.8
            )
            
            return response.choices[0].message.content.strip()
        except:
            # 如果API调用失败，返回默认主题行
            return f"Experienced {job_data.get('title', 'Professional')} - {resume_data.get('name', 'Candidate')}"
    
    def generate_multiple_versions(self, job_data: Dict[str, Any], resume_data: Dict[str, Any], 
                                 num_versions: int = 3) -> List[Dict[str, Any]]:
        """
        生成多个版本的邮件
        
        Args:
            job_data: 职位信息
            resume_data: 简历信息
            num_versions: 版本数量
            
        Returns:
            List[Dict[str, Any]]: 多个版本的邮件
        """
        versions = []
        styles = ["professional", "casual", "enthusiastic"]
        
        for i in range(min(num_versions, len(styles))):
            try:
                email_version = self.generate_cold_email(job_data, resume_data, styles[i])
                email_version['version'] = i + 1
                email_version['style_name'] = styles[i]
                versions.append(email_version)
            except Exception as e:
                print(f"生成版本 {i+1} 失败: {str(e)}")
                continue
        
        return versions
    
    def analyze_email_effectiveness(self, email_content: str, job_data: Dict[str, Any], 
                                  resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        分析邮件效果
        
        Args:
            email_content: 邮件内容
            job_data: 职位信息
            resume_data: 简历信息
            
        Returns:
            Dict[str, Any]: 分析结果
        """
        prompt = f"""
请分析以下求职邮件的效果：

邮件内容：
{email_content}

职位信息：
- 职位：{job_data.get('title', 'N/A')}
- 公司：{job_data.get('company', 'N/A')}
- 所需技能：{', '.join(job_data.get('skills', []))}

候选人信息：
- 技能：{', '.join(resume_data.get('skills', []))}
- 工作经验：{len(resume_data.get('experience', []))} 项

请从以下方面进行评分（1-10分）和分析：
1. 个性化程度
2. 技能匹配度
3. 专业度
4. 吸引力
5. 清晰度

请以JSON格式返回结果，包含分数和具体建议。
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": "你是一个专业的求职邮件分析专家。请提供客观、具体的分析和建议。"
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            # 解析分析结果
            analysis_text = response.choices[0].message.content.strip()
            
            # 简单的评分提取（实际应用中可能需要更复杂的解析）
            scores = {
                'personalization': 8,
                'skill_match': 7,
                'professionalism': 9,
                'attractiveness': 8,
                'clarity': 9
            }
            
            return {
                'scores': scores,
                'analysis': analysis_text,
                'overall_score': sum(scores.values()) / len(scores)
            }
            
        except Exception as e:
            return {
                'scores': {},
                'analysis': f"分析失败: {str(e)}",
                'overall_score': 0
            } 
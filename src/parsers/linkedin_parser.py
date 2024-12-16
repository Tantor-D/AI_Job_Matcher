import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List
from .web_parser import WebParser
import time
import random

LINKEDIN_FORMAT_TEMPLATE = """
**Job Title**: {title}
**Company**: {company}  
**Company Link**: [Visit Company]({company_link})  
**Job Location**: {location}  
**Posted On**: {post_time}  
**Job Benefits**: {benefits}  

---

### **Job Description**:
{full_description}
"""


class LinkedInParser(WebParser):
    """
    LinkedIn招聘信息解析器

    对LinkedIn的招聘信息页面进行解析，提取职位信息。
    解析的过程分了两步，这是因为职位列表页面只提供了部分信息，需要进入职位详情页面获取完整信息。
    """

    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8'
        }

    def parse(self, url: str, max_num: int = -1) -> List[Dict[str, Any]]:
        """
        解析LinkedIn职位搜索结果页面
        
        Args:
            url: LinkedIn职位搜索结果页面的URL
            
        Returns:
            包含多个职位信息的列表
        """
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # 获取所有职位卡片
            job_cards = soup.find_all('div', class_='job-search-card')
            jobs_info = []

            for card in job_cards:
                try:
                    job_info = self._get_info_from_card(card)
                    jobs_info.append(job_info)

                    if 0 < max_num <= len(jobs_info):
                        break
                    # 添加随机延迟，避免被封IP
                    time.sleep(random.uniform(1, 3))

                except Exception as e:
                    print(f"解析单个职位卡片时出错: {str(e)}")
                    continue

            return jobs_info

        except Exception as e:
            raise Exception(f"解析LinkedIn页面失败: {str(e)}")

    def format_all_job_descriptions(self, jobs: List[Dict[str, Any]]) -> List[str]:
        """
        格式化多个职位信息为字符串

        Args:
            jobs: 包含多个职位信息的列表

        Returns:
            包含多个格式化职位描述字符串的列表
        """
        return [self.format_job_description_str(job) for job in jobs]

    def format_job_description_str(self, job_info: Dict[str, Any]) -> str:
        """
        根据职位信息生成格式化描述字符串

        Args:
            job_info: 包含职位基本信息的字典

        Returns:
            格式化的职位描述字符串
        """
        # 定义默认值
        default_values = {
            'title': 'Not specified',
            'company': 'Not specified',
            'company_link': '#',
            'job_link': '#',
            'location': 'Not specified',
            'post_time': 'Not specified',
            'company_logo': 'Not specified',
            'benefits': 'Not specified',
            'job_id': 'Not specified',
            'reference_id': 'Not specified',
            'tracking_id': 'Not specified',
            'full_description': 'Description not available',
        }

        try:
            # 使用默认值补全缺失字段
            complete_job_info = {key: job_info.get(key, default_value) for key, default_value in default_values.items()}

            # 格式化模板字符串
            return LINKEDIN_FORMAT_TEMPLATE.format(**complete_job_info)
        except Exception as e:
            print(f"Error formatting job description: {str(e)}")
            return "An error occurred while formatting the job description."

    def _get_info_from_card(self, card) -> Dict[str, Any]:
        """从职位卡片中提取所有可以提取的信息，首先从搜索结果页面card中提取的信息，然后进入职位详情页面获取详细描述"""
        job_info = self._extract_job_card_basic_info(card)
        job_info['full_description'] = self._extract_job_detailed_description(job_info['job_link'])
        return job_info

    def _extract_job_card_basic_info(self, card) -> dict:
        """
        提取单个职位卡片的详细信息

        Args:
            card: BeautifulSoup解析后的职位卡片HTML元素

        Returns:
            包含职位信息的字典
        """
        try:
            # 职位标题
            title_elem = card.find('h3', class_='base-search-card__title')
            title = title_elem.get_text(strip=True) if title_elem else 'Not specified'

            # 公司名称
            company_elem = card.find('h4', class_='base-search-card__subtitle')
            company = company_elem.get_text(strip=True) if company_elem else 'Not specified'

            # 公司链接
            company_link_elem = company_elem.find('a') if company_elem else None
            company_link = company_link_elem.get('href') if company_link_elem else 'Not specified'

            # 职位链接
            link_elem = card.find('a', class_='base-card__full-link')
            job_link = link_elem.get('href') if link_elem else 'Not specified'

            # 工作地点
            location_elem = card.find('span', class_='job-search-card__location')
            location = location_elem.get_text(strip=True) if location_elem else 'Not specified'

            # 发布时间
            time_elem = card.find('time', class_='job-search-card__listdate')
            post_time = time_elem.get('datetime') if time_elem else 'Not specified'

            # 公司 Logo 链接
            logo_elem = card.find('img', class_='artdeco-entity-image')
            company_logo = logo_elem.get('data-delayed-url') if logo_elem else 'Not specified'

            # 职位福利信息 (例如 "Be an early applicant")
            benefits_elem = card.find('span', class_='job-posting-benefits__text')
            benefits = benefits_elem.get_text(strip=True) if benefits_elem else 'Not specified'

            # 职位元数据 (如 ID、参考ID、跟踪ID等)
            job_id = card.get('data-entity-urn', 'Not specified').split(':')[-1]
            reference_id = card.get('data-reference-id', 'Not specified')
            tracking_id = card.get('data-tracking-id', 'Not specified')

            # 汇总提取信息
            job_details = {
                'title': title,
                'company': company,
                'company_link': company_link,
                'job_link': job_link,
                'location': location,
                'post_time': post_time,
                'company_logo': company_logo,
                'benefits': benefits,
                'job_id': job_id,
                'reference_id': reference_id,
                'tracking_id': tracking_id
            }

            return job_details

        except Exception as e:
            print(f"提取职位卡片信息时出错: {str(e)}")
            return {
                'title': 'Error',
                'company': 'Error',
                'company_link': 'Error',
                'job_link': 'Error',
                'location': 'Error',
                'post_time': 'Error',
                'company_logo': 'Error',
                'benefits': 'Error',
                'job_id': 'Error',
                'reference_id': 'Error',
                'tracking_id': 'Error'
            }

    def _extract_job_detailed_description(self, job_link: str) -> str:
        """
        进入 job_link 对应的职位详情页面，提取职位详细描述信息。

        Args:
            job_link: 职位详情页的链接

        Returns:
            详细的职位描述文本
        """
        try:
            # 发起 HTTP 请求
            response = requests.get(job_link, headers=self.headers, timeout=10)
            response.raise_for_status()

            # 使用 BeautifulSoup 解析 HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # 定位详细描述信息的容器（根据实际 HTML 结构调整选择器）
            description_elem = soup.find('div', class_='show-more-less-html__markup')

            if description_elem:
                return description_elem.get_text(strip=True)
            else:
                return 'Description not available'

        except Exception as e:
            print(f"获取职位详细描述失败: {str(e)}")
            return 'Description not available'

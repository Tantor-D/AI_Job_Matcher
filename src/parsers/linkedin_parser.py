import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from .web_parser import WebParser
import time
import random
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import logging
import requests.exceptions

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

    def __init__(self, proxies: List[str] = None, cookies: str = None):
        # 更真实的请求头
        self.headers = {
            'User-Agent': self._get_random_user_agent(),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
        }

        # 修改代理相关的初始化
        self.proxies = list(proxies) if proxies else []  # 转换为列表以支持修改
        self.current_proxy_index = 0
        self.failed_proxies = set()  # 记录失败的代理
        
        # 添加代理健康检查的配置
        self.proxy_max_fails = 3  # 代理失败次数阈值
        self.proxy_fail_counts = {}  # 记录每个代理的失败次数

        # 设置Cookie
        if cookies:
            self.headers['Cookie'] = cookies

        # 配置重试策略
        self.session = requests.Session()
        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
        )
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

        # 配置日志
        self.logger = logging.getLogger(__name__)

    def _get_random_user_agent(self) -> str:
        """返回随机User-Agent"""
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15',
        ]
        return random.choice(user_agents)

    def _get_next_proxy(self) -> Optional[Dict[str, str]]:
        """获取下一个可用的代理"""
        if not self.proxies:
            return None
            
        # 尝试所有代理直到找到一个可用的
        attempts = len(self.proxies)
        while attempts > 0:
            proxy = self.proxies[self.current_proxy_index]
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            
            # 如果代理未被标记为失败，则使用它
            if proxy not in self.failed_proxies:
                return {'https': proxy}
                
            attempts -= 1
            
        # 如果所有代理都失败了，返回None
        return None
        
    def _check_proxy_health(self, proxy: str) -> bool:
        """检查代理是否可用"""
        try:
            test_url = "https://www.linkedin.com/robots.txt"  # 使用robots.txt作为测试URL
            response = requests.get(
                test_url,
                proxies={'https': proxy},
                headers=self.headers,
                timeout=5
            )
            return response.status_code == 200
        except:
            return False
            
    def _handle_proxy_failure(self, proxy: str):
        """处理代理失败的情况"""
        if not proxy:
            return
            
        # 更新失败计数
        self.proxy_fail_counts[proxy] = self.proxy_fail_counts.get(proxy, 0) + 1
        
        # 如果失败次数超过阈值，将代理标记为失败并从代理池中移除
        if self.proxy_fail_counts[proxy] >= self.proxy_max_fails:
            self.failed_proxies.add(proxy)
            if proxy in self.proxies:
                self.logger.warning(f"Removing failed proxy: {proxy}")
                self.proxies.remove(proxy)
                # 重置当前代理索引
                self.current_proxy_index = 0 if self.proxies else -1
                
    def _make_request(self, url: str, max_retries: int = 3) -> requests.Response:
        """发送请求并处理可能的错误"""
        last_exception = None
        failed_attempts = []  # 记录所有失败的尝试
        
        for attempt in range(max_retries):
            try:
                # 随机延迟
                time.sleep(random.uniform(2, 5))
                
                # 更新请求头
                self.headers['User-Agent'] = self._get_random_user_agent()
                
                # 获取代理
                proxies = self._get_next_proxy()
                current_proxy = proxies['https'] if proxies else None
                
                # 记录当前尝试的信息
                attempt_info = {
                    'attempt': attempt + 1,
                    'proxy': current_proxy,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
                }
                
                # 发送请求
                response = self.session.get(
                    url,
                    headers=self.headers,
                    proxies=proxies,
                    timeout=10
                )
                
                # 检查响应状态
                response.raise_for_status()
                return response
                
            except requests.exceptions.ProxyError as e:
                # 代理错误，直接处理代理失败
                error_msg = f"Proxy error with {current_proxy}: {str(e)}"
                self.logger.error(error_msg)
                attempt_info['error'] = error_msg
                failed_attempts.append(attempt_info)
                
                self._handle_proxy_failure(current_proxy)
                last_exception = e
                
            except requests.exceptions.RequestException as e:
                error_msg = f"Request failed (attempt {attempt + 1}/{max_retries}): {str(e)}"
                self.logger.warning(error_msg)
                
                attempt_info['error'] = error_msg
                failed_attempts.append(attempt_info)
                
                # 如果是代理相关的错误，处理代理失败
                if isinstance(e, (requests.exceptions.ProxyError, requests.exceptions.ConnectTimeout)):
                    self._handle_proxy_failure(current_proxy)
                    
                last_exception = e
                if attempt == max_retries - 1:
                    break
                    
                time.sleep(random.uniform(5, 10))  # 失败后等待更长时间
                
        # 如果所有重试都失败了
        if not self.proxies:
            self.logger.error("All proxies have failed, trying without proxy")
            # 尝试不使用代理发送请求
            try:
                response = self.session.get(
                    url,
                    headers=self.headers,
                    timeout=10
                )
                response.raise_for_status()
                return response
            except requests.exceptions.RequestException as e:
                error_msg = f"Final attempt without proxy failed: {str(e)}"
                self.logger.error(error_msg)
                failed_attempts.append({
                    'attempt': 'final',
                    'proxy': None,
                    'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
                    'error': error_msg
                })
                last_exception = e
        
        # 打印详细的失败信息
        print("\n=== LinkedIn访问失败详细信息 ===")
        print(f"目标URL: {url}")
        print(f"总尝试次数: {len(failed_attempts)}")
        print(f"剩余可用代理数量: {len(self.proxies)}")
        print(f"已失败代理数量: {len(self.failed_proxies)}")
        print("\n失败记录:")
        for attempt in failed_attempts:
            print(f"\n尝试 {attempt['attempt']}:")
            print(f"  时间: {attempt['timestamp']}")
            print(f"  使用代理: {attempt['proxy'] or '直接访问'}")
            print(f"  错误信息: {attempt['error']}")
        print("\n=== 失败信息结束 ===\n")
        
        # 抛出异常
        raise Exception(
            f"LinkedIn访问失败 - 已尝试{len(failed_attempts)}次\n"
            f"最后错误: {str(last_exception)}\n"
            f"剩余可用代理: {len(self.proxies)}"
        )

    def parse(self, url: str, max_num: int = -1) -> List[Dict[str, Any]]:
        """解析LinkedIn职位搜索结果页面"""
        try:
            response = self._make_request(url)
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

                except Exception as e:
                    self.logger.error(f"解析单个职位卡片时出错: {str(e)}")
                    continue

            return jobs_info

        except Exception as e:
            self.logger.error(f"解析LinkedIn页面失败: {str(e)}")
            raise

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
        """获取职位详细描述"""
        try:
            response = self._make_request(job_link)
            soup = BeautifulSoup(response.text, 'html.parser')

            description_elem = soup.find('div', class_='show-more-less-html__markup')
            return description_elem.get_text(strip=True) if description_elem else 'Description not available'

        except Exception as e:
            self.logger.error(f"获取职位详细描述失败: {str(e)}")
            return 'Description not available'

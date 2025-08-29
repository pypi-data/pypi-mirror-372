import hashlib
import json
import os
import random
import re
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
import requests
import retrying
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from gne import GeneralNewsExtractor
from htmldate import find_date
from loguru import logger
from urllib.parse import urljoin
from lxml import etree
from lxparse import LxParse
from pybloom_live import BloomFilter
import pickle
from urllib.parse import urlparse
from DrissionPage import WebPage


headers = {'user-agent':  str(UserAgent().random)}




def run_in_threads(func, datas, max_workers=10, rate_limit=None, retries=3, retry_delay=1,batch_size=None, batch_delay=0):
    """
    多线程运行函数，支持速率限制 & 自动重试 & 日志输出进度 & 批量执行

    Args:
        func (callable): 需要执行的函数，接受一个参数
        datas (iterable | list): 数据列表或可迭代对象 (如 Mongo cursor)
        max_workers (int): 最大线程数
        rate_limit (None | int | tuple):
            - None: 不限速
            - int: 每秒最多执行多少任务（固定速率）
            - tuple(min, max): 每秒任务数范围，随机选择速率
        retries (int): 每个任务失败后重试次数
        retry_delay (int | float): 重试间隔（秒）
        batch_size (None | int): 每批任务的数量（None 表示不分批）
        batch_delay (int | float): 每批之间的等待时间（秒）

    Returns:
        list: 按输入顺序对应的结果列表，失败时返回 Exception
    """
    datas = list(datas)
    total = len(datas)
    results = [None] * total
    lock = threading.Lock()
    last_time = [0.0]
    finished = 0

    def wrapper(data):
        if rate_limit:
            with lock:
                if isinstance(rate_limit, tuple):
                    rate = random.uniform(*rate_limit)
                else:
                    rate = rate_limit
                interval = 1.0 / rate
                elapsed = time.time() - last_time[0]
                if elapsed < interval:
                    time.sleep(interval - elapsed)
                last_time[0] = time.time()


        for attempt in range(1, retries + 1):
            try:
                return func(data)
            except Exception as e:
                if attempt < retries:
                    logger.warning(f"任务失败，重试 {attempt}/{retries} 次后继续: {e}")
                    time.sleep(retry_delay * attempt)
                else:
                    logger.error(f"任务最终失败: {e}")
                    return e

    for start in range(0, total, batch_size or total):
        end = min(start + (batch_size or total), total)
        batch = datas[start:end]

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_index = {executor.submit(wrapper, d): i for i, d in enumerate(batch, start)}
            for future in as_completed(future_to_index):
                idx = future_to_index[future]
                results[idx] = future.result()
                finished += 1
                logger.info(f"进度: {finished}/{total} ({finished/total:.0%})")

        if end < total and batch_delay > 0:
            logger.info(f"批次完成 {end}/{total}，等待 {batch_delay}s 再继续...")
            time.sleep(batch_delay)

    return results



def is_content_page(url, base_domain):
    parsed_url = urlparse(url)

    domain = urlparse(base_domain).netloc
    # **检查是否为相同域名**
    if parsed_url.netloc != domain:
        return None

    path = parsed_url.path
    query = parsed_url.query

    # 规则1: 统计 "/" 的数量
    slash_count = path.count("/")

    # 规则2: 判断是否有文件后缀（如 .html, .php）
    has_extension = bool(re.search(r'\.(html|php|asp|aspx|jsp|htm|shtml)$', path, re.IGNORECASE))

    # 规则3: 是否包含数字 ID（常见于内容页）
    has_numeric_id = bool(re.search(r'/\d{4,}', path)) or bool(re.search(r'id=\d+', query))

    # 规则4: 列表页通常短且以 "/" 结尾
    is_list_url = not has_extension and (path.endswith("/") or slash_count < 3)

    # 规则5: 列表页可能包含关键词
    list_keywords = ["category", "list", "news", "page", "archives", "tags"]
    contains_list_keyword = any(kw in path.lower() for kw in list_keywords)




    # **判断逻辑**：如果符合多个“内容页”特征，则判断为内容页
    if has_extension or has_numeric_id:
        return url, True  # 可能是内容页
    if is_list_url or contains_list_keyword:
        return url, False  # 可能是列表页

    # **默认情况**：如果 `/` 很多，且没有后缀，可能是内容页
    return url, False


def categorize_urls(urls, base_domain):
    """分类URL为内容页和列表页"""
    content_page, list_page = [], []
    for url in urls:
        result = is_content_page(url, base_domain)
        if result:
            if result[1]==True:
                content_page.append(result[0])
            elif result[1]==False:
                list_page.append(result[0])
    return  content_page,list_page





class URLFilter:
    def __init__(self, capacity=1000000, error_rate=0.001, file_path='url_filter.pkl'):
        """
        初始化URL过滤器
        :param capacity: 布隆过滤器容量
        :param error_rate: 误判率
        :param file_path: 过滤器保存的文件路径
        """
        self.file_path = file_path
        self.capacity = capacity
        self.error_rate = error_rate
        self.bf = self.load_filter()

    def load_filter(self):
        """
        从文件加载过滤器，如果文件不存在或为空则新建一个并保存到文件
        :return: 加载的布隆过滤器
        """
        if not os.path.exists(self.file_path) or os.path.getsize(self.file_path) == 0:
            # 如果文件不存在或为空，则新建一个过滤器并保存到文件
            print(f"文件 {self.file_path} 不存在或为空，新建布隆过滤器并保存")
            bf = BloomFilter(capacity=self.capacity, error_rate=self.error_rate)
            self.save_filter(bf)  # 保存新建的过滤器
            return bf

        # 文件存在且不为空，加载过滤器
        with open(self.file_path, 'rb') as f:
            return pickle.load(f)

    def save_filter(self, bf=None):
        """
        将过滤器保存到文件
        :param bf: 要保存的布隆过滤器，默认为 self.bf
        """
        if bf is None:
            bf = self.bf
        with open(self.file_path, 'wb') as f:
            pickle.dump(bf, f)

    def is_url_new(self, url):
        """
        检查URL是否为新URL
        :param url: 要检查的URL
        :return: True表示是新URL，False表示已存在
        """
        if url not in self.bf:
            self.bf.add(url)
            self.save_filter()  # 每次添加新URL后保存过滤器
            return True
        return False





def get_page_info(url, page_param=None, step=1, first_num=1, mode='direct', max_attempts=10, use_cache=False, cache_file=None, proxy=None,stop_max_attempt_number=3,sleep=1,has_index=False,custom_base_path=None):
    """
    获取页面信息，支持直接解析和二分查找两种模式
    :param url: 初始URL
    :param page_param: 页码参数名
    :param step: 页码步长,如果页码不是连续的，可以设置步长
    :param first_num: 起始页码
    :param mode: 模式选择，'direct'（直接解析）或 'binary'（二分查找）
    :param max_attempts: 二分查找最大尝试次数
    :param use_cache: 是否使用缓存，默认关闭
    :param cache_file: 缓存文件名
    :param proxy: 代理设置
    :return: 页面链接列表, 总页数
    :stop_max_attempt_number: 重试次数
    :sleep: 重试间隔
    :has_index: 是否首页包括页码

    """
    headers = {'user-agent': str(UserAgent().random)}
    if not cache_file:
        cache_file = 'total_pages_cache.json'

    def extract_base_url(url, page_param):
        if page_param.startswith('/'):
            pattern = rf'(.*{page_param})\d+'
        else:
            pattern = rf'(.*[?&]{page_param}=)\d+'
        match = re.search(pattern, url)
        return match.group(1) if match else url.split('?')[0]

    @retrying.retry(wait_fixed=2000, stop_max_attempt_number=3)
    def get_response(url, params=None, data=None, proxy=None):
        try:
            if data == None:
                if params == None:
                    response = requests.get(url, headers=headers, proxies=proxy, timeout=10)
                else:
                    response = requests.get(url, headers=headers, params=params, proxies=proxy, timeout=10)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    return response
            else:
                if params == None:
                    response = requests.post(url, headers=headers, data=data, proxies=proxy, timeout=10)
                else:
                    response = requests.post(url, headers=headers, data=data, params=params, proxies=proxy, timeout=10)
                if response.status_code == 200:
                    response.encoding = response.apparent_encoding
                    return response
        except Exception as e:
            logger.info(f'抓取失败,重新抓取：{url}.{e}')
            raise

    # 缓存处理
    def load_cache():
        if os.path.exists(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def save_cache(cache):
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=4)

    # 检查缓存
    if use_cache:
        cache = load_cache()
        base_url=extract_base_url(url, page_param)
        cached_data = cache.get(base_url) or cache.get(url)
        if cached_data:
            logger.success(f"从缓存中读取: \nbase_url={base_url}\n总页数={cached_data['total_pages']}\n链接：{cached_data['all_pages_link'][:3]}...")
            return cached_data['all_pages_link'],cached_data['total_pages'],
        else:
            logger.info("缓存中没有找到数据")

    if mode == 'direct':
        # 直接解析模式
        response =get_response(url,proxy=proxy).text

        body = etree.HTML(response)
        if custom_base_path:
            page_url=body.xpath(custom_base_path)
        else:
            page_url = body.xpath("//a[text()='尾页' or text()='末页' or text()='最后一页' or text()='尾 页' or text()='未页']/@href")

        if not page_url:
            logger.info("未找到尾页链接")
            return [url], 1

        full_url = urljoin(url, page_url[0])
        # 处理不同参数模式
        if page_param:
            pattern = rf'(.*{page_param})(\d+)(\.[a-zA-Z0-9]+)?' if page_param.startswith(
                '/') else rf'(.*[?&]{page_param}=)(\d+)(\.[a-zA-Z0-9]+)?'
            match = re.search(pattern, full_url)
            if match:
                base_path = match.group(1)  # 基础路径
                last_page_number = match.group(2)  # 当前页码
                extension = match.group(3) or ''  # 文件扩展名（如 .html、.php 等）

                # 生成所有分页链接
                all_pages_link = [
                    f"{base_path}{(int(last_page_number) - i) * step + first_num}{extension}"
                    for i in range(int(last_page_number) - 1, -1, -1)
                ]
                all_pages_link.append(url)
                logger.success(f"基本路径: {base_path}, 页码: {last_page_number}, 扩展名: {extension}")
                logger.info(f"所有分页链接: {all_pages_link[:3]}...")
                return all_pages_link, last_page_number

        # 默认处理逻辑
        match = re.match(r'(.*/)([^/]+?)_?(\d+)?_(\d+)(\.html)?', full_url)
        if match:
            # 提取基础路径、主编号和当前页码
            base_path = f"{match.group(1)}{match.group(2)}_{match.group(3)}_{{}}{match.group(5) or '.html'}"
            current_page_number = int(match.group(4))  # 页码
            main_id = match.group(3)  # 主编号

            # 生成所有分页链接
            if has_index:
                all_pages_link = [
                    base_path.format(page) for page in range(1, current_page_number + 1)
                ]
            else:
                all_pages_link = [
                    base_path.format(page) for page in range(2, current_page_number + 1)
                ]
                all_pages_link.append(full_url)

            logger.success(f"\n✅ 基本路径: {base_path}, 主编号: {main_id}, 页码: {current_page_number}")
            logger.info(f"\n✅所有分页链接预览: {all_pages_link[:3]}...")
            if use_cache:
                cache = load_cache()
                cache['base_url'] = {
                    'total_pages': current_page_number,
                    'all_pages_link': all_pages_link
                }
                save_cache(cache)
                logger.success(f"结果已保存到缓存文件: {cache_file}")

            return all_pages_link, current_page_number
        else:
            logger.error("❌ 无法匹配链接格式")
            return [url], 1

    else:
        def is_page_valid(page_url):
            try:
                response = requests.get(page_url, headers=headers, proxies=proxy, timeout=10)
                logger.info(f"📊是否是最后一页呢?: {page_url}")
                return response.status_code == 200
            except requests.RequestException:
                return False
        def get_page_url(base_url, page_num, page_param):
            pattern = rf'(.*{page_param})(\d+)(\.[a-zA-Z0-9]+)?' if page_param.startswith(
                '/') else rf'(.*[?&]{page_param}=)(\d+)(\.[a-zA-Z0-9]+)?'
            match = re.search(pattern, base_url)
            if match:
                base_path = match.group(1)  # 基础路径
                last_page_number = match.group(2)  # 当前页码
                extension = match.group(3) or ''  # 文件扩展名（如 .html、.php 等）
                return f'{base_path}{page_num}{extension}'
            else:
                logger.error(f'提取错误')
                return []

        # 提取base_url
        base_url = extract_base_url(url, page_param)

        # 动态扩展范围
        left, right = 1, 100
        attempts = 0
        while attempts < max_attempts:
            attempts += 1
            if is_page_valid(get_page_url(url, right, page_param)):
                left = right
                right *= 2
            else:
                break

        # 二分查找
        while left < right:
            mid = (left + right) // 2
            if is_page_valid(get_page_url(url, mid, page_param)):
                left = mid + 1
            else:
                right = mid
            time.sleep(sleep)

        total_pages = left - 1
        all_pages_link = [get_page_url(url, i, page_param) for i in range(1, total_pages + 1)]
        if use_cache:
            cache = load_cache()
            cache[f'{base_url}'] = {
                'total_pages': total_pages,
                'all_pages_link': all_pages_link
            }
            save_cache(cache)
            logger.success(f"🎉最后一页:{get_page_url(base_url, right, page_param)}")
            logger.success(f"✅ 结果已保存到缓存文件: {cache_file}，总页数: {total_pages}")


        return all_pages_link, total_pages









def get_links(url, xpath=None, proxy=None, article_nums=None, required_fields=None, base_url=None, regex=None,html=None,use_drission=False,sleep=0):
    def filter_by_fields(urls, required_fields, regex):
        """
        根据必须包含的字段和正则筛选 URL
        :param urls: URL 列表
        :param required_fields: 必须包含的字段列表
        :param regex: 正则表达式，如果不为空，则根据正则筛选 URL
        :return: 筛选后的 URL 列表
        """
        if not required_fields and not regex:
            return urls

        filtered_urls = []

        for url in urls:
            # 根据字段筛选
            if required_fields and any(field in url for field in required_fields):
                filtered_urls.append(url)
            # 根据正则筛选
            elif regex and re.match(regex, url):
                filtered_urls.append(url)

        return filtered_urls

    """
    提取内容页 URL
    :param html: 网页 HTML 内容
    :param xpath_list: XPath 表达式
    :param article_nums: 控制相似 URL 数量
    :param required_fields: 必须包含的字段列表（如 ['news', 'detail']）
    :param regex: 正则表达式筛选 URL
    :return: 筛选后的 URL 列表
    """

    @retrying.retry(wait_fixed=2000, stop_max_attempt_number=3)
    def get_response(url, params=None, data=None, proxy=None):
        try:
            if data is None:
                if params is None:
                    response = requests.get(url, headers=headers, proxies=proxy, timeout=10, verify=False)
                else:
                    response = requests.get(url, headers=headers, params=params, proxies=proxy, timeout=10)
                if '20' in f'{response.status_code}':
                    response.encoding = response.apparent_encoding
                    return response
            else:
                if params is None:
                    response = requests.post(url, headers=headers, data=data, proxies=proxy, timeout=10)
                else:
                    response = requests.post(url, headers=headers, data=data, params=params, proxies=proxy, timeout=10)
                if '20' in f'{response.status_code}':
                    response.encoding = response.apparent_encoding
                    return response
        except Exception as e:
            logger.info(f'抓取失败,重新抓取：{url}')
            logger.info(f'error:{e}')
            raise

    try:
        lx = LxParse()
        if html!=None:
            response=html
        elif use_drission==True:
            logger.info(f'使用DrissionPage')
            drission_options = {'proxy': proxy['http']} if proxy else {}
            page = WebPage(**drission_options)
            page.get(url)
            time.sleep(sleep)
            response = page.html
        else:
            response = get_response(url, proxy=proxy)
            if response is None:
                logger.error(f'抓取失败，返回 None: {url}')
                return []
            else:
                response = response.text

        if article_nums is not None:
            detail_url_list = lx.parse_list(response, article_nums=article_nums, xpath_list=xpath)
        elif xpath:
            detail_url_list = lx.parse_list(response, xpath_list=xpath)
        else:
            detail_url_list = lx.parse_list(response)

        if base_url:
            urls = [urljoin(base_url, detail_url) for detail_url in detail_url_list]
        else:
            urls = [urljoin(url, detail_url) for detail_url in detail_url_list]

        if required_fields or regex:
            urls = filter_by_fields(urls, required_fields, regex)

        if len(urls) > 0:
            logger.success(f"url:{url}；解析出链接{len(urls)}条")
            return list(set(urls))
        else:
            logger.error(f"url:{url}；未解析到链接,可传入xpath")
            return []

    except Exception as e:
        logger.error(f'解析失败:{e}')
        pass



@retrying.retry(wait_fixed=1000, stop_max_attempt_number=3)
def get_article(url, proxy=None, parsing_mode='lx', headers=headers, Filter=False,url_filter=None,use_drission=False,xpath_item=None,sleep=0):
    def clean_text_bs(html_content):
        soup = BeautifulSoup(html_content, 'html.parser')
        return soup.get_text()

    def clean_text_regex(text):
        return re.sub(r'\s+', ' ', text).strip()


    try:

        if use_drission:
            drission_options = {'proxy': proxy['http']} if proxy else {}
            tab = WebPage(**drission_options)
            tab.get(url)
            time.sleep(sleep)
            response=tab.html
        else:
            response = requests.get(url, headers=headers, proxies=proxy, timeout=5, verify=False)
            response.encoding = response.apparent_encoding
            response = response.text
        dit = {}
        if Filter and response.status_code == 200 and not url_filter.is_url_new(url):
            logger.info(f'请求已存在，跳过: {url}')
            return

        extractor = GeneralNewsExtractor()
        result_gne = extractor.extract(response)
        lx = LxParse()

        result = lx.parse_detail(response)
        _id = hashlib.md5(url.encode('utf-8')).hexdigest()
        dit['_id'] = _id
        dit['url'] = url
        dit['title'] = result.get('title', '').strip()
        if parsing_mode == 'lx':
            dit['content'] = clean_text_regex(result.get('content_format', ''))
        elif parsing_mode == 'gne':
            dit['content'] = clean_text_bs(clean_text_regex(result_gne.get('content', '')))
        elif parsing_mode=='xpath' and xpath_item:
            dit['title'] = clean_text_regex(lx.parse_detail(response, xpath_item['xpath_title']))
            dit['content'] = clean_text_regex(lx.parse_detail(response, xpath_item['xpath_content']))
        dit['updateTime'] = str(datetime.now())[:19]
        dit['addDateTime'] = str(datetime.now())[:19]
        dit['publish_time'] = find_date(response)
        if len(dit['content']) > 0:
            return dit
        else:
            logger.error(f'内容为空: {url}')
            return None
    except Exception as e:
        logger.error(f'重新抓取：{url} ，出错了')
        logger.error(f'error:{e}')
        raise

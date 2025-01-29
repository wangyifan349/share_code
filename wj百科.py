import requests
from bs4 import BeautifulSoup
from collections import deque
from fake_useragent import UserAgent
import json
import os
from concurrent.futures import ThreadPoolExecutor
import threading

# 创建锁以确保线程安全
lock = threading.Lock()

def write_to_file(title, content, links, filename):
    """将提取的内容写入文件"""
    with open(filename, 'a', encoding='utf-8') as f:
        f.write(f"标题: {title}\n")
        f.write("内容:\n")
        f.write(content + "\n")
        f.write("超链接:\n")
        for link in links:
            f.write(link + "\n")
        f.write("\n" + "=" * 40 + "\n\n")

def load_progress(progress_file):
    """从文件加载已完成和未完成的 URL"""
    if os.path.exists(progress_file):
        with open(progress_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"completed": [], "pending": []}

def save_progress(progress_file, completed, pending):
    """将已完成和未完成的 URL 保存到文件"""
    with open(progress_file, 'w', encoding='utf-8') as f:
        json.dump({"completed": completed, "pending": list(pending)}, f, ensure_ascii=False, indent=4)

def extract_content(url, session, user_agent, visited_links):
    """提取单个页面的内容和链接"""
    headers = {'User-Agent': user_agent.random}  # 随机选择请求头
    response = session.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"请求失败，状态码：{response.status_code}，链接：{url}")
        return None, None, None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    title = soup.find('h1').text.strip()  # 获取标题并去除多余空格
    content = ""
    
    # 提取段落内容
    paragraphs = soup.find('div', {'class': 'mw-parser-output'}).find_all('p')
    for para in paragraphs:
        text = para.get_text(strip=True)
        if text:  # 只添加非空段落
            content += text + " "  # 段落之间用空格分隔
    
    links = []
    # 提取页面中的链接
    for link in soup.find('div', {'class': 'mw-parser-output'}).find_all('a', href=True):
        href = link['href']
        if href.startswith('/wiki/') and href not in visited_links:
            full_url = f"https://en.wikipedia.org{href}"
            with lock:  # 确保线程安全
                visited_links.add(href)  # 添加到已访问链接
            links.append(full_url)  # 添加完整链接
    
    return title, content.strip(), links  # 返回标题、内容和链接

def bfs_extract_content(start_url, session, user_agent, visited_links, filename, progress_file):
    """执行广度优先搜索，提取页面内容和链接"""
    pending_links = deque([start_url])  # 初始化待处理链接队列
    
    # 初始阶段使用单线程
    while pending_links:
        url = pending_links.popleft()  # 从队列中取出一个链接
        title, content, links = extract_content(url, session, user_agent, visited_links)
        
        if title and content:
            write_to_file(title, content, links, filename)  # 写入文件
            print(f"已完成链接: {url}\n")
        
            for link in links:
                pending_links.append(link)  # 将新链接添加到待处理队列
        
            # 保存进度
            save_progress(progress_file, visited_links, pending_links)

    # 切换到多线程模式
    with ThreadPoolExecutor(max_workers=16) as executor:
        while pending_links:
            url = pending_links.popleft()  # 从队列中取出一个链接
            future = executor.submit(extract_content, url, session, user_agent, visited_links)
            title, content, links = future.result()  # 获取提取结果
            
            if title and content:
                write_to_file(title, content, links, filename)  # 写入文件
                print(f"已完成链接: {url}\n")
                
                for link in links:
                    with lock:  # 确保线程安全
                        pending_links.append(link)  # 将新链接添加到待处理队列
                
            # 保存进度
            save_progress(progress_file, visited_links, pending_links)

def extract_wikipedia_content(start_url, filename, progress_file):
    """提取维基百科内容，支持中断恢复"""
    progress = load_progress(progress_file)  # 加载进度
    visited_links = set(progress["completed"])  # 已访问链接集合
    
    if progress["pending"]:
        pending_links = deque(progress["pending"])  # 加载未完成的链接
    else:
        pending_links = deque([start_url])  # 初始化待处理链接
    
    session = requests.Session()  # 创建会话
    session.proxies = {'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'}  # 设置代理
    user_agent = UserAgent()  # 创建用户代理
    
    bfs_extract_content(start_url, session, user_agent, visited_links, filename, progress_file)  # 开始提取内容

# 设置起始 URL 和文件名
start_url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
output_file = 'wikipedia_content.txt'
progress_file = 'progress.json'

# 开始提取内容
extract_wikipedia_content(start_url, output_file, progress_file)

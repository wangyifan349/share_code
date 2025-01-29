import requests
from bs4 import BeautifulSoup
from collections import deque
from fake_useragent import UserAgent
import json
import os

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

def bfs_extract_content(start_url, session, user_agent, visited_links, filename, progress_file):
    """执行广度优先搜索，提取页面内容和链接"""
    pending_links = deque([start_url])
    
    while pending_links:
        url = pending_links.popleft()
        headers = {'User-Agent': user_agent.random}  # 随机选择请求头
        response = session.get(url, headers=headers)
        
        if response.status_code != 200:
            print(f"请求失败，状态码：{response.status_code}，链接：{url}")
            continue
        
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.find('h1').text
        content = ""
        
        paragraphs = soup.find('div', {'class': 'mw-parser-output'}).find_all('p')
        for para in paragraphs:
            # 删除多余的换行符和空格
            text = para.get_text(strip=True)
            if text:  # 只添加非空段落
                content += text + " "  # 段落之间用空格分隔
        
        links = []
        for link in soup.find('div', {'class': 'mw-parser-output'}).find_all('a', href=True):
            href = link['href']
            if href.startswith('/wiki/') and href not in visited_links:
                full_url = f"https://en.wikipedia.org{href}"
                visited_links.add(href)
                pending_links.append(full_url)
                links.append(full_url)
        
        write_to_file(title, content.strip(), links, filename)
        print(f"已完成链接: {url}\n")
        
        # 保存进度
        save_progress(progress_file, visited_links, pending_links)

def extract_wikipedia_content(start_url, filename, progress_file):
    """提取维基百科内容，支持中断恢复"""
    progress = load_progress(progress_file)
    visited_links = set(progress["completed"])
    
    if progress["pending"]:
        pending_links = deque(progress["pending"])
    else:
        pending_links = deque([start_url])
    
    session = requests.Session()
    session.proxies = {'http': 'http://127.0.0.1:10809', 'https': 'http://127.0.0.1:10809'}
    user_agent = UserAgent()
    
    bfs_extract_content(start_url, session, user_agent, visited_links, filename, progress_file)

# 设置起始 URL 和文件名
start_url = 'https://en.wikipedia.org/wiki/Python_(programming_language)'
output_file = 'wikipedia_content.txt'
progress_file = 'progress.json'

# 开始提取内容
extract_wikipedia_content(start_url, output_file, progress_file)

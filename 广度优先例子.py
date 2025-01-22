import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import re
from collections import deque
from fake_useragent import UserAgent
import json
import time
import os

PROXY = "http://127.0.0.1:10809"
CHECKPOINT_INTERVAL = 60  # 每隔60秒保存一次检查点

def create_session_with_proxy():
    session = requests.Session()
    session.proxies = {
        "http": PROXY,
        "https": PROXY
    }
    ua = UserAgent()
    session.headers.update({
        "User-Agent": ua.random
    })
    return session

def is_valid_wikipedia_url(url):
    wiki_pattern = re.compile(r'^https?://([a-z]+\.)?wikipedia\.org/')
    return bool(wiki_pattern.match(url))

def clean_paragraphs(paragraphs):
    cleaned_text = []
    for para in paragraphs:
        text = para.get_text().strip()
        text = re.sub(r'\[\d+\]', '', text)
        text = text.replace('[edit]', '')
        if len(text) > 20:
            cleaned_text.append(text)
    cleaned_paragraphs = "\n\n".join(cleaned_text).split("\n\n")
    return cleaned_paragraphs

def extract_title_and_content(session, url):
    try:
        response = session.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string.strip() if soup.title else "无标题"
        paragraphs = soup.find_all('p')
        paragraphs = [p for p in paragraphs if p.get_text().strip()]
        cleaned_paragraphs = clean_paragraphs(paragraphs)
        return title, cleaned_paragraphs
    except requests.RequestException as e:
        print(f"请求 {url} 时出现异常: {e}")
        return None, []

def write_to_file(filename, content):
    with open(filename, 'w', encoding='utf-8') as file:
        for line in content:
            file.write(line + "\n\n")

def load_checkpoints(filename):
    if os.path.exists(filename):
        with open(filename, 'r', encoding='utf-8') as file:
            return json.load(file)  # 加载现有检查点
    return {'seen_urls': [], 'to_crawl_urls': []}

def save_checkpoints(filename, seen_urls, to_crawl_urls):
    with open(filename, 'w', encoding='utf-8') as file:
        json.dump({'seen_urls': list(seen_urls), 'to_crawl_urls': list(to_crawl_urls)}, file, ensure_ascii=False)

def crawl_bfs(start_url, max_depth=2):
    session = create_session_with_proxy()
    checkpoints = load_checkpoints('checkpoints.json')
    seen_urls = set(checkpoints.get('seen_urls', []))
    to_crawl_urls = deque(checkpoints.get('to_crawl_urls', [(start_url, 0)]))
    last_checkpoint_time = time.time()

    while to_crawl_urls:
        current_time = time.time()
        if current_time - last_checkpoint_time > CHECKPOINT_INTERVAL:
            save_checkpoints('checkpoints.json', seen_urls, to_crawl_urls)  # 定期保存检查点
            last_checkpoint_time = current_time

        current_url, depth = to_crawl_urls.popleft()
        if depth > max_depth:
            continue
        if current_url not in seen_urls:
            seen_urls.add(current_url)
            title, paragraphs = extract_title_and_content(session, current_url)
            if title:
                print(f"\nURL: {current_url} (深度: {depth})")
                print(f"标题: {title}")
                filename = f"{re.sub(r'[\\/*?<>|]', '', title)}.txt"
                content = [f"标题: {title}"] + paragraphs
                write_to_file(filename, content)
                for i, para in enumerate(paragraphs, 1):
                    print(f"段落 {i}: {para[:100]}...")
            try:
                response = session.get(current_url, timeout=10)
                response.raise_for_status()
                soup = BeautifulSoup(response.content, 'html.parser')
                for a in soup.find_all('a', href=True):
                    link = urljoin(current_url, a['href'])
                    if is_valid_wikipedia_url(link) and link not in seen_urls:
                        to_crawl_urls.append((link, depth + 1))
            except requests.RequestException as e:
                print(f"请求 {current_url} 的链接提取时出现异常: {e}")

    # 在爬虫完成后再做一次最终的保存
    save_checkpoints('checkpoints.json', seen_urls, to_crawl_urls)

# 示例运行
start_url = "https://en.wikipedia.org/wiki/Python_(programming_language)"
crawl_bfs(start_url)

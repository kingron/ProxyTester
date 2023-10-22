import argparse
import concurrent.futures
import csv
import datetime
import os
import re
import signal
import time
from time import sleep

import requests
import urllib3
from bs4 import BeautifulSoup
from requests.exceptions import SSLError

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 有些服务器或者代理会检测 agent 字符串，如果用 curl 之类会禁止访问
agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46'
pattern = r'<urllib3\..+ object at 0x[0-9A-Fa-f]+>[,|:]\s+'
help_text = """File format(Tab separator), type value: socks4 | socks5 | http | https:
    type	server		port	user	password
    socks4	5.6.7.8		1080		
    socks5	1.2.3.4		8080	root	1234
    https	www.xyz.com	443		
    http	www.abc.com	80	dummy	none
"""


def get_proxies(schema, url):
    headers = {
        'User-Agent': agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
        'Connection': 'Disconnect'
    }
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        text = BeautifulSoup(response.text, 'html.parser').get_text()
        pat = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})(?::|\t|\s*,\s*|\s+)(\d{1,5})'
        matches = re.findall(pat, text)
        if not matches or len(matches) <= 3:  # 小于3个的一般可能是误扫描了，正常一个网站一般不会少于10个
            pat = r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\D*(\d{1,5})'
            matches = re.findall(pat, response.text)

        return list(set(f'{schema}:{ip}:{port}' for ip, port in matches))
    return []


def download_proxies(file_name: str, api_url) -> bool:
    paths = [
        ['socks5', 'https://www.proxy-list.download/api/v1/get?type=socks5'],
        ['socks5', 'https://openproxy.space/list/socks5'],
        ['http', 'https://github.com/fate0/proxylist/blob/master/proxy.list'],
        ['http', 'https://openproxy.space/list/http'],
        ['https', 'https://openproxy.space/list/https'],
        ['http', 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&country=all&ssl=all&anonymity=all'],
        ['http', 'https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=10000&country=all&ssl=all&anonymity=all'],
        ['http', 'https://www.proxy-list.download/api/v1/get?type=http'],
        ['https', 'https://www.proxy-list.download/api/v1/get?type=https'],
        ['http', 'https://free-proxy-list.net/'],
        ['http', 'https://www.kuaidaili.com/free/'],
        ['http', 'https://hidemy.io/cn/proxy-list/'],
        ['http', 'http://proxydb.net/'],
        ['http', 'https://www.aliveproxy.com/proxy-list-port-8080/'],
        ['http', 'https://www.aliveproxy.com/proxy-list-port-8000/'],
    ] if api_url is None else [['http', api_url]]
    proxies = []
    for one in paths:
        schema, path = one
        print(f'Fetching proxies from {path.split("/")[2]}...', end='\r')
        try:
            ret = get_proxies(schema, path)
            proxies += ret
            print(f'Fetch proxies from {path.split("/")[2]} success, get {len(ret)} server(s)   ')
        except Exception:
            print(f'Fetch proxies from {path.split("/")[2]} failed                 ')

    if proxies:
        if not os.path.exists(file_name):
            with open(file_name, 'w', encoding='utf-8'):
                pass  # 什么也不写入，只是创建一个空文件
        is_empty = os.path.getsize(file_name) == 0

        with open(file_name, 'a', encoding='utf-8') as file:
            if is_empty:  # 文件为空，增加内容到开头
                file.write("type	server	port	user	password\n")
            file.write('\n')
            for proxy in set(proxies):
                if proxy != '':
                    file.write('\n' + proxy.replace(':', '\t'))
            file.write('\n')
    return True


def get_speed(bytes_per_second):
    if bytes_per_second >= 1e6:  # 大于等于1兆字节/秒
        return f"{bytes_per_second / 1e6:.2f} MB/s"
    elif bytes_per_second >= 1e3:  # 大于等于1千字节/秒
        return f"{bytes_per_second / 1e3:.2f} KB/s"
    else:
        return f"{bytes_per_second:.2f} B/s"


def test_proxy(proxy_info, url, timeout=5):
    proxy_type, server, port, user, password = proxy_info

    headers = {
        'User-Agent': agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    try:
        if user and password:
            proxies = {
                'http': f'{proxy_type}://{user}:{password}@{server}:{port}',
                'https': f'{proxy_type}://{user}:{password}@{server}:{port}'
            }
        else:
            proxies = {
                'http': f'{proxy_type}://{server}:{port}',
                'https': f'{proxy_type}://{server}:{port}'
            }

        start = time.time()
        response = requests.get(url, timeout=timeout, headers=headers, proxies=proxies, verify=False)
        duration = time.time() - start  # float seconds
        speed = get_speed(len(response.content) / duration)

        preview = response.content if len(response.content) < 100 else response.content[:100] + b"..."
        preview = preview.decode('utf-8')
        if response.status_code != 200:
            preview = "HTTP " + str(response.status_code) + ": " + preview

        return ['√' if response.status_code == 200 else '¤', f'{duration:.2f}s'.rjust(6), f'{speed}'.rjust(12), preview]
    except Exception as e:
        if isinstance(e, ValueError) and str(e) == 'check_hostname requires server_hostname':
            return ['※', '      ', '            ', 'Wrong proxy type, should be HTTP but HTTPS used']
        if isinstance(e, SSLError) and 'WRONG_VERSION_NUMBER' in str(e):
            return ['※', '      ', '            ', 'Wrong proxy type, should be HTTPS but HTTP used']

        s = str(e.args[0].reason if hasattr(e.args[0], "reason") else e)
        s = re.sub(pattern, '', s).strip()
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1]  # 去掉前后 (...)
        if s.startswith("'") and s.endswith("'"):
            s = s[1:-1]  # 去掉前后 '...'
        s = s.replace("'Cannot connect to proxy.',", "Proxy error,")
        s = s.replace("Failed to establish a new connection: ", "")
        return ['×', '      ', '            ', s]


def test_task(proxy_info, url, timeout, out):
    result, duration, speed, message = test_proxy(proxy_info, url, timeout)
    message = re.sub(r'\r\n|\r|\n', ' ', message)
    host = proxy_info[1] + ":" + proxy_info[2]
    print(
        f"{result} {datetime.datetime.now():%m-%d %H:%M:%S} {proxy_info[0]:7}  {host:21}  {duration}  {speed:13}  {message}")
    if out is not None and result == '√':
        out.write(f'{proxy_info[0]}://{host}\t{duration.strip()}\t{speed.strip()}\n')
        out.flush()


def main(file, url, timeout, threads, out):
    if not os.path.exists(file):
        return

    print(f"Scanning for {args.url} with timeout {args.timeout}s and {args.threads} worker(s)...")
    with open(file, newline='') as csvfile:
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
        reader = csv.DictReader(csvfile, delimiter='\t')
        futures = []
        for row in reader:
            usr = row.get('user', None)
            pwd = row.get('password', None)
            proxy_info = (
                row['type'],
                row['server'],
                row['port'],
                usr if usr != '' else None,
                pwd if pwd != '' else None
            )
            futures.append(executor.submit(test_task, proxy_info, url, timeout, out))
        while True:  # 等待所有任务完成
            completed = [future for future in futures if future.done()]
            if len(completed) == len(futures):
                break
            sleep(1)


def exit_gracefully(signal, frame):
    print("Ctrl+C pressed...")
    os._exit(0)


signal.signal(signal.SIGINT, exit_gracefully)
if __name__ == "__main__":
    print("Hound Proxy Tester v0.2\nCopyright (C) Kingron, 2023")
    print("Project: https://github.com/kingron/ProxyTester\n")
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.epilog = help_text
    parser.add_argument('-f', dest='infile', help="proxy server list file, default: proxy.txt", default="proxy.txt")
    parser.add_argument('-n', dest='threads', type=int, help="Max concurrent threads count, default 10", default=10)
    parser.add_argument('-u', dest='url', default="https://www.baidu.com",
                        help="target url, default https://www.baidu.com")
    parser.add_argument('-t', dest='timeout', type=int, default=10, help="timeout, default 10 second")
    parser.add_argument('-a', dest='agent', default=agent, help="User agent string, default:\n" + agent)
    parser.add_argument('-o', dest='out', help="output file for good proxy")
    parser.add_argument('-d', dest="download", nargs='?', const='default',
                        help="Fetch free proxy from url DOWNLOAD, append to file which set by -f argument\n"
                             "The file lines format is ip:port")
    args = parser.parse_args()

    if args.agent is not None:
        agent = args.agent

    if args.download is not None:
        download_proxies(args.infile, args.download if args.download != 'default' else None)

    outfile = open(args.out, 'a', encoding='utf-8') if args.out else None
    main(args.infile, args.url, args.timeout, args.threads, outfile)

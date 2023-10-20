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
        if response.status_code == 200:
            return ['√', f'{duration:.2f}s'.rjust(6), f'{speed}'.rjust(12), preview]
        else:
            return ['？', f'{duration:.2f}s'.rjust(6), f'{speed}'.rjust(12), "HTTP " + str(response.status_code) + ": " + preview]
    except Exception as e:
        s = str(e.args[0].reason if hasattr(e.args[0], "reason") else e)
        s = re.sub(pattern, '', s).strip()
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1]  # 去掉前后 (...)
        if s.startswith("'") and s.endswith("'"):
            s = s[1:-1]  # 去掉前后 (...)
        s = s.replace("'Cannot connect to proxy.',", "Proxy error,")
        s = s.replace("Failed to establish a new connection: ", "")
        return ['×', '     ', '        ', s]


def test_task(proxy_info, url, timeout):
    result, duration, speed, message = test_proxy(proxy_info, url, timeout)
    message = re.sub(r'\r\n|\r|\n', ' ', message)
    host = proxy_info[1] + ":" + proxy_info[2]
    print(f"{result} {datetime.datetime.now():%m-%d %H:%M:%S} {proxy_info[0]:7}{host}\t{duration}\t{speed}\t{message}")


def main(file, url, timeout, threads):
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
            futures.append(executor.submit(test_task, proxy_info, url, timeout))
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
    print("ProxyTester v0.2\nCopyright (C) Kingron, 2023")
    print("Project: https://github.com/kingron/ProxyTester\n")
    parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
    parser.epilog = help_text
    parser.add_argument('-f', dest='infile', help="proxy server list file, default: proxy.txt", default="proxy.txt")
    parser.add_argument('-n', dest='threads', type=int, help="Max concurrent threads count, default 10", default=10)
    parser.add_argument('-u', dest='url', default="https://www.baidu.com",
                        help="target url, default https://www.baidu.com")
    parser.add_argument('-t', dest='timeout', type=int, default=10, help="timeout, default 10 second")
    parser.add_argument('-a', dest='agent', default=agent, help="User agent string, default:\n" + agent)
    args = parser.parse_args()
    if args.agent is not None:
        agent = args.agent

    main(args.infile, args.url, args.timeout, args.threads)

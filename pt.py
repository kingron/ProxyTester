import argparse
import concurrent.futures
import csv
import datetime
import re
import signal
import socket
import sys

import requests
import socks

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
executor = 0


def test_proxy(proxy_info, url, mode=0, timeout=5):
    proxy_type, server, port, user, password = proxy_info

    headers = {
        'User-Agent': agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-US;q=0.7',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
    }
    try:
        if mode == 0:
            if proxy_type == 'https':
                proxy_type = 'http'
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

            response = requests.get(url, timeout=timeout, headers=headers, proxies=proxies)
        else:
            _type = socks.PROXY_TYPE_HTTP
            if proxy_type.lower() == 'socks5':
                _type = socks.PROXY_TYPE_SOCKS5
            elif proxy_type.lower() == 'socks4':
                _type = socks.PROXY_TYPE_SOCKS4

            socks.set_default_proxy(_type, server, int(port), username=user, password=password)
            socket.socket = socks.socksocket
            response = requests.get(url, timeout=timeout, headers=headers)

        preview = response.content if len(response.content) < 100 else response.content[:100] + b"..."
        preview = preview.decode('utf-8')
        if response.status_code == 200:
            return ['√', preview]
        else:
            return ['?', "HTTP " + str(response.status_code) + ": " + preview]
    except Exception as e:
        s = str(e.args[0].reason if hasattr(e.args[0], "reason") else e)
        s = re.sub(pattern, '', s).strip()
        if s.startswith("(") and s.endswith(")"):
            s = s[1:-1]  # 去掉前后 (...)
        return ['×', s]


def test_task(proxy_info, url, mode, timeout):
    result, message = test_proxy(proxy_info, url, mode, timeout)
    message = re.sub(r'\r\n|\r|\n', ' ', message)
    host = proxy_info[1] + ":" + proxy_info[2]
    print(f"{result} {datetime.datetime.now():%Y-%m-%d %H:%M:%S}\t{proxy_info[0]:8}{host[:20]:22}\t{message}")


def main(file, url, mode, timeout, threads):
    with open(file, newline='') as csvfile:
        global executor
        executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
        reader = csv.DictReader(csvfile, delimiter='\t')
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
            executor.submit(test_task, proxy_info, url, mode, timeout)


def exit_gracefully(signal, frame):
    print("Ctrl+C pressed...")
    global executor
    if executor is not None:
        executor.shutdown(wait=False, cancel_futures=True)
    sys.exit(0)


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
    parser.add_argument('-m', dest='mode', type=int, choices=[0, 1], default=0,
                        help="proxy method, 0 = http/https, 1 = socks")
    parser.add_argument('-t', dest='timeout', type=int, default=10, help="timeout, default 10 second")
    parser.add_argument('-a', dest='agent', default=agent, help="User agent string, default:\n" + agent)
    args = parser.parse_args()
    if args.agent is not None:
        agent = args.agent

    print(f"Scanning for {args.url} with timeout {args.timeout}s ...")
    main(args.infile, args.url, args.mode, args.timeout, args.threads)

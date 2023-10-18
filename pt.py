import csv
import signal
import socket
import sys

import requests
import socks
from requests.auth import HTTPBasicAuth


def test_proxy(proxy_info, url):
    proxy_type, server, port, user, password = proxy_info

    _type = socks.PROXY_TYPE_HTTP
    if proxy_type.lower() == 'socks5':
        _type = socks.PROXY_TYPE_SOCKS5
    elif proxy_type.lower() == 'socks4':
        _type = socks.PROXY_TYPE_SOCKS4

    socks.set_default_proxy(_type, server, int(port), username=user, password=password)
    socket.socket = socks.socksocket

    try:
        response = requests.get(url, timeout=3)
        if response.status_code == 200:
            return True
    except Exception as e:
        pass

    return False


def test_proxy2(proxy_info, url):
    proxy_type, server, port, user, password = proxy_info

    try:
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
        auth = HTTPBasicAuth(user, password)
        response = requests.get(url, timeout=5, proxies=proxies, auth=auth)
        if response.status_code == 200:
            return True
    except Exception as e:
        # print(e.args[0].reason if hasattr(e.args[0], "reason") else e)
        pass

    return False


def main(file, url):
    with open(file, newline='') as csvfile:
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

            if test_proxy(proxy_info, url):
                print(f"OK\t{proxy_info}")
            else:
                print(f"--\t{proxy_info}")


def exit_gracefully(signal, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, exit_gracefully)
if __name__ == "__main__":
    print("ProxyTester v1.0\nCopyright (C) Kingron, 2023\n")
    if len(sys.argv) < 2:
        print("""Usage:
    proxytester file [url]

File format(Tab separator), type value: socks4 | socks5 | http:
type	server	port	user	password
socks5	1.2.3.4	8080	root	1234
socks4	5.6.7.8	1080		
http	www.abc.com	80	dummy	none""")
        sys.exit(1)

    file = sys.argv[1]
    url = sys.argv[2] if len(sys.argv) > 2 else "https://www.google.com"

    print(f"Scanning for {url} ...")
    main(file, url)

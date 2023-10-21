# Hound Proxy Tester

The Hound proxy tester that allows you test your proxies(http/https/socks4/socks5) on desire website, additionally it measures proxy speed time. It also allows you download proxies list from given url or free builtin server.

猎犬代理测试器，可以根据给定的代理服务器文件列表，来测试给定的目标网站是否可以通过代理访问，能够给出连接时延和下载速率报告。它也可以从互联网下载指定的URL内的代理清单并进行自动化测试，它也内置了一份默认的免费的互联网代理服务器列表供使用。

## features, 功能

- Test proxy on desire website, it's get the true availability for your target, because some proxy have rule sets or polices to disallow to access some sites.
- Report latency & speed for the real connection
- Support multithreading to improve performance
- Customized connect timeout
- Support proxy authorization, and support http/https over https proxy server as well
- Allow download/update proxy list from internet by given url or builtin free server, any internet proxy service provider website page or API was supported.
- Export passed proxies list into file

<hr/>

- 通过访问给定URL地址来实测代理服务器的可用性
- 支持输出连接时延和下载速度性能报告
- 支持自定义连接超时
- 支持多线程并发测试提高性能
- 支持代理鉴权（Basic鉴权模式），支持真正的https代理，即通过 https 代理服务器来访问 http/https 网站，但是目前绝大多数使用IP的，均为 http 代理，只不过允许通过他们访问 http/https 网站而已。真正的 https 代理服务器，一般需要域名和证书才能使用。
- 允许从互联网更新/下载代理服务器列表，程序内置了一份免费的列表可以使用。你可以指定下载地址，任意的互联网代理服务商的网页、API等均可以使用。它会智能提取网页上所有代理服务器的IP地址和端口并生成列表保存，而无论是何种网页格式。
- 支持输出测试成功的代理服务器列表到文件

## usage
```
Hound Proxy Tester v0.2
Copyright (C) Kingron, 2023
Project: https://github.com/kingron/ProxyTester

usage: pt.py [-h] [-f INFILE] [-n THREADS] [-u URL] [-t TIMEOUT] [-a AGENT]
             [-o OUT] [-d [DOWNLOAD]]

optional arguments:
  -h, --help     show this help message and exit
  -f INFILE      proxy server list file, default: proxy.txt
  -n THREADS     Max concurrent threads count, default 10
  -u URL         target url, default https://www.baidu.com
  -t TIMEOUT     timeout, default 10 second
  -a AGENT       User agent string, default:
                 Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46
  -o OUT         output file for good proxy
  -d [DOWNLOAD]  Fetch free proxy from url DOWNLOAD, append to file which set by -f argument
                 The file lines format is ip:port

File format(Tab separator), type value: socks4 | socks5 | http | https:
    type        server          port    user    password
    socks4      5.6.7.8         1080
    socks5      1.2.3.4         8080    root    1234
    https       www.xyz.com     443
    http        www.abc.com     80      dummy   none
```
## screenshots
![img.png](screen.png)

## requirements
- please install requests_httsproxy module from here: https://github.com/savandriy/requests_httpsproxy, download source, and open cmd of the source folder, and run `pip install .`
- if using python >= 3.11 or higher, it required requests==2.0.7; if using python <= 3.7, please using requests==1.26.6

## Reference
- https://www.chromium.org/developers/design-documents/secure-web-proxy/

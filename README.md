# Hound Proxy Tester

The Hound proxy tester that allows you test your proxies(http/https/socks4/socks5) on desire website, additionally it measures proxy speed time. It also allows you download proxies list from given url or free builtin server.

猎犬代理测试器，可以根据给定的代理服务器文件列表，来测试给定的目标网站是否可以通过代理访问，能够给出连接时延和下载速率报告。它也可以从互联网下载指定的URL内的代理清单并进行自动化测试，它也内置了一份默认的免费的互联网代理服务器列表供使用。

## features, 功能

- Test proxy on desire website, it's get the true availability for your target, because some proxy have rule sets or polices to disallow to access some sites.
- Report latency & speed for the real connection
- Support multithreading to improve performance
- Customized connect timeout
- Support proxy authorization, and support `HTTP/HTTPS over HTTP` and `HTTP/HTTPS over HTTPS` proxy server both
- Allow download/update proxy list from internet by given url or builtin free server, any internet proxy service provider website page or API was supported.
- Export passed proxies list into file
- Report if proxy type is wrong, for example report `Wrong proxy type, should be HTTP but HTTPS used` if set as https but the proxy server is HTTP.
- Support to verify external ip address if match the proxy or not

<hr/>

- 通过访问给定URL地址来实测代理服务器的可用性
- 支持输出连接时延和下载速度性能报告
- 支持自定义连接超时
- 支持多线程并发测试提高性能
- 支持代理鉴权（Basic鉴权模式），支持真正的https代理，即通过 https 代理服务器来访问 http/https 网站，但是目前绝大多数使用IP的，均为 http 代理，只不过允许通过他们访问 http/https 网站而已。真正的 https 代理服务器，一般需要域名和证书才能使用。
- 允许从互联网更新/下载代理服务器列表，程序内置了一份免费的列表可以使用。你可以指定下载地址，任意的互联网代理服务商的网页、API等均可以使用。它会智能提取网页上所有代理服务器的IP地址和端口并生成列表保存，而无论是何种网页格式。
- 支持输出测试成功的代理服务器列表到文件
- 错误代理类型检测和报告功能，一般以 IP 给出来的服务器都是 http 类型的代理，但许多代理供应商都错误标示了代理服务器类型为 https，实际上仅仅是支持通过 http 代理访问 https 网站(HTTP/HTTPS over HTTP)而已，这和真正的 https 代理（HTTP/HTTPS over HTTPS）是完全不同的概念，真正的 https 代理，是需要域名和SSL证书来支持的，并且你和代理服务器之间的通信是完全保密的。
- 支持验证设置代理后的IP地址验证是否与预期一致，你可以提供一个第三方的IP地址返回API接口（纯IP文本），程序内置了 https://api.ipify.org/

## usage

Just run `python pt.py -d -o result.txt`, you will get a list of working proxies servers. 

```
Hound Proxy Tester v0.3    
Copyright (C) Kingron, 2023
Project: https://github.com/kingron/ProxyTester

usage: pt.py [-h] [-f INFILE] [-n THREADS] [-u [URL]] [-t TIMEOUT] [-v [VERIFY_URL]] [-a AGENT] [-o OUT] [-d [DOWNLOAD]]

options:
  -h, --help       show this help message and exit
  -f INFILE        proxy server list file, default: proxy.txt
  -n THREADS       Max concurrent threads count, default 10
  -u [URL]         target url, default https://www.baidu.com
  -t TIMEOUT       timeout, default 10 second
  -v [VERIFY_URL]  Verify external ip address if match the proxy or not, default: https://api.ipify.org/
  -a AGENT         User agent string, default:
                   Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.46
  -o OUT           output file for good proxy
  -d [DOWNLOAD]    Fetch free proxy from url DOWNLOAD, append to file which set by -f argument
                   The file lines format is ip:port

```
## screenshots
![img.png](screen.png)

## requirements
- ~~please install requests_httsproxy module from here: https://github.com/savandriy/requests_httpsproxy, download source, and open cmd of the source folder, and run `pip install .`~~
- if using python >= 3.11 or higher, it required requests==2.0.7; if using python <= 3.7, please using requests==1.26.6
- run `pip install -r requirements.txt` then run `python pt.py`

## Reference
- https://www.chromium.org/developers/design-documents/secure-web-proxy/

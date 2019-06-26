# -*- coding: utf-8 -*-
# !/usr/bin/env python
"""
-------------------------------------------------
   File Name：     GetFreeProxy.py
   Description :  抓取免费代理
   Author :       JHao
   date：          2016/11/25
-------------------------------------------------
   Change Activity:
                   2016/11/25:
-------------------------------------------------
"""
import re
import sys
import requests
import js2py

sys.path.append('..')

from Util.WebRequest import WebRequest
from Util.utilFunction import getHtmlTree

# for debug to disable insecureWarning
requests.packages.urllib3.disable_warnings()


class GetFreeProxy(object):
    """
    proxy getter
    """

    @staticmethod
    def freeProxyFirst(page=10):
        """
        无忧代理 http://www.data5u.com/
        几乎没有能用的
        :param page: 页数
        :return:
        """
        url_list = [
            'http://www.data5u.com/',
            'http://www.data5u.com/free/gngn/index.shtml',
            'http://www.data5u.com/free/gnpt/index.shtml'
        ]
        for url in url_list:
            html_tree = getHtmlTree(url)
            ul_list = html_tree.xpath('//ul[@class="l2"]')
            for ul in ul_list:
                try:
                    yield ':'.join(ul.xpath('.//li/text()')[0:2])
                except Exception as e:
                    print(e)

    @staticmethod
    def freeProxySecond(count=100):
        """
        代理66 http://www.66ip.cn/
        :param count: 提取数量
        :return:
        """
        urls = [
            "http://www.66ip.cn/mo.php?sxb=&tqsl={count}&port=&export=&ktip=&sxa=&submit=%CC%E1++%C8%A1&textarea=",
            "http://www.66ip.cn/nmtq.php?getnum={count}&isp=0&anonymoustype=0&start=&ports=&export=&ipaddress=&area=1&proxytype=2&api=66ip",
            ]
        request = WebRequest()
        for _ in urls:
            url = _.format(count=count)
            html = GetFreeProxy.decode66ip(url).text
            print(html)
            ips = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}", html)
            for ip in ips:
                yield ip.strip()
    @staticmethod
    def decode66ip(url):
        sem = requests.session()        
        response = sem.get(url,
                    headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763",})
        #保存第一段cookie
        cookie=response.headers["Set-Cookie"]
        #print(cookie)
        js = response.text.encode("utf8").decode("utf8")
        #删除script标签并替换eval。
        js = js.replace("<script>","").replace("</script>","").replace("{eval(","{var data1 = (").replace(chr(0),chr(32))
        
        #使用js2py的js交互功能获得刚才赋值的data1对象
        context = js2py.EvalJs()
        context.execute(js)
        js_temp = context.data1
        
        #找到cookie生成语句的起始位置
        index1 = js_temp.find("document.")
        index2 = js_temp.find("};if((")
        #故技重施，替换代码中的对象以获得数据
        js_temp = js_temp[index1:index2].replace("document.cookie","data2")
        #print(js_temp)
        js_temp = 'document = {}; document.createElement = function(x){return {firstChild:{href:"http://www.66ip.cn"},innerHTML:""}}; windows={};' + js_temp
        #print(js_temp)
        context.execute(js_temp)        
        data = context.data2       
        #print(cookie) 
        cookie1=re.match(r"\_\_jsluid=(.+?);", cookie)[0]
        cookie2=re.match(r"\_\_jsl\_clearance=(.+?);", data)[0]        
        #合并cookie，重新请求网站。
        cookie = cookie1 + cookie2
        #print(cookie)
        response = sem.get(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/18.17763",
            "cookie" : cookie,
            #"Referer": url,
            #"Upgrade-Insecure-Requests": "1"
        })
        return response
    @staticmethod
    def freeProxyThird(days=1):
        """
        ip181 http://www.ip181.com/  不能用了
        :param days:
        :return:
        """
        url = 'http://www.ip181.com/'
        html_tree = getHtmlTree(url)
        try:
            tr_list = html_tree.xpath('//tr')[1:]
            for tr in tr_list:
                yield ':'.join(tr.xpath('./td/text()')[0:2])
        except Exception as e:
            pass

    @staticmethod
    def freeProxyFourth(page_count=1):
        """
        西刺代理 http://www.xicidaili.com
        :return:
        """
        url_list = [
            'http://www.xicidaili.com/nn/',  # 高匿
            'http://www.xicidaili.com/nt/',  # 透明
            'http://www.xicidaili.com/wn/',  # Https
        ]
        for each_url in url_list:
            for i in range(1, page_count + 1):
                page_url = each_url + str(i)
                tree = getHtmlTree(page_url)
                proxy_list = tree.xpath('.//table[@id="ip_list"]//tr[position()>1]')
                print(proxy_list)
                for proxy in proxy_list:
                    try:
                        yield ':'.join(proxy.xpath('./td/text()')[0:2])
                    except Exception as e:
                        pass

    @staticmethod
    def freeProxyFifth():
        """
        guobanjia http://www.goubanjia.com/
        :return:
        """
        url = "http://www.goubanjia.com/"
        tree = getHtmlTree(url)
        proxy_list = tree.xpath('//td[@class="ip"]')
        # 此网站有隐藏的数字干扰，或抓取到多余的数字或.符号
        # 需要过滤掉<p style="display:none;">的内容
        xpath_str = """.//*[not(contains(@style, 'display: none'))
                                        and not(contains(@style, 'display:none'))
                                        and not(contains(@class, 'port'))
                                        ]/text()
                                """
        for each_proxy in proxy_list:
            try:
                # :符号裸放在td下，其他放在div span p中，先分割找出ip，再找port
                ip_addr = ''.join(each_proxy.xpath(xpath_str))
                port = each_proxy.xpath(".//span[contains(@class, 'port')]/text()")[0]
                yield '{}:{}'.format(ip_addr, port)
            except Exception as e:
                pass

    @staticmethod
    def freeProxySixth():
        """
        讯代理 http://www.xdaili.cn/  已停用
        :return:
        """
        url = 'http://www.xdaili.cn/ipagent/freeip/getFreeIps?page=1&rows=10'
        request = WebRequest()
        try:
            res = request.get(url, timeout=10).json()
            for row in res['RESULT']['rows']:
                yield '{}:{}'.format(row['ip'], row['port'])
        except Exception as e:
            pass

    @staticmethod
    def freeProxySeventh():
        """
        快代理 https://www.kuaidaili.com
        """
        url_list = [
            'https://www.kuaidaili.com/free/inha/1',
            'https://www.kuaidaili.com/free/inha/2',
            'https://www.kuaidaili.com/free/inha/3',
            'https://www.kuaidaili.com/free/intr/1',
            'https://www.kuaidaili.com/free/intr/2',
            'https://www.kuaidaili.com/free/intr/3',
        ]
        for url in url_list:
            tree = getHtmlTree(url)
            proxy_list = tree.xpath('.//table//tr')
            for tr in proxy_list[1:]:
                yield ':'.join(tr.xpath('./td/text()')[0:2])

    @staticmethod
    def freeProxyEight():
        """
        秘密代理 http://www.mimiip.com  已停用
        """
        url_gngao = ['http://www.mimiip.com/gngao/%s' % n for n in range(1, 2)]  # 国内高匿
        url_gnpu = ['http://www.mimiip.com/gnpu/%s' % n for n in range(1, 2)]  # 国内普匿
        url_gntou = ['http://www.mimiip.com/gntou/%s' % n for n in range(1, 2)]  # 国内透明
        url_list = url_gngao + url_gnpu + url_gntou

        request = WebRequest()
        for url in url_list:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W].*<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyNinth():
        """
        码农代理 https://proxy.coderbusy.com/ 已停用
        :return:
        """
        urls = ['https://proxy.coderbusy.com/classical/country/cn.aspx?page=1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall('data-ip="(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})".+?>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyTen():
        """
        云代理 http://www.ip3366.net/free/
        :return:
        """
        url_type1 = ['http://www.ip3366.net/free/?stype=1&page=%s' % n for n in range(1, 4)]  # 国内高匿
        url_type2 = ['http://www.ip3366.net/free/?stype=2&page=%s' % n for n in range(1, 4)]  # 国内普通
        
        urls = url_type1 + url_type2
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxyEleven():
        """
        IP海 http://www.iphai.com/free/ng
        :return:
        """
        urls = [
            'http://www.iphai.com/free/ng',
            'http://www.iphai.com/free/np',
            'http://www.iphai.com/free/wg',
            'http://www.iphai.com/free/wp'
        ]
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>\s*?(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})\s*?</td>[\s\S]*?<td>\s*?(\d+)\s*?</td>',
                                 r.text)
            for proxy in proxies:
                yield ":".join(proxy)

    @staticmethod
    def freeProxyTwelve(page_count=2):
        """
        http://ip.jiangxianli.com/?page=
        免费代理库
        超多量
        :return:
        """
        for i in range(1, page_count + 1):
            url = 'http://ip.jiangxianli.com/?page={}'.format(i)
            html_tree = getHtmlTree(url)
            tr_list = html_tree.xpath("/html/body/div[1]/div/div[1]/div[2]/table/tbody/tr")
            if len(tr_list) == 0:
                continue
            for tr in tr_list:
                yield tr.xpath("./td[2]/text()")[0] + ":" + tr.xpath("./td[3]/text()")[0]

    @staticmethod
    def freeProxyWallFirst():
        """
        墙外网站 cn-proxy
        :return:
        """
        urls = ['http://cn-proxy.com/', 'http://cn-proxy.com/archives/218']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\w\W]<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)

    @staticmethod
    def freeProxyWallSecond():
        """
        https://proxy-list.org/english/index.php
        :return:
        """
        urls = ['https://proxy-list.org/english/index.php?p=%s' % n for n in range(1, 10)]
        request = WebRequest()
        import base64
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r"Proxy\('(.*?)'\)", r.text)
            for proxy in proxies:
                yield base64.b64decode(proxy).decode()

    @staticmethod
    def freeProxyWallThird():
        urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-1']
        request = WebRequest()
        for url in urls:
            r = request.get(url, timeout=10)
            proxies = re.findall(r'<td>(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>[\s\S]*?<td>(\d+)</td>', r.text)
            for proxy in proxies:
                yield ':'.join(proxy)


if __name__ == '__main__':
    from CheckProxy import CheckProxy

    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFirst)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySecond)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyThird)
    CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFourth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyFifth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySixth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxySeventh)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyEight)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyNinth)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyTen)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyEleven)
    # CheckProxy.checkGetProxyFunc(GetFreeProxy.freeProxyTwelve)

    # CheckProxy.checkAllGetProxyFunc()

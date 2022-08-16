import usocket
import ure
import gc
import machine
import uasyncio

from db import DB
from urllib.parse import urlencode

header = {
    'Accept':'text/plain, */*; q=0.01',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'Cache-Control': 'no-cache',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36 Edg/100.0.1185.50',
    'X-Requested-With': 'XMLHttpRequest',
}

class Response:

    def __init__(self, f):
        self.raw = f
        self.encoding = "utf-8"
        self._cached = None
        self.status_code = None
        self.reason = None
        self.headers = None
        # cookie support as dict
        self.cookies = None
        # url to see redirect targets
        self.url = None
        self.res = [
            [ure.compile('\\\\n'),''],
            [ure.compile('，'),','],
            [ure.compile('；'),';'],
            [ure.compile('：'),':'],
            [ure.compile('（'),'('],
            [ure.compile('）'),')'],
            [ure.compile('【'),'['],
            [ure.compile('】'),']'],
            [ure.compile('。'),'.'],
            [ure.compile('、'),','],
            [ure.compile(' ;'),';'],
        ]
        

    def close(self):
        if self.raw:
            self.raw.close()
            self.raw = None
        self._cached = None

    @property
    def content(self):
        if self._cached is None:
            try:
                self._cached = self.raw.read()
            finally:
                self.raw.close()
                self.raw = None
        return self._cached
    
    async def saveYoudao(self,db):
        machine.freq(240000000)
        s = ''

        tmp = self.__getStr()[50:]
        tmp = self.re(self.res,tmp)
        while tmp != None:
            s += tmp

            left = s.find('{')
            right = s.find('}')

            while left >=0 and right >= left:
                db.save(s[left:right+1])
                await uasyncio.sleep(0)
                
                s = s[right+1:]

                left = s.find('{')
                right = s.find('}')

            await uasyncio.sleep(0)

            tmp = self.__getStr()
            tmp = self.re(self.res,tmp)

        machine.freq(80000000)
        print('crawler done')
    
    def re(self,re,s):
        if s != None:
            for i in re:
                s = i[0].sub(i[1],s)
        return s

    def __getStr(self):
        getSize = 512
        byte = self.raw.read(getSize)
        if byte == b'':
            return None
        if len(byte) == getSize:
            b = self.raw.read(1)
            while len(b)!=0 and b[0]&0x80!=0:
                byte += b
                b = self.raw.read(1)
            byte += b
        s = byte.decode(self.encoding)

        # s = self.re(self.res,s)
        # print(s)
        return s

    @property
    def text(self):
        return str(self.content, self.encoding)

    def json(self):
        import ujson
        return ujson.loads(self.content)

""" method = head, get, put, patch, post, delete
url (with our without parameters)
params, cookies, headers - each as dict
if cookies are supplied, new cookies will be added
if parse_headers is false -> no cookies are returned as they are part of the header
if followRedirect = false -> the redirect URL is stored in URL
"""
def request(method, url, params=None, cookies=None, data=None, json=None, headers={}, parse_headers=True, followRedirect=True):
    if params is not None:
        if params != {}:
            url = url.rstrip('?') + '?' + urlencode(params, doseq=True)
    redir_cnt = 1
    while True:
        try:
            proto, dummy, host, path = url.split("/", 3)
        except ValueError:
            proto, dummy, host = url.split("/", 2)
            path = ""
        if proto == "http:":
            port = 80
        elif proto == "https:":
            import ussl
            port = 443
        else:
            raise ValueError("Unsupported protocol: " + proto)

        if ":" in host:
            host, port = host.split(":", 1)
            port = int(port)
        # print(host,port)
        ai = usocket.getaddrinfo(host, port, 0, usocket.SOCK_STREAM)
        ai = ai[0]
        resp_d = None
        if parse_headers is not False:
            resp_d = {}

        # print('Socket create')
        s = usocket.socket(ai[0], ai[1], ai[2])
        # 60sec timeout on blocking operations
        s.settimeout(60.0)
        try:
            # print('Socket connect')
            s.connect(ai[-1])
            if proto == "https:":
                s = ussl.wrap_socket(s, server_hostname=host)
            # print('Socket wrapped')
            s.write(b"%s /%s HTTP/1.0\r\n" % (method, path))
            # print('Socket write: ')
            # print(b"%s /%s HTTP/1.0\r\n" % (method, path))
            if "Host" not in headers:
                s.write(b"Host: %s\r\n" % host)
            # Iterate over keys to avoid tuple alloc
            for k in headers:
                s.write(k)
                s.write(b": ")
                s.write(headers[k])
                s.write(b"\r\n")
                # print(k, b": ".decode('utf-8'), headers[k], b"\r\n".decode('utf-8'))
            if cookies is not None:
                for cookie in cookies:
                    s.write(b"Cookie: ")
                    s.write(cookie)
                    s.write(b"=")
                    s.write(cookies[cookie])
                    s.write(b"\r\n")
            if json is not None:
                assert data is None
                import ujson
                data = ujson.dumps(json)
                s.write(b"Content-Type: application/json\r\n")
            if data:
                s.write(b"Content-Length: %d\r\n" % len(data))
                # print("Content-Length: %d\r\n" % len(data))
            s.write(b"Connection: close\r\n\r\n")
            if data:
                s.write(data)
                # print(data)
            print('Start reading http')
            l = s.readline()
            #print('Received protocoll and resultcode %s' % l.decode('utf-8'))
            l = l.split(None, 2)
            status = int(l[1])
            reason = ""
            if len(l) > 2:
                reason = l[2].rstrip()
            # Loop to read header data
            while True:
                l = s.readline()
                #print('Received Headerdata %s' % l.decode('utf-8'))
                if not l or l == b"\r\n":
                    break
                # Header data
                if l.startswith(b"Transfer-Encoding:"):
                    if b"chunked" in l:
                        # decode added, can't cast implicit from bytes to string
                        raise ValueError("Unsupported " + l.decode('utf-8'))
                elif l.startswith(b"Location:") and 300 <= status <= 399:
                    if not redir_cnt:
                        raise ValueError("Too many redirects")
                    redir_cnt -= 1
                    url = l[9:].decode().strip()
                    #print("Redirect to: %s" % url)
                    # set status as signal for loop
                    status = 302
                if parse_headers is False:
                    pass
                elif parse_headers is True:
                    l = l.decode()
                    # print('Headers: %s ' % l)
                    k, v = l.split(":", 1)
                    # adding cookie support (cookies are overwritten as they have the same key in dict)
                    # supplied in the request, not supported is the domain attribute of cookies, this is not set
                    # new cookies are added to the supplied cookies
                    if cookies is None:
                        cookies = {}
                    if k == 'Set-Cookie':
                        ck, cv = v.split("=", 1)
                        cookies[ck.strip()] = cv.strip()
                    # else it is not a cookie, just normal header
                    else:
                        resp_d[k] = v.strip()
                else:
                    parse_headers(l, resp_d)
        except OSError:
            s.close()
            print('Socket closed')
            raise
        # if redirect repeat else leave loop
        if status != 302:
            break
        # if redirect false leave loop
        if (status == 302) and not followRedirect:
            break
        # if 302 and redirect = true then loop
    resp = Response(s)
    resp.url = url
    resp.status_code = status
    resp.reason = reason
    if resp_d is not None:
        resp.headers = resp_d
    # adding cookie support
    resp.cookies = cookies
    return resp

def head(url, **kw):
    return request("HEAD", url, **kw)

def get(url, **kw):
    return request("GET", url, **kw)

def post(url, **kw):
    return request("POST", url, **kw)

def put(url, **kw):
    return request("PUT", url, **kw)

def patch(url, **kw):
    return request("PATCH", url, **kw)

def delete(url, **kw):
    return request("DELETE", url, **kw)

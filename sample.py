import nmap
import socket
from clojure_tools import Variable as f


def get_host_ip(words):
    """
    查询本机ip地址
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('192.168.0.1', 80))
        ip = s.getsockname()[0]
    finally:
        s.close()

    return ip


def scan_host(ip):
    """
    prefix sample '192.168.2.0/24'
    查询所有网络上有的信息
    """

    result = []
    nm = nmap.PortScanner()
    res = nm.scan(hosts=ip, arguments='-sL')
    scan = res.get('scan')
    for k, v in scan.items():
        host_infor = v.get('hostnames', )
        hostlist = [x.get('name') for x in host_infor if x.get('name') != ""]
        if len(hostlist) != 0:
            result.append((k, hostlist))
    return result


def get_dns_regional(ip):
    ip = ip
    r = ""
    if ip is not None:
        r = ip.split('.')
        r = ".".join(r[0:3])
        r = r + ".0/24"
    return r


host_self = f([
    "自己的dns",
    get_host_ip,
    scan_host,
])

host_dns_regional = f([
    "获取自己所在的作用域",
    get_host_ip,
    get_dns_regional,
])

all_host_alive_domain = f([
    host_dns_regional,
    scan_host,
])



def main():
    print("这是定义的Variable 对象", all_host_alive_domain)
    print("这是执行Variable的方法", all_host_alive_domain.value)

    
if __name__ == "main":
    main()



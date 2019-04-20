import gevent
from gevent import spawn, joinall
from gevent.monkey import patch_all
patch_all(socket=True, ssl=True)

import requests


SERVERS_LISTS = [
    'http://www.speedtest.net/speedtest-servers-static.php',
    'http://c.speedtest.net/speedtest-servers-static.php',
    'http://www.speedtest.net/speedtest-servers.php',
    'http://c.speedtest.net/speedtest-servers.php',
]



def get_servers_list_xml():
    futures = []
    for url in SERVERS_LISTS:
        future = spawn(requests.get, url)
        futures.append(future)
    
    joinall(futures)
    print("done")
    xml = ""
    for f in futures:
        resp = f.value
        print(resp.status_code)
        xml += resp.content
    return xml

def servers_from_xml(xml):
    pass

def get_closest_server(servers_list):
    pass

def get_best_server(servers_list):
    pass


def try_download(best_server):
    pass

def try_upload(best_server):
    pass

if __name__ == "__main__":
    get_servers_list()
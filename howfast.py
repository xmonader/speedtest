import gevent
from gevent import spawn, joinall
from gevent.monkey import patch_all
patch_all(socket=True, ssl=True)
import requests
from xml.etree import ElementTree
import math


def distance(origin, destination):
    """Determine distance between 2 sets of [lat,lon] in km"""

    lat1, lon1 = origin
    lat2, lon2 = destination
    radius = 6371  # km

    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) * math.sin(dlat / 2) +
         math.cos(math.radians(lat1)) *
         math.cos(math.radians(lat2)) * math.sin(dlon / 2) *
         math.sin(dlon / 2))
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    d = radius * c

    return d

SERVERS_LISTS = [
    'http://www.speedtest.net/speedtest-servers-static.php',
    'http://c.speedtest.net/speedtest-servers-static.php',
    'http://www.speedtest.net/speedtest-servers.php',
    'http://c.speedtest.net/speedtest-servers.php',
]

CONFIG_URL = "https://www.speedtest.net/speedtest-config.php"

def get_servers_list_xmls():
    futures = []
    for url in SERVERS_LISTS:
        future = spawn(requests.get, url)
        futures.append(future)
    
    joinall(futures)
    xmls = []
    for f in futures:
        resp = f.value
        xmls.append(resp.content)
    return xmls

def get_servers_from_xmls(xmls):
    servers = []

    for xml in xmls:
        root = ElementTree.fromstring(xml)

        for server in root.iter("server"):
            # calculate distance and add to servers list.
            servers.append(server)
            
    return servers


def get_closest_server(servers_list):
    pass

def get_best_server(servers_list):
    pass


def try_download(best_server):
    pass

def try_upload(best_server):
    pass

def get_config():
    # 
    pass
    

if __name__ == "__main__":
    xmls = get_servers_list_xmls()
    get_servers_from_xmls(xmls)
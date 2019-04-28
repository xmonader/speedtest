import gevent
from gevent import spawn, joinall
from gevent.monkey import patch_all
patch_all(socket=True, ssl=True, sys=True)
import requests
from xml.etree import ElementTree
import math
import timeit
import pickle
import os

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

    """
    <servers>
        <server url="http://speedtest4.xj.chinamobile.com:8080/speedtest/upload.php" lat="81.3241" lon="43.9168" name="Yili" country="China" cc="CN" sponsor="China Mobile Group XinJiang" id="17228" host="speedtest4.xj.chinamobile.com:8080"/>
        <server url="http://speedtest.oppinord.no/speedtest/upload.php" lat="70.6632" lon="23.6817" name="Hammerfest" country="Norway" cc="NO" sponsor="Hammerfest Energi Bredbånd AS" id="21239" host="speedtest.oppinord.no:8080"/>
        <server url="http://88.84.191.230/speedtest/upload.php" lat="70.0733" lon="29.7497" name="Vadso" country="Norway" cc="NO" sponsor="Varanger KraftUtvikling AS" id="4600" url2="http://speedmonster.varangerbynett.no/speedtest/upload.php" host="88.84.191.230:8080"/>
        <server url="http://speedtest.nornett.net/speedtest/upload.php" lat="69.9403" lon="23.3106" name="Alta" country="Norway" cc="NO" sponsor="Nornett AS" id="4961" url2="http://speedtest2.nornett.net/speedtest/upload.php" host="speedtest.nornett.net:8080"/>
        <server url="http://speedo.eltele.no/speedtest/upload.php" lat="69.9403" lon="23.3106" name="Alta" country="Norway" cc="NO" sponsor="Eltele AS" id="3433" host="speedo.eltele.no:8080"/>
    ...
    """
    futures = []
    for url in SERVERS_LISTS:
        future = spawn(requests.get, url)
        futures.append(future)
    
    joinall(futures)
    xmls = []
    for f in futures:
        resp = f.value
        if resp.status_code == 200:
            xmls.append(resp.content)
    return xmls

def get_servers_from_xmls(xmls):
    servers = {}

    for xml in xmls:
        root = ElementTree.fromstring(xml)

        for server in root.iter("server"):
            # calculate distance and add to servers list.
            serverinfo = server.attrib
            serverid = int(serverinfo['id'])
            servers[serverid] = serverinfo
    return servers


def get_closest_nservers(servers_list, to, n=1):
    closest = sorted(list(servers_list.values()), key=lambda server: distance((float(server['lat']),float(server['lon'])), to))
    return closest[:n]

def get_closest_server(servers_list, to):
    return get_closest_nservers(servers_list, to)[0]

def get_best_server(servers_list):
    # first only for now.
    return servers_list[0]


def try_download(best_server):
    pass

def try_upload(best_server):
    pass

def get_client_config():
    """
    <client ip="41.42.155.248" lat="31.2162" lon="29.9529" isp="TE Data" isprating="3.7" rating="0" ispdlavg="0" ispulavg="0" loggedin="0" country="EG"/>
    <server-config threadcount="4" ignoreids="1525,1716,1758,1762,1816,1834,1839,1840,1850,1854,1859,1860,1861,1871,1873,1875,1880,1902,1913,3280,3448,3695,3696,3697,3698,3699,3725,3726,3727,3728,3729,3730,3731,3733,3788,4140,4533,5085,5086,5087,5894,6130,6285,6397,6398,6412,7326,7334,7529,8591,9123,9466,9816,10221,10226,10556,10557,10558,10561,10562,10563,10564,10565,10566,10567,10901,10923,11201,11736,11737,11792,12688,12689,12861,12862,12863,13362,14209,14445,14446,14448,14804,14805,14806,14807,14808,14809,14810,14811,14812,14813,14814,14880,14881,14882,14883,14884,14908,14909,14910,14911,14946,14981,14982,14983,14984,14985,15012,15030,15034,15035,15036,15037,15079,15080,15081,15115,15181,15182,15262,15316,15359,15668,15845,15949,15950,15951,15952,15953,15954,15955,15956,15957,16030,16136,16275,16340,949,5249" notonmap="16148,17455,13544,3378,4247,9644,12549,6051,4231,12776,4139,14771,5237,17310,6385,15929,11076,5718,4810,16125,15715,3979,3088,9984,4674,988,9598,17034,5834,2151,8455,8009,6814,17040,4745,6616,2705,5681,6866,11424,3170,6563,4984,10366,6307,11266,6053,6827,10045,6562,15252,12363,8367,15418,16836,17091,10025,13185,17037,2724,4084,10469,2557,17036,1823,5045,5950,6389,4730,13152,9100,6083,17097,10323,1119,4426,3777,3704,3326,17350,10465,2721,3256,10657,6118,10258,8881,12506,5211,13040,9913,15850,13291,11365,16534,9147,13953,5651,6440,3149,13061,10586,4541,14678,17338,17160,4166,7103,15370,15213,3497,5284,7396,2706,16982,12260,11547,6151,10026,8066,5911,11123,10408,6115,4078,7352,17305,15815,10262,16152,11965,2822,6522,5326,15569,5121,5447,9264,6010,7743,6446,16747,8478,16549,2518,6195,16563,5477,6578,12212,9332,8040,14521,17312,12974,16678,17270,11465,10053,2372,8223,11181,8068,8497,17300,4297,6394,3077,17395,6225,15263,16326,12791,8836,8218,16781,17402,10676,11977,10265,1688,16676,16476,17001,15586,10176,9084,12777,6070,15904,3744,16161,6635,7567,4768,17335,11329,6057,15567,6029,5904,8879,4246,15240,9281,6433,16702,16918,16141,16325,7635,2796,5708,6101,16252,13667,17393,6689,1993,8825,12723,16754,11675,3667,5502,10264,8211,3997,16949,5623,13421,9641,14476,10703,4792,6737,6049,16067,4111,9836,9709,4089,4290,11608,16951,826,13030,3025,7537,3860,16753,2565,4049,17394,13454,9911,5210,4962,2485,13898,16653,2978,9035,5818,5652,10097,7440,6375,7617,6973,15808,2214,11348,3676,11842,5463,9508,14671,16505,6485,2605,10050,11750,7193,5919,15809,12012,15912,17311,16681,16730,2254,15199,12263,7323,4667,13873,4791,16818,10261,12536,3287,11250,1781,12652,12927,10116,8863,12557,16251,10591,6030,10546,7170,16910,16686,16888,9493,6583,6903,8109,9933,12961,7296,2268,17428,2221,12417,4168,17413,15326,7983,9560,4987,8738,3964,7192,16190,8404,13628,16157,15251,15831,1749,9540,6679,10667,10156,16785,8339,6286,15416,9942,16510,4317,7640,13583,6855,6722,7244,5303,5861,10269,7456,6047,3883,13516,6248,17249,16735,5905,9916,3864,7048,11953,12407,13655,5296,3165,13653,15853,9887,4774,1182,16613,15783,16331,2442,6074,12176,3501,16683,9384,8706,12823,16615,6559,17053,2222,3529,9951,13635,9716,6257,868,17133,16089,4632,16744,16139,7340,10614,5727,8882,11876,12497,8956,15028,15797,15992,10952,9334,12252,8906,9089,17013,7382,10444,16007,10839,10801,8631,7236,13108,9570,15630,10193,10549,13167,12384,10020,6936,4183,10194,4520,4757,13926,3385,15648,9450,12215,6031,15781,16684,6782,16122,10471,6838,11702,4938,2327,8623,11703,7429,8624,12596,4505,5334,9118,5528,8493,15131,7687,4939,4947,16991,2591,3841,12585,7076,6597,16985,11709,8628,16992,3458,4406,6321,16861,15718,9096,5020,4728,4588,17049,13242,7810,4773,12204,16993,8002,12589,12600,11712,16989,16947,3842,2189,10101,16235,6767,7198,2428,11194,2552,11430,7215,9174,8156,16416,9594,10322,9725,12694,5415,3870,6403,12775,8659,9584,12843,9049,16124,10637,6746,6454,7605,10800,7950,15224,16092,17208,15747,8978,4883,15886,5060,13384,16256,12977,15193,6749,4491,12951,10196,16487,5311,7128,9995,3984,10631,11322,17486,6261,5329,13418,6683,12718,9965,16916,14062,14059,9724,16792,16221,15872,6383,12210,7805,1169,12443,7662,6521,11823,5394,5609,7115,15492,9830,16628,6283,5431,8797,9556,1826,10560,2583,6243,2649,15535,5376,11562,9591,6455,11413,16462,7231,17078,11361,10346,10481,6432,11468,11014,15530,4706,7784,15493,11558,9966,17344,10204,8448,6756,16557,10491,14626,9282,12973,6582,15611,4182,13280,1788,2256,16460,11248,13093,9509,10574,10798,3281,8760,12409,13459,15810,10599,9603,17248,8158,9331,12635,11342,2515,15324,12473,11411,16749,8491,9668,7295,824,4836,12208,11846,16914,12632,12459,3132,15278,6537,4306,2617,7698,12942,13612,6858,6213,3917,11683,13116,4348,10327,11850,4956,17318,12895,8875,1883,7311,9575,4235,7556,5168,10769,5304,5048,10518,13258,11435,8674,8291,12616,8229,11255,8288,11102,13222,13457,8548,6370,15560,12984,12470,15854,13569,17238,13077,16348,9021,13398,12737,7804,7582,6612,11118,8874,11033,12909,10239,282,17045,7410,5248,7680,13954,5356,9856,11052,16039,11172,5963,2194,4506,2821,6110,11319,5909,12273,8261,9756,11224,16390,12207,7292,12197,7397,4958,6434,12006,7106,11815,15344,12233,13957,2157,15930,13874,13084,9104,6535,11960,5272,8370,9344,2952,15254,13566,10454,8927,15175,16082,16648,7059,11840,15443,9451,9218,16740,11735,12556,13582,17169,15983,12105,8719,16579,11314,11996,17420,15958,9266,12332,17438,13029,3825,11499,7763,11175,12814,11211,9339,6773,15071,11567,17009,15933,13982,17284,6533,11488,12322,15147,16896,15798,9000,7690,12996,16680,12668,3367,15532,9227,10990,7254,1817,6246,10312,11310,12088,12109,5889,13780,16373,16660,16203,10333,6155,1714,6200,8749,16371,16721,2171,13278,16208,17109,9749,12732,8793,13065,8017,16060,16426,16041,6355,3505,5666,11767,14329,2582,2173,10893,16429,15899,13474,13425,7318,8894,13921,5868,1818,6093,6003,12373,8453,900,16195,5181,6825,4336,16640,234,5074,4051,6359,12651,5539,16805,9974,721,8345,13676,10179,9345,8855,7393,12440,12932,16592,13057,2169,4052" forcepingid="" preferredserverid=""/>
    <download testlength="10" initialtest="250K" mintestsize="250K" threadsperurl="4"/>
    <upload testlength="10" ratio="5" initialtest="0" mintestsize="32K" threads="2" maxchunksize="512K" maxchunkcount="50" threadsperurl="4"/>
    <latency testlength="10" waittime="50" timeout="20"/>
    <socket-download testlength="15" initialthreads="4" minthreads="4" maxthreads="32" threadratio="750K" maxsamplesize="5000000" minsamplesize="32000" startsamplesize="1000000" startbuffersize="1" bufferlength="5000" packetlength="1000" readbuffer="65536"/>
    <socket-upload testlength="15" initialthreads="dyn:tcpulthreads" minthreads="dyn:tcpulthreads" maxthreads="32" threadratio="750K" maxsamplesize="1000000" minsamplesize="32000" startsamplesize="100000" startbuffersize="2" bufferlength="1000" packetlength="1000" disabled="false"/>
    <socket-latency testlength="10" waittime="50" timeout="20"/>
    <conditions>
    <cond name="tcpulthreads" download="+100000" value="8"/>
    <cond name="tcpulthreads" download="+10000" value="4"/>
    <cond name="tcpulthreads" value="2"/>
    </conditions>
    <interface template="mbps" colortcp="0"/>

    """
    config = {}
    xml = requests.get(CONFIG_URL).content
    root = ElementTree.fromstring(xml)
    client = root.find('client').attrib
    server_config = root.find('server-config').attrib
    download = root.find('download').attrib
    upload = root.find('upload').attrib
    ignore_servers = list(
        map(int, server_config['ignoreids'].split(','))
    )

    print("UPLOAD INFO: ", upload)
    ratio = int(upload['ratio'])
    upload_max = int(upload['maxchunkcount'])
    up_sizes = [32768, 65536, 131072, 262144, 524288, 1048576, 7340032]
    sizes = {
        'upload': up_sizes[ratio - 1:],
        'download': [350, 500, 750, 1000, 1500, 2000, 2500,
                        3000, 3500, 4000]
    }

    size_count = len(sizes['upload'])

    upload_count = int(math.ceil(upload_max / size_count))

    counts = {
        'upload': upload_count,
        'download': int(download['threadsperurl'])
    }

    threads = {
        'upload': int(upload['threads']),
        'download': int(server_config['threadcount']) * 2
    }

    length = {
        'upload': int(upload['testlength']),
        'download': int(download['testlength'])
    }

    lat_lon = (float(client['lat']), float(client['lon']))

    config.update({
        'client': client,
        'ignore_servers': ignore_servers,
        'sizes': sizes,
        'counts': counts,
        'threads': threads,
        'length': length,
        'upload_max': upload_count * size_count,
        'lat_lng': lat_lon,        
    })

    return config

def filter_servers(servers, ignoreids):
    before = len(servers)
    for i in ignoreids:
        if i in servers:
            del servers[i]
    after = len(servers)
    print("filtered ", after-before, "  servers..")
    return servers

def download_test(against_server, client_config):
    # print(f"executing download test against {against_server} config {client_config}")
    base_url = against_server['url']
    host_url = against_server['host']
    download_link_template = "http://{base_url}/random{size}x{size}.jpg"

    to_download = []
    download_count = client_config['counts']['download']
    download_sizes = client_config['sizes']['download']
    for i in range(download_count):
        for size in download_sizes:
            to_download.append(download_link_template.format(base_url=host_url, size=size))
    print("will test download using")
    print(to_download)

    downloaded_chunks_lens = []
    def download_one(link):
        r = requests.get(link, stream=True)
        for chunk in r.iter_content(chunk_size=10240): 
            if chunk:  # filter out keep-alive new chunks
                downloaded_chunks_lens.append(len(chunk))

    start = timeit.timeit()
    futures = []
    for link in to_download:
        futures.append(gevent.spawn(download_one, link))
    
    gevent.joinall(futures, raise_error=True, timeout=client_config['length']['download'])
    end = timeit.timeit()
    total_bytes = sum(downloaded_chunks_lens)
    speed = (total_bytes*8)/(end - start)
    print("download: ", speed/1000/1000)


def exception_callback(g):
    """Process gevent exception"""
    try:
        g.get()
    except Exception as exc:
        print(exc)


def upload_test(against_server, client_config):

    upload_url = against_server['url']
    print("uploadurl: ", upload_url)
    
    upload_count = client_config['counts']['upload']
    upload_sizes = client_config['sizes']['upload']

    def upload_one(data, size):
        r = requests.post(upload_url, data=data)
        r.raise_for_status()
        return size
    
    futures = []
    datas = {}


    # FIXME: ratio relationship with the uploadsize..
    # upload_sizes = [32768, 65536, 131072, 262144, 524288, 1048576, 7340032][:5]
    upload_sizes = [32768, 65536, 131072, 262144, 524288, 1048576, 7340032][4:]
    
    # print("upload sizes: ", upload_sizes)

    for size in upload_sizes:
        datas[size] = b"a"*size #
        # datas[size] = b"a"*524288 #*size

    requests_sizes = upload_sizes*upload_count #sorted(upload_sizes*upload_count)


    # requests_sizes = sorted(upload_sizes*upload_count)


    print(requests_sizes)

    start = timeit.timeit()
    for size in requests_sizes:
        futures.append(gevent.spawn(upload_one, datas[size], size))
        # g = gevent.spawn(upload_one, datas[size], size)
        # g.link_exception(exception_callback)
        # futures.append(g)

    gevent.joinall(futures, raise_error=True, timeout=client_config['length']['upload'])
    # gevent.wait(futures)
    end = timeit.timeit()
    total_bytes = sum([f.value for f in futures if f.successful()])
    # print("total bytes: ", total_bytes)
    speed = (total_bytes*8/(end - start))
    print("upload: ", speed/1000/1000)
    print([f.value for f in futures])
    # print([f.successful() for f in futures])
    # print([f.exception for f in futures])


if __name__ == "__main__":
    cache = "/tmp/howfast.dat"
    appsettings = {}
    if os.path.exists(cache):
        try:
            appsettings = pickle.load(open(cache))
        except:
            pass
    if 'client_config' in appsettings:
        client_config = appsettings['client_config']
    else:
        client_config = get_client_config()
        appsettings['client_config'] = client_config
    print(client_config)
    if 'servers_xmls' in appsettings:
        xmls = appsettings['servers_xmls']
    else:
        xmls = get_servers_list_xmls()
        appsettings['servers_xmls'] = xmls
    
    pickle.dump(appsettings, open(cache, "wb"))
    servers = get_servers_from_xmls(xmls)
    servers = filter_servers(servers, client_config['ignore_servers'])
    closest_5servers = get_closest_nservers(servers, client_config['lat_lng'], 5)
    # check latency..
    best_server = get_best_server(closest_5servers)
    # download_test(best_server, client_config)
    upload_test(best_server, client_config)
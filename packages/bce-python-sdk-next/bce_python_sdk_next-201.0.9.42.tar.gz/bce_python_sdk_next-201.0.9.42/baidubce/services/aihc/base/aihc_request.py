import datetime
import hmac, hashlib
import os
import time
import urllib.parse
import requests
import base64
from baidubce.bce_response import BceResponse
from urllib.parse import urlparse

# 引入环境变量配置.env文件中的配置
from dotenv import load_dotenv
load_dotenv()

def get_headers(url, method: str, ak, sk):
    domain = urllib.parse.urlparse(url).netloc
    uri = urllib.parse.urlparse(url).path
    gcloud_params = {}
    if url.find('?') > 0:
        tmp = url.split('?')[1]
        for item in tmp.split('&'):
            if item.find('=') > 0:
                gcloud_params[item.split('=')[0]] = item.split('=')[1]
            else:
                gcloud_params[item] = ""
        gcloud_uri = url.split('?')[0]

    headers = {"x-bce-date": get_canonical_time(), "Content-Type": "application/json", "Host": domain}  #
    bce_request = {
        'uri': uri,  # f"http://{domain}:8793/api/cce/service/v2/cluster/cce-lksgpvx5"
        'params': gcloud_params,
        'method': method.upper(),
        'headers': headers
    }
    # print(bce_request)
    auth = gen_authorization(bce_request, ak, sk)
    headers['Authorization'] = get_utf8_value(auth)
    return headers

def get_canonical_time(timestamp=0):
    """
    Get cannonical time.

    :type timestamp: int
    :param timestamp: None
    =======================
    :return:
        **string of canonical_time**
    """
    if timestamp == 0:
        utctime = datetime.datetime.utcnow()
    else:
        utctime = datetime.datetime.utcfromtimestamp(timestamp)
    return "%04d-%02d-%02dT%02d:%02d:%02dZ" % (
        utctime.year, utctime.month, utctime.day,
        utctime.hour, utctime.minute, utctime.second)

def gen_authorization(request, ak, sk, timestamp=None, expire_period=1800):
    """
    generate authorization string
    if not specify timestamp, then use current time;
    """
    signedheaders = []
    if "headers" in request:
        signedheaders = list(key.lower() for key in request["headers"].keys() if key != '')
        signedheaders.sort()
    authorization = build_authorization(ak, signedheaders, expire_period, timestamp)
    signingkey = _calc_signingkey(authorization, sk)
    signature = _calc_signature(signingkey, request, signedheaders)
    authorization["signature"] = signature
    return serialize_authorization(authorization)


def serialize_authorization(auth):
    """
    serialize Authorization object to authorization string
    """
    val = "/".join((auth['version'], auth['access'], auth['timestamp'], auth['period'],
                    ";".join(auth['signedheaders']), auth['signature']))
    return get_utf8_value(val)


def build_authorization(accesskey, signedheaders, period=1800, timestamp=None):
    """
    build Authorization object
    """
    auth = {}
    auth['version'] = "bce-auth-v1"
    auth['access'] = accesskey
    if not timestamp:
        auth['timestamp'] = get_canonical_time()
    else:
        auth['timestamp'] = timestamp
    auth['period'] = str(period)
    auth['signedheaders'] = signedheaders
    return auth


def _calc_signingkey(auth, sk):
    """ Get a a signing key """
    string_to_sign = "/".join((auth['version'], auth['access'],
                               auth['timestamp'], auth['period']))

    signingkey = hmac.new(bytes(sk, 'utf-8'), bytes(string_to_sign, 'utf-8'),
                          hashlib.sha256).hexdigest()
    return signingkey


def get_utf8_value(value):
    """
    Get the UTF8-encoded version of a value.
    """
    if isinstance(value, bytes):
        return value.decode('utf-8')
    return value.encode('utf-8')


def normalized_uri(uri):
    """
    Construct a normalized(except slash '/') uri
    eg. /json-api/v1/example/ ==> /json-api/v1/example/
    """
    return urllib.parse.quote(get_utf8_value(uri), safe='-_.~/')


def normalized(msg):
    """
    Construct a normalized uri
    """
    return urllib.parse.quote(get_utf8_value(msg), safe='-_.~')


def canonical_qs(params):
    """
    Construct a sorted, correctly encoded query string
    """
    keys = list(params)
    keys.sort()
    pairs = []
    for key in keys:
        if key == "authorization":
            continue
        val = normalized(params[key])
        pairs.append(urllib.parse.quote(key, safe='') + '=' + val)
    qs = '&'.join(pairs)
    return qs


def canonical_header_str(headers, signedheaders=None):
    """
    calculate canonicalized header string
    """
    headers_norm_lower = dict()
    for (k, v) in headers.items():
        key_norm_lower = normalized(k.lower())
        value_norm_lower = normalized(v.strip())
        headers_norm_lower[key_norm_lower] = value_norm_lower
    keys = list(headers_norm_lower)
    keys.sort()
    if "host" not in keys:
        raise ValueError
    header_list = []
    default_signed = ("host", "content-length", "content-type", "content-md5")
    if signedheaders:
        for key in signedheaders:
            key = normalized(key.lower())
            if key not in keys:
                raise ValueError
            if headers_norm_lower[key]:
                header_list.append(key + ":" + headers_norm_lower[key])
    else:
        for key in keys:
            if key.startswith("x-bce-") or key in default_signed:
                header_list.append(key + ":" + headers_norm_lower[key])
    return '\n'.join(header_list)


def _calc_signature(key, request, signedheaders):
    """Generate BCE signature string."""
    # Create canonical request
    params = {}
    headers = {}
    # print request
    if "params" in request:
        params = request['params']
    if "headers" in request:
        headers = request['headers']
    cr = "\n".join((request['method'].upper(),
                    normalized_uri(request['uri']),
                    canonical_qs(params),
                    canonical_header_str(headers, signedheaders)))
    signature = hmac.new(bytes(key, 'utf-8'), bytes(cr, 'utf-8'), hashlib.sha256).hexdigest()
    return signature

def aihc_request(config, response_handler_functions,
            http_method, path, body, headers, params):
    """
    封装发送请求
    """
    # 打印config.credentials的属性
    # print(dir(config))

    url = 'https://' + get_utf8_value(config.endpoint) + path
    # print(url)

    # 将params拼接到url中
    url = url + '?' + urllib.parse.urlencode(params)

    # http_method转小写
    http_method = http_method.lower()

    ak = get_utf8_value(config.credentials.access_key_id)
    sk = get_utf8_value(config.credentials.secret_access_key)
    headers.update(get_headers(url, http_method, ak, sk))
    request_func = getattr(requests, http_method)
    if params is None:
        params = {}
    if body is None:
        body = {}
    http_response = request_func(url, headers=headers, data=body)
    response = BceResponse()
    headers_list = headers
    response.set_metadata_from_headers(dict(headers_list))
    # print(response.__dict__.keys())

    for handler_function in response_handler_functions:
        if handler_function(http_response, response):
            break

    return response
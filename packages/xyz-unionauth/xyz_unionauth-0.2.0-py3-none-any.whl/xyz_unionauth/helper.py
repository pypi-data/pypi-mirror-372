# -*- coding:utf-8 -*- 
# author = 'denishuang'
from __future__ import unicode_literals, print_function

import json, base64, hashlib
from xyz_util.datautils import str2dict


def import_function(s):
    import importlib
    ps = s.split(':')
    try:
        m = importlib.import_module(ps[0])
        func = getattr(m, ps[1])
        return func
    except:
        return s


def encode_data(number, name, mobile, grade, clazz):
    s = "number=%s&name=%s&mobile=%s&grade=%s&class=%s" % (number, name, mobile, grade, clazz)
    return base64.b64encode(s.encode('utf8'))


def gen_signature(data, timestamp, token):
    s = "%s%s%s" % (data, token, timestamp)
    return hashlib.sha1(s).hexdigest()


def extract_profile(source, request):
    qs = request.query_params
    bs = qs.get("data")
    timestamp = qs.get("timestamp")
    signature = qs.get("signature")
    sign = gen_signature(bs, timestamp, source.token)
    print(bs, timestamp, source.token, signature, sign)
    if signature != sign:
        return
    s = base64.b64decode(bs).decode('utf8')
    d = str2dict(s, line_spliter='&', key_spliter='=')
    return d

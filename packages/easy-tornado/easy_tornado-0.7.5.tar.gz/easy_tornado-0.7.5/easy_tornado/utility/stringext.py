# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:24
import hashlib
import json
from json import JSONEncoder

from six import iteritems

from ..compat import utf8encode


def md5sum(text):
  """
  获取文本的MD5值
  :param text: 文本内容
  :return: md5摘要值
  """
  _ctx = hashlib.md5()
  _ctx.update(text.encode('utf-8'))
  return _ctx.hexdigest()


def parse_json(json_str):
  """
  将json字符串解析为Python数据
  :param json_str: json字符串
  :return: python对象(dict)
  """
  return json.loads(json_str)


from_json = parse_json


def as_json(subject, **kwargs):
  """
  将subject转换为json字符串
  :param subject: 待转换对象
  :type subject: object
  :param kwargs: 其余参数
  :return: 字符串
  """
  if 'ensure_ascii' not in kwargs:
    kwargs['ensure_ascii'] = False
  utf8 = 'utf8' in kwargs
  if utf8:
    kwargs.pop('utf8')
  data = json.dumps(_ensure_type(subject), **kwargs)
  return utf8encode(data) if utf8 else data


to_json = as_json


def is_json_map(value):
  """
  判断是否为json对象
  :param value: 带判断的字符串
  :return: 符合返回True
  """
  return value.startswith('{"') and value.endswith('}')


def _ensure_type(subject):
  if not (
    subject is None
    or isinstance(subject, bool)
    or isinstance(subject, tuple)
    or isinstance(subject, list)
    or isinstance(subject, set)
    or isinstance(subject, str)
    or isinstance(subject, int)
    or isinstance(subject, float)
    or isinstance(subject, dict)
    or isinstance(subject, JSONEncoder)
  ):
    return str(subject)

  if isinstance(subject, tuple):
    return tuple(_ensure_type(x) for x in subject)
  elif isinstance(subject, list):
    return list(_ensure_type(x) for x in subject)
  elif isinstance(subject, set):
    return list(_ensure_type(x) for x in subject)
  elif isinstance(subject, dict):
    return {
      k: _ensure_type(v) for k, v in iteritems(subject)
    }
  return subject

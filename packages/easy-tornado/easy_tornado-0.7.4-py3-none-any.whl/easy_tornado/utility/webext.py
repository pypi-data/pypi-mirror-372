# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:32
import urllib

import six
from six.moves import xrange

from .collection import Iterable
from .stringext import to_json
from ..compat import C_StandardError


class TimeoutError(Exception):
  """
  # 超时标记接口
  """
  pass


def build_url(host, port, context, uri, schema='http'):
  """
  构建url
  :param host: 主机
  :param port: 端口
  :param context: 上下文
  :param uri: URI路径
  :param schema: 请求模式
  :return: 完整的url
  """
  assert schema == 'http' or schema == 'https'
  return '{}://{}:{}{}{}'.format(schema, host, port, context, uri)


def request(request_url, headers=None, data=None, as_json=True, timeout=None):
  """
  发送HTTP请求
  :param request_url: 请求url
  :param headers: 头部
  :param data: 请求数据
  :param as_json: 是否以json格式发送数据
  :param timeout: 超时时间
  :return: 响应结果或超时异常
  """
  kwargs = dict()
  if timeout is not None:
    kwargs['timeout'] = timeout

  _headers = dict()
  if headers is not None:
    assert isinstance(headers, dict)
    _headers.update(headers)

  result = None
  if six.PY2:
    from urllib2 import Request
    from urllib2 import build_opener
    from urllib2 import HTTPCookieProcessor
    from urllib2 import URLError

    req = Request(request_url, headers=_headers)
    opener = build_opener(HTTPCookieProcessor())
    if data is not None:
      if as_json:
        data = to_json(data, utf8=True)
      else:
        data = urllib.urlencode(data)
    try:
      response = opener.open(req, data, **kwargs)
      result = response.read()
    except URLError as e:
      # e.reason: 输出如，[Errno 61] Connection refused，但Mac和Unix的Errno不一样
      if str(e.reason).find('Connection refused') != -1:
        raise TimeoutError
    except C_StandardError as e:
      if e.message == 'timed out':
        raise TimeoutError
  else:
    from urllib3 import PoolManager
    from urllib3.exceptions import MaxRetryError
    from urllib3.exceptions import NewConnectionError
    from urllib3.exceptions import ReadTimeoutError
    from urllib3.exceptions import RequestError

    http = PoolManager()
    if data is not None:
      if as_json:
        kwargs['body'] = to_json(data, utf8=True)
      else:
        kwargs['fields'] = data
    try:
      response = http.request(
        'POST', request_url, headers=_headers, **kwargs
      )
      result = response.data
    except RequestError as e:
      if isinstance(e, MaxRetryError) \
        and isinstance(e.reason, NewConnectionError):
        raise TimeoutError
      if isinstance(e, ReadTimeoutError):
        raise TimeoutError
  return result


def fetch_available_port(host='127.0.0.1', used_ports=None, port_range=None):
  """
  获取可用的端口号
  :param host: 主机
  :param used_ports: 端口
  :param port_range: 端口范围
  :return: 端口号
  """
  import socket

  if used_ports is None:
    used_ports = []

  if port_range is None:
    port_range = xrange(50000, 63000)
  else:
    if not isinstance(port_range, Iterable):
      s = 'port_range should be of Iterable type, but got {}'
      raise ValueError(s.format(type(port_range)))

  for port in port_range:
    if port in used_ports:
      continue

    try:
      sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
      sk.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
      sk.bind((host, port))
      sk.close()
      return port
    except C_StandardError as e:
      if str(e.args[1]) == 'Address already in use':
        continue
  raise C_StandardError('Can\'t get any available port')

# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018年8月23日 14:26:49
import asyncio
import json
import time
from concurrent.futures import ThreadPoolExecutor
from functools import partial

from tornado.concurrent import run_on_executor
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPError
from tornado.httpclient import HTTPRequest
from tornado.httpclient import HTTPResponse
from tornado.web import RequestHandler

from ..compat import C_StandardError
from ..compat import utf8decode
from ..utility.datetime import current_datetime
from ..utility.httpclient import json_print
from ..utility.printext import it_print
from ..utility.stringext import to_json


class WebApplicationHandler(RequestHandler):
  # 全局信息
  global_map = dict()

  # 错误信息
  error_mapper = dict()

  # 正常响应
  none = 0
  error_mapper[none] = 'none'

  # 无效请求(参数错误)
  invalid_request = 1001
  error_mapper[invalid_request] = 'request param is invalid'

  # 数据未找到
  not_found = 4004
  error_mapper[not_found] = 'not found'

  # 操作不支持
  not_support = 5001
  error_mapper[not_support] = 'not support'

  # 本系统错误
  system_error = 5002
  error_mapper[system_error] = 'system error'

  # 内部服务器错误
  internal_server = 5003
  error_mapper[internal_server] = 'internal server'

  # 请求超时
  request_timeout = 5005
  error_mapper[request_timeout] = 'request timeout'

  # 调试模式
  debug = False

  # 开发模式
  devel = True

  # 作为后台进程运行
  daemon = True

  default_key = 'default'

  data_key = 'data'

  r_data_key = 'r_data'

  q_data_key = 'q_data'

  # 线程池执行器
  executor = None

  @staticmethod
  def setup_config(**kwargs):
    cls = WebApplicationHandler
    cls.debug = kwargs.pop('debug', cls.debug)
    cls.devel = kwargs.pop('devel', cls.devel)
    cls.daemon = kwargs.pop('daemon', cls.daemon)
    cls.executor = kwargs.pop('executor', ThreadPoolExecutor(1))

  @run_on_executor
  def apply_async(self, invoker):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    invoker()

  @staticmethod
  def persist(**kwargs):
    pass

  @staticmethod
  def restore(**kwargs):
    cls = WebApplicationHandler
    cls.global_map.update(kwargs)

  # 加载为json数据
  def load_request_data(self):
    try:
      if self.debug:
        it_print(self.request.body)
      body = utf8decode(self.request.body)
      params = json.loads(body) if body != '' else dict()
      # 加入私有属性作为数据，否则params为空，被if not判断为真
      params['_uri'] = self.request.uri
      if self.debug:
        params['request_time'] = current_datetime()
        self.pretty_it_print(params)
    except ValueError:
      return False
    return params

  # 加载query数据
  def load_query_data(self):
    try:
      if self.debug:
        it_print(self.request.query)
      params = {
        k: [utf8decode(x) for x in v]
        for k, v in self.request.query_arguments.items()
      }
    except ValueError:
      return False
    return params

  # 异步转发请求
  @staticmethod
  def async_forward(url, data=None, callback=None,
                    method='POST', timeout=3600):
    if callback is None:
      def empty_fn(_):
        pass

      callback = empty_fn

    _data = dict()
    if data is not None:
      assert isinstance(data, dict)
      _data.update(data)

    json_data = to_json(_data)
    client = AsyncHTTPClient()
    future = client.fetch(
      url, body=json_data, method=method, request_timeout=timeout
    )

    def handle_future(_future):
      exc = future.exception()
      if isinstance(exc, HTTPError) and exc.response is not None:
        response = exc.response
      elif exc is not None:
        request = HTTPRequest(url)
        response = HTTPResponse(
          request, 599, error=exc,
          request_time=time.time() - request.start_time)
      else:
        response = _future.result()
      client.io_loop.add_callback(callback, response)

    future.add_done_callback(handle_future)

  # 同步转发请求
  async def forward(self, url, data=None, callback=None,
                    method='POST', timeout=3600):
    if callback is None:
      callback = partial(self.response, inplace=True)

    _data = dict()
    if data is not None:
      assert isinstance(data, dict)
      _data.update(data)

    json_data = to_json(_data)
    client = AsyncHTTPClient()
    response = await client.fetch(
      url, body=json_data, method=method,
      request_timeout=timeout, connect_timeout=timeout
    )
    return callback(response)

  def success_response(self, data=None, inplace=False):
    if inplace:
      self.error_response(data.pop('errno'), data.pop('error'), data)
    else:
      self.error_response(self.none, self.error_mapper[self.none], data)

  def error_response(self, errno=invalid_request, error=None, data=None):
    res = dict()
    if data is not None:
      assert isinstance(data, dict)
      res.update(data)

    res['errno'] = errno
    if error is None:
      error = self.error_mapper[errno]
    res['error'] = error

    self.__json_response(res)

  def text_response(self, text):
    self.__output_response(text)

  def json_response(self, data):
    self.__json_response(data)

  def __json_response(self, data):
    if self.debug:
      data['response_time'] = current_datetime()
      self.pretty_it_print(data)
    self.__output_response(to_json(data, sort_keys=True))

  def __output_response(self, data):
    self.write(data)
    self.finish()

  # 默认响应处理器
  def response(self, response, inplace=False):
    try:
      if self.debug:
        it_print(response.body)
      result = json.loads(response.body)
    except ValueError:
      return self.error_response(errno=self.system_error)
    return self.success_response(result, inplace=inplace)

  def data_received(self, chunk):
    pass

  @staticmethod
  def pretty_it_print(data):
    json_print(data)

  @staticmethod
  def exists(key):
    return key in WebApplicationHandler.global_map

  @staticmethod
  def store(key, value):
    self = WebApplicationHandler
    self.global_map[key] = value

  @staticmethod
  def release(key):
    self = WebApplicationHandler
    if self.exists(key):
      self.global_map.pop(key)

  @staticmethod
  def retrieve(key, default=None):
    self = WebApplicationHandler
    if self.exists(key):
      return self.global_map[key]
    return default

  def p(self, key, data=None, **kwargs):
    if key in data:
      return data[key]

    if self.default_key in kwargs:
      return kwargs[self.default_key]

    raise C_StandardError(
      'request parameter [{}] does not present'.format(key)
    )

  def q(self, key, data=None, multiple=False, type_fn=str, **kwargs):
    if data is None:
      data = self.load_query_data()

    if key not in data:
      if self.default_key in kwargs:
        return kwargs[self.default_key]

      return C_StandardError(
        'query parameter [{}] does not present'.format(key)
      )

    values = data[key]
    if multiple:
      return [type_fn(x) for x in values]
    return type_fn(values[0])

  def v(self, key, **kwargs):
    if self.data_key in kwargs:
      data = kwargs[self.data_key]
      if key in data:
        return data[key]

    if self.q_data_key in kwargs:
      data = kwargs[self.q_data_key]
    else:
      data = self.load_query_data()
    if key in data:
      values = data[key]
      multiple = kwargs.pop('multiple', False)
      type_fn = kwargs.pop('type_fn', str)
      if multiple:
        return [type_fn(x) for x in values]
      return type_fn(values[0])

    if self.r_data_key in kwargs:
      data = kwargs[self.r_data_key]
    else:
      data = self.load_request_data()
    if key in data:
      return data[key]

    if self.default_key in kwargs:
      return kwargs[self.default_key]

    raise C_StandardError(
      'parameter [{}] does not present'.format(key)
    )

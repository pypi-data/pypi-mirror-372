# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:25
from __future__ import print_function

from .datetime import Timer
from .printext import it_print
from .stringext import parse_json
from .stringext import to_json
from .webext import request


def print_indent(message):
  """
  缩进打印
  :param message: 待打印消息
  """
  it_print(message, indent=2)


def print_prefix(subject, msg=None):
  """
  以某个消息为前缀打印
  :param subject: 打印内容
  :param msg: 消息前缀
  """
  if msg is not None:
    subject = msg + ' ' + subject
  it_print(subject)


def print_dict(data, msg=None):
  """
  打印字典
  :param data: 数据
  :param msg: 消息提要
  """
  if msg is not None:
    it_print(msg)
  for key in data:
    value = data[key]
    print_indent('{} => {}'.format(key, value))


def json_print(data):
  """
  以json形式打印
  :param data: 待打印数据
  """
  it_print(to_json(data, indent=2, sort_keys=True, ensure_ascii=False))


def print_json(json_string):
  """
  打印json字符串
  :param json_string: json字符串
  :return:
  """
  json_print(parse_json(json_string))


class HttpTest(object):
  """
  Http API测试工具
  """
  debug = True

  def __init__(self, url=None):
    self.url = url

  def set_url(self, host, context, port=80, https=False):
    schema = 'https' if https else 'http'
    self.url = '{}://{}:{}{}'.format(schema, host, port, context)

  def request_url(self, url, data=None, as_json=True, timeout=None):
    # 请求地址
    request_url = url
    if self.debug:
      print_prefix(request_url, "url:")

    # 请求数据
    if data is None:
      data = {}

    if self.debug:
      # 起始时间
      timer = Timer()
      timer.display_start("request at: ")

      # 打印请求数据
      it_print("request:")
      if len(data) != 0:
        json_print(data)

    # 发起请求
    res = request(request_url, data, as_json, timeout)

    if self.debug:
      timer.finish()
      # 打印结果
      it_print("response:")
      if res is not None:
        print_json(res)
      else:
        it_print()

      # 结束时间
      timer.display_finish("finished at: ")
      it_print("time cost: {} s".format(timer.cost()))

      it_print()
    return res

  def request(self, uri, data=None, as_json=True, timeout=None):
    return self.request_url('{}{}'.format(self.url, uri), data, as_json, timeout)

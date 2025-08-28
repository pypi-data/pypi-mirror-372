# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:03
import json

from .printext import it_print
from ..compat import C_StandardError


class InternalError(C_StandardError):

  def __init__(self, *args, **kwargs):
    super(InternalError, self).__init__(*args, **kwargs)


def raise_print(*args, **kwargs):
  """
  print message and raise InternalError
  :param args: see it_print
  :param kwargs: it_print
  """
  _do_print(*args, **kwargs)
  message = kwargs.pop('message', 'Unknown')
  raise InternalError(message)


def exit_print(*args, **kwargs):
  """
  print message and exit
  :param args: see it_print
  :param kwargs: see it_print
  """
  _do_print(*args, **kwargs)
  errno = kwargs.pop('errno', 0)
  exit(int(errno))


def _do_print(*args, **kwargs):
  if 'device' not in kwargs:
    kwargs['device'] = 2

  print_fn = kwargs.pop('print_fn', it_print)
  print_fn(*args, **kwargs)


def try_trace_json(data, e, offset=50, ignore=False, prefix=''):
  """
  跟踪JSON解码错误的具体位置
  :param data: 原始数据
  :param e: 异常实例
  :param offset: 打印错误位置偏移
  :param ignore: 若为JSON解码错误是否忽略
  :param prefix: 前置打印消息
  :return:
  """
  if isinstance(e, json.decoder.JSONDecodeError):
    start = max(0, e.pos - offset)
    end = min(len(data), e.pos + offset)
    print_fn = it_print if ignore else raise_print
    print_fn('%s%s' % (prefix, data[start:end]), device=2)

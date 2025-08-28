# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:30
from six.moves import xrange

from .collection import Iterable


def contain_keys(data, *keys):
  """
  检测字典data中是否包含指定的所有键
  :param data: 数据
  :param keys: 键集
  :return: 若data包含keys中所有键则返回True, 否则返回False
  """
  if len(keys) == 1:
    keys = keys[0]

  if not isinstance(keys, Iterable):
    return False

  for key in keys:
    if key not in data:
      return False
  return True


def in_range(num, range_from, range_to):
  """
  检测数字是否在范围[range_from, range_to]内
  :param num: 待检测数值
  :param range_from: 起始范围
  :param range_to: 结束范围
  :return: 若num在范围内返回True, 否则返回False
  """
  return num in xrange(range_from, range_to + 1)

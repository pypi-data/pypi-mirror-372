# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:01
from typing import Iterable


def unique_list(items):
  """
  获取无重复的列表
  :param items: 可迭代对象
  :return: 无重复的list对象
  """
  if not isinstance(items, Iterable):
    return items
  return list(set(items))

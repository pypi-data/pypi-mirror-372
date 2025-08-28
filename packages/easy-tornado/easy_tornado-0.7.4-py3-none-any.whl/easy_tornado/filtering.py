# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/11 12:42
from six import exec_


def filter_dict_object(data, *keys, **kwargs):
  """
  获取字典中想要/不要的键, 取决于kwargs参数
  :param data: 字典对象
  :param keys: 需要保留的键
  :param kwargs: 关键字参数
  :return 过滤掉的字典内容
  """
  if not isinstance(data, dict):
    raise TypeError('expected dict type, but got {}'.format(type(data)))
  result = dict()
  keep = False
  if 'keep' in kwargs and kwargs.pop('keep'):
    keep = True
  all_keys = list(data.keys())
  for key in all_keys:
    if keep:
      if key not in keys:
        result[key] = data.pop(key)
    else:
      if key in keys:
        result[key] = data.pop(key)
  return result


def filter_module_methods(module_object, filter_fn=None):
  """
  列出模块方法
  :param module_object: 模块对象
  :param filter_fn: 过滤函数 lambda 方法名: bool
  :return: 满足条件的方法列表
  """

  def _filter_fn_default(x):
    return x.strip() != '' and x[0].islower() and not (x.startswith('_') or x.startswith('__'))

  def _filter_fn_method(x, _):
    exec_('import sys')
    return eval('callable(sys.modules[_.__name__].{})'.format(x))

  if filter_fn is None:
    filter_fn = _filter_fn_default

  def fn(x):
    return filter_fn(x) and _filter_fn_method(x, module_object)

  return list(filter(fn, dir(module_object)))

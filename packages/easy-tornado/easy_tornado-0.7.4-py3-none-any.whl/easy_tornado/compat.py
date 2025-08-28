# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/14 10:53
import sys

import six

python2 = six.PY2
python3 = six.PY3

if python2:
  C_StandardError = Exception
  C_MAXINT = sys.maxint

  from six.moves import reload_module

  reload_module(sys)
  sys.setdefaultencoding('utf-8')
elif python3:
  C_StandardError = BaseException
  C_MAXINT = sys.maxsize


def cse_message(e):
  """
  获取异常消息
  :param e: 异常实例
  :return: 异常消息
  """
  assert isinstance(e, C_StandardError)

  if python2:
    result = e.message
    if result == '':
      result = str(e)
    return result

  if python3:
    if len(e.args) >= 1:
      return e.args[0]
    return ''


def utf8decode(text):
  """
  将text解码为unicode
  :param text: 待解码字符
  :return: 解码后的内容
  """
  return text.decode('utf-8')


utf8_decode = utf8decode


def utf8encode(text):
  """
  将text编码为UTF8
  :param text: 待编码内容
  :return: UTF8编码
  """
  return text.encode('utf-8')


utf8_encode = utf8encode

TYPE_NAME = 'type' if python2 else 'class'
TYPE_FUNCTION = "<{} 'function'>".format(TYPE_NAME)
TYPE_CLASS = "<{} 'type'>".format(TYPE_NAME)


def compat_warning(new_module, *functions):
  """
  用于无警告移动函数
  :param new_module: 新模块
  :param functions: 移动的函数名
  """
  import warnings

  class_count, func_count = 0, 0
  moved_classes, moved_functions = [], []
  for fn in functions:
    type_name = str(type(fn))
    if type_name == TYPE_CLASS:
      class_count += 1
      moved_classes.append(fn.__name__)
    elif type_name == TYPE_FUNCTION:
      func_count += 1
      moved_functions.append(fn.__name__)

  kwargs = {
    'module_name': new_module.__name__,
    'class_count': class_count,
    'func_count': func_count,
    'moved_classes': ','.join(moved_classes),
    'moved_functions': ','.join(moved_functions),

  }

  fmts = ['\n', 'Compatibility warning!\n']
  _fmts = ['  ']
  if class_count > 0:
    _fmts.append('{class_count} classes and ')
  if func_count > 0:
    _fmts.append('{func_count} functions ')
  _fmts.append('have been moved to "{module_name}".\n')
  fmts.append(''.join(_fmts))

  if class_count > 0:
    fmts.append('  classes: "{moved_classes}".\n')
  if func_count > 0:
    fmts.append('  functions: "{moved_functions}".\n')
  fmts.append('  please upgrade to the newest version.')

  warnings.warn(''.join(fmts).format(**kwargs))

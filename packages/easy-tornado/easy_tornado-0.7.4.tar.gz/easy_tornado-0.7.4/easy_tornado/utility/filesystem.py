# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:07
import codecs
import hashlib
import io
import os
import shutil
import subprocess
import tempfile
from functools import partial

from decorator import contextmanager

from .collection import Iterable
from .stringext import from_json
from .stringext import to_json
from ..compat import utf8encode


def abspath(file_obj):
  """
  获取文件绝对路径, 一般在调用文件传__file__对象
  :param file_obj: 文件对象
  :return: 文件的绝对路径
  """
  return os.path.abspath(file_obj)


def absdir(file_obj):
  """
  获取文件所在目录绝对路径, 一般在调用文件传__file__对象
  :param file_obj: 文件对象
  :return: 文件的所在的目录的绝对路径
  """
  _abspath = abspath(file_obj)
  return os.path.dirname(_abspath)


def dirname(path):
  """
  获取路径父路径
  :param path: 路径
  :return: 父路径
  """
  return os.path.dirname(path)


def file_exists(path):
  """
  判断文件是否存在
  :param path: 文件路径
  :return: 文件存在返回True, 否则返回False
  """
  return os.path.islink(path) or os.path.exists(path)


def file_size(path):
  """
  获取文件大小
  :param path: 文件路径
  :return: 文件大小
  """
  return os.path.getsize(path)


def file_lines(path):
  """
  获取文件行数, 通过Shell命令
  :param path: 文件路径
  :return: 文件行数
  """
  if not file_exists(path):
    return -1

  return sum(1 for _ in open(path))


def remove_file(path, ignore_errors=True):
  """
  移除文件(文件及目录)
  :param path: 文件路径
  :param ignore_errors: 是否忽略错误
  :raise 若路径不存在, 则无操作; 若路径既非文件且又非目录则产生ValueError
  """
  if not file_exists(path):
    return

  if os.path.isfile(path) or os.path.islink(path):
    os.remove(path)
  elif os.path.isdir(path):
    shutil.rmtree(path, ignore_errors=ignore_errors)
  else:
    raise ValueError('path should be either a file or directory')


def create_if_not_exists(path):
  """
  如果对应路径不存在的话，则进行创建
  :param path: 文件路径
  :return 若文件已存在且非目录, 抛出ValueError异常
  """
  if os.path.exists(path) and not os.path.isdir(path):
    raise ValueError('path {} exists but is not a directory')

  if not os.path.exists(path):
    os.makedirs(path, exist_ok=True)


def concat_path(base_path, sub_path=None, utf8=False):
  """
  拼接路径
  :param base_path: 基本路径
  :param sub_path: 子路径
  :param utf8: 控制是否使用utf8编码(如传输C库)
  :return: 拼接后的路径
  """
  assert base_path is not None
  if sub_path is None:
    path = base_path
  else:
    path = os.path.join(base_path, sub_path)
  return utf8encode(path) if utf8 else path


"""
  拼接路径函数别名
"""
cp = concat_path

"""
  拼接作为C库的路径参数
"""
clp = partial(concat_path, utf8=True)


def is_abspath(file_path):
  """
  判断是否为绝对路径
  :param file_path: 文件路径
  :return: 若为绝对路径返回True, 否则返回False
  """
  cond = file_path is not None and isinstance(file_path, str)
  return cond and file_path.startswith('/')


def basename(file_path):
  return os.path.basename(file_path)


def refine_path(base_path, holder, key):
  """
  修正路径(将holder中key对应的值增加base_path)
  :param base_path: 基本路径
  :param holder: 路径容器
  :param key: 路径键或索引
  """
  if isinstance(holder, dict):
    assert key in holder
  elif isinstance(holder, list):
    assert isinstance(key, int) and 0 <= key < len(holder)
  else:
    s = 'holder should be either dict or list, but got {}'
    raise TypeError(s.format(type(holder)))

  if not is_abspath(holder[key]):
    holder[key] = cp(base_path, holder[key])


def file_md5sum(file_path):
  """
  计算文件的MD5值
  :param file_path: 文件路径
  :return: 文件MD5
  """
  if not os.path.isfile(file_path):
    return
  ctx = hashlib.md5()
  with open(file_path, 'rb') as fp:
    while True:
      b = fp.read(8096)
      if not b:
        break
      ctx.update(b)
  return ctx.hexdigest()


def file_append(path_append_to, path_append_from):
  """
  将path_append_from的文件内容追加文件到path_append_to中
  :param path_append_to: 待追加内容的文件
  :param path_append_from: 待追加内容所在文件
  :return: 追加结果
  """
  kwargs = {
    'path_append_from': path_append_from,
    'path_append_to': path_append_to
  }
  if not file_exists(path_append_to):
    cmd_create_fmt = 'cp {path_append_from} {path_append_to}'
    cmd_create_str = cmd_create_fmt.format(**kwargs)
    try:
      subprocess.check_call(cmd_create_str, shell=True)
    except subprocess.CalledProcessError:
      return False
  else:
    cmd_append_fmt = 'cat {path_append_from} >> {path_append_to}'
    cmd_append_str = cmd_append_fmt.format(**kwargs)
    try:
      subprocess.check_call(cmd_append_str, shell=True)
    except subprocess.CalledProcessError:
      return False
  return True


def load_file_contents(path, pieces=True, strip=True, glue='', **kwargs):
  """
  读取文件内容
  :param path: 文件路径
  :param pieces: 是否按行返回
  :param strip: 是否对每行进行strip操作
  :param glue: 将pieces连接在一起的符号
  :return: 若文件不存在返回None, 若可正确读取则返回按行分割的内容列表
  """
  if not file_exists(path):
    return None

  if 'encoding' not in kwargs:
    kwargs['encoding'] = 'UTF-8'

  with codecs.open(path, 'r', **kwargs) as fp:
    lines = fp.readlines()
    if strip:
      lines = [x.strip() for x in lines]

    if pieces:
      return lines

    return glue.join([x for x in lines])


def load_json_contents(path):
  return from_json(load_file_contents(path, pieces=False, strip=True))


def write_line(wfp, line):
  """
  向文件中写入一行
  :param wfp: 文件写对象
  :param line: 行内容
  """
  if wfp:
    wfp.write(line.strip())
    wfp.write('\n')


def write_pid(path, **kwargs):
  """
  将pid写入到路径所在文件
  :param path: 路径
  """
  if 'encoding' not in kwargs:
    kwargs['encoding'] = 'UTF-8'
  with codecs.open(path, 'w', **kwargs) as wfp:
    wfp.write(str(os.getpid()))


def write_file_contents(path, contents, newline=False, **kwargs):
  """
  写入内容至文件
  :param path: 文件路径
  :param contents: 待写入内容
  :param newline: 是否追加新行
  """
  if 'encoding' not in kwargs:
    kwargs['encoding'] = 'UTF-8'
  with codecs.open(path, 'w', **kwargs) as wfp:
    wfp.write(contents)
    if newline:
      wfp.write('\n')


def write_json_contents(path, data, newline=False):
  """
  写入JSON内容
  :param path: 文件路径
  :param data: 待写入数据
  :param newline: 是否追加新行
  """
  json_str = to_json(data)
  write_file_contents(path, json_str, newline=newline)


def write_iterable_contents(path, iterable_obj, obj2line_func=lambda x: x):
  """
  将可迭代的数据按行的形式写入文件
  :param path: 文件路径
  :param iterable_obj: 可迭代对象
  :param obj2line_func: 将对象映射为行的函数
  """
  with open(path, 'w') as wfp:
    for obj in iterable_obj:
      write_line(wfp, obj2line_func(obj))


@contextmanager
def work_dir(path=None):
  cwd = os.getcwd()
  try:
    if path is not None:
      os.chdir(path)
      yield
  finally:
    os.chdir(cwd)


@contextmanager
def mkdtemp():
  """
  创建临时路径, 并在退出域时删除该路径
  :return 临时路径
  """
  path = tempfile.mkdtemp()
  create_if_not_exists(path)
  yield path
  shutil.rmtree(path)


@contextmanager
def mkstemp():
  """
  创建临时文件, 并在退出域时删除该路径
  :return 临时路径
  """
  path = tempfile.mkstemp()
  yield path[1]
  remove_file(path[1])


@contextmanager
def open_files(*paths, **kwargs):
  """
  批量打开文件
  :param paths: 文件路径
  :param kwargs: 关键字参数(包含打开文件句柄的函数open_fn及相应的函数调用关键字参数)
  :return: 文件句柄
  """
  handles = []
  if not isinstance(paths, Iterable):
    paths = [paths]

  open_fn = kwargs.pop('open_fn', io.open)
  if not callable(open_fn):
    s = 'open_fn should be callable type, but got {}'
    raise TypeError(s.format(type(open_fn)))

  for path in paths:
    handles.append(open_fn(path, **kwargs))

  yield handles

  for handle in handles:
    handle.close()

# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:28
from __future__ import division

import datetime
import time

from .printext import it_print
from ..functional import deprecated


def current_timestamp():
  """
  获取当前时间戳
  :return: 时间戳
  """
  return time.time()


def current_datetime_r():
  """
  获取当前datetime
  :return: 时间戳
  """
  return datetime.datetime.now()


def current_datetime(timestamp=None):
  """
  获取当前日期
  :param timestamp: 时间戳
  :return: 日期时间格式字符串 形如 2018-11-19 10:20:35
  """
  return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(timestamp))


def current_datetime_str(timestamp=None):
  """
  获取当前时间戳对应的日期时间字符串
  :param timestamp: 时间戳
  :return: 日期时间字符串 形如 20181119102035
  """
  return time.strftime("%Y%m%d%H%M%S", time.localtime(timestamp))


def current_datetime_str_s(timestamp=None):
  """
  获取当前时间戳对应的以T连接的日期、时间字符串
  :param timestamp: 时间戳
  :return: 日期时间字符串 形如 20181119T102035
  """
  return time.strftime("%Y%m%dT%H%M%S", time.localtime(timestamp))


def current_datetime_str_d(timestamp=None):
  """
  获取当前时间戳对应的以-连接的日期、时间字符串, 日期时间内容通过.连接
  :param timestamp: 时间戳
  :return: 日期时间字符串 形如 2018.11.19-10.20.35
  """
  return time.strftime("%Y.%m.%d-%H.%M.%S", time.localtime(timestamp))


def current_datetime_str_r(datetime_r=None):
  """
  获取当前时间戳对应的以T作为分割的日期、时间字符串
  :param datetime_r: datetime.datetime对象
  :return: 日期时间微秒字符串 形如 2021.05.20-11.03.21-082161
  """
  if datetime_r is None or not isinstance(datetime_r, datetime.datetime):
    datetime_r = current_datetime_r()
  return datetime_r.strftime("%Y.%m.%d-%H.%M.%S-%f")


@deprecated(new_fn=current_datetime_str_r, version='0.8.0')
def current_datetime_r_str(datetime_r=None):
  return current_datetime_str_r(datetime_r)


def current_date(timestamp=None):
  """
  获取当前日期
  :param timestamp: 时间戳
  :return: 日期时间格式字符串 形如 2018-11-19
  """
  return time.strftime("%Y-%m-%d", time.localtime(timestamp))


def current_date_str(timestamp=None):
  """
  获取当前日期
  :param timestamp: 时间戳
  :return: 日期时间格式字符串 形如 20181119
  """
  return time.strftime("%Y%m%d", time.localtime(timestamp))


def current_time(timestamp=None):
  """
  获取当前时间
  :param timestamp: 时间戳
  :return: 日期时间格式字符串 形如 10:20:35
  """
  return time.strftime("%H:%M:%S", time.localtime(timestamp))


def current_time_str(timestamp=None):
  """
  获取当前时间
  :param timestamp: 时间戳
  :return: 日期时间格式字符串 形如 10:20:35
  """
  return time.strftime("%H%M%S", time.localtime(timestamp))


def current_time_str_m(datetime_r=None):
  """
  获取当前时间
  :param datetime_r: datetime.datetime对象
  :return: 时间/微秒格式字符串 形如 10.20.35-987
  """
  if datetime_r is None or not isinstance(datetime_r, datetime.datetime):
    datetime_r = current_datetime_r()
  return datetime_r.strftime("%H.%M.%S-%f")


class Timer(object):
  """
  计时器类
  """

  # 无效时间戳标志
  _invalid_ts = -1

  def __init__(self, debug=False):
    self._debug = debug
    self._start_ts = self._invalid_ts
    self._finish_ts = self._invalid_ts
    self.reset()

  def reset(self):
    """
    重新计时
    """
    self._start_ts = time.time()
    self._finish_ts = self._invalid_ts
    if self._debug:
      self.display_start('start at: ')

  @property
  def start_ts(self):
    return self._start_ts

  @property
  def finish_ts(self):
    return self._finish_ts

  @property
  def elapsed(self):
    return time.time() - self.start_ts

  def start(self):
    self.reset()
    return self.start_ts

  def finish(self):
    self._finish_ts = time.time()
    return self.finish_ts

  @property
  def stopped(self):
    return self._finish_ts != self._invalid_ts

  def cost(self):
    self._set_finish()
    return self._finish_ts - self._start_ts

  def state_dict(self):
    return {
      'start_ts': self.start_ts,
      'finish_ts': self.finish_ts
    }

  def load_state_dict_(self, state_dict):
    self._start_ts = state_dict['start_ts']
    self._finish_ts = state_dict['finish_ts']

  def display_start(self, msg=None):
    Timer._display_datetime(self._start_ts, msg)

  def display_finish(self, msg=None):
    self._set_finish()
    Timer._display_datetime(self._finish_ts, msg)

  def display_cost(self, msg=None):
    cost = self.cost()
    prefix = ''
    if msg:
      prefix = '{}'.format(msg)
    it_print('{} cost {}'.format(prefix, self.format(cost)))

  @classmethod
  def format(cls, seconds):
    assert seconds >= 0
    seconds = int(seconds)

    if seconds < 60:
      return '{} seconds'.format(seconds)
    elif 60 <= seconds < 120:
      return cls._format('{} minute {}', seconds, 60)
    elif 120 <= seconds < 3600:
      return cls._format('{} minutes {}', seconds, 60)
    elif 3600 <= seconds < 7200:
      return cls._format('{} hour {}', seconds, 3600)
    elif 7200 <= seconds < 86400:
      return cls._format('{} hours {}', seconds, 3600)
    elif 86400 <= seconds < 172800:
      return cls._format('{} day {}', seconds, 86400)
    else:
      return cls._format('{} days {}', seconds, 86400)

  def _set_finish(self):
    if not self.stopped:
      self.finish()

  @staticmethod
  def _display_datetime(ts, msg=None):
    _tmp_msg = current_datetime(ts)
    if msg is not None:
      if not msg.endswith(' '):
        msg += ' '
      _tmp_msg = msg + _tmp_msg
    it_print(_tmp_msg)

  @classmethod
  def _format(cls, fmt, seconds, factor):
    return fmt.format(seconds // factor, cls.format(seconds % factor))

  def __repr__(self):
    msg = ['start at {}'.format(current_datetime(self.start_ts))]
    if self.stopped:
      msg.append('finished at {}'.format(
        current_datetime(self.finish_ts)
      ))
    return ', '.join(msg)


def timed(description=None, num_pre_blanklines=0, num_suf_blanklines=0):
  """
  计时标记
  :param description: 计时描述
  :param num_pre_blanklines: 输出计时前空行数
  :param num_suf_blanklines: 输出计时后空行数
  :return: 包装函数
  """

  def function_wrapper(fn):
    """
        标记为统计运行时间的函数
        :param fn: 被测函数
        """
    assert callable(fn)

    def wrapper(*args, **kwargs):
      _description = fn.__name__
      if description is not None and not callable(description):
        _description = description

      if num_pre_blanklines > 0:
        [it_print() for _ in range(num_pre_blanklines)]
      timer = Timer()
      timer.display_start('{} start at'.format(_description))
      result = fn(*args, **kwargs)
      timer.display_finish('{} complete at'.format(_description))
      timer.display_cost(_description)
      if num_suf_blanklines > 0:
        [it_print() for _ in range(num_pre_blanklines)]

      return result

    return wrapper

  if callable(description):
    return function_wrapper(fn=description)

  return function_wrapper

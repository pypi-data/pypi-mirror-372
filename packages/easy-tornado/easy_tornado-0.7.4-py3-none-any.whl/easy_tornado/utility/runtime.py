# -*- coding: utf-8 -*-
# author: 王树根
# email: wangshugen@ict.ac.cn
# date: 2018/11/19 11:22
import signal
from os import kill

import psutil

from . import exit_print
from .filesystem import file_exists
from .filesystem import load_file_contents
from .filesystem import remove_file
from .printext import it_print


def kill_process(pid_path, signum=None, remove=True):
  """
  向pid_path文件内容中的PID发送信号
  :param pid_path: pid文件路径
  :param signum: 信号值
  :param remove: 是否移除pid文件
  """
  if not file_exists(pid_path):
    return None

  if signum is None:
    signum = signal.SIGKILL

  # 读取PID文件
  pid = int(load_file_contents(pid_path)[0].strip())

  # 向该进程发送信号
  try:
    kill(pid, signum)
  except OSError as e:
    if len(e.args) != 2 or e.args[1] != 'No such process':
      return None

  # 移除PID文件
  if remove:
    remove_file(pid_path)

  return True


def query_process(pid_path):
  """
  :param pid_path PID文件路径
  """
  if not file_exists(pid_path):
    exit_print('{} does not exist, please check it manually!'.format(pid_path))

  pid = int(load_file_contents(pid_path, pieces=False))
  if psutil.pid_exists(pid):
    it_print("Process is running with PID={} !".format(pid))
  else:
    it_print("Process is not running with PID={} !".format(pid))

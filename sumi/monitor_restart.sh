#!/bin/bash

# 获取当前进程id
current_pid=$$
#echo $current_pid

# 获取当前进程信息
#process_info=$(ps -p $current_pid  -o pid,ppid,cmd)
#process_info=$(ps -p $current_pid  -o pid)
#echo "$process_info"


## 终止当前
#kill "$current_pid"


while true; do
  # 启动Pyhton文件
  python3 "/home/cb/shubin/sumi/stream_fetch.py"

  # 获取这个进程id号
  echo $(ps aux | grep "stream_fetch.py" | grep -v grep | awk '{print $2}')

  echo "Program exited with an error. Restarting..."
  # 杀死这个python进程
  kill -s 9 $(ps aux | grep "stream_fetch.py" | grep -v grep | awk '{print $2}')


done
#!/bin/bash
processNum=`ps -ef | grep shutdown.py | grep -v grep | wc -l`
if [ $processNum -eq 0 ];then
    sudo python3 /home/pi/proj/shutdown.py &
fi
processNum=`ps -ef | grep playsound.py | grep -v grep | wc -l`
if [ $processNum -eq 0 ];then
    python3 /home/pi/proj/playsound.py &
fi
sudo python3 /home/pi/proj/main.py

#!/bin/bash
config=config_dev.py
function restart {
port=$1
pid=$(ps -ef |grep uwsgi |grep -v grep |grep ${port} |awk '{print $2}' |sort |uniq |head -1)
echo "restarting port ${port}..."
while [ ! -z ${pid} ]
do
    kill -9 ${pid}
    echo "port ${port}: pid ${pid} killed..."
    pid=$(ps -ef |grep uwsgi |grep -v grep |grep ${port} |awk '{print $2}' |sort |uniq |head -1)
done
nohup uwsgi --http 0.0.0.0:8088 --http-websockets --env signature/settings.py --file signature/wsgi.py --processes 16 --threads 8 &
sleep 3
pid=$(ps -ef |grep uwsgi |grep -v grep |grep ${port} |awk '{print $2}' |sort |uniq |head -1)
if [ ! -z ${pid} ];then
    echo "port ${port} restarted ok."
    ps -ef |grep uwsgi |grep -v grep |grep $port
else
    echo "port ${port} restarted failed. pls check!"
    ps -ef |grep uwsgi |grep -v grep |grep $port
fi
}
restart 8088
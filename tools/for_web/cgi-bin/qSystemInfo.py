#!/usr/bin/python
import time
import sys
import time
import datetime
from socket import socket
import os
import subprocess
import json
from webcommon import *


szCassIP1="127.0.0.1"
szCassDB="tqdb1"
szBinDir='/home/tqdb/codes/tqdb/tools/'

allInfo=[] #[key, val]

def runCql(szCql, objRet):
    p = subprocess.Popen(["/var/cassandra/bin/cqlsh", "-e", szCql], cwd="/var/cassandra/bin/",  
                         stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    objRet['output'], objRet['err'] = p.communicate()
    objRet['retcode'] = p.returncode
def runCmd(cmd):
    proc = subprocess.Popen(cmd,shell=True, stdout=subprocess.PIPE)
    ret = []
    while True:
        line = proc.stdout.readline()
        if line is not None and line != '':
            ret.append(line.replace('\n', ''))
        else:
            break
    return ret

if False:
	tmpFile="/tmp/qsummery.%d.%d.txt"%(os.getpid(),time.mktime(datetime.datetime.now().timetuple()))
        objRet = {}
	cql="select * from %s.tick where symbol='%s' order by datetime limit 10;" % (szCassDB, sym)
        runCql(cql, objRet)
        summery['tick.first'] = objRet['output']

if True: #get system time zone
    linuxFamily = '?'
    if True:
        tempId = runCmd('cat /etc/os-release | grep "^ID="')[0]
        if tempId.find("rhel")>=0: linuxFamily="RedHat"
        elif tempId.find("centos")>=0: linuxFamily="RedHat"
        elif tempId.find("debian")>=0: linuxFamily="Debian"

    zones = []
    lines = runCmd('readlink -s /etc/localtime')
    for line in lines:
        zones.append(line)

    zones.append(os.path.realpath('/etc/localtime'))

    for i in range(0,len(zones)):
        posi = zones[i].find("zoneinfo/")
        if posi > 0:
            zones[i] = zones[i][posi+9:]
    tzdbVer = "?"
    if linuxFamily == "Debian":
        tzdbVer = runCmd('dpkg -s tzdata  | grep Version')[0].replace('Version: ','')
    elif linuxFamily == "RedHat":
        tzdbVer = runCmd('yum list installed | grep tzdata.noarch | awk "{print \\$2}"')
    lines = []
    lines.append('Now=%s' % ', '.join(runCmd("date +'%Y-%m-%d %H:%M:%S (%Z)'")))
    lines.append('TimeZone=%s (/etc/localtime)' % ', '.join(zones))
    lines.append('TimeZone=%s (/etc/timezone)' % ', '.join(runCmd('cat /etc/timezone')))
    lines.append('tzdata Version=%s' % tzdbVer)
    allInfo.append(['Server Time', '<br>'.join(lines)])

if True:
    lines = runCmd('cat /etc/crontab | grep purgeTick.sh | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Purge Tick Schedule', '<br>'.join(lines)])
    lines = runCmd('cat /etc/crontab | grep build1MinFromTick.sh | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Build 1Min Schedule', '<br>'.join(lines)])
    lines = runCmd('cat /etc/crontab | grep build1SecFromTick.sh | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Build 1Sec Schedule', '<br>'.join(lines)])
    lines = runCmd('cat /etc/crontab | grep -E "reboot|shutdown|halt" | sed "s/^ *//" | grep -v "^#"')
    allInfo.append(['Reboot Schedule', '<br>'.join(lines)])


if True:
    lines = []
    #lines += ["----%s %s----" % (linuxFamily, ''.join(runCmd('arch')))]
    lines += runCmd('grep -E "^PRETTY_NAME=" /etc/os-release | sed "s/\\"//g" | cut -f 2 -d "="')
    lines += [''.join(runCmd('arch'))] 
    allInfo.append(['Linux Info', '<br>'.join(lines)])

if True:
    lines = []
    lines += runCmd('cat /proc/cpuinfo | grep -E "cores|model name" |sort | uniq ')
    allInfo.append(['CPUs Info', '<br>'.join(lines)])

if True:
    lines = runCmd('top -bn1 | head -10 | sed "s/ /\&nbsp;/g"')
    allInfo.append(['Top Info', '<br>'.join(lines)])

if True:
    lines = runCmd('df -h| sed "s/ /\&nbsp;/g"')
    allInfo.append(['Disk Info', '<br>'.join(lines)])
sys.stdout.write("Content-Type: text/html\r\n")
sys.stdout.write("\r\n")
sys.stdout.write("<html>")
sys.stdout.write("<body><link rel='stylesheet' type='text/css' href='/style.css'>")
sys.stdout.write("<table >")
sys.stdout.write("<tr class='grayThing smallfont'><td>Item</td><td>Info</td></tr>")
for info in allInfo:
    sys.stdout.write("<tr onmouseover=\"this.className='yellowThing';\" onmouseout=\"this.className='whiteThing';\">")
    sys.stdout.write("<td><font size='-1'>%s</font></td><td><font size='-1'>%s</font></td></tr>"%(info[0], info[1]))
sys.stdout.write("</table>")
sys.stdout.write("</body></html>")
sys.stdout.write("\r\n")
sys.stdout.flush()

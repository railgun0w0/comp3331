# import socket programming library 
#import socket 
from socket import *
import os
import sys
# import thread module 
from _thread import *
import threading 
import json
from datetime import datetime,date,timedelta
import random

blockingdic = {}
blockdic = {}
blocktime = 0
loginuser = []
tempidlist = []
# thread function 
def threaded(c): 
    while True: 
        global blockingdic
        global blockdic
        global loginuser
        global tempidlist
        data = c.recv(1024) 
        if not data: 
            print('Someone disconnect') 
            break
        request = json.loads(data.decode('utf-8'))
        if request['messagetype'] == 'credentials':
            credentials = {}
            with open('credentials.txt') as file:
                for line in file.readlines():
                    pairs = line.split(' ')
                    credentials[pairs[0]] = pairs[1].strip()
            if request['username'] in blockingdic:
                timenow = datetime.now()
                timeblocked = blockingdic[request['username']]
                blockedtime = timenow - timeblocked
                if blockedtime.total_seconds() < blocktime:
                    c.send(bytes('B',encoding='utf-8'))
                    continue
                else:
                    blockingdic.pop(request['username'])
            if request['username'] in credentials and request['password'] == credentials[request['username']]:
                c.send(bytes('Y',encoding='utf-8'))
                loginuser.append(str(request['username']))
                username = request['username']
                print(f'{username} log in')
            else:
                if request['username'] not in blockdic:
                    blockdic[request['username']] = 1
                else:
                    blockdic[request['username']] += 1
                if blockdic[request['username']] == 3:
                    blockdic.pop(request['username'])
                    blockingdic[request['username']] = datetime.now()
                    c.send(bytes('NB',encoding='utf-8'))
                else:
                    c.send(bytes('N',encoding='utf-8'))
        elif request['messagetype'] == 'logout':
            username = request['username']
            loginuser.remove(str(request['username']))
            print(f'{username} logout')
            continue
        elif request['messagetype'] == 'downloadtempid':
            username = request['username']
            tempid = ''.join(["{}".format(random.randint(0, 9)) for num in range(0, 20)])
            while tempid in tempidlist:
                tempid = ''.join(["{}".format(random.randint(0, 9)) for num in range(0, 20)])
            creattime = datetime.now()
            expiredtime = creattime + timedelta(minutes = 15)
            newline = username + ' ' + tempid + ' ' + creattime.strftime('%d/%m/%Y %H:%M:%S') + ' ' + expiredtime.strftime('%d/%m/%Y %H:%M:%S') + '\n'
            newtempidfile = open('tempIDs.txt','a')
            newtempidfile.write(newline)
            newtempidfile.close()
            message = tempid + ',' + creattime.strftime('%d/%m/%Y %H:%M:%S') + ',' + expiredtime.strftime('%d/%m/%Y %H:%M:%S')
            print(f'> user: {username}\n> Tempid: \n{tempid}')
            c.send(bytes(message, encoding='utf-8'))
        elif request['messagetype'] == 'uploadcontactlog':
            contactlist = {}
            username = request['username']
            print(f'>received contact from {username}')
            for i in request['log']:
                contactid = i
                contactcreattime = request['log'][i]['createtime']
                contactexpiretime = request['log'][i]['expiredtime']
                contactuser = {}
                contactuser['createtime'] = contactcreattime
                contactuser['expiredtime'] = contactexpiretime
                contactlist[contactid] = contactuser
                print(f'{contactid},\n{contactcreattime},\n{contactexpiretime};\n')
            print('> Contact log checking')
            tempiduser = {}
            with open('tempIDs.txt') as file:
                for line in file.readlines():
                    #print(line)
                    data = {}
                    pairs = line.split(' ')
                    starttime = pairs[2].strip() + ' ' + pairs[3].strip()
                    expiredtime = pairs[4].strip() + ' ' + pairs[5].strip()
                    data['tele'] = pairs[0]
                    data['createtime'] = starttime
                    data['expiredtime'] = expiredtime
                    tempiduser[pairs[1]] = data
            #print(tempiduser)
            userlist = []
            for i in contactlist:
                if i in tempiduser and i not in userlist:
                    tele = tempiduser[i]['tele']
                    tid = i
                    Ctime = tempiduser[i]['createtime']
                    userlist.append(i)
                    print(f'{tele},\n{Ctime},\n{tid};\n')
    # connection closed 
    c.close() 


def start(port): 
    # get ip from os 
    #host = 'localhost' 
    hostname = gethostname()
    host = gethostbyname(hostname)
    serverPort = port
    s = socket(AF_INET, SOCK_STREAM) 
    # start TCP servers socket 
    s.bind((host, port)) 
    print(f"Server working on {host}:{serverPort}")
    print("socket binded to port", serverPort) 

    # put the socket into listening mode 
    s.listen(5) 
    print("socket is listening") 
    # clear and create empty tempID.txt
    f = open('tempIDs.txt','w')
    f.close()
    # forever loop until client wants to exit 
    while True: 

        # establish connection with client 
        c, addr = s.accept() 

        # one client connect in 
        print('Connected to :', addr[0], ':', addr[1]) 

        # Start a new thread and return its identifier 
        start_new_thread(threaded, (c,)) 

    s.close() 
# Helper function
def setblocktime(time):
    global blocktime
    blocktime = time
    return


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('required port and block_duration time\nTry python3 server.py <server_port> <block_duration>')
        exit()
    port = int (sys.argv[1])
    blocktime = int (sys.argv[2])
    # set blocking time as global 
    setblocktime(blocktime)
    start(port)
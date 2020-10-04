import sys
import os
import json
from _thread import *
from socket import *
from datetime import datetime,date,timedelta
from threading import Timer

tempid = {}
def loginserver(username, password, clientSocket):
    sentence = {
        'messagetype':'credentials',
        'username': username,
        'password': password
    }
    clientSocket.send(bytes(json.dumps(sentence),encoding='utf-8'))
    while 1:
        receivedSentence = clientSocket.recv(1024)
        received = receivedSentence.decode('utf-8')
        #print('>>>>>>>>>>>>>>>>>>>>>>')
        #print(received)
        if received == 'Y':
            print('> Welcome to the BlueTrace Simulator')
            break
        elif received == 'N':
            print('> Invalid Passsword. Please try again')
            newpassword = input('>password: ')
            sentence['password'] = newpassword
            clientSocket.send(bytes(json.dumps(sentence),encoding='utf-8'))
        elif received  == 'NB':
            print('> Invalid Passsword. Your account has been blocked. Please try again later')
            exit()
        elif received  == 'B':
            print('> Your account is blocked due to multiple login failures. Please try again later')
            exit()

def download(username, clientSocket):
    global tempid
    sentence = {
        'messagetype':'downloadtempid',
        'username': username
    }
    clientSocket.send(bytes(json.dumps(sentence),encoding='utf-8'))
    receivedSentence = clientSocket.recv(1024)
    tempidline = receivedSentence.decode('utf-8')
    pairs = tempidline.split(',')
    tempid['tempid'] = pairs[0]
    tempid['createtime'] = pairs[1].strip()
    tempid['expiredtime'] = pairs[2].strip()
    print(f'> TempID: \n{pairs[0]}')

def upload(username, clientSocket):
    if not os.path.exists('z5223796_contactlog.txt'):
        print('contact log is empty')
        return
    if os.path.getsize('z5223796_contactlog.txt') == 0:
        print('contact log is empty')
        return
    if tempid == {}:
        print('tempid is empty,try download_tempid')
        return
    log = {}
    with open('z5223796_contactlog.txt') as file:
        for line in file.readlines():
            time = {}
            pairs = line.split(' ')
            starttime = pairs[1].strip() + ' ' + pairs[2].strip()
            expiredtime = pairs[3].strip() + ' ' + pairs[4].strip()
            time['createtime'] = starttime
            time['expiredtime'] = expiredtime
            print(f'{pairs[0]},\n{starttime},\n{expiredtime};\n')
            log[pairs[0]] = time
    sentence = {
        'messagetype':'uploadcontactlog',
        'username': username,
        'log': log
    }
    clientSocket.send(bytes(json.dumps(sentence),encoding='utf-8'))

def logout(username, clientSocket):
    sentence = {
        'messagetype':'logout',
        'username': username
    }
    clientSocket.send(bytes(json.dumps(sentence),encoding='utf-8'))
    #print(tempid)
    print('You have log out.Goodbye.')
    clientSocket.close()
    exit()

def sendbeacon(udpip,udpport):
    serverName = udpip
    serverPort = int(udpport)
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    if tempid == {}:
        print('You do not have a tempid, will send all 0s and invalid time')
        message = '1,00000000000000000000,01/01/1970 00:00:00,01/01/1970 00:00:00'
        print(f'00000000000000000000,\n01/01/1970 00:00:00,\n01/01/1970 00:00:00.\n')
        clientSocket.sendto(bytes(message,encoding='utf-8'),(serverName, serverPort))
        clientSocket.close()
        return
    createtime = tempid['createtime']
    expiredtime = tempid['expiredtime']
    tid = tempid['tempid']
    message = f'1,{tid},{createtime},{expiredtime}'
    print(f'{tid},\n{createtime},\n{expiredtime}.\n')
    clientSocket.sendto(bytes(message,encoding='utf-8'),(serverName, serverPort))
    clientSocket.close()
    return

def udpserver(udpport):
    hostname = gethostname()
    udpclientip = gethostbyname(hostname)
    serverSocket = socket(AF_INET, SOCK_DGRAM)
    #print(f'working on {udpclientip}')
    serverSocket.bind((udpclientip, udpport))
    start_new_thread(revbeacon,(serverSocket, ))


def revbeacon(serverSocket):   
    while 1:
        message, clientAddress = serverSocket.recvfrom(2048)
        beaconmessage = message.decode('utf-8')
        pair = beaconmessage.split(',')
        tid = pair[1]
        ctime = pair[2]
        etime = pair[3]
        timenow = datetime.now()
        strtimenow = timenow.strftime('%d/%m/%Y %H:%M:%S')
        ctimeint = datetime.strptime(ctime,'%d/%m/%Y %H:%M:%S')
        etimeint = datetime.strptime(etime,'%d/%m/%Y %H:%M:%S')
        logstr = tid +' ' + ctime + ' '+ etime + '\n'
        print(f' received beacon:\n{tid},\n{ctime},\n{etime}.\nCurrent time is:\n{strtimenow}.\n')
        if timenow >= ctimeint and timenow <= etimeint:
            print('The beacon is valid.')
            if not os.path.exists('z5223796_contactlog.txt'):
                log = open('z5223796_contactlog.txt','w')
            else:
                log = open('z5223796_contactlog.txt','a')
            log.write(logstr)
            log.close()
            t = Timer(180,dellog,(logstr,))
            t.start()
        else:
            print('The beacon is invalid.')
        
def dellog(string):
    oldlog = open('z5223796_contactlog.txt','r')
    lines = oldlog.readlines()
    oldlog.close()
    newlog = open('z5223796_contactlog.txt','w')
    for line in lines:
        if line.strip('\n') != string.strip('\n'):
            newlog.write(line)
    newlog.close()

def connectwithserver(host, port, udpport):
    serverName = host
    serverPort = port
    # connection with tcp server
    clientSocket = socket(AF_INET, SOCK_STREAM)
    clientSocket.connect((serverName, serverPort))
    username = input('> username: ')
    password = input('> password: ')
    loginserver(username, password, clientSocket)
    
    # print('login succful')
    #open udp server
    udpserver(udpport)
    f = open('z5223796_contactlog.txt','w')
    f.close()
    #start_new_thread(udpserver, udpport)
    while 1:
        command = input('> ')
        beaconlist = command.split()
        if command == 'Download_tempID':
            download(username, clientSocket)
            continue
        elif command == 'Upload_contact_log':
            upload(username, clientSocket)
            continue
        elif command == 'logout':
            logout(username, clientSocket)
        elif beaconlist[0] == 'Beacon':
            if len(beaconlist) != 3:
                print("require ip and port. Try again")
                continue
            udpip = beaconlist[1]
            udpport = beaconlist[2]
            sendbeacon(udpip,udpport)
            continue
        else:
            print('Error. Invalid command')
            continue
    clientSocket.close()

if __name__ == '__main__':
    if len(sys.argv) != 4:
        print('required host prot UDP port')
        exit()
    host = sys.argv[1]
    serverport = int (sys.argv[2])
    udpport = int (sys.argv[3])
    connectwithserver(host, serverport,udpport)
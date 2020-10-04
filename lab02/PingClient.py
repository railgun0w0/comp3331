# PYthon 3.7.3 use cse machine 


from socket import *
import sys
import time
import statistics

def ping (host,port):
    serverName = host
    serverPort = port
    clientSocket = socket(AF_INET, SOCK_DGRAM)
    
    #Create UDP client socket
    seqnum = 3331
    pingtimes = 0
    rtts = []
    while(pingtimes < 15):
        pingtimes += 1
        starttime = time.time() * 1000
        message = 'PING' + ' ' + str(seqnum) + ' ' + str(starttime) + '\r\n'
        clientSocket.sendto(message.encode('utf-8'),(serverName, serverPort))
        clientSocket.settimeout(0.6)
        #Waits up to 600 ms to receive a reply
        try:
            modifiedMessage, serverAddress = clientSocket.recvfrom(2048)
            gettime = time.time() * 1000
            usetime = gettime - starttime
            rtts.append(usetime)
            print(f'Ping to {serverName}, seq = {seqnum}, rtt = {int(usetime)} ms')
            seqnum += 1
        except timeout:
            print(f'Ping to {serverName}, seq = {seqnum}, timeout')
            seqnum += 1
    print('transmission finished')
    if len(rtts) > 0:
        minrtt = min(rtts)
        maxrtt = max(rtts)
        avertt = statistics.mean(rtts)
        print(f'MINIMUM RTT is {int(minrtt)} ms, MAXIMUM RTT is {int(maxrtt)} ms, AVERAGE RTT is {int(avertt)} ms\n')
    else:
        print('ALL TIME OUT,Check Host port again\n')
    clientSocket.close()
    # Close the socket

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('required host prot')
        exit(1)
    host = sys.argv[1]
    port = int (sys.argv[2])
    ping(host, port)

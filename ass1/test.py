def dellog(string):
    oldlog = open('1.txt','r')
    lines = oldlog.readlines()
    oldlog.close()
    newlog = open('1.txt','w')
    for line in lines:
        if line.strip('\n') != string.strip('\n'):
            newlog.write(line)
    newlog.close()

if __name__ == '__main__':
    string = 'b'
    dellog(string)
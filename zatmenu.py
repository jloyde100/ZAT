import os
import sys

def mainMenu():
    #os.system('clear')   
    print '1) Server status'
    print '2) Start server'
    print '3) Stop server'
    print '0) Exit'
    print 'Enter your choice: '
    tAns=sys.stdin.readline()
    sAns=tAns.strip()
    return sAns 

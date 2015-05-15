import wl;
import os;
import time;
import operator;
import sys;
import datetime;


##==============================================
## getQueueInfo:  
## This procedure returns several collections.  
## An sorted set of indexes,  a collection of 
## comma separated strings containing queue stats,
## and a list of destinations (queues/topics)
## This comma separated strings contain the 
## following:
## Date,
## Time, 
## Queue or Topic Name,
## Managed Server Name,
## Current message count,
## Pending message count, 
## High message count,
## Total Messages Received count

def getQueueInfo():
    wl.domainRuntime()
    servers = wl.domainRuntimeService.getServerRuntimes();

    conslimit=os.getenv('CONSUMER_LIMIT')
    msglimit=os.getenv('MSG_LIMIT')
    totallimit=os.getenv('TOTAL_LIMIT')
    pendinglimit=os.getenv('PENDING_MSG_LIMIT')
    rcvdlimit=os.getenv('RECEIVED_MSG_LIMIT')
    try:
        if len(conslimit)==0:
             conslimit='0';
    except:
        conslimit='0';

    try:
        if len(msglimit)==0:
             msglimit='0';
    except:
        msglimit='0';

        #if len(totallimit)==0:
    totallimit='0';

    try:
        if len(pendinglimit)==0:
           pendinglimit='0';
    except:
        pendinglimit='0';

    try:
        if len(rcvdlimit)==0:
           rcvdlimit='0';
    except:
        rcvdlimit='0';

    destnameonly="";
    dest={}

    results=[]

    ctr=0;
    rcvdtotal=0

    errorString='';

    if (len(servers) > 0):
         for server in servers:
            try:
              jmsRuntime = server.getJMSRuntime();
              jmsServers = jmsRuntime.getJMSServers();
              for jmsServer in jmsServers:
                  destinations = jmsServer.getDestinations();
                  for destination in destinations:
                      destname=destination.getName()
                      destnameonly=destname.split('!',1)[1]
                      serveronly=destnameonly.split('@',1)[0]
                      destnamewithoutserver=destname.split('@',1)[1]
                      if destination.getConsumersCurrentCount()>=int(conslimit):
                         if destination.getMessagesCurrentCount()>=int(msglimit):
                           if destination.getConsumersTotalCount()>=int(totallimit):
                               if destination.getMessagesPendingCount()>=int(pendinglimit):
                                  if destination.getMessagesReceivedCount()>=int(rcvdlimit):
                                     dest[destnamewithoutserver+','+server.getName()]=ctr
                                     results.append(str(datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S'))+','+destnamewithoutserver+','+server.getName()+','+str(destination.getMessagesCurrentCount())+','+str(destination.getMessagesPendingCount())+','+str(destination.getMessagesHighCount())+','+str(destination.getMessagesReceivedCount()))
                                     ctr=ctr+1
            except:
              errorString="Unexpected error while querying managed server: ", sys.exc_info()[0], sys.exc_info()[1], 'Skipping this server...'

    mykeys=dest.keys()
    myvalues=dest.values()
    mykeys.sort()
    return mykeys, results, dest


##==============================================
## getServerStatus:  
## This procecdure returns a colleciton of comma
## separated strings containing the status of 
## managed servers in a domain along with heap usage 
## information:
## Current Date,
## Current Time, 
## Managed Server Name,
## Current Status (RUNNING, SHUTDOWN, etc.),
## Health, 
## Started Date (used to tell how long it has been up),
## Started Time, 
## Heap Free,
## Heap Max,
## Percentage of Heap Used

def getServerStatus():
    import time;
    stoppedSvrCnt=0;
    runningSvrCnt=0;
    startingSvrCnt=0;
    otherSvrCnt=0;
    wl.cd('/')
    wl.domainConfig()
    serverNames = wl.cmo.getServers()
    wl.domainRuntime()
 
    results=[]

    for name in serverNames:
        try:
            wl.cd("/ServerLifeCycleRuntimes/" + name.getName())
            serverState = wl.cmo.getState()
            actTime='';

            if serverState == "RUNNING":
                wl.cd('../../ServerRuntimes/'+name.getName())
                actTime=wl.cmo.getActivationTime()
                x = time.gmtime(actTime/1000)
                timestr=" " + str(x[0]) + "/" + str(x[1]).zfill(2) + "/" + str(x[2]).zfill(2) + "," + str(x[3]).zfill(2) + ":" + str(x[4]).zfill(2)+':'+str(x[5]).zfill(2)
                wl.cd('JVMRuntime/'+name.getName())
                heapfree=wl.cmo.getHeapFreeCurrent();
                heapfreeperc=wl.cmo.getHeapFreePercent()
                heapmax=wl.cmo.getHeapSizeMax()
                heapused=100-heapfreeperc
                wl.cd('../..')
                serverHealth = str(wl.cmo.getOverallHealthState())
                healthok='State:HEALTH_OK'
                for serverComp in serverHealth.split(','):
                    if serverComp.find('State:')>-1:
                       healthok=serverComp
                runningSvrCnt=runningSvrCnt+1
                linestring=str(datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S'))+',' + name.getName() + ',\033[1;32m' + serverState + '\033[0m'
                if healthok=='State:HEALTH_OK':
                      linestring=linestring+',\033[1;32mHEALTHY\033[0m,'+timestr+','+str(heapfree)+','+str(heapmax)+','+str(heapused)
                else:
                      linestring=linestring+',\033[1;33m  WARNING \033[0m,'+timestr+','+str(heapfree)+','+str(heapmax)+','+str(heapused)
                      for serverComp in serverHealth.split(','):
                          holdvalue=serverComp.split(':')
                          if holdvalue[0]=='ReasonCode':
                             linestring=linestring+'\n'
                          if holdvalue[0]!='MBean':
                             linestring=linestring+',\033[0;33m '+holdvalue[1].upper()+ '\033[0m'
                results.append(linestring);
            elif serverState == "STARTING":
                startingSvrCnt=startingSvrCnt+1;
                results.append(',' + name.getName() + ',\033[1;33m' + serverState + '\033[0m,,,,');
            elif serverState == "SHUTDOWN":
                otherSvrCnt=otherSvrCnt+1;
                results.append(',' + name.getName() + ',\033[1;31m' + serverState + '\033[0m,,,,');
            else:
                stoppedSvrCnt=stoppedSvrCnt+1
                results.append(',' + name.getName() + ',\033[1;34m' + serverState + '\033[0m,,,,');
            wl.cd('../..')
        except:
            pass;

    return results;


##==============================================
## getSocketConnectionInfo:  
## You pass this function your application name
## that contains a socket resource adapter like
## EXTSubsystem or FAASubsystem.
## This procecdure returns a colleciton of comma
## separated strings containing metics about the 
## Socket Resource Adapter connection pool.
## Current Date,
## Current Time, 
## Managed Server Name,
## Application Name,
## Current state of the socket resource adapter
##  (Activated)
## Current Number of Active Socket Connections,
## High Number of Socket Connections,
## Number of Rejected Socket Connections,
## Maximum Number of Socket Connections,
## Last Date that Shrinking happened,
## Last Time that Shrinking happened,
## Countdown to the next Shrinking  


def getSocketConnectionInfo(appname):
    import time;
    wl.domainRuntime()
    wl.cd('/')
    wl.cd('ServerRuntimes')
    svrnames=wl.ls(returnMap='true')
    results=[]
    for svr in svrnames:
        print svr
        if svr!='AdminServer':
           wl.cd('/ServerRuntimes/'+svr+'/ApplicationRuntimes/'+appname+'/ComponentRuntimes/'+appname+'_SocketResourceAdapter/')
           rastate=wl.cmo.getState();
           wl.cd('/ServerRuntimes/'+svr+'/ApplicationRuntimes/'+appname+'/ComponentRuntimes/'+appname+'_SocketResourceAdapter/ConnectionPools/eis/JCAAdapter/socketServerConnectionFactory')
           raactivecount=wl.cmo.getActiveConnectionsCurrentCount()
           raactivehigh=wl.cmo.getActiveConnectionsHighCount()
           rarejectedtotal=wl.cmo.getConnectionsRejectedTotalCount()
           ramaxcapacity=wl.cmo.getMaxCapacity()
           ralastshrinktime=wl.cmo.getLastShrinkTime()
           radisplayshrinktime=time.strftime('%Y-%m-%d,%H:%M:%S', time.localtime(ralastshrinktime/1000))
           rashrinkcountdown=wl.cmo.getShrinkCountDownTime()
           results.append(str(datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S'))+','+svr+','+appname+','+rastate+','+str(raactivecount)+','+str(raactivehigh)+','+str(rarejectedtotal)+','+str(ramaxcapacity)+','+radisplayshrinktime+','+str(rashrinkcountdown))
    return results




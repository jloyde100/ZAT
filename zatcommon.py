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
                results.append(str(datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S'))+',' + name.getName() + ',\033[1;33m' + serverState + '\033[0m,,,,,,');
            elif serverState == "SHUTDOWN":
                otherSvrCnt=otherSvrCnt+1;
                results.append(str(datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S'))+',' + name.getName() + ',\033[1;31m' + serverState + '\033[0m,,,,,,');
            else:
                stoppedSvrCnt=stoppedSvrCnt+1
                results.append(str(datetime.datetime.now().strftime('%Y-%m-%d,%H:%M:%S'))+',' + name.getName() + ',\033[1;34m' + serverState + '\033[0m,,,,,,');
            wl.cd('../..')
        except:
            pass;

    return results;


#====================================
# Stop a server given as parameter
#====================================

def stopSvr(svr):
  try:
     wl.state(svr)
     wl.shutdown(svr, 'Server',force='true',block='false')
     wl.state(svr)
  except wl.WLSTException, we:
     wl.dumpStack()
  except Exception, e:
     print svr+': Error in shutting down -'+str(e)
     pass

#====================================
# Start a server given as parameter
#====================================

def startSvr(svr):
  try:
     wl.state(svr)
     wl.start(svr, 'Server',block='false')
     wl.state(svr)
  except Exception, e:
     print svr+': Error in startup up -'+str(e)
     pass


#===================================
# Get environment information
#===================================

def getInfo():
    from xml.dom import minidom
    wlLoc=os.getenv('WL_HOME')
    xmldoc = minidom.parse(wlLoc+'/../domain-registry.xml')
    itemlist = xmldoc.getElementsByTagName('domain')
    if os.path.exists('./zatconfig'): 
       print 'Config file already exists'
    else:
       f=open('./zatconfig','a')
       print >>f,'adminURL=t3://localhost:7001'
       if len(itemlist)>1:
          print 'More than one domain found'
       for s in itemlist:
           print >>f,'domainPath='+(s.attributes['location'].value)
       f.close()

import wl;
import sys;
import os;
import ConfigParser;

def checkLimits(domainHome):
     domName=domainHome.replace('/opt/oracle/product/12c/wls/user_projects/domains/','').upper()
     props = ConfigParser.ConfigParser();
     props.read('./limits.properties');
     sections=props.sections();
     for section in sections:
         if section==domName:
            print str(section)
            options=props.options(section)
            for option in options:
                print 'Max '+option+' Limit = '+str(props.get(section,option))
                if option=='stuckthreads':
                   cd('ThreadPoolRuntime/ThreadPoolRuntime');
                   currentstuckthreads=cmo.getStuckThreadCount();
                   print 'Current stuck threads:'+str(currentstuckthreads)
                   if currentstuckthreads>int(props.get(section,option)):
                      print 'Exceeded Stuck Thread Limit'
                      threadDump()
                   cd('../..');
                if option=='jdbcconnections':
                   cd('JDBCServiceRuntime');
                   svrnames=ls(returnMap='true');
                   for svrname in svrnames:
                       print str(svrname)
                       cd(svrname+'/JDBCDataSourceRuntimeMBeans');
                       dsnames=ls(returnMap='true');
                       for dsname in dsnames:
                           print str(dsname)
                           cd(dsname+'/Instances/data');
                           currrentjdbcconns=cmo.getActiveConnectionsCurrentCount();
                           print 'Current JDBC Connections:'+str(currrentjdbcconns)
                           if currrentjdbcconns>int(props.get(section,option)):
                              print 'Exceeded max jdbc connections'
                           cd('../../..');
                       cd('../..');
                   cd('..');

def connectServers(domainHome):
    domInfo=ConfigParser.ConfigParser();
    domInfo.read('./domainInfo.txt');
    srvrs=domInfo.get('SERVERS','serverlist');
    for srvr in srvrs.split(','):
        port=domInfo.get(srvr.strip(),'serverport');
        machine=domInfo.get(srvr.strip(),'machine');
        print 'Connecting to t3://'+machine+':'+port
        connect('','','t3://'+machine+':'+port);
        serverRuntime();
        checkLimits(domainHome);
        disconnect()

def continuousCheck():
    import time;
    domainhome=os.getenv('DOMAIN_HOME');
    while 1==1:
       connectServers(domainhome);
       print 'Sleeping for 30'
       time.sleep(30);


continuousCheck()

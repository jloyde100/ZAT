import os
import zatcommon

zatcommon.getInfo()

loadProperties("zatconfig")

if not os.path.exists("wl.py"):
   writeIniFile("wl.py")

if os.path.exists("configfile.secure"):
   try:
       connect(userConfigFile="./configfile.secure", userKeyFile="./keyfile.secure", url=adminURL) 
   except:
       print 'Please make sure your Admin Server is running and reachable'
       exit()
else:
   connect()
   storeUserConfig("./configfile.secure","./keyfile.secure")

import zatmenu

command=zatmenu.mainMenu()
while command!='0':
   if command=='1':
      statusLines=zatcommon.getServerStatus()
      columns='Date,Time,Server,Status,Health,Started Date,Time,Heap Free,Heap Max,%HeapUsed'
      heading=''
      for col in columns.split(','):
          heading=heading+col.ljust(15)
      #print 'Column Length - '+str(len(columns.split(',')))

      print heading
      for status in statusLines:
          statusline=''
          #print 'Status Length - '+str(len(status.split(',')))
          for statcol in status.split(','):
              statusline=statusline+statcol.ljust(15)
          print statusline
 
   elif command=='2':
      print 'Enter the server name to start:'
      svrname = sys.stdin.readline();
      zatcommon.startSvr(svrname.strip());
   elif command=='3':
      print 'Enter the server name to stop:'
      svrname = sys.stdin.readline();
      zatcommon.stopSvr(svrname.strip());

   command=zatmenu.mainMenu()

exit()

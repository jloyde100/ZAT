import os

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
import zatcommon

command=zatmenu.mainMenu()
while command!='0':
   if command=='1':
      statusLines=zatcommon.getServerStatus()
      print 'Date,Time,Server,Status,Started Date,Started Time,Heap Free,Heap Max,%HeapUsed'
      for status in statusLines:
          print status 
   elif command=='2':
      print 'Enter the server name to restart:'
      svrname = sys.stdin.readline();
      zatcommon.startSvr(svrname.strip());

   command=zatmenu.mainMenu()

exit()

import os

myurl="t3://localhost:7001"

if not os.path.exists("wl.py"):
   writeIniFile("wl.py")

if os.path.exists("configfile.secure"):
   connect(userConfigFile="./configfile.secure", userKeyFile="./keyfile.secure", url=myurl) 
else:
   connect()
   storeUserConfig("./configfile.secure","./keyfile.secure")

exit()

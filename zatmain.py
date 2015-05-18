import os

loadProperties("zatconfig")

if not os.path.exists("wl.py"):
   writeIniFile("wl.py")

if os.path.exists("configfile.secure"):
   connect(userConfigFile="./configfile.secure", userKeyFile="./keyfile.secure", url=adminURL) 
else:
   connect()
   storeUserConfig("./configfile.secure","./keyfile.secure")

exit()

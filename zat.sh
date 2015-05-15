#!/bin/bash

echo "Welcome to ZAT"

if [ -z "$WL_HOME" ]; then
   echo "You environment is not set properly."
   echo "Please source the setWLSEnv.sh file that comes with weblogic"
else 
   $WL_HOME/common/bin/wlst.sh zatmain.py
fi

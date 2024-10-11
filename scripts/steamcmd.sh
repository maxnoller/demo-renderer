#!/bin/bash

# Check if the environment variable UPDATE_730 is set
if [ -n "$UPDATE_730" ]; then
    /opt/steamcmd/steamcmd.sh +force_install_dir /home/steam/cs2 +login anonymous +app_update 730 validate +quit
else
    /opt/steamcmd/steamcmd.sh +quit
fi

# If steamclient.so is not already there make folder and create symlink
[ -f /root/.steam/sdk64/steamclient.so ] ||
sudo mkdir -p /root/.steam/sdk64/ &&
sudo ln -s /opt/steamcmd/linux64/steamclient.so /root/.steam/sdk64/steamclient.so


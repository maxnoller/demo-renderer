#!/bin/bash

/opt/steamcmd/steamcmd.sh +force_install_dir /home/steam/cs2 +login anonymous +app_update 730 validate +quit

sudo mkdir -p /root/.steam/sdk64
sudo ln -s /opt/steamcmd/linux64/steamclient.so /root/.steam/sdk64/steamclient.so


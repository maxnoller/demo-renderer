#!/bin/bash
export DISPLAY=:99

export STEAM_USERNAME=$(cat /run/secrets/steam_username)
export STEAM_PASS=$(cat /run/secrets/steam_pass)
/usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf

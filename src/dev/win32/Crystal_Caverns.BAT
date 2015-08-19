@echo off
title Crystal Caverns
set MAX_CHANNELS=999999
set STATE_SERVER=4002
set ASTRON_IP=127.0.0.1:7100
set EVENT_LOGGER_IP=127.0.0.1:7198
set DISTRICT_NAME=Crystal
set BASE_CHANNEL=403000000

echo ===============================
echo Starting Crystal Caverns...
echo ppython: "src/dependencies/panda/python/ppython.exe"
echo District name: %DISTRICT_NAME%
echo Base channel: %BASE_CHANNEL%
echo Max channels: %MAX_CHANNELS%
echo State Server: %STATESERVER%
echo Astron IP: %ASTRON_IP%
echo Event Logger IP: %EVENTLOGGER_IP%
echo ===============================

cd ../../../
:main
"src/dependencies/panda/python/ppython.exe" ^
	-m src.toontown.ai.ServiceStart ^
	--base-channel %BASE_CHANNEL% ^
               --max-channels %MAX_CHANNELS% --stateserver %STATE_SERVER% ^
               --astron-ip %ASTRON_IP% --eventlogger-ip %EVENT_LOGGER_IP% ^
               --district-name "%DISTRICT_NAME%"